"""
课程生成服务 - 监督者+生成者架构的主入口
"""

import json
import logging
import uuid
import io
from typing import AsyncGenerator, Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from .supervisor import CourseSupervisor
from .generator import ChapterGenerator, GeneratorPromptBuilder
from .models import (
    GenerationState, CourseOutline, ChapterResult, ReviewResult,
    ReviewStatus, ChapterQualityStandards, ChapterOutline
)
from app.services.gemini_service import gemini_service
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)


class CourseGenerationService:
    """
    课程生成服务

    使用监督者+生成者架构：
    - 监督者：生成大纲、审核章节、决定是否重做
    - 生成者：根据指令生成单个章节
    """

    def __init__(self):
        self.supervisor = CourseSupervisor()
        self.generator = ChapterGenerator()

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

            outline = await self.supervisor.generate_outline(state, system_prompt)

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
                    }
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

                        # === 步骤检测已完成，跳过章节级别评审，直接通过 ===
                        logger.info(f"Chapter {chapter_index + 1} step-by-step check completed, skipping chapter review")
                        break

                    except ValueError as e:
                        logger.error(f"Failed to parse chapter {chapter_index + 1}: {e}")

                        # JSON解析失败，只重试骨架生成（最多2次额外重试）
                        state.increment_attempt()

                        if state.current_attempt <= 2:
                            # 让监督者分析 JSON 错误并生成修复指导
                            json_fix_guidance = await self.supervisor.analyze_json_error(
                                raw_response=full_response,
                                error_message=str(e),
                                chapter_index=chapter_index
                            )
                            state.last_json_error = str(e)
                            state.json_fix_guidance = json_fix_guidance

                            yield {
                                "event": "skeleton_retry",
                                "data": {
                                    "index": chapter_index,
                                    "attempt": state.current_attempt,
                                    "reason": f"骨架JSON解析失败，重新生成骨架",
                                    "error": str(e)[:200]
                                }
                            }
                            continue
                        else:
                            # 超过重试次数，使用默认骨架
                            logger.warning(f"Chapter {chapter_index + 1} JSON parse failed after retries, using default skeleton")
                            chapter = self._get_default_chapter_skeleton(chapter_outline, chapter_index)
                            # 使用默认骨架后直接跳出循环
                            break

                # 保存章节
                if chapter:
                    state.add_completed_chapter(chapter)

                    # 处理章节中的图片
                    chapter_dict = self._chapter_to_dict(chapter)
                    chapter_dict = await self._process_chapter_images(chapter_dict, state.course_title)

                    yield {
                        "event": "chapter_complete",
                        "data": {
                            "index": chapter_index,
                            "total": outline.total_chapters,
                            "chapter": chapter_dict,
                            "attempts": state.current_attempt + 1
                        }
                    }

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
            "script": [
                {
                    "step_id": step.step_id,
                    "type": step.type,
                    "title": step.title,
                    "content": step.content,
                    "simulator_spec": {
                        "mode": step.simulator_spec.mode,
                        "name": step.simulator_spec.name,
                        "description": step.simulator_spec.description,
                        "variables": step.simulator_spec.variables,
                        "custom_code": step.simulator_spec.custom_code
                    } if step.simulator_spec else None,
                    "assessment_spec": step.assessment_spec,
                    "diagram_spec": step.diagram_spec
                }
                for step in chapter.script
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

        for step in chapter_dict.get("script", []):
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
                        "chapter_type": chapter_outline.chapter_type.value
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
        for i, step in enumerate(chapter.script):
            step_passed = False
            max_step_retries = 2

            for retry in range(max_step_retries):
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
                                "learning_objectives": chapter.learning_objectives
                            },
                            system_prompt=generator_system_prompt,
                            min_length=150,
                            max_length=400
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
                                    "elements": step.diagram_spec.get('elements', [])
                                },
                                system_prompt=generator_system_prompt,
                                min_length=80,
                                max_length=200
                            )
                            desc = step.diagram_spec['description']

                        if len(desc) >= 50:
                            logger.info(f"[Step Check] Step {i+1} diagram description passed: {len(desc)} chars")
                        else:
                            logger.warning(f"[Step Check] Step {i+1} diagram description too short ({len(desc)} chars)")
                            step_passed = False
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
                                    "options": q.get('options', [])
                                },
                                system_prompt=generator_system_prompt,
                                min_length=30,
                                max_length=100
                            )

                        if len(q.get('explanation', '')) < 20:
                            all_explanations_ok = False
                            logger.warning(f"[Step Check] Question {q_idx+1} explanation too short")

                    if all_explanations_ok:
                        step_passed = True
                        logger.info(f"[Step Check] Step {i+1} assessment passed: {len(questions)} questions")
                    else:
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
                                "variables": step.simulator_spec.variables
                            },
                            system_prompt=generator_system_prompt,
                            min_length=50,
                            max_length=150
                        )
                        desc = step.simulator_spec.description

                    if len(desc) >= 30:
                        step_passed = True
                        logger.info(f"[Step Check] Step {i+1} simulator description passed: {len(desc)} chars")
                    else:
                        logger.warning(f"[Step Check] Step {i+1} simulator description too short ({len(desc)} chars)")
                        continue

                else:
                    # 其他类型步骤直接通过
                    step_passed = True

                if step_passed:
                    break

            if not step_passed:
                logger.warning(f"[Step Check] Step {i+1} '{step.title}' failed after {max_step_retries} retries, using current content")

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

    async def _generate_text_content(
        self,
        content_type: str,
        context: Dict[str, Any],
        system_prompt: str,
        min_length: int,
        max_length: int
    ) -> str:
        """生成单个文本内容"""
        from app.services.claude_service import ClaudeService

        # 方案B：强化提示词，强调纯文本输出
        format_warning = """
【输出格式要求 - 必须遵守】
- 直接输出纯文本，不要使用任何代码块（如 ```json 或 ```）
- 不要使用 JSON 格式（如 {"content": "..."}）
- 不要在文本中使用转义字符（如 \\n 或 \\"）
- 直接输出中文文字内容"""

        prompts = {
            "rationale": f"""请为以下章节生成设计理念说明。

课程：{context.get('course_title', '')}
章节：{context.get('chapter_title', '')}
学习目标：{', '.join(context.get('learning_objectives', []))}
章节类型：{context.get('chapter_type', '')}

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

要求：
- {min_length}-{max_length}字
- 详细描述图片应该展示的内容
- 包括：主题、场景、元素、布局、风格
- 描述越详细，生成的图片越准确
{format_warning}""",

            "question_explanation": f"""请为以下选择题生成答案解析。

问题：{context.get('question', '')}
正确答案：{context.get('correct_answer', '')}
选项：{', '.join(context.get('options', []))}

要求：
- {min_length}-{max_length}字
- 解释为什么正确答案是对的
- 简要说明其他选项为什么不对
{format_warning}""",

            "simulator_description": f"""请为以下模拟器生成详细描述。

课程：{context.get('course_title', '')}
章节：{context.get('chapter_title', '')}
模拟器名称：{context.get('simulator_name', '')}
变量：{', '.join([v.get('label', v.get('name', '')) for v in context.get('variables', [])])}

要求：
- {min_length}-{max_length}字
- 说明模拟器要展示什么概念
- 描述交互效果和视觉呈现
{format_warning}"""
        }

        prompt = prompts.get(content_type, prompts["step_body"])

        try:
            claude_service = ClaudeService()
            response = await claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=500
            )
            # 方案A：使用清理函数处理响应
            return self._clean_text_response(response)
        except Exception as e:
            logger.error(f"Failed to generate {content_type}: {e}")
            return f"[内容生成失败: {content_type}]"

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

        # 是否使用递进式生成（新策略）
        use_progressive = True

        for step_idx, step in enumerate(chapter.script):
            if step.type == 'simulator' and step.simulator_spec:
                # 方案C：如果变量为空或太少，添加默认变量
                if not step.simulator_spec.variables or len(step.simulator_spec.variables) < 3:
                    logger.warning(f"Simulator '{step.simulator_spec.name}' has insufficient variables, adding defaults...")
                    step.simulator_spec.variables = self._get_default_variables(
                        step.simulator_spec.name,
                        step.simulator_spec.description,
                        chapter.title
                    )

                code = step.simulator_spec.custom_code or ""
                code_lines = len([l for l in code.split('\n') if l.strip()])

                # 如果代码为空或太短，生成新代码
                if code_lines < 20:
                    logger.info(f"Generating code for simulator '{step.simulator_spec.name}'...")

                    # 构建章节上下文
                    chapter_context = f"""
课程：{state.course_title}
章节：{chapter.title}
学习目标：{', '.join(chapter.learning_objectives)}
模拟器主题：{chapter_outline.suggested_simulator or step.simulator_spec.description}
"""

                    if use_progressive:
                        # ========== 递进式生成（新策略）==========
                        logger.info(f"Using progressive generation for '{step.simulator_spec.name}'...")

                        try:
                            result_code = None
                            async for event in self.generator.generate_simulator_code_progressive(
                                simulator_name=step.simulator_spec.name,
                                simulator_description=step.simulator_spec.description,
                                variables=step.simulator_spec.variables,
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

                            if result_code:
                                step.simulator_spec.custom_code = result_code
                                new_lines = len([l for l in result_code.split('\n') if l.strip()])
                                logger.info(f"Progressive generation completed: {new_lines} lines")

                                # 质量评分检查
                                quality_passed, quality_score, quality_report = self.generator.validate_code_quality(
                                    code=result_code,
                                    variables=step.simulator_spec.variables,
                                    threshold=70
                                )

                                if quality_passed:
                                    logger.info(f"Simulator '{step.simulator_spec.name}' quality score: {quality_score.total_score}/100 - PASSED")
                                else:
                                    logger.warning(f"Simulator '{step.simulator_spec.name}' quality score: {quality_score.total_score}/100 - FAILED, using fallback")
                                    step.simulator_spec.custom_code = self._get_fallback_simulator_code(
                                        step.simulator_spec.name,
                                        step.simulator_spec.variables
                                    )

                        except Exception as e:
                            logger.error(f"Progressive generation failed: {e}")
                            step.simulator_spec.custom_code = self._get_fallback_simulator_code(
                                step.simulator_spec.name,
                                step.simulator_spec.variables
                            )

                    else:
                        # ========== 原有生成逻辑（保留作为备选）==========
                        error_history: List[Dict[str, Any]] = []
                        max_simulator_retries = 3

                        for retry in range(max_simulator_retries):
                            try:
                                # 如果有错误历史，获取调整后的提示词
                                additional_prompt = ""
                                if error_history:
                                    check_result = await self.supervisor.check_step_immediately(
                                        state=state,
                                        chapter=chapter,
                                        step_index=step_idx,
                                        previous_errors=error_history
                                    )
                                    additional_prompt = check_result.get('adjusted_prompt', '')

                                # 单独生成模拟器代码
                                new_code = await self.generator.generate_simulator_code(
                                    simulator_name=step.simulator_spec.name,
                                    simulator_description=step.simulator_spec.description,
                                    variables=step.simulator_spec.variables,
                                    chapter_context=chapter_context,
                                    system_prompt=generator_system_prompt,
                                    additional_prompt=additional_prompt
                                )

                                if new_code:
                                    step.simulator_spec.custom_code = new_code
                                    new_lines = len([l for l in new_code.split('\n') if l.strip()])
                                    logger.info(f"Simulator code generated: {new_lines} lines")

                                    # === 碎片化检查：立即检查生成的代码 ===
                                    check_result = await self.supervisor.check_step_immediately(
                                        state=state,
                                        chapter=chapter,
                                        step_index=step_idx,
                                        previous_errors=error_history
                                    )

                                    if check_result['approved']:
                                        # === 新增：质量评分检查 ===
                                        quality_passed, quality_score, quality_report = self.generator.validate_code_quality(
                                            code=new_code,
                                            variables=step.simulator_spec.variables,
                                            threshold=70  # 质量阈值
                                        )

                                        if quality_passed:
                                            logger.info(f"Simulator '{step.simulator_spec.name}' passed check and quality score: {quality_score.total_score}/100")
                                            break
                                        else:
                                            # 质量评分不通过，记录问题并重试
                                            logger.warning(f"Simulator quality score too low: {quality_score.total_score}/100")
                                            error_history.append({
                                                'retry': retry,
                                                'issues': quality_score.issues,
                                                'error_type': 'low_quality_score',
                                                'quality_score': quality_score.total_score,
                                                'quality_report': quality_report
                                            })

                                            if retry < max_simulator_retries - 1:
                                                logger.info(f"Retrying due to low quality score ({retry + 1}/{max_simulator_retries})...")
                                                continue
                                            else:
                                                # 最后一次重试，接受当前代码
                                                logger.warning(f"Accepting code with quality score {quality_score.total_score}/100 after {max_simulator_retries} retries")
                                                break
                                    else:
                                        # 检查失败，记录错误
                                        error_history.append({
                                            'retry': retry,
                                            'issues': check_result['issues'],
                                            'error_type': check_result.get('error_type')
                                        })

                                        if retry < max_simulator_retries - 1:
                                            # 让AI决定是修改还是重新生成
                                            decision = await self.supervisor.get_revision_or_regenerate_decision(
                                                state=state,
                                                chapter=chapter,
                                                step_index=step_idx,
                                                check_result=check_result
                                            )

                                            logger.info(f"AI decision: {decision['decision']} - {decision['reason']}")

                                            if decision['decision'] == 'revise':
                                                # 修改模式：保留部分代码，只修改问题部分
                                                # 这里通过 additional_prompt 传递修改指导
                                                pass
                                            # regenerate 模式会在下一次循环重新生成

                                            continue
                                        else:
                                            logger.warning(f"Simulator check failed after {max_simulator_retries} retries, using current version")

                                    # 检查是否是 fallback 代码
                                    if 'Fallback 模拟器' in new_code or '基础模拟器' in new_code:
                                        if retry < max_simulator_retries - 1:
                                            error_history.append({
                                                'retry': retry,
                                                'issues': ['生成了 fallback 代码'],
                                                'error_type': 'fallback_code'
                                            })
                                            logger.warning(f"Got fallback code, retrying ({retry + 1}/{max_simulator_retries})...")
                                            continue
                                        else:
                                            logger.warning(f"Using fallback code after {max_simulator_retries} retries")
                                    break

                            except Exception as e:
                                error_msg = str(e)
                                logger.error(f"Failed to generate simulator code (attempt {retry + 1}): {error_msg}")

                                # 解析错误类型
                                if error_msg.startswith('invalid_api:'):
                                    error_type = 'invalid_api'
                                elif error_msg.startswith('missing_function:'):
                                    error_type = 'missing_function'
                                else:
                                    error_type = 'exception'

                                error_history.append({
                                    'retry': retry,
                                    'issues': [error_msg],
                                    'error_type': error_type
                                })
                                if retry < max_simulator_retries - 1:
                                    continue
                                # 最后一次重试失败，使用 fallback 代码
                                step.simulator_spec.custom_code = self._get_fallback_simulator_code(
                                    step.simulator_spec.name,
                                    step.simulator_spec.variables
                                )

        yield {"event": "_chapter_done", "data": {"chapter": chapter}}

    def _get_default_variables(self, name: str, description: str, chapter_title: str) -> list:
        """
        方案C：根据模拟器名称和描述生成默认变量

        当骨架生成的变量为空或不足时，提供合理的默认变量
        """
        # 通用默认变量模板
        default_vars = [
            {"name": "param1", "label": "参数1", "min": 0, "max": 100, "default": 50, "step": 1, "unit": ""},
            {"name": "param2", "label": "参数2", "min": 0, "max": 100, "default": 50, "step": 1, "unit": ""},
            {"name": "param3", "label": "参数3", "min": 0, "max": 100, "default": 50, "step": 1, "unit": ""},
            {"name": "param4", "label": "参数4", "min": 0, "max": 100, "default": 50, "step": 1, "unit": ""},
            {"name": "speed", "label": "速度", "min": 1, "max": 100, "default": 50, "step": 1, "unit": ""},
        ]

        # 根据关键词匹配更合适的变量
        keywords = (name + " " + description + " " + chapter_title).lower()

        if any(k in keywords for k in ["速度", "speed", "运动", "移动"]):
            default_vars[0] = {"name": "speed", "label": "速度", "min": 1, "max": 100, "default": 50, "step": 1, "unit": "m/s"}
        if any(k in keywords for k in ["质量", "mass", "重量"]):
            default_vars[1] = {"name": "mass", "label": "质量", "min": 1, "max": 100, "default": 10, "step": 1, "unit": "kg"}
        if any(k in keywords for k in ["力", "force", "推力"]):
            default_vars[2] = {"name": "force", "label": "力", "min": 0, "max": 100, "default": 20, "step": 1, "unit": "N"}
        if any(k in keywords for k in ["时间", "time", "周期"]):
            default_vars[3] = {"name": "time", "label": "时间", "min": 1, "max": 60, "default": 10, "step": 1, "unit": "s"}
        if any(k in keywords for k in ["数量", "count", "个数"]):
            default_vars[4] = {"name": "count", "label": "数量", "min": 1, "max": 20, "default": 5, "step": 1, "unit": "个"}
        if any(k in keywords for k in ["比例", "ratio", "百分比"]):
            default_vars[0] = {"name": "ratio", "label": "比例", "min": 0, "max": 100, "default": 50, "step": 5, "unit": "%"}
        if any(k in keywords for k in ["温度", "temperature", "热"]):
            default_vars[1] = {"name": "temperature", "label": "温度", "min": 0, "max": 100, "default": 25, "step": 1, "unit": "°C"}
        if any(k in keywords for k in ["距离", "distance", "长度"]):
            default_vars[2] = {"name": "distance", "label": "距离", "min": 1, "max": 100, "default": 50, "step": 1, "unit": "m"}
        if any(k in keywords for k in ["角度", "angle", "旋转"]):
            default_vars[3] = {"name": "angle", "label": "角度", "min": 0, "max": 360, "default": 45, "step": 5, "unit": "°"}
        if any(k in keywords for k in ["频率", "frequency", "hz"]):
            default_vars[4] = {"name": "frequency", "label": "频率", "min": 1, "max": 100, "default": 10, "step": 1, "unit": "Hz"}

        return default_vars

    def _get_fallback_simulator_code(self, name: str, variables: list) -> str:
        """生成教育性 fallback 模拟器代码（委托给 generator）"""
        return self.generator._get_fallback_code(name, variables)

    def _get_default_chapter_skeleton(self, chapter_outline: 'ChapterOutline', chapter_index: int) -> 'ChapterResult':
        """生成默认章节骨架（当JSON解析多次失败时使用）"""
        from .models import ChapterResult, ChapterStep, SimulatorSpec
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
                simulator_spec=SimulatorSpec(
                    name=chapter_outline.suggested_simulator or f'{chapter_outline.title}模拟器',
                    description='',
                    variables=[
                        {'name': 'param1', 'label': '参数1', 'min': 0, 'max': 100, 'default': 50, 'step': 1, 'unit': ''},
                        {'name': 'param2', 'label': '参数2', 'min': 0, 'max': 100, 'default': 50, 'step': 1, 'unit': ''},
                        {'name': 'param3', 'label': '参数3', 'min': 0, 'max': 100, 'default': 50, 'step': 1, 'unit': ''}
                    ],
                    custom_code=''
                )
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
                    code = new_step.simulator_spec.custom_code or ""
                    code_lines = len([l for l in code.split('\n') if l.strip()])

                    if code_lines < 20:
                        chapter_outline = state.outline.chapters[chapter_index]
                        chapter_context = f"""
课程：{state.course_title}
章节：{chapter.title}
学习目标：{', '.join(chapter.learning_objectives)}
模拟器主题：{chapter_outline.suggested_simulator or new_step.simulator_spec.description}
"""
                        new_code = await self.generator.generate_simulator_code(
                            simulator_name=new_step.simulator_spec.name,
                            simulator_description=new_step.simulator_spec.description,
                            variables=new_step.simulator_spec.variables,
                            chapter_context=chapter_context,
                            system_prompt=generator_system_prompt
                        )
                        if new_code:
                            new_step.simulator_spec.custom_code = new_code

                # 替换原步骤
                chapter.script[step_index] = new_step
                state.increment_step_retry(step_index)
                fixed_steps.append(step_index)

                logger.info(f"步骤 {step_index + 1} 修复成功")

            except Exception as e:
                logger.error(f"修复步骤 {step_index + 1} 失败: {e}")
                state.increment_step_retry(step_index)

        return fixed_steps
