"""
课程生成任务队列服务 (2026-02-23)

基于 Redis 的轻量级任务队列，支持：
- 提交生成任务到队列
- 查询任务状态和进度
- 取消排队中/进行中的任务
- 并发控制（通过 MAX_CONCURRENT_GENERATIONS 配置）

所有并发参数通过环境变量控制，升配服务器只需改配置。
"""

import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.redis import get_redis
from app.db.session import AsyncSessionLocal
from app.models.models import GenerationTask, GenerationTaskStatus

logger = logging.getLogger(__name__)

# Redis key 前缀
QUEUE_KEY = "hercu:gen:queue"                    # 任务队列 (Redis List)
PROGRESS_KEY_PREFIX = "hercu:gen:progress:"      # 任务进度 (Redis Hash)
RUNNING_KEY = "hercu:gen:running"                # 正在运行的任务集合 (Redis Set)
CANCEL_KEY_PREFIX = "hercu:gen:cancel:"          # 取消标记 (Redis Key)
REQUEST_DEDUP_KEY_PREFIX = "hercu:gen:reqdedup:"  # 客户端请求幂等键


class TaskQueueService:
    """课程生成任务队列"""

    _REQUIRED_PROGRESS_FIELDS = {
        "status",
        "progress_pct",
        "current_phase",
        "chapters_completed",
        "chapters_total",
    }

    @staticmethod
    def _progress_key(task_id: str) -> str:
        return f"{PROGRESS_KEY_PREFIX}{task_id}"

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _is_progress_complete(progress: Dict[str, Any]) -> bool:
        if not progress:
            return False
        return all(field in progress for field in TaskQueueService._REQUIRED_PROGRESS_FIELDS)

    @staticmethod
    def _normalize_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
        status = str(snapshot.get("status") or GenerationTaskStatus.PENDING.value)
        progress_pct = max(0, min(100, TaskQueueService._safe_int(snapshot.get("progress_pct"), 0)))
        chapters_completed = max(0, TaskQueueService._safe_int(snapshot.get("chapters_completed"), 0))
        chapters_total = max(0, TaskQueueService._safe_int(snapshot.get("chapters_total"), 0))
        current_phase = str(snapshot.get("current_phase") or "")
        package_id = snapshot.get("package_id")
        error_message = snapshot.get("error_message")
        if isinstance(package_id, bytes):
            package_id = package_id.decode("utf-8", errors="ignore")
        if isinstance(error_message, bytes):
            error_message = error_message.decode("utf-8", errors="ignore")
        if not current_phase:
            if status == GenerationTaskStatus.PENDING.value:
                current_phase = "排队中"
            elif status == GenerationTaskStatus.RUNNING.value:
                current_phase = "处理中"
        return {
            "status": status,
            "progress_pct": progress_pct,
            "current_phase": current_phase,
            "chapters_completed": chapters_completed,
            "chapters_total": chapters_total,
            "package_id": package_id or "",
            "error_message": error_message or "",
        }

    @staticmethod
    def _snapshot_to_redis_mapping(snapshot: Dict[str, Any]) -> Dict[str, str]:
        normalized = TaskQueueService._normalize_snapshot(snapshot)
        return {
            "status": normalized["status"],
            "progress_pct": str(normalized["progress_pct"]),
            "current_phase": normalized["current_phase"],
            "chapters_completed": str(normalized["chapters_completed"]),
            "chapters_total": str(normalized["chapters_total"]),
            "package_id": normalized["package_id"],
            "error_message": normalized["error_message"],
        }

    @staticmethod
    def _snapshot_from_task(task: GenerationTask) -> Dict[str, Any]:
        return TaskQueueService._normalize_snapshot({
            "status": task.status,
            "progress_pct": task.progress_pct or 0,
            "current_phase": task.current_phase or "",
            "chapters_completed": task.chapters_completed or 0,
            "chapters_total": task.chapters_total or 0,
            "package_id": task.package_id or "",
            "error_message": task.error_message or "",
        })

    @staticmethod
    async def _write_progress_snapshot(redis, task_id: str, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        normalized = TaskQueueService._normalize_snapshot(snapshot)
        await redis.hset(TaskQueueService._progress_key(task_id), mapping=TaskQueueService._snapshot_to_redis_mapping(normalized))
        await redis.expire(TaskQueueService._progress_key(task_id), settings.GENERATION_PROGRESS_TTL)
        return normalized

    @staticmethod
    async def _load_db_task(task_id: str) -> Optional[GenerationTask]:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(GenerationTask).where(GenerationTask.id == task_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def submit_task(
        admin_id: int,
        course_title: str,
        source_material: str,
        source_info: str,
        processor_id: str,
        processor_prompt: Optional[str] = None,
        client_request_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        """提交生成任务到队列"""
        task_id = str(uuid.uuid4())
        redis = await get_redis()
        dedupe_key: Optional[str] = None

        # 幂等提交：同一 admin + client_request_id 只创建一个任务
        if client_request_id:
            dedupe_key = f"{REQUEST_DEDUP_KEY_PREFIX}{admin_id}:{client_request_id.strip()}"
            existing_task_id = await redis.get(dedupe_key)
            if existing_task_id:
                if isinstance(existing_task_id, bytes):
                    existing_task_id = existing_task_id.decode("utf-8", errors="ignore")
                status = await TaskQueueService.get_task_status(str(existing_task_id))
                if status:
                    logger.info("任务幂等命中: admin=%s request_id=%s task=%s", admin_id, client_request_id, existing_task_id)
                    return {
                        "task_id": str(existing_task_id),
                        "status": status.get("status", "pending"),
                        "queue_position": 0,
                        "deduplicated": True,
                    }
                await redis.delete(dedupe_key)

        # 检查队列长度
        queue_len = await redis.llen(QUEUE_KEY)
        if queue_len >= settings.GENERATION_QUEUE_MAX_SIZE:
            raise ValueError(f"生成队列已满（{queue_len}/{settings.GENERATION_QUEUE_MAX_SIZE}），请稍后再试")

        # 清理 source_material 中的 null 字节和控制字符（PDF 提取可能带入）
        import re
        source_material = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', source_material)

        # 写入数据库
        should_close = False
        if db is None:
            db = AsyncSessionLocal()
            should_close = True

        try:
            task = GenerationTask(
                id=task_id,
                admin_id=admin_id,
                status=GenerationTaskStatus.PENDING.value,
                course_title=course_title,
                source_material=source_material,
                source_info=source_info,
                processor_id=processor_id,
                processor_prompt=processor_prompt,
                progress_pct=0,
                current_phase="排队中",
                chapters_completed=0,
                chapters_total=0,
            )
            db.add(task)
            await db.commit()

            # 推入 Redis 队列
            task_payload = json.dumps({
                "task_id": task_id,
                "admin_id": admin_id,
                "course_title": course_title,
                "source_material": source_material,
                "source_info": source_info,
                "processor_id": processor_id,
                "processor_prompt": processor_prompt,
            }, ensure_ascii=False)
            await redis.rpush(QUEUE_KEY, task_payload)

            # 初始化进度（完整快照）
            await TaskQueueService._write_progress_snapshot(
                redis,
                task_id,
                {
                    "status": GenerationTaskStatus.PENDING.value,
                    "progress_pct": 0,
                    "current_phase": "排队中",
                    "chapters_completed": 0,
                    "chapters_total": 0,
                    "package_id": "",
                    "error_message": "",
                },
            )
            await redis.hset(TaskQueueService._progress_key(task_id), mapping={
                "queue_position": str(queue_len + 1),
            })
            if dedupe_key:
                await redis.set(
                    dedupe_key,
                    task_id,
                    ex=max(86400, settings.GENERATION_PROGRESS_TTL),
                )

            logger.info(f"任务已提交: {task_id}, 队列位置: {queue_len + 1}")

            return {
                "task_id": task_id,
                "status": "pending",
                "queue_position": queue_len + 1,
                "deduplicated": False,
            }
        finally:
            if should_close:
                await db.close()

    @staticmethod
    async def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态和进度（优先 Redis，缺失时回退 DB 并回补 Redis）"""
        redis = await get_redis()
        progress = await redis.hgetall(TaskQueueService._progress_key(task_id))
        if TaskQueueService._is_progress_complete(progress):
            normalized = TaskQueueService._normalize_snapshot(progress)
            return {
                "task_id": task_id,
                "status": normalized["status"],
                "progress_pct": normalized["progress_pct"],
                "current_phase": normalized["current_phase"],
                "chapters_completed": normalized["chapters_completed"],
                "chapters_total": normalized["chapters_total"],
                "package_id": normalized["package_id"] or None,
                "error_message": normalized["error_message"] or None,
            }

        task = await TaskQueueService._load_db_task(task_id)
        if not task:
            return None

        snapshot = TaskQueueService._snapshot_from_task(task)
        if task.status in (GenerationTaskStatus.PENDING.value, GenerationTaskStatus.RUNNING.value) or progress:
            await TaskQueueService._write_progress_snapshot(redis, task_id, snapshot)

        return {
            "task_id": task_id,
            "status": snapshot["status"],
            "progress_pct": snapshot["progress_pct"],
            "current_phase": snapshot["current_phase"],
            "chapters_completed": snapshot["chapters_completed"],
            "chapters_total": snapshot["chapters_total"],
            "course_title": task.course_title,
            "package_id": snapshot["package_id"] or None,
            "error_message": snapshot["error_message"] or None,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }

    @staticmethod
    async def update_progress(
        task_id: str,
        status: Optional[str] = None,
        progress_pct: Optional[int] = None,
        current_phase: Optional[str] = None,
        chapters_completed: Optional[int] = None,
        chapters_total: Optional[int] = None,
        package_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        """更新任务进度（Redis 全量快照 + DB 关键字段回写）"""
        redis = await get_redis()
        progress_key = TaskQueueService._progress_key(task_id)
        current_progress = await redis.hgetall(progress_key)
        snapshot: Dict[str, Any]

        if TaskQueueService._is_progress_complete(current_progress):
            snapshot = TaskQueueService._normalize_snapshot(current_progress)
        else:
            task = await TaskQueueService._load_db_task(task_id)
            if task is None and not current_progress:
                # 任务已经被删除，避免重建僵尸进度键
                return
            if task is not None:
                snapshot = TaskQueueService._snapshot_from_task(task)
            else:
                snapshot = TaskQueueService._normalize_snapshot(current_progress)

        if status is not None:
            snapshot["status"] = status
        if progress_pct is not None:
            snapshot["progress_pct"] = progress_pct
        if current_phase is not None:
            snapshot["current_phase"] = current_phase
        if chapters_completed is not None:
            snapshot["chapters_completed"] = chapters_completed
        if chapters_total is not None:
            snapshot["chapters_total"] = chapters_total
        if package_id is not None:
            snapshot["package_id"] = package_id
        if error_message is not None:
            snapshot["error_message"] = error_message

        normalized = await TaskQueueService._write_progress_snapshot(redis, task_id, snapshot)

        # 关键字段回写 DB，防止 Redis 键失效后状态丢失
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(GenerationTask).where(GenerationTask.id == task_id).values(
                    status=normalized["status"],
                    progress_pct=normalized["progress_pct"],
                    current_phase=normalized["current_phase"],
                    chapters_completed=normalized["chapters_completed"],
                    chapters_total=normalized["chapters_total"],
                    package_id=normalized["package_id"] or None,
                    error_message=normalized["error_message"] or None,
                )
            )
            await db.commit()

    @staticmethod
    async def cancel_task(task_id: str, admin_id: int) -> bool:
        """取消任务（排队中直接移除，运行中设置取消标记）"""
        redis = await get_redis()

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(GenerationTask).where(
                    GenerationTask.id == task_id,
                    GenerationTask.admin_id == admin_id,
                )
            )
            task = result.scalar_one_or_none()
            if not task:
                return False

            if task.status in (GenerationTaskStatus.COMPLETED.value, GenerationTaskStatus.CANCELLED.value):
                return False

            if task.status == GenerationTaskStatus.PENDING.value:
                # 排队中：从队列移除
                queue_items = await redis.lrange(QUEUE_KEY, 0, -1)
                for item in queue_items:
                    data = json.loads(item)
                    if data.get("task_id") == task_id:
                        await redis.lrem(QUEUE_KEY, 1, item)
                        break

            elif task.status == GenerationTaskStatus.RUNNING.value:
                # 运行中：设置取消标记，Worker 会检查并退出
                await redis.set(f"{CANCEL_KEY_PREFIX}{task_id}", "1", ex=600)

            # 从 RUNNING_KEY 移除（无论是否在里面）
            await redis.srem(RUNNING_KEY, task_id)

            # 保留任务记录，便于退出登录/关闭应用后回看历史
            await db.execute(
                update(GenerationTask).where(GenerationTask.id == task_id).values(
                    status=GenerationTaskStatus.CANCELLED.value,
                    completed_at=datetime.now(timezone.utc),
                    current_phase="任务已取消",
                    error_message="用户取消",
                )
            )
            await db.commit()

            await TaskQueueService.update_progress(
                task_id,
                status=GenerationTaskStatus.CANCELLED.value,
                current_phase="任务已取消",
                error_message="用户取消",
            )
            # 注意：running 任务取消依赖 cancel key，让 worker 感知后优雅退出

            logger.info(f"任务已取消并保留记录: {task_id}")
            return True

    @staticmethod
    async def is_cancelled(task_id: str) -> bool:
        """检查任务是否被取消（Worker 在生成过程中定期调用）"""
        redis = await get_redis()
        return await redis.exists(f"{CANCEL_KEY_PREFIX}{task_id}") > 0

    @staticmethod
    async def list_tasks(admin_id: Optional[int] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """获取任务列表"""
        async with AsyncSessionLocal() as db:
            query = select(GenerationTask).order_by(GenerationTask.created_at.desc()).limit(limit)
            if admin_id is not None:
                query = query.where(GenerationTask.admin_id == admin_id)
            result = await db.execute(query)
            tasks = result.scalars().all()

            task_list = []
            redis = await get_redis()
            for t in tasks:
                snapshot = TaskQueueService._snapshot_from_task(t)
                if t.status in (GenerationTaskStatus.PENDING.value, GenerationTaskStatus.RUNNING.value):
                    progress = await redis.hgetall(TaskQueueService._progress_key(t.id))
                    if TaskQueueService._is_progress_complete(progress):
                        snapshot = TaskQueueService._normalize_snapshot(progress)
                    else:
                        # Redis 缺失/不完整时以 DB 为准回补，避免出现 unknown
                        await TaskQueueService._write_progress_snapshot(redis, t.id, snapshot)

                task_list.append({
                    "task_id": t.id,
                    "course_title": t.course_title,
                    "status": snapshot["status"],
                    "progress_pct": snapshot["progress_pct"],
                    "current_phase": snapshot["current_phase"],
                    "chapters_completed": snapshot["chapters_completed"],
                    "chapters_total": snapshot["chapters_total"],
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "started_at": t.started_at.isoformat() if t.started_at else None,
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                    "package_id": snapshot["package_id"] or t.package_id,
                    "error_message": snapshot["error_message"] or t.error_message,
                })

            return task_list

    @staticmethod
    async def delete_task(task_id: str, admin_id: int) -> bool:
        """删除任务记录（仅允许删除已完成/已取消/失败的任务）"""
        redis = await get_redis()

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(GenerationTask).where(
                    GenerationTask.id == task_id,
                    GenerationTask.admin_id == admin_id,
                )
            )
            task = result.scalar_one_or_none()
            if not task:
                return False

            if task.status in (GenerationTaskStatus.PENDING.value, GenerationTaskStatus.RUNNING.value):
                return False  # 不允许删除进行中的任务

            await db.delete(task)
            await db.commit()

        # 清理 Redis
        await redis.delete(f"{PROGRESS_KEY_PREFIX}{task_id}")
        await redis.delete(f"{CANCEL_KEY_PREFIX}{task_id}")
        await redis.srem(RUNNING_KEY, task_id)

        logger.info(f"任务已删除: {task_id}")
        return True

    @staticmethod
    async def retry_task(task_id: str, admin_id: int) -> Optional[Dict[str, Any]]:
        """重试已取消/失败的任务（用原参数重新提交）"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(GenerationTask).where(
                    GenerationTask.id == task_id,
                    GenerationTask.admin_id == admin_id,
                )
            )
            task = result.scalar_one_or_none()
            if not task:
                return None

            if task.status not in (GenerationTaskStatus.CANCELLED.value, GenerationTaskStatus.FAILED.value):
                return None

            # 用原参数重新提交
            return await TaskQueueService.submit_task(
                admin_id=admin_id,
                course_title=task.course_title,
                source_material=task.source_material,
                source_info=task.source_info or "",
                processor_id=task.processor_id or "",
                processor_prompt=task.processor_prompt,
                client_request_id=None,
            )

    @staticmethod
    async def get_queue_info() -> Dict[str, Any]:
        """获取队列概况"""
        redis = await get_redis()
        queue_len = await redis.llen(QUEUE_KEY)
        running_count = await redis.scard(RUNNING_KEY)
        return {
            "queue_length": queue_len,
            "running_count": running_count,
            "max_concurrent": settings.MAX_CONCURRENT_GENERATIONS,
            "max_queue_size": settings.GENERATION_QUEUE_MAX_SIZE,
        }
