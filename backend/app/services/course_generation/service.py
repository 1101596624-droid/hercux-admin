"""
课程生成服务 - 监督者+生成者架构的主入口
"""

import json
import logging
import uuid
from typing import AsyncGenerator, Dict, Any, Optional, List
from datetime import datetime

from .supervisor import CourseSupervisor
from .generator import ChapterGenerator, GeneratorPromptBuilder
from .models import (
    GenerationState, CourseOutline, ChapterResult, ReviewResult,
    ReviewStatus, ChapterQualityStandards
)

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
                    except ValueError as e:
                        logger.error(f"Failed to parse chapter {chapter_index + 1}: {e}")
                        state.increment_attempt()
                        yield {
                            "event": "chapter_retry",
                            "data": {
                                "index": chapter_index,
                                "attempt": state.current_attempt,
                                "reason": f"解析失败: {str(e)}"
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

                    yield {
                        "event": "chapter_complete",
                        "data": {
                            "index": chapter_index,
                            "total": outline.total_chapters,
                            "chapter": self._chapter_to_dict(chapter),
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
