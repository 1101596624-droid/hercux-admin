# ============================================
# converters.py - HERCU Studio 数据转换工具
# ============================================

from typing import Dict, Any, List
from .enums import TeachingFormType, ComplexityLevel, AssessmentType
from .content_specs import TextContentSpec, AssessmentQuestion, AssessmentSpec, AITutorSpec, ConversationGoal
from .lesson import Lesson, LessonStep
from .statistics import PackageStatistics, FormDistribution, ComplexityDistribution, ResourcesNeeded


def convert_old_node_to_lesson(node: Dict[str, Any], lesson_id: str) -> Lesson:
    """将旧的 node 结构转换为新的 lesson 结构"""
    steps = []
    step_index = 1

    content = node.get("content", {})

    # L1 直觉层 -> text_content
    if content.get("L1_intuition"):
        l1 = content["L1_intuition"]
        steps.append(LessonStep(
            step_id=f"{lesson_id}_S{step_index:03d}",
            type=TeachingFormType.TEXT_CONTENT.value,
            title="直觉理解",
            content=TextContentSpec(
                body=l1.get("text", ""),
                key_points=[]
            )
        ))
        step_index += 1

    # L2 机制层 -> illustrated_content (如果有 key_points) 或 text_content
    if content.get("L2_mechanism"):
        l2 = content["L2_mechanism"]
        key_points = l2.get("key_points", [])
        if key_points:
            steps.append(LessonStep(
                step_id=f"{lesson_id}_S{step_index:03d}",
                type=TeachingFormType.ILLUSTRATED_CONTENT.value,
                title="原理机制",
                content=TextContentSpec(
                    body=l2.get("text", ""),
                    key_points=key_points
                )
            ))
        else:
            steps.append(LessonStep(
                step_id=f"{lesson_id}_S{step_index:03d}",
                type=TeachingFormType.TEXT_CONTENT.value,
                title="原理机制",
                content=TextContentSpec(
                    body=l2.get("text", ""),
                    key_points=[]
                )
            ))
        step_index += 1

    # L3 本质层 -> text_content
    if content.get("L3_essence"):
        l3 = content["L3_essence"]
        body = l3.get("core_insight", "")
        formulas = l3.get("formulas", [])
        if formulas:
            body += "\n\n核心公式：\n" + "\n".join(formulas)
        steps.append(LessonStep(
            step_id=f"{lesson_id}_S{step_index:03d}",
            type=TeachingFormType.TEXT_CONTENT.value,
            title="本质总结",
            content=TextContentSpec(
                body=body,
                key_points=[]
            )
        ))
        step_index += 1

    # AI Tutor -> ai_tutor step
    ai_tutor = node.get("ai_tutor", {})
    if ai_tutor and (ai_tutor.get("on_enter") or ai_tutor.get("hints")):
        steps.append(LessonStep(
            step_id=f"{lesson_id}_S{step_index:03d}",
            type=TeachingFormType.AI_TUTOR.value,
            title="AI 答疑",
            trigger="optional_user_request",
            ai_spec=AITutorSpec(
                opening_message=ai_tutor.get("on_enter", "有什么问题想问我吗？"),
                conversation_goals=[
                    ConversationGoal(goal="解答学习问题", examples=ai_tutor.get("hints", []))
                ],
                max_turns=5
            )
        ))
        step_index += 1

    # Quiz -> assessment step
    quiz = node.get("quiz", {})
    if quiz and quiz.get("questions"):
        questions = []
        for q in quiz["questions"]:
            questions.append(AssessmentQuestion(
                question=q.get("question", ""),
                options=q.get("options", []),
                correct=str(q.get("correct", 0)),
                explanation=q.get("explanation", "")
            ))
        steps.append(LessonStep(
            step_id=f"{lesson_id}_S{step_index:03d}",
            type=TeachingFormType.ASSESSMENT.value,
            title="知识检测",
            assessment_spec=AssessmentSpec(
                type=AssessmentType.QUICK_CHECK.value,
                questions=questions,
                pass_required=False
            )
        ))
        step_index += 1

    # 确定复杂度
    if len(steps) <= 2:
        complexity = ComplexityLevel.SIMPLE.value
    elif len(steps) <= 4:
        complexity = ComplexityLevel.STANDARD.value
    elif len(steps) <= 5:
        complexity = ComplexityLevel.RICH.value
    else:
        complexity = ComplexityLevel.COMPREHENSIVE.value

    return Lesson(
        lesson_id=lesson_id,
        title=node.get("title", ""),
        total_steps=len(steps),
        rationale="从旧结构转换",
        script=steps,
        estimated_minutes=node.get("estimated_minutes", 30),
        prerequisites=node.get("prerequisites", []),
        learning_objectives=node.get("learning_objectives", []),
        complexity_level=complexity
    )


def calculate_statistics(lessons: List[Lesson]) -> PackageStatistics:
    """计算课程包统计信息"""
    stats = PackageStatistics()
    stats.total_lessons = len(lessons)

    form_dist = FormDistribution()
    complexity_dist = ComplexityDistribution()
    resources = ResourcesNeeded()

    for lesson in lessons:
        stats.total_steps += lesson.total_steps

        # 复杂度分布
        if lesson.complexity_level == ComplexityLevel.SIMPLE.value:
            complexity_dist.simple += 1
        elif lesson.complexity_level == ComplexityLevel.STANDARD.value:
            complexity_dist.standard += 1
        elif lesson.complexity_level == ComplexityLevel.RICH.value:
            complexity_dist.rich += 1
        elif lesson.complexity_level == ComplexityLevel.COMPREHENSIVE.value:
            complexity_dist.comprehensive += 1

        # 教学形式分布和资源统计
        for step in lesson.script:
            if step.type == TeachingFormType.TEXT_CONTENT.value:
                form_dist.text_content += 1
            elif step.type == TeachingFormType.ILLUSTRATED_CONTENT.value:
                form_dist.illustrated_content += 1
                if step.diagram_spec:
                    resources.diagrams += 1
            elif step.type == TeachingFormType.VIDEO.value:
                form_dist.video += 1
                resources.videos += 1
                if step.video_spec and step.video_spec.duration:
                    # 解析时长 "3:00" -> 3 分钟
                    try:
                        parts = step.video_spec.duration.split(":")
                        minutes = int(parts[0])
                        resources.video_minutes += minutes
                    except:
                        pass
            elif step.type == TeachingFormType.SIMULATOR.value:
                form_dist.simulator += 1
                resources.simulators += 1
            elif step.type == TeachingFormType.AI_TUTOR.value:
                form_dist.ai_tutor += 1
            elif step.type in [TeachingFormType.ASSESSMENT.value, TeachingFormType.QUICK_CHECK.value]:
                form_dist.assessment += 1

    stats.form_distribution = form_dist
    stats.complexity_distribution = complexity_dist
    stats.resources_needed = resources

    return stats
