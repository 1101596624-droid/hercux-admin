# ============================================
# processors/ca_social.py - 加州社会科学 HSS 框架处理器
# ============================================
# 基于 California History-Social Science Framework
# Inquire → Investigate → Analyze → Communicate → Assess
# 参考: https://www.cde.ca.gov/ci/hs/cf/
# 核心理念: Inquiry-Based Learning, Historical Thinking,
#           Civic Engagement, Multiple Perspectives

from typing import Dict, List, Any, Optional

from .base import BaseProcessor, ProcessorInfo, ProcessorRegistry
from .intelligent import ContentAnalysis, TeachingFormType


@ProcessorRegistry.register
class CASocialProcessor(BaseProcessor):
    """
    加州社会科学 HSS 框架处理器

    California HSS Framework 核心理念:
    - Inquiry-Based Learning (探究式学习): 以问题驱动历史探究
    - Historical Thinking (历史思维): 史料分析、因果推理、时空观念
    - Civic Engagement (公民参与): 培养知情公民的责任感
    - Multiple Perspectives (多元视角): 从不同立场理解历史事件
    - Evidence-Based Argumentation (循证论证): 基于证据的历史论证

    教学流程: Inquire → Investigate → Analyze → Communicate → Assess
    适用: 历史、地理、政治、经济、公民教育、社会学
    """

    processor_info = ProcessorInfo(
        id="ca_social",
        name="CA Social Studies HSS",
        description="加州HSS框架：提出问题→史料探究→批判分析→论证表达→综合评估",
        version="1.0.0",
        author="HERCU Studio",
        tags=["加州标准", "HSS", "历史", "社会科学", "探究", "公民"],
        color="#EF4444",
        icon="landmark",
    )

    PHASES = [
        {
            "phase": "inquire",
            "label": "Inquire 提出问题",
            "step_type": "text_content",
            "purpose": "提出驱动性问题(Compelling Question)和支撑性问题(Supporting Questions)，建立探究框架",
            "prompt_guidance": "以一个引人深思的历史/社会问题开场(Compelling Question)。这个问题应该没有简单的对错答案，需要深入探究。提供2-3个支撑性问题(Supporting Questions)帮助分解探究方向。简要介绍历史背景和时代语境。",
        },
        {
            "phase": "investigate",
            "label": "Investigate 史料探究",
            "step_type": "simulator",
            "purpose": "交互式史料分析、地图探索、时间线浏览或数据可视化，让学生接触一手/二手史料",
            "prompt_guidance": "设计交互式探究工具：(1)时间线(timeline)展示事件发展脉络 (2)地图探索展示空间分布 (3)史料对比分析不同来源的记载 (4)数据可视化展示社会经济变化。学生应能通过交互发现历史规律和因果关系。",
        },
        {
            "phase": "analyze",
            "label": "Analyze 批判分析",
            "step_type": "ai_tutor",
            "purpose": "AI引导多视角分析，培养Historical Thinking Skills和批判性思维",
            "prompt_guidance": "AI导师引导批判性分析：(1)这个事件的原因和结果是什么？(Causation) (2)不同群体如何看待这个事件？(Perspective) (3)这个史料可靠吗？作者的立场是什么？(Sourcing) (4)这个事件和今天有什么联系？(Continuity & Change) 培养Historical Thinking Skills。",
        },
        {
            "phase": "communicate",
            "label": "Communicate 论证表达",
            "step_type": "text_content",
            "purpose": "基于证据的论证写作(Evidence-Based Argumentation)，形成有理有据的历史观点",
            "prompt_guidance": "设计论证写作任务：(1)明确论点(Claim) (2)提供证据(Evidence)——至少引用2-3条史料 (3)推理论证(Reasoning)——解释证据如何支持论点 (4)回应反驳(Counterclaim)。提供CER(Claim-Evidence-Reasoning)写作框架。",
        },
        {
            "phase": "assess",
            "label": "Assess 综合评估",
            "step_type": "assessment",
            "purpose": "评估历史思维能力、史料分析能力和论证质量",
            "prompt_guidance": "设计多层次评估：(1)事实性问题(Who/What/When/Where) (2)分析性问题(Why/How/So What) (3)评价性问题(要求学生表达观点并引用证据)。至少1道题要求多视角分析。每道题都要有详细解释。",
        },
    ]

    def analyze_content(self, content: str, context: Dict[str, Any] = None) -> ContentAnalysis:
        context = context or {}
        content_lower = content.lower()

        has_history = any(kw in content_lower for kw in ["历史", "朝代", "战争", "革命", "history", "war"])
        has_geography = any(kw in content_lower for kw in ["地理", "地图", "气候", "地形", "geography"])
        has_civics = any(kw in content_lower for kw in ["政治", "民主", "法律", "公民", "government", "civics"])

        complexity = "standard"
        if sum([has_history, has_geography, has_civics]) >= 2:
            complexity = "advanced"

        return ContentAnalysis(
            has_dynamic_process=has_history,
            has_structural_relationship=True,
            requires_hands_on_practice=False,
            has_common_misconceptions=True,
            needs_personalized_guidance=True,
            is_gateway_to_next=True,
            complexity_level=complexity,
            recommended_forms=self.recommend_forms(None),
            rationale="CA HSS Framework: 提出问题→史料探究→批判分析→论证表达→综合评估",
        )

    def recommend_forms(self, analysis: Any) -> List[str]:
        return [p["step_type"] for p in self.PHASES]

    def build_structure_prompt(
        self, source_material: str, course_title: str, context: Dict[str, Any] = None
    ) -> str:
        context = context or {}
        return f"""你是一位精通加州HSS框架的社会科学课程设计师。

【课程标题】
{course_title}

【源素材】
{source_material}

【CA History-Social Science Framework 核心理念】
1. Inquiry-Based Learning: 以Compelling Question驱动探究
2. Historical Thinking Skills: 因果推理、时空观念、史料分析
3. Civic Engagement: 培养知情、负责的公民
4. Multiple Perspectives: 从不同立场理解事件
5. Evidence-Based Argumentation: 基于证据的论证

【教学流程】
每个课时遵循: Inquire(提问) → Investigate(探究) → Analyze(分析) → Communicate(论证) → Assess(评估)

【C3 Framework (College, Career, and Civic Life)】
- Dimension 1: Developing Questions and Planning Inquiries
- Dimension 2: Applying Disciplinary Concepts and Tools
- Dimension 3: Evaluating Sources and Using Evidence
- Dimension 4: Communicating Conclusions and Taking Informed Action

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
      "compelling_question": "驱动性问题",
      "historical_thinking_focus": "重点培养的历史思维技能",
      "recommended_forms": ["text_content", "simulator", "ai_tutor", "text_content", "assessment"],
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
        compelling_q = lesson_info.get("compelling_question", "")
        ht_focus = lesson_info.get("historical_thinking_focus", "")

        phase_instructions = "\n".join([
            f"**Step {i+1}: {p['label']}** (type: {p['step_type']})\n"
            f"  目的: {p['purpose']}\n"
            f"  要求: {p['prompt_guidance']}"
            for i, p in enumerate(self.PHASES)
        ])

        return f"""你是一位精通加州HSS框架的社会科学教师。请为以下课时生成完整的教学内容。

【课程信息】
- 课程标题：{course_title}
- 当前课时：第 {lesson_index + 1} 课 / 共 {total_lessons} 课
- 课时标题：{lesson_info.get('title', '')}
- 学习目标：{', '.join(lesson_info.get('learning_objectives', []))}
- 驱动性问题：{compelling_q}
- 历史思维重点：{ht_focus}

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
  "rationale": "CA HSS Framework教学设计理念",
  "learning_objectives": ["目标1", "目标2"],
  "complexity_level": "standard",
  "estimated_minutes": 预计时长,
  "script": [
    {{
      "step_id": "S001",
      "type": "text_content",
      "title": "Inquire: [驱动性问题]",
      "content": {{
        "body": "提出问题，建立探究框架...",
        "key_points": ["支撑性问题1", "支撑性问题2"]
      }}
    }},
    {{
      "step_id": "S002",
      "type": "simulator",
      "title": "Investigate: [史料探究]",
      "simulator_spec": {{
        "name": "探究工具名称",
        "description": "描述(≥30字)",
        "mode": "html",
        "inputs": [],
        "outputs": [],
        "instructions": ["探究说明1", "探究说明2"],
        "html_content": ""
      }}
    }},
    {{
      "step_id": "S003",
      "type": "ai_tutor",
      "title": "Analyze: [批判分析]",
      "ai_spec": {{
        "opening_message": "让我们从多个角度分析这个历史事件...",
        "probing_questions": [],
        "diagnostic_focus": {{"key_concepts": [], "common_misconceptions": []}},
        "max_turns": 6
      }}
    }},
    {{
      "step_id": "S004",
      "type": "text_content",
      "title": "Communicate: [论证表达]",
      "content": {{
        "body": "CER论证写作任务...",
        "key_points": ["Claim要求", "Evidence要求", "Reasoning要求"]
      }}
    }},
    {{
      "step_id": "S005",
      "type": "assessment",
      "title": "Assess: [综合评估]",
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
1. Inquire的Compelling Question必须是开放性的，没有简单对错
2. Investigate要让学生接触真实史料或数据
3. Analyze要引导多视角分析，不是灌输单一观点
4. Communicate要求CER论证框架，引用证据
5. Assess要覆盖事实→分析→评价三个层次
"""

    def get_style_prompt(self) -> str:
        return """使用加州HSS框架风格：
- Inquire: Compelling Question驱动探究
- Investigate: 接触一手/二手史料，交互式探索
- Analyze: 多视角批判分析，Historical Thinking
- Communicate: CER论证写作，基于证据
- Assess: 事实→分析→评价三层评估
- 贯穿Civic Engagement和Multiple Perspectives"""

    def process_lesson(self, raw_lesson: Dict[str, Any], lesson_info: Dict[str, Any]) -> Dict[str, Any]:
        script = raw_lesson.get("script", [])
        phase_labels = ["Inquire", "Investigate", "Analyze", "Communicate", "Assess"]
        for i, step in enumerate(script[:5]):
            if i < len(phase_labels) and not step.get("title", "").startswith(phase_labels[i]):
                step["title"] = f"{phase_labels[i]}: {step.get('title', '')}"
        return raw_lesson
