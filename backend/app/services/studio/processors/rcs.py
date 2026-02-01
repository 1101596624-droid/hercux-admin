# ============================================
# processors/rcs.py - RCS 三层讲解处理器
# ============================================
# 兼容旧版 L1/L2/L3 三层讲解结构

from typing import Dict, List, Any, Optional

from .base import BaseProcessor, ProcessorInfo, ProcessorRegistry
from .intelligent import (
    ContentAnalysis,
    TeachingFormType,
)


# 复杂度级别
class ComplexityLevel:
    SIMPLE = "simple"
    STANDARD = "standard"
    ADVANCED = "advanced"


@ProcessorRegistry.register
class RCSProcessor(BaseProcessor):
    """
    RCS 三层讲解处理器

    基于 Recognize-Comprehend-Synthesize 三层结构：
    - L1 直觉层 (Recognize): 建立直觉理解
    - L2 机制层 (Comprehend): 深入原理机制
    - L3 本质层 (Synthesize): 提炼核心本质

    此处理器保持与旧版课程包的兼容性
    """

    processor_info = ProcessorInfo(
        id="rcs",
        name="RCS 三层讲解",
        description="经典的直觉-机制-本质三层递进式讲解结构",
        version="1.0.0",
        author="HERCU Studio",
        tags=["经典", "三层", "递进"],
        color="#10b981",
        icon="layers"
    )

    # ==================== 抽象方法实现 ====================

    def analyze_content(self, content: str, context: Dict[str, Any] = None) -> ContentAnalysis:
        """
        RCS 模式下的内容分析

        RCS 模式固定使用三层文字结构，不做复杂的形式推荐
        """
        context = context or {}

        # RCS 模式固定使用文字内容 + 测验
        analysis = ContentAnalysis(
            has_dynamic_process=False,
            is_physical_action=False,
            has_structural_relationship=True,  # RCS 本身就是结构化的
            requires_hands_on_practice=False,
            has_parameter_feedback_loop=False,
            has_common_misconceptions=False,
            needs_personalized_guidance=False,
            is_gateway_to_next=False,
            complexity_level=ComplexityLevel.STANDARD,
            recommended_forms=[
                TeachingFormType.TEXT_CONTENT.value,
                TeachingFormType.TEXT_CONTENT.value,
                TeachingFormType.TEXT_CONTENT.value,
                TeachingFormType.AI_TUTOR.value,
                TeachingFormType.QUICK_CHECK.value,
            ],
            rationale="RCS 三层讲解模式：L1直觉 → L2机制 → L3本质 → AI答疑 → 检测"
        )

        return analysis

    def recommend_forms(self, analysis: ContentAnalysis) -> List[str]:
        """
        RCS 模式固定返回三层结构
        """
        return [
            TeachingFormType.TEXT_CONTENT.value,  # L1 直觉层
            TeachingFormType.TEXT_CONTENT.value,  # L2 机制层
            TeachingFormType.TEXT_CONTENT.value,  # L3 本质层
            TeachingFormType.AI_TUTOR.value,      # AI 答疑
            TeachingFormType.QUICK_CHECK.value,   # 快速检测
        ]

    def build_structure_prompt(
        self,
        source_material: str,
        course_title: str,
        context: Dict[str, Any] = None
    ) -> str:
        """构建课程结构生成的 prompt（RCS 风格）"""
        context = context or {}

        prompt = f"""你是一位专业的课程设计师，请使用 RCS 三层讲解法设计课程结构。

【课程标题】
{course_title}

【源素材】
{source_material}

【RCS 三层讲解法】
每个课时都遵循三层递进结构：
- L1 直觉层 (Recognize): 用类比、比喻建立直觉理解，让学员"感觉懂了"
- L2 机制层 (Comprehend): 深入原理机制，解释"为什么是这样"
- L3 本质层 (Synthesize): 提炼核心本质，形成可迁移的认知框架

【输出格式】
请输出 JSON 格式的课程结构：
```json
{{
  "title": "课程标题",
  "description": "课程描述",
  "estimated_hours": 预计学时,
  "lessons": [
    {{
      "title": "课时标题",
      "summary": "课时摘要",
      "learning_objectives": ["学习目标1", "学习目标2"],
      "l1_preview": "L1 直觉层预览（一句话）",
      "l2_preview": "L2 机制层预览（一句话）",
      "l3_preview": "L3 本质层预览（一句话）",
      "prerequisites": [前置课时索引列表],
      "estimated_minutes": 预计时长
    }}
  ]
}}
```

请确保：
1. 每个课时都能清晰地分为三层
2. 三层之间有明确的递进关系
3. 课时之间有合理的依赖关系
"""
        return prompt

    def build_lesson_prompt(
        self,
        source_material: str,
        course_title: str,
        lesson_info: Dict[str, Any],
        lesson_index: int,
        total_lessons: int,
        previous_summary: str = "",
        context: Dict[str, Any] = None
    ) -> str:
        """构建单个课时内容生成的 prompt（RCS 风格）"""
        context = context or {}

        prompt = f"""你是一位专业的课程内容设计师，请使用 RCS 三层讲解法为以下课时生成详细内容。

【课程信息】
- 课程标题：{course_title}
- 当前课时：第 {lesson_index + 1} 课 / 共 {total_lessons} 课
- 课时标题：{lesson_info.get('title', '')}
- 学习目标：{', '.join(lesson_info.get('learning_objectives', []))}

【上一课时摘要】
{previous_summary if previous_summary else "（这是第一课）"}

【源素材】
{source_material}

【RCS 三层讲解法要求】

**L1 直觉层 (Recognize)**
- 目的：建立直觉理解，让学员"感觉懂了"
- 方法：使用类比、比喻、生活化例子
- 长度：100-200 字
- 语气：亲切、易懂

**L2 机制层 (Comprehend)**
- 目的：深入原理机制，解释"为什么"
- 方法：逻辑推导、因果分析、关键要点
- 长度：200-400 字
- 语气：专业、清晰

**L3 本质层 (Synthesize)**
- 目的：提炼核心本质，形成认知框架
- 方法：抽象总结、公式化、可迁移原则
- 长度：100-200 字
- 语气：精炼、深刻

【输出格式】
请输出 JSON 格式的课时脚本：
```json
{{
  "title": "课时标题",
  "rationale": "RCS 三层讲解：从直觉到机制再到本质的递进式学习",
  "learning_objectives": ["目标1", "目标2"],
  "complexity_level": "standard",
  "estimated_minutes": 预计时长,
  "script": [
    {{
      "step_id": "S001",
      "type": "text_content",
      "title": "L1 直觉理解",
      "content": {{
        "body": "L1 层内容...",
        "key_points": []
      }}
    }},
    {{
      "step_id": "S002",
      "type": "text_content",
      "title": "L2 原理机制",
      "content": {{
        "body": "L2 层内容...",
        "key_points": ["要点1", "要点2", "要点3"]
      }}
    }},
    {{
      "step_id": "S003",
      "type": "text_content",
      "title": "L3 本质总结",
      "content": {{
        "body": "L3 层内容...",
        "key_points": []
      }}
    }},
    {{
      "step_id": "S004",
      "type": "ai_tutor",
      "title": "AI 答疑",
      "trigger": "optional_user_request",
      "ai_spec": {{
        "opening_message": "学完这一课了！有什么问题想问我吗？",
        "conversation_goals": [
          {{"goal": "解答学习问题", "examples": ["相关问题示例"]}}
        ],
        "max_turns": 5
      }}
    }},
    {{
      "step_id": "S005",
      "type": "assessment",
      "title": "知识检测",
      "assessment_spec": {{
        "type": "quick_check",
        "questions": [
          {{
            "question": "检测问题",
            "options": ["A. 选项1", "B. 选项2", "C. 选项3"],
            "correct": "A",
            "explanation": "解释"
          }}
        ],
        "pass_required": false
      }}
    }}
  ]
}}
```

【重要提示】
1. 严格遵循 L1 → L2 → L3 的递进结构
2. 每一层都要有明确的教学目的
3. L2 层必须包含 key_points
4. 测验问题要覆盖三层的核心内容
"""
        return prompt

    def get_style_prompt(self) -> str:
        """获取风格描述"""
        return """使用 RCS 三层讲解风格：
- L1 直觉层：用类比和比喻建立直觉理解
- L2 机制层：深入原理，解释因果关系
- L3 本质层：提炼核心，形成认知框架
- 三层递进，由浅入深"""

    def process_lesson(self, raw_lesson: Dict[str, Any], lesson_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        后处理课时内容

        确保 RCS 结构的完整性
        """
        # 检查是否有完整的三层结构
        script = raw_lesson.get("script", [])

        # 标记三层
        layer_titles = {
            0: "L1 直觉理解",
            1: "L2 原理机制",
            2: "L3 本质总结",
        }

        for i, step in enumerate(script[:3]):
            if step.get("type") == "text_content" and i in layer_titles:
                # 确保标题包含层级标识
                if not step.get("title", "").startswith("L"):
                    step["title"] = layer_titles[i]

        return raw_lesson


# RCS 风格的 Prompt 模板
RCS_LESSON_TEMPLATE = """
【L1 直觉层】
{l1_content}

【L2 机制层】
{l2_content}

关键要点：
{key_points}

【L3 本质层】
{l3_content}
"""
