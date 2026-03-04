# ============================================
# processors/ca_science_5e.py - 加州理科 NGSS 5E 教学模型处理器
# ============================================
# 基于 Next Generation Science Standards (NGSS) 的 5E 教学模型
# Engage → Explore → Explain → Elaborate → Evaluate
# 参考: https://www.cde.ca.gov/pd/ca/sc/ngssstandards.asp
#       https://www.sdcoe.net/ngss/evidence-based-practices/5e-model-of-instruction

from typing import Dict, List, Any, Optional

from .base import BaseProcessor, ProcessorInfo, ProcessorRegistry
from .intelligent import ContentAnalysis, TeachingFormType


@ProcessorRegistry.register
class CAScience5EProcessor(BaseProcessor):
    """
    加州理科 NGSS 5E 教学模型处理器

    5E Instructional Model (Bybee, 2006):
    - Engage (激发): 用现象/问题激发好奇心，暴露先验概念
    - Explore (探究): 动手实验/模拟，收集数据，发现规律
    - Explain (讲解): 基于探究引入正式科学概念和原理
    - Elaborate (拓展): 将概念迁移到新情境，深化理解
    - Evaluate (评估): 形成性评估，检测概念掌握和科学实践能力

    适用学科: 物理、化学、生物、地球科学、工程技术
    适用年级: K-12 (内容深度由AI根据素材自动调节)
    """

    processor_info = ProcessorInfo(
        id="ca_science_5e",
        name="CA Science 5E",
        description="加州NGSS 5E教学模型：Engage→Explore→Explain→Elaborate→Evaluate",
        version="1.0.0",
        author="HERCU Studio",
        tags=["加州标准", "NGSS", "5E", "理科", "探究式"],
        color="#0EA5E9",
        icon="flask",
    )

    # 5E 阶段定义
    PHASES = [
        {
            "phase": "engage",
            "label": "Engage 激发兴趣",
            "step_type": "text_content",
            "purpose": "用引人入胜的自然现象、矛盾事实或驱动性问题激发好奇心，激活学生已有的科学概念",
            "prompt_guidance": "以一个令人惊讶的科学现象或日常生活中的矛盾开场。提出驱动性问题(Driving Question)。不要直接给出答案，让学生产生'为什么会这样？'的疑问。",
        },
        {
            "phase": "explore",
            "label": "Explore 动手探究",
            "step_type": "simulator",
            "purpose": "通过交互式模拟器让学生自主操作变量、收集数据、观察规律，体验科学探究过程",
            "prompt_guidance": "设计一个可操作的科学模拟器。学生应能调节至少2个变量，观察因变量的变化。模拟器要能让学生自己发现规律，而不是被动展示结论。",
        },
        {
            "phase": "explain",
            "label": "Explain 概念讲解",
            "step_type": "text_content",
            "purpose": "基于学生在Explore阶段的发现，正式引入科学概念、原理和术语，建立概念框架",
            "prompt_guidance": "从学生在探究中可能发现的规律出发，引入正式的科学概念。使用'你在模拟器中观察到...'这样的衔接。包含关键术语定义、核心公式和原理解释。配合key_points总结要点。",
        },
        {
            "phase": "elaborate",
            "label": "Elaborate 拓展应用",
            "step_type": "ai_tutor",
            "purpose": "AI苏格拉底式追问，引导学生将概念迁移到新情境，纠正常见误区，深化理解",
            "prompt_guidance": "AI导师以苏格拉底式提问引导学生将刚学的概念应用到新的情境中。设计3-4个递进式问题：基础应用→变式应用→跨学科迁移。重点诊断常见misconceptions。",
        },
        {
            "phase": "evaluate",
            "label": "Evaluate 评估检测",
            "step_type": "assessment",
            "purpose": "形成性评估，检测学生对科学概念的理解深度和科学实践能力",
            "prompt_guidance": "设计3-5道题目，覆盖三个层次：(1)概念回忆 (2)概念应用 (3)分析推理。至少1道题要求学生解释'为什么'而不仅是'是什么'。每道题都要有详细的解释。",
        },
    ]

    def analyze_content(self, content: str, context: Dict[str, Any] = None) -> ContentAnalysis:
        """5E模式下的内容分析"""
        context = context or {}
        content_lower = content.lower()

        # 5E模式固定使用五阶段结构，但根据内容调整复杂度
        has_math = any(kw in content_lower for kw in ["公式", "计算", "方程", "formula", "equation"])
        has_experiment = any(kw in content_lower for kw in ["实验", "观察", "测量", "experiment"])

        complexity = "standard"
        if has_math and has_experiment:
            complexity = "advanced"
        elif has_math or has_experiment:
            complexity = "standard"
        else:
            complexity = "simple"

        return ContentAnalysis(
            has_dynamic_process=True,
            is_physical_action=False,
            has_structural_relationship=True,
            requires_hands_on_practice=True,
            has_parameter_feedback_loop=True,
            has_common_misconceptions=True,
            needs_personalized_guidance=True,
            is_gateway_to_next=True,
            complexity_level=complexity,
            recommended_forms=self.recommend_forms(None),
            rationale="NGSS 5E教学模型：激发→探究→讲解→拓展→评估，强调科学实践和概念建构",
        )

    def recommend_forms(self, analysis: Any) -> List[str]:
        """5E固定返回五阶段步骤类型"""
        return [p["step_type"] for p in self.PHASES]

    def build_structure_prompt(
        self, source_material: str, course_title: str, context: Dict[str, Any] = None
    ) -> str:
        context = context or {}
        return f"""你是一位精通加州NGSS标准的科学课程设计师。请使用5E教学模型设计课程结构。

【课程标题】
{course_title}

【源素材】
{source_material}

【5E教学模型 (Next Generation Science Standards)】
每个课时严格遵循5个阶段：
1. Engage (激发): 用现象或问题激发好奇心
2. Explore (探究): 动手实验/模拟，自主发现
3. Explain (讲解): 引入正式科学概念
4. Elaborate (拓展): 概念迁移到新情境
5. Evaluate (评估): 形成性评估

【NGSS三维整合】
每个课时都应整合三个维度：
- Disciplinary Core Ideas (学科核心概念)
- Science and Engineering Practices (科学与工程实践)
- Crosscutting Concepts (跨学科概念: 因果关系、系统模型、尺度比例等)

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
      "driving_question": "本课时的驱动性问题",
      "core_idea": "对应的学科核心概念",
      "science_practice": "涉及的科学实践",
      "crosscutting_concept": "涉及的跨学科概念",
      "recommended_forms": ["text_content", "simulator", "text_content", "ai_tutor", "assessment"],
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
        driving_q = lesson_info.get("driving_question", "")
        core_idea = lesson_info.get("core_idea", "")

        phase_instructions = "\n".join([
            f"**Step {i+1}: {p['label']}** (type: {p['step_type']})\n"
            f"  目的: {p['purpose']}\n"
            f"  要求: {p['prompt_guidance']}"
            for i, p in enumerate(self.PHASES)
        ])

        return f"""你是一位精通NGSS 5E教学模型的科学教师。请为以下课时生成完整的5E教学内容。

【课程信息】
- 课程标题：{course_title}
- 当前课时：第 {lesson_index + 1} 课 / 共 {total_lessons} 课
- 课时标题：{lesson_info.get('title', '')}
- 学习目标：{', '.join(lesson_info.get('learning_objectives', []))}
- 驱动性问题：{driving_q}
- 学科核心概念：{core_idea}

【上一课时摘要】
{previous_summary if previous_summary else "（这是第一课）"}

【源素材】
{source_material}

【5E教学阶段详细要求】
{phase_instructions}

【输出格式】
```json
{{
  "title": "课时标题",
  "rationale": "5E教学设计理念说明",
  "learning_objectives": ["目标1", "目标2"],
  "complexity_level": "standard",
  "estimated_minutes": 预计时长,
  "script": [
    {{
      "step_id": "S001",
      "type": "text_content",
      "title": "Engage: [具体标题]",
      "content": {{
        "body": "以引人入胜的现象开场...",
        "key_points": []
      }}
    }},
    {{
      "step_id": "S002",
      "type": "simulator",
      "title": "Explore: [具体标题]",
      "simulator_spec": {{
        "name": "模拟器名称",
        "description": "模拟器描述(≥30字)",
        "mode": "html",
        "inputs": [],
        "outputs": [],
        "instructions": ["操作说明1", "操作说明2", "操作说明3"],
        "html_content": ""
      }}
    }},
    {{
      "step_id": "S003",
      "type": "text_content",
      "title": "Explain: [具体标题]",
      "content": {{
        "body": "基于探究结果引入概念...",
        "key_points": ["要点1", "要点2", "要点3"]
      }}
    }},
    {{
      "step_id": "S004",
      "type": "ai_tutor",
      "title": "Elaborate: [具体标题]",
      "ai_spec": {{
        "opening_message": "你在模拟器中发现了...现在让我们把这个概念应用到新的情境中。",
        "probing_questions": [
          {{
            "question": "苏格拉底式问题",
            "intent": "检测概念迁移能力",
            "expected_elements": ["关键词"],
            "follow_ups": {{
              "if_correct": "追问",
              "if_superficial": "引导",
              "if_misconception": "纠正"
            }}
          }}
        ],
        "diagnostic_focus": {{
          "key_concepts": ["核心概念"],
          "common_misconceptions": ["常见误区"]
        }},
        "max_turns": 6
      }}
    }},
    {{
      "step_id": "S005",
      "type": "assessment",
      "title": "Evaluate: [具体标题]",
      "assessment_spec": {{
        "type": "quick_check",
        "questions": [
          {{
            "question": "问题",
            "options": ["A. 选项", "B. 选项", "C. 选项", "D. 选项"],
            "correct": "A",
            "explanation": "详细解释"
          }}
        ],
        "pass_required": true
      }}
    }}
  ],
  "summary": "本课时摘要"
}}
```

【关键原则】
1. Engage必须以现象或问题开场，不能直接讲概念
2. Explore的模拟器必须让学生能自主发现规律
3. Explain要从探究结果自然过渡到正式概念
4. Elaborate的AI追问要引导概念迁移，不是简单复述
5. Evaluate要覆盖记忆、理解、应用三个层次
"""

    def get_style_prompt(self) -> str:
        return """使用加州NGSS 5E教学模型风格：
- Engage: 以现象驱动好奇心，不直接给答案
- Explore: 让学生通过模拟器自主发现规律
- Explain: 从探究结果自然引入科学概念
- Elaborate: AI苏格拉底式追问，引导概念迁移
- Evaluate: 三层次评估(记忆→理解→应用)
- 整合NGSS三维: 核心概念 + 科学实践 + 跨学科概念"""

    def process_lesson(self, raw_lesson: Dict[str, Any], lesson_info: Dict[str, Any]) -> Dict[str, Any]:
        """后处理：确保5E阶段标签完整"""
        script = raw_lesson.get("script", [])
        phase_labels = ["Engage", "Explore", "Explain", "Elaborate", "Evaluate"]
        for i, step in enumerate(script[:5]):
            if i < len(phase_labels) and not step.get("title", "").startswith(phase_labels[i]):
                step["title"] = f"{phase_labels[i]}: {step.get('title', '')}"
        return raw_lesson
