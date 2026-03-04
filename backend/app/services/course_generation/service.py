"""
课程生成服务 - 监督者+生成者架构的主入口
"""

import json
import logging
import uuid
import io
import os
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

import httpx

from .supervisor import CourseSupervisor
from .generator import ChapterGenerator, GeneratorPromptBuilder
from .models import (
    GenerationState, CourseOutline, ChapterResult, ReviewResult,
    ReviewStatus, ChapterQualityStandards, ChapterOutline,
    HTMLSimulatorSpec, HTMLSimulatorQualityScore, HTMLSimulatorQualityStandards
)
from .standards_loader import get_standards_loader
from app.services.gemini_service import gemini_service
from app.services.storage_service import storage_service
from app.core.config import settings

logger = logging.getLogger(__name__)
LLM_OUTPUT_TOKEN_LIMIT = 8192


class StepContentRetryExhaustedError(RuntimeError):
    """步骤重试耗尽，触发章节级重试或失败。"""


class CourseGenerationService:
    """
    课程生成服务

    使用监督者+生成者架构：
    - 监督者：生成大纲、审核章节、决定是否重做
    - 生成者：根据指令生成单个章节
    """

    def __init__(self, db=None):
        self.db = db  # 保存db用于动态阈值计算
        self.supervisor = CourseSupervisor()
        self.generator = ChapterGenerator(db=db)  # 传递db用于模板学习 (2026-02-11)
        self.standards_loader = get_standards_loader()  # 新增：标准加载器

    async def generate_course_stream(
        self,
        course_title: str,
        source_material: str,
        source_info: str,
        processor_id: str,
        processor_prompt: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式生成课程

        Yields SSE events:
        - phase: 阶段更新
        - outline: 大纲生成完成
        - chapter_start: 开始生成章节
        - chunk: 内容片段
        - chapter_review: 章节审核结果
        - chapter_complete: 章节完成
        - chapter_retry: 章节重试
        - complete: 全部完成
        - error: 错误
        """

        # 初始化状态
        state = GenerationState(
            course_title=course_title,
            source_material=source_material,
            source_info=source_info,
            processor_id=processor_id
        )

        system_prompt = processor_prompt or self._get_default_system_prompt(processor_id)
        generator_system_prompt = GeneratorPromptBuilder.build_system_prompt(processor_id)

        try:
            # === 阶段1：生成大纲 ===
            yield {
                "event": "phase",
                "data": {
                    "phase": 1,
                    "message": "监督者正在分析源材料，生成课程大纲...",
                    "processor": {"id": processor_id}
                }
            }

            # 【新增】加载处理器结构约束
            processor_constraints = None
            try:
                from app.models.models import StudioProcessor
                from sqlalchemy import select
                result = await self.db.execute(
                    select(StudioProcessor).where(StudioProcessor.id == processor_id)
                )
                processor = result.scalar_one_or_none()
                if processor and processor.structure_constraints:
                    processor_constraints = processor.structure_constraints
                    logger.info(f"Loaded processor constraints: {processor_constraints}")
            except Exception as e:
                logger.error(f"Failed to load processor constraints: {e}")
                raise

            outline = await self.supervisor.generate_outline(state, system_prompt, processor_constraints)

            # === 新增：自动识别学科并记录到状态 ===
            classification = self.detect_course_subject(course_title, outline)
            state.subject_classification = classification  # 保存到状态中供后续使用

            logger.info(f"Course classified as '{classification['subject_name']}' with confidence {classification['confidence']:.2f}")

            yield {
                "event": "outline",
                "data": {
                    "outline": {
                        "title": outline.title,
                        "description": outline.description,
                        "total_chapters": outline.total_chapters,
                        "estimated_hours": outline.estimated_hours,
                        "difficulty": outline.difficulty,
                        "chapters": [
                            {
                                "index": ch.index,
                                "title": ch.title,
                                "chapter_type": ch.chapter_type.value,
                                "suggested_simulator": ch.suggested_simulator
                            }
                            for ch in outline.chapters
                        ]
                    },
                    "classification": classification  # 新增：返回学科分类信息
                }
            }

            # === 阶段2：逐章生成 ===
            yield {
                "event": "phase",
                "data": {
                    "phase": 2,
                    "message": "开始生成章节内容...",
                    "processor": {"id": processor_id}
                }
            }

            for chapter_index in range(outline.total_chapters):
                chapter_outline = outline.chapters[chapter_index]

                # 重置单步重试计数（新章节）
                state.reset_step_retries()
                state.current_attempt = 0
                state.last_json_error = None
                state.json_fix_guidance = None
                state.last_step_error = None
                state.step_fix_guidance = None

                # 通知开始生成章节
                yield {
                    "event": "chapter_start",
                    "data": {
                        "index": chapter_index,
                        "total": outline.total_chapters,
                        "title": chapter_outline.title,
                        "attempt": state.current_attempt + 1
                    }
                }

                # 生成并审核章节（可能多次重试）
                chapter = None
                review = None

                while state.can_retry():
                    # 获取生成提示词
                    prompt = self.supervisor.get_chapter_generation_prompt(
                        state=state,
                        chapter_index=chapter_index,
                        previous_rejection=review if review and not review.is_approved() else None
                    )

                    # 流式生成章节
                    full_response = ""
                    async for chunk in self.generator.generate_chapter_stream(
                        prompt=prompt,
                        system_prompt=generator_system_prompt
                    ):
                        full_response += chunk
                        yield {
                            "event": "chunk",
                            "data": {
                                "content": chunk,
                                "chapter_index": chapter_index,
                                "attempt": state.current_attempt + 1
                            }
                        }

                    # 解析章节
                    try:
                        chapter = self.generator.parse_streaming_response(full_response)

                        # === 碎片化检查第1步：检查章节骨架 ===
                        skeleton_check = await self.supervisor.check_chapter_skeleton(
                            state=state,
                            chapter=chapter,
                            chapter_index=chapter_index
                        )

                        if not skeleton_check['approved']:
                            yield {
                                "event": "skeleton_check",
                                "data": {
                                    "chapter_index": chapter_index,
                                    "approved": False,
                                    "action": skeleton_check['action'],
                                    "issues": skeleton_check['issues']
                                }
                            }

                            if skeleton_check['action'] == 'regenerate':
                                # 骨架问题太多，需要重新生成
                                state.increment_attempt()
                                if state.can_retry():
                                    yield {
                                        "event": "chapter_retry",
                                        "data": {
                                            "index": chapter_index,
                                            "attempt": state.current_attempt,
                                            "reason": "章节骨架结构问题过多，需要重新生成",
                                            "issues": skeleton_check['issues']
                                        }
                                    }
                                    continue
                                raise RuntimeError(
                                    f"Chapter {chapter_index + 1} skeleton check requires regenerate but retries exhausted: "
                                    f"{'; '.join(skeleton_check['issues'])}"
                                )
                            # action == 'revise' 时继续，后续步骤会修复

                        # === 分步生成：填充所有长文本内容（带步骤检测）===
                        chapter = await self._generate_all_content_with_check(
                            chapter=chapter,
                            chapter_outline=chapter_outline,
                            generator_system_prompt=generator_system_prompt,
                            state=state
                        )

                        # === 碎片化检查第2步：逐步检查并生成模拟器代码 ===
                        async for sim_event in self._generate_simulator_codes_with_check(
                            chapter=chapter,
                            chapter_outline=chapter_outline,
                            generator_system_prompt=generator_system_prompt,
                            state=state,
                            chapter_index=chapter_index
                        ):
                            if sim_event.get("event") == "_chapter_done":
                                chapter = sim_event["data"]["chapter"]
                            else:
                                yield sim_event

                        # 重置上次失败痕迹，避免污染后续章节提示词
                        state.last_json_error = None
                        state.json_fix_guidance = None
                        state.last_step_error = None
                        state.step_fix_guidance = None

                        # === 步骤检测已完成，跳过章节级别评审，直接通过 ===
                        logger.info(f"Chapter {chapter_index + 1} step-by-step check completed, skipping chapter review")
                        break

                    except ValueError as e:
                        logger.error(f"Failed to parse chapter {chapter_index + 1}: {e}")
                        error_type, is_truncated = self._classify_json_parse_failure(str(e), full_response)

                        # 让监督者分析 JSON 错误并生成修复指导（按失败原因）
                        json_fix_guidance = await self.supervisor.analyze_json_error(
                            raw_response=full_response,
                            error_message=str(e),
                            chapter_index=chapter_index,
                            error_type=error_type,
                            is_truncated=is_truncated
                        )
                        state.last_json_error = f"{error_type}: {str(e)}"
                        state.json_fix_guidance = json_fix_guidance

                        state.increment_attempt()

                        if state.can_retry():
                            yield {
                                "event": "skeleton_retry",
                                "data": {
                                    "index": chapter_index,
                                    "attempt": state.current_attempt,
                                    "reason": "骨架JSON解析失败，重新生成骨架",
                                    "error_type": error_type,
                                    "is_truncated": is_truncated,
                                    "error": str(e)[:200]
                                }
                            }
                            continue

                        raise RuntimeError(
                            f"Chapter {chapter_index + 1} JSON parse retries exhausted "
                            f"(type={error_type}, truncated={is_truncated}): {e}"
                        )
                    except StepContentRetryExhaustedError as e:
                        logger.error(f"Step content retry exhausted in chapter {chapter_index + 1}: {e}")
                        state.last_step_error = str(e)
                        state.step_fix_guidance = await self.supervisor.analyze_step_retry_guidance(
                            state=state,
                            chapter_title=chapter_outline.title,
                            step_index=-1,
                            step_type="chapter_level",
                            step_title="章节整体重试",
                            failure_reason=str(e),
                            attempt=state.current_attempt + 1,
                            max_attempts=state.max_attempts
                        )

                        state.increment_attempt()

                        if state.can_retry():
                            yield {
                                "event": "chapter_retry",
                                "data": {
                                    "index": chapter_index,
                                    "attempt": state.current_attempt,
                                    "reason": "步骤内容重试耗尽，执行章节级重试",
                                    "error": str(e)[:200]
                                }
                            }
                            continue

                        raise RuntimeError(
                            f"Chapter {chapter_index + 1} step retries exhausted after chapter-level retries: {e}"
                        )

                if chapter is None:
                    raise RuntimeError(
                        f"Chapter {chapter_index + 1} generation ended without valid content after {state.current_attempt} attempts"
                    )

                # 保存章节
                if chapter:
                    state.add_completed_chapter(chapter)

                    # 处理章节中的图片
                    chapter_dict = self._chapter_to_dict(chapter)
                    chapter_dict = await self._process_chapter_images(chapter_dict, state.course_title)

                    # === Phase 3: 章节质量评分与学习反馈循环 (2026-02-11) ===
                    quality_score = None
                    try:
                        from app.services.learning import ChapterScorer, UnifiedTemplateService

                        scorer = ChapterScorer()
                        quality_score = scorer.evaluate(chapter_dict)

                        logger.info(f"Chapter '{chapter.title}' quality score: {quality_score.total_score:.1f}/100")

                        # 如果质量达到90+分，保存为模板供future agent学习
                        if quality_score.total_score >= 90.0 and self.generator.db:
                            await self._save_chapter_as_template(
                                chapter=chapter_dict,
                                quality_score=quality_score,
                                subject=state.subject_classification.get('subject_id', 'physics') if state.subject_classification else 'physics',
                                topic=chapter.title
                            )
                            logger.info(f"✨ High-quality chapter (score: {quality_score.total_score:.1f}) saved as template for future learning")

                        # 记录评分结果到数据库（用于监控和分析）
                        if self.generator.db:
                            template_service = UnifiedTemplateService(self.generator.db)
                            await template_service.record_quality_evaluation(
                                content_type='chapter_content',
                                content_id=chapter.lesson_id,
                                quality_score=quality_score.total_score,
                                score_breakdown={
                                    'depth_score': quality_score.depth_score,
                                    'structure_score': quality_score.structure_score,
                                    'visual_score': quality_score.visual_score,
                                    'teaching_score': quality_score.teaching_score,
                                    'simulator_score': quality_score.simulator_score,
                                },
                                saved_as_template=(quality_score.total_score >= 90.0)
                            )
                    except Exception as e:
                        logger.error(f"Failed to evaluate/save chapter quality: {e}")
                        # 不中断流程，继续生成

                    yield {
                        "event": "chapter_complete",
                        "data": {
                            "index": chapter_index,
                            "total": outline.total_chapters,
                            "chapter": chapter_dict,
                            "attempts": state.current_attempt + 1,
                            "quality_score": quality_score.total_score if quality_score else None
                        }
                    }

            # === 后处理：确保至少有一个 ai_tutor 步骤 ===
            await self._ensure_ai_tutor_steps(state, generator_system_prompt)

            # === 阶段3：打包课程 ===
            yield {
                "event": "phase",
                "data": {
                    "phase": 3,
                    "message": "正在打包课程...",
                    "processor": {"id": processor_id}
                }
            }

            # 构建最终课程包
            package = self._build_course_package(state)

            yield {
                "event": "complete",
                "data": {
                    "package": package,
                    "stats": {
                        "total_chapters": len(state.completed_chapters),
                        "total_simulators": len(state.used_simulators),
                        "generation_time": (datetime.utcnow() - state.started_at).total_seconds()
                    }
                }
            }

        except Exception as e:
            logger.error(f"Course generation failed: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": {
                    "message": str(e),
                    "phase": "generation"
                }
            }

    def _get_default_system_prompt(self, processor_id: str) -> str:
        """获取默认系统提示词"""
        prompts = {
            'default': "你是一位专业的课程设计专家，擅长将复杂知识转化为易于理解的学习内容。",
            'academic': "你是一位学术型课程设计专家，注重理论深度和学术严谨性。",
            'practical': "你是一位实践型课程设计专家，注重实际应用和动手操作。",
            'sports': "你是一位运动科学课程设计专家，擅长运动生物力学和技术动作分析。"
        }
        return prompts.get(processor_id, prompts['default'])

    def _chapter_to_dict(self, chapter: ChapterResult) -> Dict[str, Any]:
        """将章节转换为字典"""
        return {
            "lesson_id": chapter.lesson_id,
            "title": chapter.title,
            "order": chapter.order,
            "total_steps": chapter.total_steps,
            "rationale": chapter.rationale,
            "steps": [
                {
                    "step_id": step.step_id,
                    "type": step.type,
                    "title": step.title,
                    "content": step.content,
                    "simulator_spec": {
                        "mode": step.simulator_spec.mode if hasattr(step.simulator_spec, 'mode') else "html",
                        "name": step.simulator_spec.name,
                        "description": step.simulator_spec.description,
                        "html_content": step.simulator_spec.html_content if hasattr(step.simulator_spec, 'html_content') else "",
                        # 兼容旧字段
                        "custom_code": step.simulator_spec.html_content if hasattr(step.simulator_spec, 'html_content') else ""
                    } if step.simulator_spec else None,
                    "assessment_spec": step.assessment_spec,
                    "diagram_spec": step.diagram_spec,
                    "ai_spec": step.ai_spec
                }
                for step in chapter.steps
            ],
            "estimated_minutes": chapter.estimated_minutes,
            "learning_objectives": chapter.learning_objectives,
            "complexity_level": chapter.complexity_level
        }

    def _build_course_package(self, state: GenerationState) -> Dict[str, Any]:
        """构建课程包"""
        outline = state.outline

        # 计算总时长
        total_minutes = sum(ch.estimated_minutes for ch in state.completed_chapters)

        # 生成边（章节之间的关系）
        edges = []
        for i in range(len(state.completed_chapters) - 1):
            edges.append({
                "from": f"lesson_{i + 1}",
                "to": f"lesson_{i + 2}",
                "type": "prerequisite"
            })

        return {
            "id": str(uuid.uuid4()),
            "version": "3.0.0",  # 新架构版本
            "meta": {
                "title": state.course_title,
                "description": outline.description if outline else "",
                "source_info": state.source_info,
                "total_lessons": len(state.completed_chapters),
                "estimated_hours": total_minutes / 60,
                "style": state.processor_id,
                "difficulty": outline.difficulty if outline else "intermediate",
                "created_at": datetime.utcnow().isoformat(),
                "architecture": "supervisor-generator"
            },
            "lessons": [self._chapter_to_dict(ch) for ch in state.completed_chapters],
            "edges": edges,
            "quality_stats": {
                "used_simulators": state.used_simulators,
                "covered_topics": state.covered_topics
            }
        }

    async def _process_illustrated_content(
        self,
        step_dict: Dict[str, Any],
        course_title: str,
        lesson_title: str
    ) -> Dict[str, Any]:
        """处理图文内容，生成所需图片"""
        diagram_spec = step_dict.get("diagram_spec")
        step_title = step_dict.get("title", "图文内容")

        if diagram_spec:
            # 检查是否已有图片
            if not diagram_spec.get("image_url"):
                logger.info(f"Generating image for illustrated content: {step_title}")

                try:
                    # 调用 Gemini 生成图片
                    image_data = await gemini_service.generate_diagram(
                        diagram_spec=diagram_spec,
                        course_title=course_title,
                        lesson_title=lesson_title
                    )

                    if image_data:
                        # 保存图片
                        diagram_id = diagram_spec.get("diagram_id", str(uuid.uuid4())[:8])
                        filename = f"diagram_{diagram_id}.png"

                        # 使用 storage_service 保存
                        image_info = await self._save_generated_image(
                            image_data, filename, "diagrams"
                        )

                        if image_info:
                            diagram_spec["image_url"] = image_info["file_url"]
                            diagram_spec["image_generated"] = True
                            logger.info(f"Image generated and saved: {image_info['file_url']}")
                        else:
                            logger.warning(f"Failed to save image for: {step_title}")
                            diagram_spec["image_url"] = None
                            diagram_spec["image_generated"] = False
                    else:
                        logger.warning(f"Failed to generate image for: {step_title}")
                        diagram_spec["image_url"] = None
                        diagram_spec["image_generated"] = False

                except Exception as e:
                    logger.error(f"Error generating image for {step_title}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    diagram_spec["image_url"] = None
                    diagram_spec["image_generated"] = False

                # 确保更新 step 中的 diagram_spec
                step_dict["diagram_spec"] = diagram_spec
        else:
            # 如果没有 diagram_spec，创建一个默认的
            logger.warning(f"No diagram_spec found for illustrated_content: {step_title}, creating default")
            step_dict["diagram_spec"] = {
                "type": "static_diagram",
                "description": step_title,
                "image_url": None,
                "image_generated": False
            }

        return step_dict

    async def _save_generated_image(
        self,
        image_data: bytes,
        filename: str,
        category: str = "images",
        target_width: int = 800,
        target_height: int = 600
    ) -> Optional[Dict[str, Any]]:
        """
        保存生成的图片，自动转换格式并裁剪到目标尺寸

        Args:
            image_data: 图片二进制数据
            filename: 文件名
            category: 存储类别
            target_width: 目标宽度
            target_height: 目标高度
        """
        try:
            from PIL import Image

            # 打开图片
            image = Image.open(io.BytesIO(image_data))

            # 转换为 RGB (处理 RGBA、P 等模式)
            if image.mode == "RGBA":
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            # 智能调整到目标尺寸
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)

            # 确保目录存在
            storage_dir = storage_service.directories.get(category, storage_service.directories["images"])
            storage_dir.mkdir(parents=True, exist_ok=True)

            # 生成唯一文件名 (统一使用 .jpg 格式)
            unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
            if not unique_filename.endswith('.jpg'):
                unique_filename = unique_filename.rsplit('.', 1)[0] + '.jpg'

            file_path = storage_dir / unique_filename

            # 保存为 JPEG 格式，优化质量和大小
            image.save(file_path, "JPEG", quality=85, optimize=True)

            # 返回文件信息 (使用 /upload/ 前缀匹配静态文件挂载路径)
            return {
                "filename": unique_filename,
                "file_path": str(file_path),
                "file_url": f"/upload/{category}/{unique_filename}",
                "width": image.size[0],
                "height": image.size[1]
            }

        except Exception as e:
            logger.error(f"Failed to save generated image: {e}")
            return None

    async def _process_chapter_images(
        self,
        chapter_dict: Dict[str, Any],
        course_title: str
    ) -> Dict[str, Any]:
        """处理章节中的所有图片"""
        lesson_title = chapter_dict.get("title", "")

        for step in chapter_dict.get("steps", []):
            step_type = step.get("type", "")
            if step_type == "illustrated_content":
                await self._process_illustrated_content(step, course_title, lesson_title)

        return chapter_dict

    async def _generate_all_content(
        self,
        chapter: 'ChapterResult',
        chapter_outline: 'ChapterOutline',
        generator_system_prompt: str,
        state: GenerationState
    ) -> 'ChapterResult':
        """
        分步生成：填充所有长文本内容（旧版本，保留兼容）
        """
        return await self._generate_all_content_with_check(
            chapter, chapter_outline, generator_system_prompt, state
        )

    async def _generate_all_content_with_check(
        self,
        chapter: 'ChapterResult',
        chapter_outline: 'ChapterOutline',
        generator_system_prompt: str,
        state: GenerationState
    ) -> 'ChapterResult':
        """
        分步生成：填充所有长文本内容，每个步骤独立检测

        检测标准：
        - text_content: body长度 >= 100字
        - illustrated_content: body长度 >= 80字，diagram描述 >= 50字
        - assessment: 每个问题有explanation >= 20字
        - simulator: description >= 30字（代码由专门方法处理）
        """
        from .models import ChapterResult

        # 1. 生成 rationale
        if not chapter.rationale or len(chapter.rationale) < 20:
            logger.info(f"Generating rationale for chapter '{chapter.title}'...")
            for attempt in range(2):
                chapter.rationale = await self._generate_text_content(
                    content_type="rationale",
                    context={
                        "course_title": state.course_title,
                        "chapter_title": chapter.title,
                        "learning_objectives": chapter.learning_objectives,
                        "chapter_type": chapter_outline.chapter_type.value,
                        "subject": state.subject_classification.get('subject_id', 'physics') if state.subject_classification else 'physics'
                    },
                    system_prompt=generator_system_prompt,
                    min_length=50,
                    max_length=150
                )
                if len(chapter.rationale) >= 50:
                    logger.info(f"[Step Check] Rationale passed: {len(chapter.rationale)} chars")
                    break
                else:
                    logger.warning(f"[Step Check] Rationale too short ({len(chapter.rationale)} chars), retrying...")

        # 2. 生成每个步骤的内容
        for i, step in enumerate(chapter.steps):
            step_passed = False
            max_step_retries = max(1, state.max_step_retries)
            last_failure_reason = ""
            step_retry_guidance = ""

            for retry in range(max_step_retries):
                if retry > 0 and last_failure_reason:
                    step_retry_guidance = await self.supervisor.analyze_step_retry_guidance(
                        state=state,
                        chapter_title=chapter.title,
                        step_index=i,
                        step_type=step.type,
                        step_title=step.title,
                        failure_reason=last_failure_reason,
                        attempt=retry + 1,
                        max_attempts=max_step_retries
                    )
                    state.last_step_error = last_failure_reason
                    state.step_fix_guidance = step_retry_guidance
                else:
                    step_retry_guidance = ""

                # === text_content / illustrated_content ===
                if step.type in ['text_content', 'illustrated_content']:
                    body = ""
                    if step.content:
                        if isinstance(step.content, dict):
                            body = step.content.get('body', '')
                        elif isinstance(step.content, str):
                            body = step.content

                    min_body_length = 100 if step.type == 'text_content' else 80

                    if not body or len(body) < min_body_length:
                        logger.info(f"Generating body for step '{step.title}' (attempt {retry+1})...")
                        new_body = await self._generate_text_content(
                            content_type="step_body",
                            context={
                                "course_title": state.course_title,
                                "chapter_title": chapter.title,
                                "step_title": step.title,
                                "step_type": step.type,
                                "key_points": step.content.get('key_points', []) if isinstance(step.content, dict) else [],
                                "learning_objectives": chapter.learning_objectives,
                                "subject": state.subject_classification.get('subject_id', 'physics') if state.subject_classification else 'physics'
                            },
                            system_prompt=generator_system_prompt,
                            min_length=150,
                            max_length=400,
                            retry_guidance=step_retry_guidance
                        )

                        if isinstance(step.content, dict):
                            step.content['body'] = new_body
                        else:
                            step.content = {'body': new_body, 'key_points': []}
                        body = new_body

                    # 检测 body 长度
                    if len(body) >= min_body_length:
                        step_passed = True
                        logger.info(f"[Step Check] Step {i+1} '{step.title}' body passed: {len(body)} chars")
                    else:
                        logger.warning(f"[Step Check] Step {i+1} body too short ({len(body)} chars, need {min_body_length}+)")
                        last_failure_reason = (
                            f"step_body_too_short: {len(body)} < {min_body_length}, "
                            f"step={i + 1}, title={step.title}, retry={retry + 1}/{max_step_retries}"
                        )
                        continue

                    # === illustrated_content 额外检测 diagram_spec ===
                    if step.type == 'illustrated_content' and step.diagram_spec:
                        desc = step.diagram_spec.get('description', '')
                        if not desc or len(desc) < 50:
                            logger.info(f"Generating diagram description for step '{step.title}'...")
                            step.diagram_spec['description'] = await self._generate_text_content(
                                content_type="diagram_description",
                                context={
                                    "course_title": state.course_title,
                                    "chapter_title": chapter.title,
                                    "step_title": step.title,
                                    "diagram_type": step.diagram_spec.get('type', 'static_diagram'),
                                    "elements": step.diagram_spec.get('elements', []),
                                    "subject": state.subject_classification.get('subject_id', 'physics') if state.subject_classification else 'physics'
                                },
                                system_prompt=generator_system_prompt,
                                min_length=80,
                                max_length=200,
                                retry_guidance=step_retry_guidance
                            )
                            desc = step.diagram_spec['description']

                        if len(desc) >= 50:
                            logger.info(f"[Step Check] Step {i+1} diagram description passed: {len(desc)} chars")
                        else:
                            logger.warning(f"[Step Check] Step {i+1} diagram description too short ({len(desc)} chars)")
                            step_passed = False
                            last_failure_reason = (
                                f"diagram_description_too_short: {len(desc)} < 50, "
                                f"step={i + 1}, title={step.title}, retry={retry + 1}/{max_step_retries}"
                            )
                            continue

                # === assessment ===
                elif step.type == 'assessment' and step.assessment_spec:
                    questions = step.assessment_spec.get('questions', [])
                    all_explanations_ok = True

                    for q_idx, q in enumerate(questions):
                        if not q.get('explanation') or len(q.get('explanation', '')) < 20:
                            logger.info(f"Generating explanation for question {q_idx+1}...")
                            q['explanation'] = await self._generate_text_content(
                                content_type="question_explanation",
                                context={
                                    "question": q.get('question', ''),
                                    "correct_answer": q.get('correct', ''),
                                    "options": q.get('options', []),
                                    "subject": state.subject_classification.get('subject_id', 'physics') if state.subject_classification else 'physics'
                                },
                                system_prompt=generator_system_prompt,
                                min_length=30,
                                max_length=100,
                                retry_guidance=step_retry_guidance
                            )

                        if len(q.get('explanation', '')) < 20:
                            all_explanations_ok = False
                            logger.warning(f"[Step Check] Question {q_idx+1} explanation too short")

                    if all_explanations_ok:
                        step_passed = True
                        logger.info(f"[Step Check] Step {i+1} assessment passed: {len(questions)} questions")
                    else:
                        last_failure_reason = (
                            f"assessment_explanations_incomplete: step={i + 1}, "
                            f"title={step.title}, retry={retry + 1}/{max_step_retries}"
                        )
                        continue

                # === ai_tutor ===
                elif step.type == 'ai_tutor':
                    spec = step.ai_spec or {}
                    if not spec.get('opening_message') or len(spec.get('opening_message', '')) < 10 \
                       or not spec.get('probing_questions'):
                        logger.info(f"Generating AI tutor content for step '{step.title}' (attempt {retry+1})...")
                        step.ai_spec = await self._generate_ai_tutor_content(
                            context={
                                "course_title": state.course_title,
                                "chapter_title": chapter.title,
                                "step_title": step.title,
                                "learning_objectives": chapter.learning_objectives
                            },
                            system_prompt=generator_system_prompt,
                            retry_guidance=step_retry_guidance
                        )
                    step_passed = bool(step.ai_spec and step.ai_spec.get('opening_message'))
                    if step_passed:
                        logger.info(f"[Step Check] Step {i+1} ai_tutor passed")
                        break
                    else:
                        last_failure_reason = (
                            f"ai_tutor_invalid: missing opening_message/probing_questions, "
                            f"step={i + 1}, title={step.title}, retry={retry + 1}/{max_step_retries}"
                        )
                        continue

                # === simulator (只检测description，代码由专门方法处理) ===
                elif step.type == 'simulator' and step.simulator_spec:
                    desc = step.simulator_spec.description or ''
                    if len(desc) < 30:
                        logger.info(f"Generating simulator description for '{step.simulator_spec.name}'...")
                        step.simulator_spec.description = await self._generate_text_content(
                            content_type="simulator_description",
                            context={
                                "course_title": state.course_title,
                                "chapter_title": chapter.title,
                                "simulator_name": step.simulator_spec.name,
                                "subject": state.subject_classification.get('subject_id', 'physics') if state.subject_classification else 'physics'
                            },
                            system_prompt=generator_system_prompt,
                            min_length=50,
                            max_length=150,
                            retry_guidance=step_retry_guidance
                        )
                        desc = step.simulator_spec.description

                    if len(desc) >= 30:
                        step_passed = True
                        logger.info(f"[Step Check] Step {i+1} simulator description passed: {len(desc)} chars")
                    else:
                        logger.warning(f"[Step Check] Step {i+1} simulator description too short ({len(desc)} chars)")
                        last_failure_reason = (
                            f"simulator_description_too_short: {len(desc)} < 30, "
                            f"step={i + 1}, title={step.title}, retry={retry + 1}/{max_step_retries}"
                        )
                        continue

                else:
                    # 其他类型步骤直接通过
                    step_passed = True

                if step_passed:
                    break

            if not step_passed:
                failure_detail = (
                    f"[Step Check] Step {i+1} '{step.title}' failed after {max_step_retries} retries. "
                    f"Last reason: {last_failure_reason or 'unknown'}"
                )
                logger.error(failure_detail)
                raise StepContentRetryExhaustedError(failure_detail)

        return chapter

    def _clean_text_response(self, response: str) -> str:
        """
        清理AI响应，移除JSON包装和处理转义字符

        方案A：防御性清理，确保返回纯文本
        """
        if not response:
            return ""

        text = response.strip()

        # 1. 移除 ```json 和 ``` 包装
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        # 2. 如果是 {"content": "..."} 格式，提取实际内容
        if text.startswith("{") and text.endswith("}"):
            try:
                import json
                data = json.loads(text)
                if isinstance(data, dict):
                    # 尝试提取 content 字段
                    if "content" in data:
                        text = data["content"]
                    elif "text" in data:
                        text = data["text"]
                    elif "body" in data:
                        text = data["body"]
                    elif len(data) == 1:
                        # 只有一个字段，取其值
                        text = list(data.values())[0]
                        if not isinstance(text, str):
                            text = response.strip()
            except:
                pass  # 不是有效JSON，保持原样

        # 3. 处理转义序列（如果是字面字符串）
        if "\\n" in text or "\\\"" in text:
            try:
                # 尝试解码转义序列
                text = text.encode('utf-8').decode('unicode_escape')
            except:
                # 手动替换常见转义
                text = text.replace("\\n", "\n")
                text = text.replace("\\\"", "\"")
                text = text.replace("\\'", "'")
                text = text.replace("\\t", "\t")

        # 4. 清理多余空白
        text = text.strip()

        return text

    def _classify_json_parse_failure(self, error_message: str, raw_response: str) -> tuple[str, bool]:
        """分类JSON解析错误，识别是否疑似被截断。"""
        message = (error_message or "").lower()
        response = (raw_response or "").strip()

        truncated_markers = [
            "unterminated string",
            "unexpected end",
            "end of data",
            "eof",
            "expecting value",
        ]
        escaping_markers = [
            "invalid \\escape",
            "invalid control character",
            "unterminated string",
        ]

        unbalanced_braces = response.count("{") != response.count("}")
        unbalanced_brackets = response.count("[") != response.count("]")
        response_tail_incomplete = bool(response) and not response.endswith("}")
        is_truncated = (
            any(m in message for m in truncated_markers) or
            unbalanced_braces or
            unbalanced_brackets or
            response_tail_incomplete
        )

        if is_truncated:
            return "truncated_output", True
        if any(m in message for m in escaping_markers):
            return "invalid_escape_or_string", False
        if "extra data" in message:
            return "extra_text_outside_json", False
        if "expecting property name enclosed in double quotes" in message:
            return "invalid_property_quotes", False
        return "invalid_json_structure", False

    async def _generate_text_content(
        self,
        content_type: str,
        context: Dict[str, Any],
        system_prompt: str,
        min_length: int,
        max_length: int,
        retry_guidance: str = ""
    ) -> str:
        """生成单个文本内容（增强版：注入学习上下文）"""
        from app.services.llm_factory import get_llm_service
        from app.services.learning import UnifiedTemplateService

        # === 学习上下文注入 (2026-02-11: Phase 3 Learning Integration) ===
        learning_context = ""
        if self.generator.db:
            try:
                template_service = UnifiedTemplateService(self.generator.db)

                # 根据内容类型检索相关模板
                subject = context.get('subject', 'physics')  # 从context获取学科
                topic = context.get('chapter_title', '')  # 使用章节标题作为主题

                # 检索高质量章节模板（只需要1-2个例子）
                templates = await template_service.get_similar_templates(
                    template_type='chapter_content',
                    subject=subject,
                    topic=topic,
                    min_quality=90.0,  # 只学习90+分的高质量模板
                    limit=2
                )

                if templates:
                    # 分析模板并提取学习insights
                    patterns = template_service.analyze_patterns(templates)
                    learning_context = template_service.format_learning_context(
                        patterns=patterns,
                        templates=templates,
                        template_type='chapter_content'
                    )
                    logger.info(f"Injected learning context from {len(templates)} high-quality templates (avg score: {patterns['avg_quality_score']:.1f})")
            except Exception as e:
                logger.warning(f"Failed to inject learning context: {e}")
                # 继续生成，不中断流程

        # 方案B：强化提示词，强调纯文本输出
        format_warning = """
【输出格式要求 - 必须遵守】
- 直接输出纯文本，不要使用任何代码块（如 ```json 或 ```）
- 不要使用 JSON 格式（如 {"content": "..."}）
- 不要在文本中使用转义字符（如 \\n 或 \\"）
- 直接输出中文文字内容"""
        retry_guidance_block = (
            f"\n【本次重试修复指导】\n{retry_guidance}\n"
            if retry_guidance else ""
        )

        prompts = {
            "rationale": f"""请为以下章节生成设计理念说明。

课程：{context.get('course_title', '')}
章节：{context.get('chapter_title', '')}
学习目标：{', '.join(context.get('learning_objectives', []))}
章节类型：{context.get('chapter_type', '')}

{learning_context}
{retry_guidance_block}

要求：
- {min_length}-{max_length}字
- 说明本章的教学设计思路
- 解释为什么这样安排内容
{format_warning}""",

            "step_body": f"""请为以下学习步骤生成正文内容。

课程：{context.get('course_title', '')}
章节：{context.get('chapter_title', '')}
步骤标题：{context.get('step_title', '')}
步骤类型：{context.get('step_type', '')}
要点：{', '.join(context.get('key_points', []))}
学习目标：{', '.join(context.get('learning_objectives', []))}

{learning_context}
{retry_guidance_block}

要求：
- {min_length}-{max_length}字
- 围绕要点展开详细讲解
- 逻辑清晰，层次分明
- 使用专业术语但要有解释
{format_warning}""",

            "diagram_description": f"""请为以下图片生成详细描述（用于AI图片生成）。

课程：{context.get('course_title', '')}
章节：{context.get('chapter_title', '')}
步骤标题：{context.get('step_title', '')}
图片类型：{context.get('diagram_type', '')}
包含元素：{', '.join(context.get('elements', []))}

【生成步骤 - 必须按顺序执行】
第一步：场景分析
- 列出图中所有元素（人物、物体、箭头、标注等）
- 明确每个元素的位置（上/下/左/右/中心）和朝向（面向左/右/前方）
- 明确元素之间的空间关系（A在B的左上方、C包含D等）
- 如果有运动/过程，明确方向（从左到右、顺时针、向上等）

第二步：基于分析写详细描述
要求：
- {min_length}-{max_length}字
- 详细描述图片应该展示的内容
- 包括：主题、场景、元素、布局、风格
- 描述越详细，生成的图片越准确
{retry_guidance_block}
{format_warning}""",

            "question_explanation": f"""请为以下选择题生成答案解析。

问题：{context.get('question', '')}
正确答案：{context.get('correct_answer', '')}
选项：{', '.join(context.get('options', []))}

要求：
- {min_length}-{max_length}字
- 解释为什么正确答案是对的
- 简要说明其他选项为什么不对
{retry_guidance_block}
{format_warning}""",

            "simulator_description": f"""请为以下模拟器生成详细描述。

课程：{context.get('course_title', '')}
章节：{context.get('chapter_title', '')}
模拟器名称：{context.get('simulator_name', '')}

要求：
- {min_length}-{max_length}字
- 说明模拟器要展示什么概念
- 描述交互效果和视觉呈现
{retry_guidance_block}
{format_warning}"""
        }

        prompt = prompts.get(content_type, prompts["step_body"])

        try:
            claude_service = get_llm_service()
            response = await claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=LLM_OUTPUT_TOKEN_LIMIT
            )
            # 方案A：使用清理函数处理响应
            return self._clean_text_response(response)
        except Exception as e:
            logger.error(f"Failed to generate {content_type}: {e}")
            return f"[内容生成失败: {content_type}]"

    async def _generate_ai_tutor_content(
        self,
        context: Dict[str, Any],
        system_prompt: str,
        retry_guidance: str = ""
    ) -> Dict[str, Any]:
        """生成AI导师步骤内容"""
        from app.services.llm_factory import get_llm_service
        import json

        course_title = context.get('course_title', '')
        chapter_title = context.get('chapter_title', '')
        step_title = context.get('step_title', chapter_title)
        objectives = ', '.join(context.get('learning_objectives', []))
        retry_guidance_block = (
            f"\n【本次重试修复指导】\n{retry_guidance}\n"
            if retry_guidance else ""
        )

        prompt = f"""请为以下课程章节生成AI导师对话内容（苏格拉底式提问），用于检验学生对核心概念的理解。

课程：{course_title}
章节：{chapter_title}
步骤标题：{step_title}
学习目标：{objectives}

请输出一个JSON对象，包含以下字段：
{{
    "mode": "proactive_assessment",
    "opening_message": "AI导师的开场白（50-150字，引导学生思考本章核心问题）",
    "probing_questions": [
        {{
            "question": "探测性问题1",
            "intent": "该问题的意图",
            "expected_elements": ["期望学生提到的要素1", "要素2"]
        }},
        {{
            "question": "探测性问题2",
            "intent": "该问题的意图",
            "expected_elements": ["期望学生提到的要素1", "要素2"]
        }},
        {{
            "question": "探测性问题3",
            "intent": "该问题的意图",
            "expected_elements": ["期望学生提到的要素1", "要素2"]
        }}
    ],
    "diagnostic_focus": {{
        "key_concepts": ["本章核心概念1", "核心概念2", "核心概念3"],
        "common_misconceptions": ["常见误区1", "常见误区2"]
    }},
    "max_turns": 6
}}

要求：
- opening_message 要有亲和力，引导学生思考
- probing_questions 至少3个，由浅入深
- diagnostic_focus 中的 key_concepts 和 common_misconceptions 要与学习目标相关
- 严格遵守课程标准，不得输出占位内容
- 单次输出token上限为 {LLM_OUTPUT_TOKEN_LIMIT}
- 请直接输出JSON，不要有其他内容
{retry_guidance_block}"""

        try:
            claude_service = get_llm_service()
            response = await claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=LLM_OUTPUT_TOKEN_LIMIT
            )

            # 尝试解析JSON
            text = response.strip()
            # 移除可能的 ```json ``` 包装
            if text.startswith('```'):
                text = text.split('\n', 1)[1] if '\n' in text else text[3:]
            if text.endswith('```'):
                text = text.rsplit('```', 1)[0]
            text = text.strip()

            ai_spec = json.loads(text)

            # 确保必要字段
            if 'max_turns' not in ai_spec:
                ai_spec['max_turns'] = 6
            if 'mode' not in ai_spec:
                ai_spec['mode'] = 'proactive_assessment'

            logger.info(f"AI tutor content generated successfully for '{step_title}'")
            return ai_spec

        except Exception as e:
            logger.error(f"Failed to generate AI tutor content: {e}, using fallback")
            # Fallback: 基于章节标题生成最小可用默认内容
            return {
                "mode": "proactive_assessment",
                "opening_message": f"同学你好！我们刚刚学习了「{chapter_title}」的内容。在继续之前，我想通过几个问题来帮助你巩固理解。请用你自己的话来回答，不需要追求标准答案。",
                "probing_questions": [
                    {
                        "question": f"你能用自己的话解释一下「{chapter_title}」中最核心的概念是什么吗？",
                        "intent": "检验学生对核心概念的基本理解",
                        "expected_elements": ["核心概念的定义", "基本原理"]
                    },
                    {
                        "question": f"在「{chapter_title}」中，你觉得哪个知识点最容易被误解？为什么？",
                        "intent": "探测学生对常见误区的认识",
                        "expected_elements": ["常见误区", "正确理解"]
                    },
                    {
                        "question": f"如果要把「{chapter_title}」的知识应用到实际场景中，你会怎么做？",
                        "intent": "检验学生的应用能力",
                        "expected_elements": ["实际应用场景", "操作步骤"]
                    }
                ],
                "diagnostic_focus": {
                    "key_concepts": [chapter_title],
                    "common_misconceptions": ["概念混淆", "理解片面"]
                },
                "max_turns": 6
            }

    async def _generate_simulator_codes(
        self,
        chapter: 'ChapterResult',
        chapter_outline: 'ChapterOutline',
        generator_system_prompt: str,
        state: GenerationState
    ) -> 'ChapterResult':
        """
        分步生成：为章节中的模拟器单独生成代码（旧方法，保留兼容）
        """
        async for event in self._generate_simulator_codes_with_check(
            chapter=chapter,
            chapter_outline=chapter_outline,
            generator_system_prompt=generator_system_prompt,
            state=state,
            chapter_index=0
        ):
            if event.get("event") == "_chapter_done":
                return event["data"]["chapter"]
        return chapter

    async def _generate_simulator_codes_with_check(
        self,
        chapter: 'ChapterResult',
        chapter_outline: 'ChapterOutline',
        generator_system_prompt: str,
        state: GenerationState,
        chapter_index: int
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        碎片化检查版本：为章节中的模拟器单独生成代码，每个生成后立即检查

        Yields:
            SSE events (simulator_progress) during generation
            Final event: {"event": "_chapter_done", "data": {"chapter": ChapterResult}}
        """
        from .models import ChapterResult

        # 构建章节上下文
        chapter_context = f"""
课程：{state.course_title}
章节：{chapter.title}
学习目标：{', '.join(chapter.learning_objectives)}
章节主题：{chapter_outline.suggested_simulator if hasattr(chapter_outline, 'suggested_simulator') else chapter.title}
"""

        # 课程生成默认走 Agent 生成，确保与独立 Agent 测试链路一致
        use_agent_generation = os.environ.get("SIMULATOR_USE_AGENT_GENERATION", "1").lower() not in ("0", "false", "no")
        force_regen = os.environ.get("SIMULATOR_FORCE_REGENERATE", "1").lower() not in ("0", "false", "no")
        subject_id, agent_subject = self._get_simulator_subjects(state)

        for step_idx, step in enumerate(chapter.steps):
            if step.type == 'simulator' and step.simulator_spec:
                code = step.simulator_spec.html_content or ""
                code_lines = len([l for l in code.split('\n') if l.strip()])
                should_generate = force_regen or code_lines < 20

                if not should_generate:
                    continue

                logger.info(
                    f"Generating HTML simulator: '{step.simulator_spec.name}' "
                    f"(use_agent={use_agent_generation}, force_regen={force_regen}, subject={subject_id})"
                )

                try:
                    result_code = None

                    if use_agent_generation:
                        yield {
                            "event": "simulator_progress",
                            "data": {
                                "simulator_name": step.simulator_spec.name,
                                "step_index": step_idx,
                                "round": 1,
                                "max_rounds": 1,
                                "stage": "agent_queue",
                                "message": "提交到Agent异步生成队列..."
                            }
                        }
                        agent_result = await self._generate_simulator_via_agent_task(
                            simulator_name=step.simulator_spec.name,
                            simulator_description=step.simulator_spec.description,
                            chapter_context=chapter_context,
                            subject=agent_subject
                        )
                        result_code = agent_result.get("code", "")
                        yield {
                            "event": "simulator_progress",
                            "data": {
                                "simulator_name": step.simulator_spec.name,
                                "step_index": step_idx,
                                "round": 1,
                                "max_rounds": 1,
                                "stage": "agent_done",
                                "message": (
                                    f"Agent完成: quality={agent_result.get('quality_score', 0):.2f}, "
                                    f"lines={agent_result.get('line_count', 0)}"
                                )
                            }
                        }
                    else:
                        logger.info(f"Using local progressive generation for '{step.simulator_spec.name}'...")
                        async for event in self.generator.generate_simulator_code_progressive(
                            simulator_name=step.simulator_spec.name,
                            simulator_description=step.simulator_spec.description,
                            chapter_context=chapter_context,
                            system_prompt=generator_system_prompt
                        ):
                            if event["type"] == "progress":
                                yield {
                                    "event": "simulator_progress",
                                    "data": {
                                        "simulator_name": step.simulator_spec.name,
                                        "step_index": step_idx,
                                        "round": event["round"],
                                        "max_rounds": event["max_rounds"],
                                        "stage": event["stage"],
                                        "message": event["message"]
                                    }
                                }
                            elif event["type"] == "result":
                                result_code = event["code"]

                    if not result_code:
                        logger.warning(f"Simulator '{step.simulator_spec.name}' returned empty code")
                        continue

                    new_lines = len([l for l in result_code.split('\n') if l.strip()])
                    min_quality_norm = self._get_min_quality_norm()
                    min_quality_score = min_quality_norm * 100.0

                    # === 动态阈值 + 硬门禁 (2026-03-01) ===
                    from .template_service import TemplateService
                    template_service = TemplateService(self.db)
                    thresholds = await template_service.calculate_dynamic_thresholds(subject=subject_id)

                    dynamic_pass_threshold = max(thresholds['pass_threshold'], min_quality_score)
                    dynamic_save_threshold = max(thresholds['save_threshold'], min_quality_score)

                    logger.info(
                        f"Dynamic thresholds({subject_id}) - Phase: {thresholds['phase']}, "
                        f"Pass: {dynamic_pass_threshold:.1f}, Save: {dynamic_save_threshold:.1f}, "
                        f"Templates: {thresholds['template_count']}, Avg: {thresholds['avg_quality']:.1f}"
                    )

                    quality_passed, quality_score, _ = self.generator.validate_html_quality(
                        code=result_code,
                        threshold=dynamic_pass_threshold
                    )

                    if not quality_passed:
                        logger.warning(
                            f"Simulator '{step.simulator_spec.name}' rejected by local quality gate: "
                            f"{quality_score.total_score}/100 < {dynamic_pass_threshold:.1f}"
                        )
                        continue

                    # 通过门禁后再落库到章节，避免覆盖为低质量代码
                    step.simulator_spec.html_content = result_code
                    logger.info(f"Simulator accepted: '{step.simulator_spec.name}' ({new_lines} lines)")

                    if quality_score.total_score >= dynamic_save_threshold:
                        try:
                            await self._save_simulator_as_template(
                                code=result_code,
                                spec=step.simulator_spec,
                                quality_score=quality_score,
                                subject=subject_id,
                                topic=step.simulator_spec.name
                            )
                        except Exception as e:
                            logger.error(f"Failed to save simulator as template: {e}")
                    else:
                        logger.info(
                            f"Score {quality_score.total_score} below save threshold "
                            f"{dynamic_save_threshold:.1f}, not saved as template"
                        )

                except Exception as e:
                    logger.error(f"Simulator generation failed: {e}")
                    if not step.simulator_spec.html_content:
                        logger.warning(f"Simulator generation truly failed and no fallback code exists")
                    else:
                        logger.info(
                            f"Keep previous simulator code ({len(step.simulator_spec.html_content)} chars) "
                            f"because new generation failed"
                        )

        yield {"event": "_chapter_done", "data": {"chapter": chapter}}

    def _get_min_quality_norm(self) -> float:
        """读取统一质量门槛，支持 0~1 或 0~100 两种写法。"""
        raw_value = os.environ.get("SIMULATOR_TEMPLATE_MIN_QUALITY", "0.85")
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            value = 0.85
        if value > 1.0:
            value = value / 100.0
        return max(0.0, min(1.0, value))

    def _get_simulator_subjects(self, state: GenerationState) -> tuple[str, str]:
        """
        返回：
        - subject_id: backend模板库使用（physics/mathematics/...）
        - agent_subject: 传给Agent的学科中文名（数学/物理/...）
        """
        classification = getattr(state, "subject_classification", None) or {}
        subject_id = classification.get("subject_id") or "physics"
        subject_name = classification.get("subject_name") or subject_id
        subject_to_agent = {
            "physics": "物理",
            "chemistry": "化学",
            "biology": "生物",
            "mathematics": "数学",
            "history": "历史",
            "geography": "地理",
            "computer_science": "计算机",
            "medicine": "医学",
        }
        return subject_id, subject_to_agent.get(subject_id, subject_name)

    async def _generate_simulator_via_agent_task(
        self,
        simulator_name: str,
        simulator_description: str,
        chapter_context: str,
        subject: str
    ) -> Dict[str, Any]:
        """
        通过 Agent 异步任务接口生成模拟器，并执行硬门禁：
        - quality_score >= SIMULATOR_TEMPLATE_MIN_QUALITY (默认0.85)
        - line_count >= SIMULATOR_TEMPLATE_MIN_LINES (默认500)
        """
        base_url = settings.AGENT_BASE_URL.rstrip("/")
        submit_url = f"{base_url}/enhance/simulator/tasks"

        min_quality = self._get_min_quality_norm()
        min_lines = int(os.environ.get("SIMULATOR_TEMPLATE_MIN_LINES", "500"))
        max_attempts = max(1, int(os.environ.get("SIMULATOR_AGENT_MAX_ATTEMPTS", "2")))
        timeout_sec = max(60, int(os.environ.get("SIMULATOR_AGENT_TASK_TIMEOUT_SEC", "2160")))
        poll_interval = max(1.0, float(os.environ.get("SIMULATOR_AGENT_POLL_INTERVAL_SEC", "2")))
        allow_below_gate = os.environ.get("SIMULATOR_ALLOW_BELOW_GATE", "0").lower() in ("1", "true", "yes")

        best_result: Optional[Dict[str, Any]] = None
        best_quality = -1.0

        timeout = httpx.Timeout(connect=15.0, read=30.0, write=30.0, pool=30.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(1, max_attempts + 1):
                payload = {
                    "topic": simulator_name,
                    "subject": subject,
                    "variables": None,
                    "chapter_context": chapter_context,
                    "simulator_description": simulator_description or "",
                    "complexity_level": "advanced",
                }
                submit_resp = await client.post(submit_url, json=payload)
                submit_resp.raise_for_status()
                submit_data = submit_resp.json()
                task_id = submit_data.get("task_id")
                if not task_id:
                    raise RuntimeError("Agent任务创建成功但未返回task_id")

                logger.info(
                    f"Agent simulator task submitted: {task_id} "
                    f"(attempt {attempt}/{max_attempts}, subject={subject})"
                )

                status_url = f"{submit_url}/{task_id}"
                loop = asyncio.get_running_loop()
                started = loop.time()
                while True:
                    elapsed = loop.time() - started
                    if elapsed > timeout_sec:
                        raise TimeoutError(f"Agent任务超时: {task_id} (> {timeout_sec}s)")

                    await asyncio.sleep(poll_interval)
                    status_resp = await client.get(status_url)
                    status_resp.raise_for_status()
                    task_data = status_resp.json()
                    status = task_data.get("status")

                    if status in ("queued", "running"):
                        continue

                    if status == "succeeded":
                        result = task_data.get("result") or {}
                        code = (result.get("code") or "").strip()
                        quality = float(result.get("quality_score") or 0.0)
                        valid = bool(result.get("valid"))
                        line_count = int(result.get("line_count") or len([l for l in code.split("\n") if l.strip()]))
                        result["line_count"] = line_count

                        if quality > best_quality and code:
                            best_quality = quality
                            best_result = result

                        if code and valid and quality >= min_quality and line_count >= min_lines:
                            return result

                        logger.warning(
                            f"Agent result below gate (attempt {attempt}/{max_attempts}): "
                            f"valid={valid}, quality={quality:.2f}<{min_quality:.2f}, "
                            f"lines={line_count}<{min_lines}"
                        )
                        break

                    error_code = task_data.get("error_code")
                    error_message = task_data.get("error_message")
                    logger.warning(
                        f"Agent task failed/canceled (attempt {attempt}/{max_attempts}): "
                        f"task_id={task_id}, status={status}, code={error_code}, msg={error_message}"
                    )
                    break

        if best_result and allow_below_gate:
            logger.warning(
                f"Returning below-gate simulator due to SIMULATOR_ALLOW_BELOW_GATE=1 "
                f"(quality={best_result.get('quality_score', 0):.2f}, "
                f"lines={best_result.get('line_count', 0)})"
            )
            return best_result

        best_quality_text = f"{best_quality:.2f}" if best_quality >= 0 else "N/A"
        raise RuntimeError(
            f"Agent simulator generation did not pass gate after {max_attempts} attempts "
            f"(min_quality={min_quality:.2f}, min_lines={min_lines}, best_quality={best_quality_text})"
        )

    async def _save_simulator_as_template(
        self,
        code: str,
        spec: 'HTMLSimulatorSpec',
        quality_score: 'HTMLSimulatorQualityScore',
        subject: str,
        topic: str
    ):
        """
        保存高质量模拟器作为模板，用于future agent学习 (2026-02-11)

        Args:
            code: HTML代码
            spec: 模拟器规格
            quality_score: 质量评分
            subject: 学科 (如 "physics", "mathematics")
            topic: 主题 (如 spec.name的标准化版本)
        """
        from app.models.models import SimulatorTemplate
        from sqlalchemy import select
        import re

        if not self.generator.db:
            logger.warning("No database session available, cannot save template")
            return

        # 标准化topic名称 (移除特殊字符，转为小写下划线)
        topic_normalized = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]+', '_', topic).lower().strip('_')

        # 入待审核硬门禁：代码行数>=500 且 质量>=0.85
        code_lines = len([l for l in code.split('\n') if l.strip()])
        min_lines_for_pending = int(os.environ.get("SIMULATOR_TEMPLATE_MIN_LINES", "500"))
        min_quality_norm = self._get_min_quality_norm()
        min_quality_score = min_quality_norm * 100.0

        if code_lines < min_lines_for_pending or quality_score.total_score < min_quality_score:
            logger.info(
                f"Template skip ({subject}/{topic_normalized}): "
                f"lines={code_lines}/{min_lines_for_pending}, "
                f"quality={quality_score.total_score:.1f}/{min_quality_score:.1f}"
            )
            return

        # 检查是否已存在同名模板
        result = await self.generator.db.execute(
            select(SimulatorTemplate).where(
                SimulatorTemplate.subject == subject,
                SimulatorTemplate.topic == topic_normalized
            )
        )
        existing = result.scalar_one_or_none()

        if existing and existing.quality_score >= quality_score.total_score:
            logger.info(f"Template already exists with score {existing.quality_score}, skipping save")
            return

        # 提取代码指标
        has_setup_update = 'requestAnimationFrame' in code  # 简单检测动画模式
        variable_count = 0  # HTML模拟器不使用variables，设为0

        # 提取视觉元素 (简单分析)
        visual_elements = []
        if 'arc(' in code or 'circle' in code.lower():
            visual_elements.append('circles')
        if 'fillRect' in code or 'strokeRect' in code:
            visual_elements.append('rectangles')
        if 'fillText' in code or 'strokeText' in code:
            visual_elements.append('labels')
        if 'beginPath' in code and 'lineTo' in code:
            visual_elements.append('paths')

        # 构建元数据
        metadata = {
            "common_apis": self._extract_canvas_apis(code),
            "color_scheme": self._extract_colors(code),
            "animation_patterns": [],
            "interaction_types": [],
            "structure_insights": f"Score: {quality_score.total_score}/100"
        }

        if 'requestAnimationFrame' in code:
            metadata["animation_patterns"].append("requestAnimationFrame")
        if 'addEventListener' in code:
            if "'mousemove'" in code or '"mousemove"' in code:
                metadata["interaction_types"].append("mouse_tracking")
            if "'click'" in code or '"click"' in code:
                metadata["interaction_types"].append("mouse_click")
        if 'type="range"' in code:
            metadata["interaction_types"].append("slider_control")

        # 创建或更新模板
        if existing:
            # 更新现有模板
            existing.code = code
            existing.quality_score = quality_score.total_score
            existing.line_count = code_lines
            existing.variable_count = variable_count
            existing.has_setup_update = has_setup_update
            existing.visual_elements = visual_elements
            existing.template_metadata = metadata
            existing.status = 'pending'  # 二次入库也必须回到待审核
            logger.info(f"Updated template {subject}/{topic_normalized} with improved quality score")
        else:
            # 创建新模板
            new_template = SimulatorTemplate(
                subject=subject,
                topic=topic_normalized,
                code=code,
                quality_score=quality_score.total_score,
                line_count=code_lines,
                variable_count=variable_count,
                has_setup_update=has_setup_update,
                visual_elements=visual_elements,
                template_metadata=metadata,
                status='pending'
            )
            self.generator.db.add(new_template)
            logger.info(f"Created new template {subject}/{topic_normalized} with score {quality_score.total_score}")

        await self.generator.db.commit()

    def _extract_canvas_apis(self, code: str) -> list:
        """提取代码中使用的Canvas API"""
        apis = []
        common_apis = [
            'fillRect', 'strokeRect', 'clearRect', 'arc', 'beginPath', 'closePath',
            'moveTo', 'lineTo', 'stroke', 'fill', 'fillText', 'strokeText',
            'save', 'restore', 'translate', 'rotate', 'scale'
        ]
        for api in common_apis:
            if api + '(' in code:
                apis.append(api)
        return apis[:15]  # 最多15个

    def _extract_colors(self, code: str) -> list:
        """提取代码中使用的颜色值"""
        import re
        # 匹配 #RRGGBB 格式
        hex_colors = re.findall(r'#[0-9A-Fa-f]{6}', code)
        # 匹配 rgb() 格式
        rgb_colors = re.findall(r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)', code)
        # 去重并限制数量
        all_colors = list(set(hex_colors + rgb_colors))
        return all_colors[:8]  # 最多8个颜色

    async def _ensure_ai_tutor_steps(self, state: 'GenerationState', generator_system_prompt: str):
        """后处理：确保课程中至少有一个 ai_tutor 步骤"""
        from .models import ChapterStep
        import uuid

        # 检查是否已有 ai_tutor 步骤
        has_ai_tutor = False
        for chapter in state.completed_chapters:
            for step in chapter.steps:
                if step.type == 'ai_tutor':
                    has_ai_tutor = True
                    break
            if has_ai_tutor:
                break

        if has_ai_tutor:
            logger.info("[PostProcess] Course already has ai_tutor step(s), skipping injection")
            return

        logger.info("[PostProcess] No ai_tutor step found, injecting one...")

        # 选择第一个含 assessment 的章节，在其第一个 assessment 前注入
        target_chapter = None
        insert_index = None

        for chapter in state.completed_chapters:
            for i, step in enumerate(chapter.steps):
                if step.type == 'assessment':
                    target_chapter = chapter
                    insert_index = i
                    break
            if target_chapter:
                break

        # 如果没有含 assessment 的章节，选择最后一个章节的末尾
        if not target_chapter:
            target_chapter = state.completed_chapters[-1] if state.completed_chapters else None
            if target_chapter:
                insert_index = len(target_chapter.steps)

        if not target_chapter:
            logger.warning("[PostProcess] No chapters available for ai_tutor injection")
            return

        # 生成 ai_tutor 内容
        ai_spec = await self._generate_ai_tutor_content(
            context={
                "course_title": state.course_title,
                "chapter_title": target_chapter.title,
                "step_title": f"AI导师：{target_chapter.title}概念检测",
                "learning_objectives": target_chapter.learning_objectives
            },
            system_prompt=generator_system_prompt
        )

        # 创建 ai_tutor 步骤
        ai_tutor_step = ChapterStep(
            step_id=str(uuid.uuid4()),
            type='ai_tutor',
            title=f'AI导师：{target_chapter.title}概念检测',
            ai_spec=ai_spec
        )

        # 注入步骤
        target_chapter.steps.insert(insert_index, ai_tutor_step)
        target_chapter.total_steps = len(target_chapter.steps)

        logger.info(f"[PostProcess] Injected ai_tutor step into chapter '{target_chapter.title}' at position {insert_index}")

    def _get_default_chapter_skeleton(self, chapter_outline: 'ChapterOutline', chapter_index: int) -> 'ChapterResult':
        """生成默认章节骨架（当JSON解析多次失败时使用）"""
        from .models import ChapterResult, ChapterStep, HTMLSimulatorSpec
        import uuid

        # 创建基础步骤
        steps = [
            ChapterStep(
                step_id=str(uuid.uuid4()),
                type='text_content',
                title=f'{chapter_outline.title} - 概述',
                content={'body': '', 'key_points': ['要点1', '要点2', '要点3']}
            ),
            ChapterStep(
                step_id=str(uuid.uuid4()),
                type='illustrated_content',
                title=f'{chapter_outline.title} - 图文讲解',
                content={'body': '', 'key_points': ['要点1', '要点2']},
                diagram_spec={'description': '', 'style': 'educational'}
            ),
            ChapterStep(
                step_id=str(uuid.uuid4()),
                type='text_content',
                title=f'{chapter_outline.title} - 详解',
                content={'body': '', 'key_points': ['要点1', '要点2', '要点3']}
            ),
            ChapterStep(
                step_id=str(uuid.uuid4()),
                type='simulator',
                title=f'{chapter_outline.title} - 互动模拟',
                simulator_spec=HTMLSimulatorSpec(
                    name=chapter_outline.suggested_simulator or f'{chapter_outline.title}模拟器',
                    description='',
                    html_content='',
                    mode='html'
                )
            ),
            ChapterStep(
                step_id=str(uuid.uuid4()),
                type='ai_tutor',
                title=f'{chapter_outline.title} - AI导师',
                ai_spec={
                    "mode": "proactive_assessment",
                    "opening_message": "",
                    "probing_questions": [
                        {"question": "问题1", "intent": "检验理解", "expected_elements": ["要素1"]},
                        {"question": "问题2", "intent": "深入探测", "expected_elements": ["要素1"]},
                        {"question": "问题3", "intent": "应用检测", "expected_elements": ["要素1"]}
                    ],
                    "diagnostic_focus": {"key_concepts": [chapter_outline.title], "common_misconceptions": ["误区1"]},
                    "max_turns": 6
                }
            ),
            ChapterStep(
                step_id=str(uuid.uuid4()),
                type='assessment',
                title=f'{chapter_outline.title} - 测验',
                assessment_spec={
                    'type': 'quick_check',
                    'questions': [
                        {'question': '问题1', 'options': ['选项A', '选项B', '选项C', '选项D'], 'correctIndex': 0, 'explanation': ''},
                        {'question': '问题2', 'options': ['选项A', '选项B', '选项C', '选项D'], 'correctIndex': 0, 'explanation': ''}
                    ]
                }
            )
        ]

        return ChapterResult(
            lesson_id=str(uuid.uuid4()),
            title=chapter_outline.title,
            order=chapter_index,
            total_steps=len(steps),
            rationale='',
            script=steps,
            estimated_minutes=15,
            learning_objectives=chapter_outline.learning_objectives or ['学习目标1', '学习目标2', '学习目标3'],
            complexity_level=chapter_outline.complexity_level or 'standard'
        )

    async def _try_fix_problematic_steps(
        self,
        chapter: 'ChapterResult',
        review: 'ReviewResult',
        state: GenerationState,
        generator_system_prompt: str,
        chapter_index: int
    ) -> List[int]:
        """
        尝试修复有问题的步骤（单步重做）

        Args:
            chapter: 当前章节
            review: 审核结果
            state: 生成状态
            generator_system_prompt: 生成器系统提示词
            chapter_index: 章节索引

        Returns:
            成功修复的步骤索引列表
        """
        fixed_steps = []

        # 获取需要修复的步骤
        problematic_step_reviews = [
            sr for sr in review.step_reviews
            if not sr.is_approved()
        ]

        if not problematic_step_reviews:
            return fixed_steps

        logger.info(f"尝试单步修复 {len(problematic_step_reviews)} 个问题步骤")

        for step_review in problematic_step_reviews:
            step_index = step_review.step_index

            # 检查是否可以重试该步骤
            if not state.can_retry_step(step_index):
                logger.warning(f"步骤 {step_index + 1} 已达到最大重试次数，跳过")
                continue

            try:
                # 获取重做上下文
                step_context = self.supervisor.get_step_regeneration_context(
                    state=state,
                    chapter=chapter,
                    step_index=step_index,
                    step_review=step_review
                )

                # 重新生成步骤
                new_step = await self.generator.generate_single_step(
                    step_type=step_review.step_type,
                    step_context=step_context,
                    issues=step_review.issues,
                    suggestions=step_review.suggestions,
                    system_prompt=generator_system_prompt
                )

                # 如果是模拟器，需要单独生成代码
                if new_step.type == 'simulator' and new_step.simulator_spec:
                    code = new_step.simulator_spec.html_content or ""
                    code_lines = len([l for l in code.split('\n') if l.strip()])

                    if code_lines < 20:
                        # TODO: 这里应该使用 progressive 生成方法
                        # 暂时跳过，因为旧的 generate_simulator_code 方法已删除
                        logger.warning(f"Simulator code too short ({code_lines} lines), but skipping regeneration in fix flow")
                        # chapter_outline = state.outline.chapters[chapter_index]
                        # ... (旧代码已删除)

                # 替换原步骤
                chapter.steps[step_index] = new_step
                state.increment_step_retry(step_index)
                fixed_steps.append(step_index)

                logger.info(f"步骤 {step_index + 1} 修复成功")

            except Exception as e:
                logger.error(f"修复步骤 {step_index + 1} 失败: {e}")
                state.increment_step_retry(step_index)

        return fixed_steps

    # ==================== 学科分类系统 ====================

    def detect_course_subject(self, course_title: str, outline: Optional[CourseOutline] = None) -> Dict[str, Any]:
        """
        识别课程所属学科（受控自治分类）

        Args:
            course_title: 课程标题
            outline: 课程大纲（可选）

        Returns:
            {
                'subject_id': 学科ID (physics, chemistry, etc.),
                'subject_name': 学科名称 (物理学, 化学, etc.),
                'confidence': 置信度 (0-1),
                'is_science': 是否理科（决定是否生成模拟器）,
                'matched_keywords': 匹配的关键词列表,
                'color_scheme': 推荐配色方案,
                'visualization_elements': 推荐可视化元素,
                'decision': existing | new_subject_candidate,
                'candidate_subject': 新学科候选信息（仅 decision=new_subject_candidate 时非空）
            }
        """
        import re

        # 收集文本信息（标题权重更高）
        title_text = (course_title or "").lower().strip()
        text = title_text
        if outline:
            text += " " + (outline.description or "").lower()
            text += " " + " ".join(outline.core_concepts or []).lower()
            for ch in outline.chapters[:3]:  # 只取前3章
                text += " " + (ch.title or "").lower()
                text += " " + " ".join(ch.key_concepts or []).lower()

        subject_catalog: Dict[str, Dict[str, Any]] = {
            "physics": {
                "name": "物理学",
                "is_science": True,
                "keywords": ["物理", "大学物理", "力学", "电磁", "光学", "热力学", "牛顿", "加速度", "physics"],
            },
            "chemistry": {
                "name": "化学",
                "is_science": True,
                "keywords": ["化学", "有机化学", "无机化学", "分子", "原子", "反应", "chemistry"],
            },
            "biology": {
                "name": "生物学",
                "is_science": True,
                "keywords": ["生物", "分子生物学", "细胞生物学", "遗传学", "生态学", "biology", "dna"],
            },
            "mathematics": {
                "name": "数学",
                "is_science": True,
                "keywords": ["数学", "高等数学", "代数", "几何", "微积分", "函数", "mathematics", "math"],
            },
            "engineering": {
                "name": "工程",
                "is_science": False,
                "keywords": ["工程", "机械设计", "机械", "电气", "自动化", "通信", "土木", "engineering"],
            },
            "computer_science": {
                "name": "计算机科学",
                "is_science": False,
                "keywords": ["计算机", "数据结构", "算法", "编程", "软件工程", "computer science", "algorithm"],
            },
            "history": {
                "name": "历史",
                "is_science": False,
                "keywords": ["历史", "中国近代史", "中国近现代史", "世界史", "history"],
            },
            "economics": {
                "name": "经济学",
                "is_science": False,
                "keywords": ["经济学", "宏观经济学", "微观经济学", "金融", "会计", "economics"],
            },
            "law": {
                "name": "法学",
                "is_science": False,
                "keywords": ["法学", "法律", "宪法学", "宪法", "民法", "刑法", "law"],
            },
            "literature": {
                "name": "文学",
                "is_science": False,
                "keywords": ["文学", "英语写作", "写作", "文艺", "literature"],
            },
            "psychology": {
                "name": "心理学",
                "is_science": False,
                "keywords": ["心理学", "认知心理学", "心理健康", "psychology"],
            },
            "management": {
                "name": "管理学",
                "is_science": False,
                "keywords": ["管理学", "企业战略管理", "企业管理", "工商管理", "management"],
            },
            "philosophy": {
                "name": "哲学",
                "is_science": False,
                "keywords": ["哲学", "西方哲学史", "伦理学", "逻辑学", "philosophy"],
            },
            "geography": {
                "name": "地理",
                "is_science": False,
                "keywords": ["地理", "自然地理学", "人文地理", "地质", "geography"],
            },
            "art": {
                "name": "艺术",
                "is_science": False,
                "keywords": ["美术", "美术史", "西方美术史", "艺术", "art"],
            },
            "education": {
                "name": "教育学",
                "is_science": False,
                "keywords": ["教育学", "教育心理学", "教学法", "课程论", "education"],
            },
            "medicine": {
                "name": "医学",
                "is_science": False,
                "keywords": ["医学", "人体解剖学", "解剖学", "临床", "medicine"],
            },
            "agriculture": {
                "name": "农学",
                "is_science": False,
                "keywords": ["农学", "作物栽培学", "作物栽培", "农业", "畜牧", "agriculture"],
            },
        }

        scores: Dict[str, float] = {}
        matched: Dict[str, List[str]] = {}
        for subject_id, subject_info in subject_catalog.items():
            score = 0.0
            keywords_matched: List[str] = []
            for keyword in subject_info["keywords"]:
                key = keyword.lower()
                if key and key in text:
                    weight = 2.0 if key in title_text else 1.0
                    if len(key) >= 4:
                        weight += 0.4
                    score += weight
                    keywords_matched.append(keyword)
            if score > 0:
                scores[subject_id] = score
                matched[subject_id] = keywords_matched

        def _new_candidate() -> Dict[str, Any]:
            normalized = re.sub(r"[^a-z0-9_]+", "_", title_text)
            normalized = re.sub(r"_+", "_", normalized).strip("_")[:40] or "new_subject"
            return {
                "proposed_subject_id": normalized,
                "proposed_subject_name": (course_title or "新学科").strip()[:24] or "新学科",
                "reason": "low_confidence_or_no_match",
                "evidence": [],
            }

        def _build(subject_id: str, confidence: float, keywords: List[str], decision: str, candidate: Optional[Dict[str, Any]]) -> Dict[str, Any]:
            info = subject_catalog.get(subject_id, {"name": "通用", "is_science": False})
            return {
                "subject_id": subject_id,
                "subject_name": info["name"] if subject_id in subject_catalog else "通用",
                "is_science": bool(info.get("is_science", False)),
                "confidence": float(max(0.0, min(1.0, confidence))),
                "matched_keywords": keywords,
                "color_scheme": self.standards_loader.get_subject_color_scheme(subject_id),
                "visualization_elements": self.standards_loader.get_recommended_elements_for_subject(subject_id),
                "decision": decision,
                "candidate_subject": candidate,
            }

        if not scores:
            logger.info("No subject keywords matched for '%s', fallback to general with candidate", course_title)
            return _build(
                subject_id="general",
                confidence=0.0,
                keywords=[],
                decision="new_subject_candidate",
                candidate=_new_candidate(),
            )

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_subject_id, best_score = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0.0
        margin = (best_score - second_score) / max(best_score, 1.0)
        coverage = min(1.0, best_score / max(2.0, len(subject_catalog[best_subject_id]["keywords"]) * 0.25))
        confidence = round(max(0.0, min(1.0, 0.70 * coverage + 0.30 * max(0.0, margin))), 3)
        decision = "existing"

        if confidence < 0.34 or (second_score > 0 and margin < 0.15 and best_score < 3.0):
            candidate = _new_candidate()
            candidate["evidence"] = matched.get(best_subject_id, [])[:5]
            candidate["closest_existing_subject"] = best_subject_id
            logger.info(
                "Low-confidence subject classification for '%s': best=%s score=%.2f second=%.2f conf=%.2f -> general candidate",
                course_title,
                best_subject_id,
                best_score,
                second_score,
                confidence,
            )
            return _build(
                subject_id="general",
                confidence=confidence,
                keywords=matched.get(best_subject_id, [])[:8],
                decision="new_subject_candidate",
                candidate=candidate,
            )

        logger.info(
            "Detected subject '%s' for '%s' (score=%.2f, second=%.2f, confidence=%.2f)",
            best_subject_id,
            course_title,
            best_score,
            second_score,
            confidence,
        )
        return _build(
            subject_id=best_subject_id,
            confidence=confidence,
            keywords=matched.get(best_subject_id, [])[:8],
            decision=decision,
            candidate=None,
        )

    async def auto_classify_and_update_course(
        self,
        course_id: str,
        course_title: str,
        outline: Optional[CourseOutline] = None
    ) -> Dict[str, Any]:
        """
        自动识别课程学科并更新到数据库

        Args:
            course_id: 课程ID
            course_title: 课程标题
            outline: 课程大纲（可选）

        Returns:
            分类结果字典
        """
        # 识别学科
        classification = self.detect_course_subject(course_title, outline)

        # TODO: 将分类结果保存到数据库
        # 示例代码（需要根据实际数据库结构调整）:
        # await db.update_course_subject(course_id, classification['subject_id'])

        logger.info(f"Course '{course_id}' classified as '{classification['subject_name']}' (confidence: {classification['confidence']:.2f})")

        return classification

    async def _save_chapter_as_template(
        self,
        chapter: Dict[str, Any],
        quality_score: 'ChapterQualityScore',
        subject: str,
        topic: str
    ):
        """
        保存高质量章节作为模板，用于future agent学习 (2026-02-11: Phase 3)

        Args:
            chapter: 章节内容字典
            quality_score: ChapterQualityScore对象
            subject: 学科 (如 "physics", "mathematics")
            topic: 主题 (章节标题)
        """
        from app.services.learning import UnifiedTemplateService, ChapterScorer
        import re

        if not self.generator.db:
            logger.warning("No database session available, cannot save chapter template")
            return

        try:
            template_service = UnifiedTemplateService(self.generator.db)
            scorer = ChapterScorer()

            # 标准化topic名称 (移除特殊字符，转为小写下划线)
            topic_normalized = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]+', '_', topic).lower().strip('_')

            # 提取章节元数据用于学习
            metadata = scorer.extract_metadata(chapter)

            # 添加额外的学习insights
            metadata['quality_breakdown'] = {
                'depth_score': quality_score.depth_score,
                'structure_score': quality_score.structure_score,
                'visual_score': quality_score.visual_score,
                'teaching_score': quality_score.teaching_score,
                'simulator_score': quality_score.simulator_score,
            }

            # 保存评分详情
            score_breakdown = {
                'depth_score': quality_score.depth_score,
                'structure_score': quality_score.structure_score,
                'visual_score': quality_score.visual_score,
                'teaching_score': quality_score.teaching_score,
                'simulator_score': quality_score.simulator_score,
            }

            # 保存为模板
            await template_service.save_as_template(
                template_type='chapter_content',
                subject=subject,
                topic=topic_normalized,
                content=chapter,  # 完整章节内容
                quality_score=quality_score.total_score,
                score_breakdown=score_breakdown,
                metadata=metadata,
                difficulty_level=chapter.get('complexity_level', 'standard')
            )

            logger.info(f"Chapter template saved: {subject}/{topic_normalized} (score: {quality_score.total_score:.1f})")

        except Exception as e:
            logger.error(f"Failed to save chapter as template: {e}")
            import traceback
            logger.error(traceback.format_exc())
