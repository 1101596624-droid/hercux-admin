# ============================================
# generation/v2_generator.py - V2 生成器（基于处理器插件）
# ============================================

from typing import AsyncGenerator
from processors import get_processor
from json_utils import safe_parse_json


class V2Generator:
    """V2 课程生成器 - 使用处理器插件系统"""

    def __init__(self, provider):
        self.provider = provider

    async def generate_stream(
        self,
        source_material: str,
        course_title: str,
        processor_id: str = "intelligent",
        source_info: str = ""
    ) -> AsyncGenerator[dict, None]:
        """
        使用处理器插件系统的 v2 流式生成

        第一阶段：生成课程结构（使用处理器的 build_structure_prompt）
        第二阶段：逐个生成每个课时的详细内容（使用处理器的 build_lesson_prompt）

        Yields dict with:
        - type: "phase" | "structure" | "lesson_start" | "chunk" | "lesson_complete" | "complete" | "error"
        - data: 相关数据
        """
        try:
            # 获取处理器
            processor = get_processor(processor_id)
            processor_info = processor.get_info()

            yield {"type": "phase", "data": {
                "phase": 1,
                "message": f"正在使用 {processor_info['name']} 分析素材，设计课程结构...",
                "processor": processor_info
            }}

            # ========== 第一阶段：生成课程结构 ==========
            structure_prompt = processor.build_structure_prompt(
                source_material=source_material,
                course_title=course_title
            )
            structure_content = ""

            async for chunk in self.provider.generate_stream(structure_prompt, max_tokens=16000):
                structure_content += chunk
                yield {"type": "chunk", "data": {"content": chunk, "phase": 1}}

            # 解析结构
            structure = safe_parse_json(structure_content)
            if not structure:
                yield {"type": "error", "data": {"message": "无法解析课程结构，请重试"}}
                return

            # 处理器后处理结构
            structure = processor.process_structure(structure)

            lessons_outline = structure.get("lessons", [])
            meta = {
                "title": structure.get("title", course_title),
                "description": structure.get("description", ""),
                "estimated_hours": structure.get("estimated_hours", len(lessons_outline) * 0.5)
            }
            total_lessons = len(lessons_outline)

            yield {"type": "structure", "data": {
                "meta": meta,
                "lessons_count": total_lessons,
                "lessons_outline": lessons_outline,
                "processor": processor_info
            }}

            # ========== 第二阶段：逐个生成课时内容 ==========
            yield {"type": "phase", "data": {
                "phase": 2,
                "message": f"开始生成 {total_lessons} 个课时的详细内容..."
            }}

            completed_lessons = []
            previous_summary = ""

            for i, lesson_outline in enumerate(lessons_outline):
                yield {"type": "lesson_start", "data": {
                    "index": i,
                    "total": total_lessons,
                    "title": lesson_outline.get("title", f"课时 {i+1}"),
                    "recommended_forms": lesson_outline.get("recommended_forms", []),
                    "complexity_level": lesson_outline.get("complexity_level", "standard")
                }}

                # 使用处理器构建课时 prompt
                lesson_prompt = processor.build_lesson_prompt(
                    source_material=source_material,
                    course_title=course_title,
                    lesson_info=lesson_outline,
                    lesson_index=i,
                    total_lessons=total_lessons,
                    previous_summary=previous_summary
                )

                lesson_content = ""
                async for chunk in self.provider.generate_stream(lesson_prompt, max_tokens=12000):
                    lesson_content += chunk
                    yield {"type": "chunk", "data": {"content": chunk, "phase": 2, "lesson_index": i}}

                # 解析课时内容
                lesson_data = safe_parse_json(lesson_content)

                if lesson_data:
                    # 处理器后处理课时
                    lesson_data = processor.process_lesson(lesson_data, lesson_outline)

                    # 保存摘要用于下一课时衔接
                    previous_summary = lesson_data.get("summary", f"课时 {i+1}: {lesson_outline.get('title', '')}")

                    # 合并课时大纲和详细内容
                    full_lesson = {
                        "title": lesson_data.get("title", lesson_outline.get("title")),
                        "rationale": lesson_data.get("rationale", lesson_outline.get("rationale", "")),
                        "learning_objectives": lesson_data.get("learning_objectives", lesson_outline.get("learning_objectives", [])),
                        "complexity_level": lesson_data.get("complexity_level", lesson_outline.get("complexity_level", "standard")),
                        "estimated_minutes": lesson_data.get("estimated_minutes", lesson_outline.get("estimated_minutes", 30)),
                        "prerequisites": lesson_outline.get("prerequisites", []),
                        "script": lesson_data.get("script", [])
                    }
                    completed_lessons.append(full_lesson)

                    yield {"type": "lesson_complete", "data": {
                        "index": i,
                        "total": total_lessons,
                        "lesson": full_lesson
                    }}
                else:
                    # 解析失败，使用基本结构
                    basic_lesson = {
                        "title": lesson_outline.get("title", f"课时 {i+1}"),
                        "rationale": lesson_outline.get("rationale", ""),
                        "learning_objectives": lesson_outline.get("learning_objectives", []),
                        "complexity_level": lesson_outline.get("complexity_level", "standard"),
                        "estimated_minutes": lesson_outline.get("estimated_minutes", 30),
                        "prerequisites": lesson_outline.get("prerequisites", []),
                        "script": []
                    }
                    completed_lessons.append(basic_lesson)
                    yield {"type": "lesson_complete", "data": {
                        "index": i,
                        "total": total_lessons,
                        "lesson": basic_lesson,
                        "warning": "课时内容解析失败，使用基本结构"
                    }}

            # ========== 组装最终课程包 ==========
            final_raw = {
                "meta": meta,
                "lessons": completed_lessons
            }

            yield {"type": "complete", "data": {
                "raw": final_raw,
                "processor_id": processor_id
            }}

        except Exception as e:
            yield {"type": "error", "data": {"message": str(e)}}

    async def generate_stream_resume(
        self,
        source_material: str,
        course_title: str,
        processor_id: str,
        source_info: str,
        resume_from_lesson: int,
        completed_lessons: list,
        lessons_outline: list,
        meta: dict = None
    ) -> AsyncGenerator[dict, None]:
        """
        断点续传：从指定课时继续生成
        跳过已完成的课时，从 resume_from_lesson 开始继续
        """
        try:
            # 获取处理器
            processor = get_processor(processor_id)
            processor_info = processor.get_info()

            # 发送恢复信息
            yield {"type": "phase", "data": {
                "phase": 2,
                "message": f"从课时 {resume_from_lesson + 1} 继续生成...",
                "processor": processor_info
            }}

            # 发送已有的结构信息
            total_lessons = len(lessons_outline)
            yield {"type": "structure", "data": {
                "meta": meta or {"title": course_title, "description": "", "estimated_hours": total_lessons * 0.5},
                "lessons_count": total_lessons,
                "lessons_outline": lessons_outline,
                "processor": processor_info
            }}

            # 使用已完成的课时
            all_lessons = list(completed_lessons)

            # 计算上一课时的摘要（用于衔接）
            previous_summary = ""
            if resume_from_lesson > 0 and len(completed_lessons) > 0:
                last_completed = completed_lessons[-1]
                previous_summary = last_completed.get("summary", f"课时 {resume_from_lesson}: {last_completed.get('title', '')}")

            # 从中断处继续生成
            for i in range(resume_from_lesson, total_lessons):
                lesson_outline = lessons_outline[i]

                yield {"type": "lesson_start", "data": {
                    "index": i,
                    "total": total_lessons,
                    "title": lesson_outline.get("title", f"课时 {i+1}"),
                    "recommended_forms": lesson_outline.get("recommended_forms", []),
                    "complexity_level": lesson_outline.get("complexity_level", "standard")
                }}

                # 使用处理器构建课时 prompt
                lesson_prompt = processor.build_lesson_prompt(
                    source_material=source_material,
                    course_title=course_title,
                    lesson_info=lesson_outline,
                    lesson_index=i,
                    total_lessons=total_lessons,
                    previous_summary=previous_summary
                )

                lesson_content = ""
                async for chunk in self.provider.generate_stream(lesson_prompt, max_tokens=12000):
                    lesson_content += chunk
                    yield {"type": "chunk", "data": {"content": chunk, "phase": 2, "lesson_index": i}}

                # 解析课时内容
                lesson_data = safe_parse_json(lesson_content)

                if lesson_data:
                    # 处理器后处理课时
                    lesson_data = processor.process_lesson(lesson_data, lesson_outline)

                    # 保存摘要用于下一课时衔接
                    previous_summary = lesson_data.get("summary", f"课时 {i+1}: {lesson_outline.get('title', '')}")

                    # 合并课时大纲和详细内容
                    full_lesson = {
                        "title": lesson_data.get("title", lesson_outline.get("title")),
                        "rationale": lesson_data.get("rationale", lesson_outline.get("rationale", "")),
                        "learning_objectives": lesson_data.get("learning_objectives", lesson_outline.get("learning_objectives", [])),
                        "complexity_level": lesson_data.get("complexity_level", lesson_outline.get("complexity_level", "standard")),
                        "estimated_minutes": lesson_data.get("estimated_minutes", lesson_outline.get("estimated_minutes", 30)),
                        "prerequisites": lesson_outline.get("prerequisites", []),
                        "script": lesson_data.get("script", [])
                    }
                    all_lessons.append(full_lesson)

                    yield {"type": "lesson_complete", "data": {
                        "index": i,
                        "total": total_lessons,
                        "lesson": full_lesson
                    }}
                else:
                    # 解析失败，使用基本结构
                    basic_lesson = {
                        "title": lesson_outline.get("title", f"课时 {i+1}"),
                        "rationale": lesson_outline.get("rationale", ""),
                        "learning_objectives": lesson_outline.get("learning_objectives", []),
                        "complexity_level": lesson_outline.get("complexity_level", "standard"),
                        "estimated_minutes": lesson_outline.get("estimated_minutes", 30),
                        "prerequisites": lesson_outline.get("prerequisites", []),
                        "script": []
                    }
                    all_lessons.append(basic_lesson)
                    yield {"type": "lesson_complete", "data": {
                        "index": i,
                        "total": total_lessons,
                        "lesson": basic_lesson,
                        "warning": "课时内容解析失败，使用基本结构"
                    }}

            # 组装最终课程包
            final_raw = {
                "meta": meta or {"title": course_title, "description": "", "estimated_hours": total_lessons * 0.5},
                "lessons": all_lessons
            }

            yield {"type": "complete", "data": {
                "raw": final_raw,
                "processor_id": processor_id
            }}

        except Exception as e:
            yield {"type": "error", "data": {"message": str(e)}}
