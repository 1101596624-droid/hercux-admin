"""
课程生成后台 Worker (2026-02-23)

独立进程，从 Redis 队列消费课程生成任务。
使用 asyncio.Semaphore 控制并发数，通过 MAX_CONCURRENT_GENERATIONS 环境变量配置。

启动方式:
    python -m app.services.course_generation.worker

Supervisor 配置:
    [program:hercu-worker]
    command=/www/wwwroot/hercu-backend/venv/bin/python -m app.services.course_generation.worker
    directory=/www/wwwroot/hercu-backend
    ...
"""

import asyncio
import json
import logging
import signal
import sys
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# 确保项目根目录在 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.core.config import settings
from app.db.redis import get_redis
from app.db.session import AsyncSessionLocal
from app.models.models import GenerationTask, GenerationTaskStatus, StudioPackage, StudioPackageStatus
from app.services.course_generation.task_queue import (
    TaskQueueService, QUEUE_KEY, RUNNING_KEY, CANCEL_KEY_PREFIX
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("hercu.worker")

# 优雅退出标记
shutdown_event = asyncio.Event()


async def run_generation_task(task_payload: dict, semaphore: asyncio.Semaphore):
    """执行单个课程生成任务"""
    task_id = task_payload["task_id"]
    redis = await get_redis()

    async with semaphore:
        progress_state: Dict[str, Any] = {
            "status": "running",
            "progress_pct": 1,
            "current_phase": "正在初始化...",
            "chapters_completed": 0,
            "chapters_total": 0,
            "package_id": None,
            "error_message": None,
        }
        heartbeat_stop = asyncio.Event()
        heartbeat_task: Optional[asyncio.Task] = None
        heartbeat_stopped = False

        async def _update_progress(**kwargs):
            for key, value in kwargs.items():
                if key in progress_state:
                    progress_state[key] = value
            await TaskQueueService.update_progress(
                task_id,
                status=progress_state["status"],
                progress_pct=int(progress_state["progress_pct"] or 0),
                current_phase=str(progress_state["current_phase"] or ""),
                chapters_completed=int(progress_state["chapters_completed"] or 0),
                chapters_total=int(progress_state["chapters_total"] or 0),
                package_id=progress_state.get("package_id"),
                error_message=progress_state.get("error_message"),
            )

        async def _heartbeat_loop():
            while not heartbeat_stop.is_set():
                try:
                    await asyncio.wait_for(heartbeat_stop.wait(), timeout=15)
                except asyncio.TimeoutError:
                    try:
                        if await TaskQueueService.is_cancelled(task_id):
                            break
                        await TaskQueueService.update_progress(
                            task_id,
                            status=progress_state["status"],
                            progress_pct=int(progress_state["progress_pct"] or 0),
                            current_phase=str(progress_state["current_phase"] or ""),
                            chapters_completed=int(progress_state["chapters_completed"] or 0),
                            chapters_total=int(progress_state["chapters_total"] or 0),
                            package_id=progress_state.get("package_id"),
                            error_message=progress_state.get("error_message"),
                        )
                    except Exception:
                        logger.exception("任务进度心跳刷新失败: %s", task_id)

        async def _stop_heartbeat():
            nonlocal heartbeat_stopped
            if heartbeat_stopped:
                return
            heartbeat_stopped = True
            heartbeat_stop.set()
            if heartbeat_task is not None:
                await asyncio.gather(heartbeat_task, return_exceptions=True)

        # 标记为运行中
        await redis.sadd(RUNNING_KEY, task_id)
        await _update_progress(
            status="running",
            progress_pct=1,
            current_phase="正在初始化...",
            chapters_completed=0,
            chapters_total=0,
            package_id=None,
            error_message=None,
        )

        async with AsyncSessionLocal() as db:
            # 更新数据库状态
            from sqlalchemy import select, update as sql_update
            await db.execute(
                sql_update(GenerationTask).where(GenerationTask.id == task_id).values(
                    status=GenerationTaskStatus.RUNNING.value,
                    started_at=datetime.now(timezone.utc),
                    completed_at=None,
                    progress_pct=1,
                    current_phase="正在初始化...",
                    chapters_completed=0,
                    chapters_total=0,
                    package_id=None,
                    error_message=None,
                )
            )
            await db.commit()
            heartbeat_task = asyncio.create_task(_heartbeat_loop())

            try:
                from app.api.v1.endpoints.studio import _build_generation_source_material
                from app.schemas.studio import GenerateRequestV2
                from app.services.course_generation import CourseGenerationService

                service = CourseGenerationService(db=db)
                package_data = None
                chapters_total = 0
                await _update_progress(progress_pct=3, current_phase="正在解析素材...")
                try:
                    resolved_source_material = await _build_generation_source_material(
                        GenerateRequestV2(
                            source_material=task_payload.get("source_material", "") or "",
                            source_upload_ids=[],
                            course_title=task_payload.get("course_title", ""),
                            processor_id=task_payload.get("processor_id", "") or "default",
                            source_info=task_payload.get("source_info", "") or "",
                        )
                    )
                except Exception as exc:
                    detail = getattr(exc, "detail", None)
                    if detail is not None and not isinstance(detail, str):
                        detail = json.dumps(detail, ensure_ascii=False)
                    raise RuntimeError(f"素材解析失败: {detail or str(exc)}") from exc

                await _update_progress(progress_pct=5, current_phase="素材解析完成，开始生成大纲...")

                async for event in service.generate_course_stream(
                    course_title=task_payload["course_title"],
                    source_material=resolved_source_material,
                    source_info=task_payload.get("source_info", ""),
                    processor_id=task_payload.get("processor_id", ""),
                    processor_prompt=task_payload.get("processor_prompt"),
                ):
                    # 检查取消标记
                    if await TaskQueueService.is_cancelled(task_id):
                        logger.info(f"任务被取消: {task_id}")
                        await db.execute(
                            sql_update(GenerationTask).where(GenerationTask.id == task_id).values(
                                status=GenerationTaskStatus.CANCELLED.value,
                                completed_at=datetime.now(timezone.utc),
                                current_phase="任务已取消",
                                error_message="用户取消",
                            )
                        )
                        await db.commit()
                        await _update_progress(
                            status=GenerationTaskStatus.CANCELLED.value,
                            current_phase="任务已取消",
                            error_message="用户取消",
                        )
                        await redis.delete(f"{CANCEL_KEY_PREFIX}{task_id}")
                        return

                    event_type = event.get("event", "")
                    event_data = event.get("data", {})

                    # 根据事件类型更新进度
                    if event_type == "outline":
                        outline = event_data.get("outline", {})
                        chapters_total = len(outline.get("chapters", []))
                        await _update_progress(
                            current_phase="大纲已生成，开始生成章节...",
                            chapters_total=chapters_total,
                            progress_pct=10,
                        )

                    elif event_type == "chapter_start":
                        idx = event_data.get("index", 0)
                        title = event_data.get("title", "")
                        await _update_progress(
                            current_phase=f"正在生成第{idx+1}章: {title}",
                            chapters_completed=idx,
                            progress_pct=10 + int(80 * idx / max(chapters_total, 1)),
                        )

                    elif event_type == "chapter_complete":
                        idx = event_data.get("index", 0)
                        await _update_progress(
                            chapters_completed=idx + 1,
                            progress_pct=10 + int(80 * (idx + 1) / max(chapters_total, 1)),
                        )

                    elif event_type == "complete":
                        package_data = event_data.get("package")
                        await _update_progress(
                            current_phase="正在保存课程包...",
                            progress_pct=95,
                        )
                    elif event_type == "error":
                        err_msg = ""
                        err_phase = ""
                        if isinstance(event_data, dict):
                            err_msg = str(event_data.get("message", "")).strip()
                            err_phase = str(event_data.get("phase", "")).strip()
                        else:
                            err_msg = str(event_data).strip()

                        if not err_msg:
                            err_msg = "课程生成失败（生成服务返回 error 事件）"
                        if err_phase:
                            err_msg = f"[{err_phase}] {err_msg}"
                        raise RuntimeError(err_msg)

                # 保存课程包
                if package_data:
                    pkg_id = await _save_package(db, package_data, task_payload.get("processor_id", ""))

                    # 自动发布到课程管理系统
                    course_id = await _auto_publish_package(db, pkg_id)
                    if course_id:
                        logger.info(f"课程包已自动发布: {pkg_id} -> course_id={course_id}")
                    else:
                        logger.warning(f"课程包自动发布失败: {pkg_id}")

                    # 入库成功 → 删除任务记录；入库失败 → 保留记录供排查
                    if course_id:
                        await _update_progress(
                            status="completed",
                            progress_pct=100,
                            current_phase="课程生成完成",
                            package_id=pkg_id,
                            error_message=None,
                        )
                        await db.execute(
                            sql_update(GenerationTask).where(GenerationTask.id == task_id).values(
                                status=GenerationTaskStatus.COMPLETED.value,
                                completed_at=datetime.now(timezone.utc),
                                package_id=pkg_id,
                                current_phase="课程生成完成",
                                progress_pct=100,
                                error_message=None,
                            )
                        )
                        await db.commit()
                        await redis.delete(f"{CANCEL_KEY_PREFIX}{task_id}")
                        logger.info(f"任务完成并保留记录: {task_id}, 课程包: {pkg_id}, course_id: {course_id}")
                    else:
                        await db.execute(
                            sql_update(GenerationTask).where(GenerationTask.id == task_id).values(
                                status=GenerationTaskStatus.FAILED.value,
                                completed_at=datetime.now(timezone.utc),
                                package_id=pkg_id,
                                error_message="课程包已保存但自动发布失败，请手动发布",
                            )
                        )
                        await db.commit()
                        await _update_progress(
                            status="failed",
                            progress_pct=100,
                            current_phase="自动发布失败", package_id=pkg_id,
                            error_message="课程包已保存但自动发布失败，请手动发布",
                        )
                        logger.warning(f"任务部分完成: {task_id}, 课程包已保存({pkg_id})但发布失败")
                else:
                    raise RuntimeError("生成流结束但未收到 complete 事件")

            except Exception as e:
                logger.error(f"任务失败: {task_id}, 错误: {e}", exc_info=True)
                error_msg = str(e)[:500]
                await db.execute(
                    sql_update(GenerationTask).where(GenerationTask.id == task_id).values(
                        status=GenerationTaskStatus.FAILED.value,
                        completed_at=datetime.now(timezone.utc),
                        error_message=error_msg,
                    )
                )
                await db.commit()
                await _update_progress(
                    status="failed",
                    error_message=error_msg,
                    current_phase="生成失败",
                )
            finally:
                await _stop_heartbeat()
                await redis.srem(RUNNING_KEY, task_id)


async def _save_package(db, pkg: dict, processor_id: str) -> str:
    """保存课程包到数据库，返回 package_id"""
    import uuid as uuid_mod
    meta = pkg.get("meta", {})
    pkg_id = pkg.get("id", str(uuid_mod.uuid4()))
    package = StudioPackage(
        id=pkg_id,
        title=meta.get("title", "Untitled"),
        description=meta.get("description", ""),
        source_info=meta.get("source_info", ""),
        style=meta.get("style", processor_id),
        status=StudioPackageStatus.DRAFT,
        meta=meta,
        lessons=pkg.get("lessons", []),
        edges=pkg.get("edges", []),
        global_ai_config=pkg.get("global_ai_config", {}),
        total_lessons=meta.get("total_lessons", len(pkg.get("lessons", []))),
        estimated_hours=meta.get("estimated_hours", 0),
        processor_id=processor_id,
    )
    db.add(package)
    await db.commit()
    return pkg_id


async def _auto_publish_package(db, package_id: str) -> Optional[int]:
    """自动将课程包发布到课程管理系统，返回 course_id"""
    try:
        import uuid as uuid_mod
        from sqlalchemy import select
        from app.services.package_importer import PackageImporterV2, CoursePackageV2

        result = await db.execute(
            select(StudioPackage).where(StudioPackage.id == package_id)
        )
        package = result.scalar_one_or_none()
        if not package:
            logger.error(f"自动发布失败: 找不到课程包 {package_id}")
            return None

        # 给缺少 id 的 edges 补上
        edges = package.edges or []
        for edge in edges:
            if "id" not in edge:
                edge["id"] = str(uuid_mod.uuid4())

        package_data = {
            "id": package.id,
            "version": "2.0.0",
            "meta": package.meta or {
                "title": package.title,
                "description": package.description or "",
                "source_info": package.source_info or "",
                "total_lessons": package.total_lessons or 0,
                "estimated_hours": package.estimated_hours or 0,
                "style": package.style or "default",
            },
            "lessons": package.lessons or [],
            "edges": edges,
            "global_ai_config": package.global_ai_config or {},
        }

        course_package = CoursePackageV2(**package_data)
        importer = PackageImporterV2(db)
        import_result = await importer.import_package(course_package)

        package.status = StudioPackageStatus.PUBLISHED
        package.course_id = import_result["course_id"]
        await db.commit()

        return import_result["course_id"]
    except Exception as e:
        logger.error(f"自动发布课程包失败 {package_id}: {e}", exc_info=True)
        await db.rollback()
        return None


async def worker_loop():
    """Worker 主循环：从 Redis 队列取任务并执行"""
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_GENERATIONS)
    redis = await get_redis()
    tasks = set()

    # === 启动清理：重置 Redis running set ===
    stale_count = await redis.scard(RUNNING_KEY)
    if stale_count > 0:
        logger.warning(f"清理 {stale_count} 个僵尸 running 任务")
        await redis.delete(RUNNING_KEY)

    # 将数据库中 status=running 的任务重置为 pending 并重新入队
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select, update as sql_update
        result = await db.execute(
            select(GenerationTask).where(GenerationTask.status == GenerationTaskStatus.RUNNING.value)
        )
        stale_tasks = result.scalars().all()
        for t in stale_tasks:
            await db.execute(
                sql_update(GenerationTask).where(GenerationTask.id == t.id).values(
                    status=GenerationTaskStatus.PENDING.value,
                    started_at=None,
                )
            )
            payload = json.dumps({
                "task_id": t.id,
                "admin_id": t.admin_id,
                "course_title": t.course_title,
                "source_material": t.source_material or "",
                "source_info": t.source_info or "",
                "processor_id": t.processor_id or "",
                "processor_prompt": t.processor_prompt,
            }, ensure_ascii=False)
            await redis.rpush(QUEUE_KEY, payload)
            logger.info(f"重新入队: {t.id} - {t.course_title}")
        await db.commit()

    logger.info(f"Worker 启动，最大并发: {settings.MAX_CONCURRENT_GENERATIONS}")

    while not shutdown_event.is_set():
        try:
            # 清理已完成的 task
            done = {t for t in tasks if t.done()}
            for t in done:
                try:
                    t.result()  # 触发异常（如果有）
                except Exception as e:
                    logger.error(f"任务异常: {e}")
            tasks -= done

            # 从队列取任务（阻塞1秒）
            item = await redis.blpop(QUEUE_KEY, timeout=1)
            if item is None:
                continue

            _, payload_str = item
            payload = json.loads(payload_str)
            task_id = payload.get("task_id")

            # 检查是否已取消
            if await TaskQueueService.is_cancelled(task_id):
                logger.info(f"跳过已取消的任务: {task_id}")
                continue

            logger.info(f"开始处理任务: {task_id} - {payload.get('course_title')}")
            task = asyncio.create_task(run_generation_task(payload, semaphore))
            tasks.add(task)

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Worker 循环异常: {e}", exc_info=True)
            await asyncio.sleep(2)

    # 等待所有运行中的任务完成
    if tasks:
        logger.info(f"等待 {len(tasks)} 个任务完成...")
        await asyncio.gather(*tasks, return_exceptions=True)

    logger.info("Worker 已停止")


def handle_shutdown(signum, frame):
    """信号处理：优雅退出"""
    logger.info(f"收到信号 {signum}，准备退出...")
    shutdown_event.set()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    logger.info("=" * 50)
    logger.info("HERCU 课程生成 Worker 启动")
    logger.info(f"最大并发生成数: {settings.MAX_CONCURRENT_GENERATIONS}")
    logger.info(f"任务超时: {settings.GENERATION_TASK_TIMEOUT}s")
    logger.info("=" * 50)

    asyncio.run(worker_loop())
