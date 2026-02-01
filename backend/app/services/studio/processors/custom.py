# ============================================
# processors/custom.py - 自定义处理器
# ============================================
# 支持从数据库加载的自定义处理器

from typing import Dict, List, Any, Optional

from .base import BaseProcessor, ProcessorInfo, ProcessorRegistry
from models import (
    ContentAnalysis,
    TeachingFormType,
    ComplexityLevel,
)


class CustomProcessor(BaseProcessor):
    """
    自定义处理器

    基于数据库存储的 system_prompt 动态创建的处理器
    """

    def __init__(
        self,
        processor_id: str,
        name: str,
        description: str,
        system_prompt: str,
        color: str = "#6366f1",
        icon: str = "Sparkles"
    ):
        """
        初始化自定义处理器

        Args:
            processor_id: 处理器 ID
            name: 处理器名称
            description: 处理器描述
            system_prompt: 系统提示词
            color: UI 颜色
            icon: UI 图标
        """
        super().__init__()
        self.system_prompt = system_prompt
        self.processor_info = ProcessorInfo(
            id=processor_id,
            name=name,
            description=description,
            version="1.0.0",
            author="Custom",
            tags=["自定义"],
            color=color,
            icon=icon
        )

    def analyze_content(self, content: str, context: Dict[str, Any] = None) -> ContentAnalysis:
        """
        分析内容特性

        使用默认分析逻辑，实际分析由 LLM 完成
        """
        context = context or {}

        analysis = ContentAnalysis(
            has_dynamic_process=False,
            is_physical_action=False,
            has_structural_relationship=False,
            requires_hands_on_practice=False,
            has_parameter_feedback_loop=False,
            has_common_misconceptions=False,
            needs_personalized_guidance=False,
            is_gateway_to_next=False,
            complexity_level=ComplexityLevel.STANDARD,
        )

        # 简单的关键词检测
        content_lower = content.lower()

        dynamic_keywords = ["动作", "步骤", "流程", "过程", "演示", "操作"]
        if any(kw in content_lower for kw in dynamic_keywords):
            analysis.has_dynamic_process = True

        action_keywords = ["深蹲", "卧推", "硬拉", "引体", "姿势", "动作要领"]
        if any(kw in content_lower for kw in action_keywords):
            analysis.is_physical_action = True

        structure_keywords = ["原理", "机制", "关系", "层级", "分类", "因果"]
        if any(kw in content_lower for kw in structure_keywords):
            analysis.has_structural_relationship = True

        practice_keywords = ["练习", "实践", "应用", "设计", "规划", "制定"]
        if any(kw in content_lower for kw in practice_keywords):
            analysis.requires_hands_on_practice = True

        analysis.recommended_forms = self.recommend_forms(analysis)

        return analysis

    def recommend_forms(self, analysis: ContentAnalysis) -> List[str]:
        """根据内容分析结果推荐教学形式"""
        forms = []

        # 基础内容载体
        if analysis.has_dynamic_process:
            if analysis.is_physical_action:
                forms.append(TeachingFormType.VIDEO.value)
            else:
                forms.append(TeachingFormType.ILLUSTRATED_CONTENT.value)
        elif analysis.has_structural_relationship:
            forms.append(TeachingFormType.ILLUSTRATED_CONTENT.value)
        else:
            forms.append(TeachingFormType.TEXT_CONTENT.value)

        # 实践环节
        if analysis.requires_hands_on_practice:
            if analysis.has_parameter_feedback_loop:
                forms.append(TeachingFormType.SIMULATOR.value)
            else:
                forms.append(TeachingFormType.PRACTICE.value)

        # AI 介入
        if analysis.has_common_misconceptions or analysis.needs_personalized_guidance:
            forms.append(TeachingFormType.AI_TUTOR.value)

        # 检测环节
        if analysis.is_gateway_to_next:
            forms.append(TeachingFormType.ASSESSMENT.value)
        else:
            forms.append(TeachingFormType.QUICK_CHECK.value)

        return forms

    def build_structure_prompt(
        self,
        source_material: str,
        course_title: str,
        context: Dict[str, Any] = None
    ) -> str:
        """构建课程结构生成的 prompt"""
        context = context or {}

        prompt = f"""{self.system_prompt}

【课程标题】
{course_title}

【源素材】
{source_material}

【设计原则】
1. 内容决定形式：不是每个课时都要有视频/模拟器
2. 最小充分原则：用最少的形式达到最好的效果
3. 智能规划：根据内容特性推荐最优组合

【教学形式选择指南】
- 概念定义 → text_content（文字足够）
- 原理机制 → illustrated_content（需要可视化）
- 动作技术 → video（必须看到动态过程）
- 决策应用 → simulator（需要动手实践）
- 深度理解考察 → ai_tutor（主动追问，诊断误区）
- 知识检验 → assessment 或 quick_check

【课时复杂度等级】
- simple: 1-2 steps（概念定义、术语）
- standard: 3-4 steps（原理机制）
- rich: 4-5 steps（动作技术）
- comprehensive: 5-6 steps（案例分析、综合应用）

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
      "content_analysis": {{
        "has_dynamic_process": true/false,
        "is_physical_action": true/false,
        "has_structural_relationship": true/false,
        "requires_hands_on_practice": true/false,
        "has_parameter_feedback_loop": true/false,
        "has_common_misconceptions": true/false,
        "needs_personalized_guidance": true/false,
        "is_gateway_to_next": true/false
      }},
      "recommended_forms": ["form1", "form2"],
      "complexity_level": "simple/standard/rich/comprehensive",
      "rationale": "为什么选择这些教学形式",
      "prerequisites": [前置课时索引列表],
      "estimated_minutes": 预计时长
    }}
  ]
}}
```

请确保：
1. 每个课时的教学形式选择都有明确的理由
2. 课时之间有合理的依赖关系
3. 复杂度分布合理
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
        """构建单个课时内容生成的 prompt"""
        context = context or {}

        recommended_forms = lesson_info.get("recommended_forms", ["text_content", "quick_check"])
        complexity = lesson_info.get("complexity_level", "standard")
        rationale = lesson_info.get("rationale", "")

        form_instructions = self._build_form_instructions(recommended_forms)

        prompt = f"""{self.system_prompt}

【课程信息】
- 课程标题：{course_title}
- 当前课时：第 {lesson_index + 1} 课 / 共 {total_lessons} 课
- 课时标题：{lesson_info.get('title', '')}
- 学习目标：{', '.join(lesson_info.get('learning_objectives', []))}

【设计决策】
- 推荐教学形式：{', '.join(recommended_forms)}
- 复杂度等级：{complexity}
- 选择理由：{rationale}

【上一课时摘要】
{previous_summary if previous_summary else "（这是第一课）"}

【源素材】
{source_material}

【教学形式规格说明】
{form_instructions}

【输出格式】
请输出 JSON 格式的课时脚本：
```json
{{
  "title": "课时标题",
  "rationale": "为什么选择这些教学形式",
  "learning_objectives": ["目标1", "目标2"],
  "complexity_level": "{complexity}",
  "estimated_minutes": 预计时长,
  "script": [
    // 根据推荐的教学形式生成对应的 step
  ]
}}
```

【重要提示】
1. 严格按照推荐的教学形式生成 steps
2. 每个 step 必须包含完整的规格信息
3. 内容要与学习目标紧密对应
4. 保持与上一课时的连贯性
"""
        return prompt

    def _build_form_instructions(self, forms: List[str]) -> str:
        """构建教学形式的详细说明"""
        instructions = []

        form_specs = {
            "text_content": """
【text_content 规格】
```json
{
  "step_id": "S00X",
  "type": "text_content",
  "title": "步骤标题",
  "content": {
    "body": "正文内容（支持 Markdown）",
    "key_points": ["要点1", "要点2"]
  }
}
```""",
            "illustrated_content": """
【illustrated_content 规格】
```json
{
  "step_id": "S00X",
  "type": "illustrated_content",
  "title": "步骤标题",
  "content": {
    "text": "说明文字"
  },
  "diagram_spec": {
    "diagram_id": "DIAG-XXX",
    "type": "static_diagram/flowchart/line_chart/pyramid/comparison",
    "description": "图表描述",
    "annotations": [{"position": "top/bottom/left/right", "text": "标注"}],
    "design_notes": "设计说明"
  }
}
```""",
            "video": """
【video 规格】
```json
{
  "step_id": "S00X",
  "type": "video",
  "title": "步骤标题",
  "video_spec": {
    "video_id": "VID-XXX",
    "duration": "3:00",
    "script": {
      "scenes": [
        {"timecode": "00:00-00:30", "scene": "场景描述", "narration": "旁白"}
      ]
    },
    "production_notes": "制作说明"
  },
  "embedded_interactions": [
    {"timestamp": "01:30", "type": "pause_and_ask", "question": "问题", "options": ["A", "B"], "correct": "A"}
  ]
}
```""",
            "simulator": """
【simulator 规格 - 必须从预设模板中选择】
重要：模拟器必须从以下预设模板中选择，不允许自定义生成！

【可用模板列表】

=== 田径类 ===
- sports_sprint_start: 短跑起跑技术 - 展示蹲踞式起跑的预备、起跑、加速阶段
- sports_jump_approach: J形助跑跳高 - 展示跳高的J形助跑路线
- sports_long_jump: 跳远技术分析 - 展示助跑、起跳、腾空、落地四阶段
- sports_shot_put: 铅球投掷技术 - 展示握球、滑步、转体、推球技术
- sports_hurdles: 跨栏技术分析 - 展示起跑、跨栏、着地、冲刺技术
- sports_relay_race: 接力赛跑技术 - 展示交接棒技术和配合
- sports_discus_throw: 铁饼投掷技术 - 展示握饼、旋转、出手技术
- sports_pole_vault: 撑杆跳高技术 - 展示持杆助跑、插杆起跳、摆体过杆、落地技术
- sports_javelin_throw: 标枪投掷技术 - 展示持枪助跑、交叉步、投掷、跟随技术

=== 球类运动 ===
- sports_basketball_shooting: 篮球投篮技术 - 展示投篮的准备、瞄准、出手、跟随动作
- sports_basketball_dunk: 篮球扣篮技术 - 展示单手扣篮、双手扣篮、战斧扣篮、风车扣篮等高难度扣篮
- sports_football_kick: 足球射门技术 - 展示助跑、支撑、摆腿、击球技术
- sports_football_bicycle_kick: 足球倒钩射门技术 - 展示倒钩射门的起跳、腾空、击球、落地技术
- sports_tennis_serve: 网球发球技术 - 展示抛球、引拍、击球、随挥四阶段
- sports_volleyball_spike: 排球扣球技术 - 展示助跑、起跳、挥臂、击球技术
- sports_badminton_smash: 羽毛球扣杀技术 - 展示准备、起跳、挥拍、击球技术
- sports_table_tennis_serve: 乒乓球发球技术 - 展示抛球、引拍、击球、落点控制
- sports_golf_swing: 高尔夫挥杆技术 - 展示站位、上杆、下杆、击球、收杆技术
- sports_hockey_shot: 曲棍球射门技术 - 展示持杆、引杆、击球、跟随技术

=== 游泳和体操 ===
- sports_swimming_stroke: 游泳泳姿分析 - 展示自由泳、蛙泳、蝶泳、仰泳四种泳姿
- sports_gymnastics_vault: 体操跳马技术 - 展示助跑、起跳、腾空、落地四阶段
- sports_gymnastics_floor_flip: 体操自由操空翻技术 - 展示前空翻、后空翻、侧空翻等高难度空翻动作
- sports_gymnastics_high_bar: 体操单杠大回环技术 - 展示单杠大回环、飞行动作、下法等高难度技术

=== 武术和格斗 ===
- sports_taekwondo_kick: 跆拳道踢腿技术 - 展示前踢、横踢、后踢等基本腿法
- sports_boxing_punch: 拳击出拳技术 - 展示直拳、勾拳、摆拳等基本拳法
- sports_fencing_lunge: 击剑弓步刺技术 - 展示准备姿势、弓步、刺击、收回技术

=== 冬季运动 ===
- sports_skiing_slalom: 高山滑雪回转技术 - 展示转弯、重心转移、立刃技术
- sports_figure_skating_spin: 花样滑冰旋转技术 - 展示直立旋转、蹲转、燕式旋转技术
- sports_figure_skating_jump: 花样滑冰跳跃技术 - 展示阿克塞尔跳、勾手跳、后外点冰跳等高难度跳跃

=== 水上运动 ===
- sports_diving_platform: 跳水技术分析 - 展示起跳、空中动作、入水技术
- sports_diving_twist: 跳水转体技术 - 展示向前转体、向后转体、向内转体等高难度动作
- sports_rowing_technique: 赛艇划桨技术 - 展示拉桨、推桨、回桨技术

=== 其他运动 ===
- sports_archery_shot: 射箭技术分析 - 展示站位、搭箭、拉弓、瞄准、释放技术
- sports_cycling_sprint: 自行车冲刺技术 - 展示踏频、姿势、发力技术
- sports_weightlifting_snatch: 举重抓举技术 - 展示准备、提铃、发力、支撑技术
- sports_yoga_pose: 瑜伽体式分析 - 展示山式、战士式、树式、下犬式等体式

=== 物理学 ===
- physics_force_composition: 力的合成与分解 - 展示平行四边形法则
- physics_projectile_motion: 抛体运动分析 - 展示不同角度的抛物线轨迹
- physics_circuit: 电路原理模拟 - 展示串联、并联电路
- physics_pendulum: 单摆运动分析 - 展示周期与摆长的关系

=== 艺术 ===
- art_color_wheel: 色彩理论模拟 - 展示色轮、互补色、类似色等色彩关系
- art_composition: 构图原理模拟 - 展示三分法、黄金分割等构图原理

```json
{
  "step_id": "S00X",
  "type": "simulator",
  "title": "动作演示：XXX",
  "simulator_spec": {
    "template_id": "从上面列表中选择一个模板ID",
    "customization": {
      "title_override": "可选：自定义标题",
      "description_override": "可选：自定义描述"
    }
  }
}
```

注意：
1. template_id 必须是上面列表中的有效ID
2. 根据课程内容选择最匹配的模板
3. 如果没有合适的模板，请使用 video 或 illustrated_content 代替""",
            "ai_tutor": """
【ai_tutor 规格】
```json
{
  "step_id": "S00X",
  "type": "ai_tutor",
  "title": "AI 导师考察",
  "trigger": "auto_after_content/required",
  "ai_spec": {
    "mode": "proactive_assessment",
    "opening_message": "开场白",
    "probing_questions": [
      {
        "question": "考察问题",
        "intent": "考察意图",
        "expected_elements": ["关键要素"],
        "follow_ups": {
          "if_superficial": "追问",
          "if_misconception": "纠正",
          "if_correct": "提升"
        }
      }
    ],
    "diagnostic_focus": {
      "key_concepts": ["核心概念"],
      "common_misconceptions": ["常见误区"],
      "transfer_scenarios": ["应用场景"]
    },
    "mastery_criteria": "掌握标准",
    "max_turns": 6
  }
}
```""",
            "assessment": """
【assessment 规格】
```json
{
  "step_id": "S00X",
  "type": "assessment",
  "title": "测验标题",
  "assessment_spec": {
    "type": "quick_check/scenario_quiz/open_ended/multiple_choice",
    "questions": [
      {
        "question": "问题",
        "options": ["A. 选项1", "B. 选项2"],
        "correct": "A",
        "explanation": "解释"
      }
    ],
    "pass_required": true/false
  }
}
```""",
            "quick_check": """
【quick_check 规格】
```json
{
  "step_id": "S00X",
  "type": "assessment",
  "title": "快速检测",
  "assessment_spec": {
    "type": "quick_check",
    "questions": [
      {"question": "问题", "options": ["A", "B", "C"], "correct": "A"}
    ],
    "pass_required": false
  }
}
```""",
            "practice": """
【practice 规格】
```json
{
  "step_id": "S00X",
  "type": "practice",
  "title": "练习",
  "content": {
    "instructions": "练习说明",
    "tasks": ["任务1", "任务2"]
  }
}
```"""
        }

        for form in forms:
            if form in form_specs:
                instructions.append(form_specs[form])

        return "\n".join(instructions)

    def get_style_prompt(self) -> str:
        """获取风格描述"""
        return self.system_prompt


def create_custom_processor(
    processor_id: str,
    name: str,
    description: str,
    system_prompt: str,
    color: str = "#6366f1",
    icon: str = "Sparkles"
) -> CustomProcessor:
    """
    创建自定义处理器实例

    Args:
        processor_id: 处理器 ID
        name: 处理器名称
        description: 处理器描述
        system_prompt: 系统提示词
        color: UI 颜色
        icon: UI 图标

    Returns:
        CustomProcessor 实例
    """
    return CustomProcessor(
        processor_id=processor_id,
        name=name,
        description=description,
        system_prompt=system_prompt,
        color=color,
        icon=icon
    )
