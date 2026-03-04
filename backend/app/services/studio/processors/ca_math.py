# ============================================
# processors/ca_math.py - 加州数学框架处理器
# ============================================
# 基于 California Mathematics Framework 2023
# Launch → Explore → Discuss → Synthesize → Practice
# 参考: https://www.cde.ca.gov/ci/ma/cf/
# 核心理念: Big Ideas, Investigation, Problem-Based Learning

from typing import Dict, List, Any, Optional

from .base import BaseProcessor, ProcessorInfo, ProcessorRegistry
from .intelligent import ContentAnalysis, TeachingFormType


@ProcessorRegistry.register
class CAMathProcessor(BaseProcessor):
    """
    加州数学框架 2023 处理器

    CA Math Framework 核心理念:
    - Big Ideas (大概念): 围绕核心数学思想组织教学
    - Investigation (探究): 问题驱动的数学探究
    - Multiple Representations (多元表征): 数形结合，多角度理解
    - Productive Struggle (有效挣扎): 允许学生在挑战中成长
    - Mathematical Discourse (数学对话): 通过讨论深化理解

    教学流程: Launch → Explore → Discuss → Synthesize → Practice
    适用: 代数、几何、微积分、统计、数论等所有数学分支
    """

    processor_info = ProcessorInfo(
        id="ca_math",
        name="CA Math Framework",
        description="加州数学框架2023：问题驱动→探究建模→协作讨论→归纳总结→分层练习",
        version="1.0.0",
        author="HERCU Studio",
        tags=["加州标准", "数学", "问题驱动", "探究", "建模"],
        color="#8B5CF6",
        icon="calculator",
    )

    PHASES = [
        {
            "phase": "launch",
            "label": "Launch 问题引入",
            "step_type": "illustrated_content",
            "purpose": "呈现真实情境中的数学问题，激发数学思考，建立问题意识",
            "prompt_guidance": "用一个真实生活情境或有趣的数学谜题开场(Three-Act Task风格)。第一幕：展示情境，引发好奇。提出核心问题但不给解法。配合图表或示意图帮助学生理解问题。",
        },
        {
            "phase": "explore",
            "label": "Explore 探究建模",
            "step_type": "simulator",
            "purpose": "交互式数学建模，学生操作参数观察数学关系，建立直觉",
            "prompt_guidance": "设计数学模拟器让学生操作变量，观察数学关系。支持多元表征：数值表格、函数图像、几何图形同步变化。学生应能通过操作发现数学规律，而不是被动接受公式。",
        },
        {
            "phase": "discuss",
            "label": "Discuss 数学对话",
            "step_type": "ai_tutor",
            "purpose": "AI引导数学对话，比较不同解法，发展数学推理和论证能力",
            "prompt_guidance": "AI导师引导数学讨论：(1)你在模拟器中发现了什么规律？(2)能用数学语言描述吗？(3)还有其他解法吗？(4)这个规律在什么条件下成立？重点培养Mathematical Reasoning。",
        },
        {
            "phase": "synthesize",
            "label": "Synthesize 归纳总结",
            "step_type": "text_content",
            "purpose": "提炼数学概念、公式和定理，建立知识框架，连接Big Ideas",
            "prompt_guidance": "从学生的探究和讨论中归纳出正式的数学概念。给出严谨的定义、公式和定理。用key_points总结核心要点。连接到更大的数学思想(Big Ideas)。展示概念间的联系。",
        },
        {
            "phase": "practice",
            "label": "Practice 分层练习",
            "step_type": "assessment",
            "purpose": "分层评估：基础计算→概念理解→问题解决，支持Productive Struggle",
            "prompt_guidance": "设计分层题目：(1)基础计算题(Fluency) (2)概念理解题(Understanding) (3)问题解决题(Application)。每道题都要有详细的解题过程。最后一道应是开放性问题，鼓励多种解法。",
        },
    ]

    def analyze_content(self, content: str, context: Dict[str, Any] = None) -> ContentAnalysis:
        context = context or {}
        content_lower = content.lower()

        has_geometry = any(kw in content_lower for kw in ["几何", "图形", "面积", "体积", "geometry"])
        has_algebra = any(kw in content_lower for kw in ["方程", "函数", "代数", "algebra", "equation"])
        has_stats = any(kw in content_lower for kw in ["统计", "概率", "数据", "statistics", "probability"])

        complexity = "standard"
        if has_geometry and has_algebra:
            complexity = "advanced"

        return ContentAnalysis(
            has_dynamic_process=True,
            has_structural_relationship=True,
            requires_hands_on_practice=True,
            has_parameter_feedback_loop=True,
            has_common_misconceptions=True,
            needs_personalized_guidance=True,
            is_gateway_to_next=True,
            complexity_level=complexity,
            recommended_forms=self.recommend_forms(None),
            rationale="CA Math Framework: 问题驱动→探究建模→数学对话→归纳总结→分层练习",
        )

    def recommend_forms(self, analysis: Any) -> List[str]:
        return [p["step_type"] for p in self.PHASES]

    def build_structure_prompt(
        self, source_material: str, course_title: str, context: Dict[str, Any] = None
    ) -> str:
        context = context or {}
        return f"""你是一位精通加州数学框架(2023)的数学课程设计师。

【课程标题】
{course_title}

【源素材】
{source_material}

【CA Math Framework 2023 核心理念】
1. Big Ideas (大概念): 每个课时围绕一个核心数学思想
2. Investigation (探究): 问题驱动，不是公式先行
3. Multiple Representations (多元表征): 数、形、表、图多角度
4. Productive Struggle (有效挣扎): 给学生思考空间
5. Mathematical Discourse (数学对话): 通过讨论深化理解

【教学流程】
每个课时遵循: Launch(问题引入) → Explore(探究建模) → Discuss(数学对话) → Synthesize(归纳总结) → Practice(分层练习)

【Standards for Mathematical Practice (SMP)】
课程应培养以下数学实践能力：
- SMP1: 理解问题并坚持解决
- SMP2: 抽象和定量推理
- SMP3: 构建论证和批判推理
- SMP4: 用数学建模
- SMP5: 策略性使用工具
- SMP6: 注重精确性
- SMP7: 寻找和利用结构
- SMP8: 寻找和表达规律

【输出格式】
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
      "big_idea": "本课时的核心数学大概念",
      "smp_focus": ["SMP4", "SMP7"],
      "recommended_forms": ["illustrated_content", "simulator", "ai_tutor", "text_content", "assessment"],
      "complexity_level": "simple/standard/advanced",
      "prerequisites": [],
      "estimated_minutes": 预计时长
    }}
  ]
}}
```
"""

    def build_lesson_prompt(
        self, source_material: str, course_title: str, lesson_info: Dict[str, Any],
        lesson_index: int, total_lessons: int, previous_summary: str = "",
        context: Dict[str, Any] = None,
    ) -> str:
        context = context or {}
        big_idea = lesson_info.get("big_idea", "")
        smp_focus = lesson_info.get("smp_focus", [])

        phase_instructions = "\n".join([
            f"**Step {i+1}: {p['label']}** (type: {p['step_type']})\n"
            f"  目的: {p['purpose']}\n"
            f"  要求: {p['prompt_guidance']}"
            for i, p in enumerate(self.PHASES)
        ])

        return f"""你是一位精通加州数学框架的数学教师。请为以下课时生成完整的教学内容。

【课程信息】
- 课程标题：{course_title}
- 当前课时：第 {lesson_index + 1} 课 / 共 {total_lessons} 课
- 课时标题：{lesson_info.get('title', '')}
- 学习目标：{', '.join(lesson_info.get('learning_objectives', []))}
- 大概念(Big Idea)：{big_idea}
- 数学实践重点：{', '.join(smp_focus) if smp_focus else '综合'}

【上一课时摘要】
{previous_summary if previous_summary else "（这是第一课）"}

【源素材】
{source_material}

【教学阶段详细要求】
{phase_instructions}

【输出格式】
```json
{{
  "title": "课时标题",
  "rationale": "CA Math Framework教学设计理念",
  "learning_objectives": ["目标1", "目标2"],
  "complexity_level": "standard",
  "estimated_minutes": 预计时长,
  "script": [
    {{
      "step_id": "S001",
      "type": "illustrated_content",
      "title": "Launch: [真实情境问题]",
      "content": {{"body": "情境描述...", "key_points": []}},
      "diagram_spec": {{
        "diagram_id": "DIAG-001",
        "type": "static_diagram",
        "description": "问题情境示意图"
      }}
    }},
    {{
      "step_id": "S002",
      "type": "simulator",
      "title": "Explore: [数学探究]",
      "simulator_spec": {{
        "name": "数学模拟器",
        "description": "描述(≥30字)",
        "mode": "html",
        "inputs": [],
        "outputs": [],
        "instructions": ["操作说明1", "操作说明2"],
        "html_content": ""
      }}
    }},
    {{
      "step_id": "S003",
      "type": "ai_tutor",
      "title": "Discuss: [数学对话]",
      "ai_spec": {{
        "opening_message": "你在探究中发现了什么规律？",
        "probing_questions": [],
        "diagnostic_focus": {{"key_concepts": [], "common_misconceptions": []}},
        "max_turns": 6
      }}
    }},
    {{
      "step_id": "S004",
      "type": "text_content",
      "title": "Synthesize: [概念归纳]",
      "content": {{
        "body": "归纳数学概念和公式...",
        "key_points": ["要点1", "要点2", "要点3"]
      }}
    }},
    {{
      "step_id": "S005",
      "type": "assessment",
      "title": "Practice: [分层练习]",
      "assessment_spec": {{
        "type": "quick_check",
        "questions": [],
        "pass_required": true
      }}
    }}
  ],
  "summary": "本课时摘要"
}}
```

【关键原则】
1. Launch必须用真实情境引入，不能直接给公式
2. Explore的模拟器要支持多元表征(数值+图形)
3. Discuss要引导学生用数学语言表达发现
4. Synthesize从探究结果归纳，不是凭空给出定理
5. Practice分三层：计算流畅→概念理解→问题解决
"""

    def get_style_prompt(self) -> str:
        return """使用加州数学框架2023风格：
- Launch: 真实情境问题驱动，Three-Act Task风格
- Explore: 交互式数学建模，多元表征
- Discuss: 数学对话，比较解法，发展推理
- Synthesize: 从探究归纳概念，连接Big Ideas
- Practice: 分层练习(Fluency→Understanding→Application)
- 贯穿Standards for Mathematical Practice"""

    def process_lesson(self, raw_lesson: Dict[str, Any], lesson_info: Dict[str, Any]) -> Dict[str, Any]:
        """后处理：确保数学教学阶段标签"""
        script = raw_lesson.get("script", [])
        phase_labels = ["Launch", "Explore", "Discuss", "Synthesize", "Practice"]
        for i, step in enumerate(script[:5]):
            if i < len(phase_labels) and not step.get("title", "").startswith(phase_labels[i]):
                step["title"] = f"{phase_labels[i]}: {step.get('title', '')}"
        return raw_lesson
