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

                        # === 分步生成：为模拟器单独生成代码 ===
                        chapter = await self._generate_simulator_codes(
                            chapter=chapter,
                            chapter_outline=chapter_outline,
                            generator_system_prompt=generator_system_prompt,
                            state=state
                        )

                    except ValueError as e:
                        logger.error(f"Failed to parse chapter {chapter_index + 1}: {e}")

                        # 让监督者分析 JSON 错误并生成修复指导
                        json_fix_guidance = await self.supervisor.analyze_json_error(
                            raw_response=full_response,
                            error_message=str(e),
                            chapter_index=chapter_index
                        )

                        state.increment_attempt()
                        state.last_json_error = str(e)
                        state.json_fix_guidance = json_fix_guidance

                        yield {
                            "event": "chapter_retry",
                            "data": {
                                "index": chapter_index,
                                "attempt": state.current_attempt,
                                "reason": f"JSON解析失败: {str(e)}",
                                "fix_guidance": json_fix_guidance
                            }
                        }
                        continue

                    # 审核章节
                    review = await self.supervisor.ai_review_chapter(
                        state=state,
                        chapter=chapter,
                        chapter_index=chapter_index
                    )

                    yield {
                        "event": "chapter_review",
                        "data": {
                            "index": chapter_index,
                            "status": review.status.value,
                            "score": review.overall_score,
                            "issues": review.issues,
                            "simulator_issues": review.simulator_issues,
                            "comment": review.review_comment
                        }
                    }

                    if review.is_approved():
                        # 审核通过
                        break
                    else:
                        # 需要重试
                        state.increment_attempt()
                        if state.can_retry():
                            yield {
                                "event": "chapter_retry",
                                "data": {
                                    "index": chapter_index,
                                    "attempt": state.current_attempt,
                                    "reason": review.get_rejection_reason()
                                }
                            }
                        else:
                            # 达到最大重试次数，使用当前版本
                            logger.warning(f"Chapter {chapter_index + 1} reached max retries, using current version")

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

    async def _generate_simulator_codes(
        self,
        chapter: 'ChapterResult',
        chapter_outline: 'ChapterOutline',
        generator_system_prompt: str,
        state: GenerationState
    ) -> 'ChapterResult':
        """
        分步生成：为章节中的模拟器单独生成代码

        由于提示词要求 AI 将 custom_code 留空，这里为所有模拟器生成代码。
        这样可以避免在一个大 JSON 中嵌入长代码导致的转义问题。
        """
        from .models import ChapterResult

        for step in chapter.script:
            if step.type == 'simulator' and step.simulator_spec:
                code = step.simulator_spec.custom_code or ""
                code_lines = len([l for l in code.split('\n') if l.strip()])

                # 如果代码为空或太短，生成新代码
                if code_lines < 20:
                    logger.info(f"Generating code for simulator '{step.simulator_spec.name}'...")

                    try:
                        # 构建章节上下文
                        chapter_context = f"""
课程：{state.course_title}
章节：{chapter.title}
学习目标：{', '.join(chapter.learning_objectives)}
模拟器主题：{chapter_outline.suggested_simulator or step.simulator_spec.description}
"""

                        # 单独生成模拟器代码
                        new_code = await self.generator.generate_simulator_code(
                            simulator_name=step.simulator_spec.name,
                            simulator_description=step.simulator_spec.description,
                            variables=step.simulator_spec.variables,
                            chapter_context=chapter_context,
                            system_prompt=generator_system_prompt
                        )

                        if new_code:
                            step.simulator_spec.custom_code = new_code
                            new_lines = len([l for l in new_code.split('\n') if l.strip()])
                            logger.info(f"Simulator code generated: {new_lines} lines")

                    except Exception as e:
                        logger.error(f"Failed to generate simulator code: {e}")
                        # 生成一个基础的占位代码
                        step.simulator_spec.custom_code = self._get_fallback_simulator_code(
                            step.simulator_spec.name,
                            step.simulator_spec.variables
                        )

        return chapter

    def _get_fallback_simulator_code(self, name: str, variables: list) -> str:
        """生成一个基础的占位模拟器代码"""
        var_reads = "\n".join([
            f"  const {v.get('name', f'var{i}')} = ctx.getVar('{v.get('name', f'var{i}')}');"
            for i, v in enumerate(variables)
        ])

        return f'''// {name} - 基础模拟器
let elements = {{}};

function setup(ctx) {{
  const {{ width, height }} = ctx;

  // 标题
  elements.title = ctx.createText('{name}', width/2, 30, {{
    fontSize: 24, fontWeight: 'bold', color: '#ffffff'
  }});

  // 背景
  ctx.createRect(width/2, height/2, width-40, height-80, '#1a2a3a', 12);

  // 提示文字
  elements.hint = ctx.createText('拖动下方滑块查看效果变化', width/2, height/2, {{
    fontSize: 18, color: '#94a3b8'
  }});
}}

function update(ctx) {{
  const {{ width, height, math, time }} = ctx;
{var_reads}

  // 基础动画
  const pulse = math.sin(time * 2) * 0.1 + 1;
}}
'''
