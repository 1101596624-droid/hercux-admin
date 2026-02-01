# ============================================
# processors/intelligent.py - 智能教学规划处理器
# ============================================

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from .base import BaseProcessor, ProcessorInfo, ProcessorRegistry


@dataclass
class ContentAnalysis:
    """内容分析结果"""
    has_dynamic_process: bool = False
    is_physical_action: bool = False
    has_structural_relationship: bool = False
    requires_hands_on_practice: bool = False
    has_parameter_feedback_loop: bool = False
    has_common_misconceptions: bool = False
    needs_personalized_guidance: bool = False
    is_gateway_to_next: bool = False
    complexity_level: str = "standard"
    recommended_forms: List[str] = field(default_factory=list)
    rationale: str = ""


# 教学形式类型
class TeachingFormType:
    TEXT_CONTENT = "text_content"
    ILLUSTRATED_CONTENT = "illustrated_content"
    VIDEO = "video"
    SIMULATOR = "simulator"
    AI_TUTOR = "ai_tutor"
    ASSESSMENT = "assessment"
    QUICK_CHECK = "quick_check"
    PRACTICE = "practice"


@ProcessorRegistry.register
class IntelligentProcessor(BaseProcessor):
    """智能教学规划处理器"""

    processor_info = ProcessorInfo(
        id="intelligent",
        name="智能教学规划",
        description="基于内容特性分析，智能推荐最优教学形式组合",
        version="2.0.0",
        author="HERCU Studio",
        tags=["智能", "自适应", "多形式"],
        color="#6366f1",
        icon="sparkles"
    )

    def analyze_content(self, content: str, context: Dict[str, Any] = None) -> ContentAnalysis:
        """分析内容特性"""
        context = context or {}
        analysis = ContentAnalysis()
        content_lower = content.lower()

        # 检测动态过程
        if any(kw in content_lower for kw in ["动作", "步骤", "流程", "过程", "演示", "操作"]):
            analysis.has_dynamic_process = True

        # 检测身体动作
        if any(kw in content_lower for kw in ["深蹲", "卧推", "硬拉", "姿势", "动作要领"]):
            analysis.is_physical_action = True

        # 检测结构关系
        if any(kw in content_lower for kw in ["原理", "机制", "关系", "层级", "分类", "因果"]):
            analysis.has_structural_relationship = True

        # 检测实践需求
        if any(kw in content_lower for kw in ["练习", "实践", "应用", "设计", "规划"]):
            analysis.requires_hands_on_practice = True

        # 检测参数反馈循环
        if any(kw in content_lower for kw in ["调整", "参数", "优化", "反馈", "结果"]):
            analysis.has_parameter_feedback_loop = True

        # 检测常见误区
        if any(kw in content_lower for kw in ["误区", "错误", "常见问题", "注意", "避免"]):
            analysis.has_common_misconceptions = True

        analysis.recommended_forms = self.recommend_forms(analysis)
        analysis.rationale = self._generate_rationale(analysis)

        return analysis

    def recommend_forms(self, analysis: ContentAnalysis) -> List[str]:
        """推荐教学形式"""
        forms = []

        # 基础内容载体
        if analysis.has_dynamic_process:
            if analysis.is_physical_action:
                forms.append(TeachingFormType.VIDEO)
            else:
                forms.append(TeachingFormType.ILLUSTRATED_CONTENT)
        elif analysis.has_structural_relationship:
            forms.append(TeachingFormType.ILLUSTRATED_CONTENT)
        else:
            forms.append(TeachingFormType.TEXT_CONTENT)

        # 实践环节
        if analysis.requires_hands_on_practice:
            if analysis.has_parameter_feedback_loop:
                forms.append(TeachingFormType.SIMULATOR)
            else:
                forms.append(TeachingFormType.PRACTICE)

        # AI 介入
        if analysis.has_common_misconceptions or analysis.needs_personalized_guidance:
            forms.append(TeachingFormType.AI_TUTOR)

        # 检测环节
        if analysis.is_gateway_to_next:
            forms.append(TeachingFormType.ASSESSMENT)
        else:
            forms.append(TeachingFormType.QUICK_CHECK)

        return forms

    def build_structure_prompt(
        self,
        source_material: str,
        course_title: str,
        context: Dict[str, Any] = None
    ) -> str:
        """构建课程结构生成的 prompt"""
        return f"""你是一位专业的课程设计师，请根据以下素材设计课程结构。

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
        recommended_forms = lesson_info.get("recommended_forms", ["text_content", "quick_check"])
        complexity = lesson_info.get("complexity_level", "standard")
        rationale = lesson_info.get("rationale", "")

        form_instructions = self._build_form_instructions(recommended_forms)

        return f"""你是一位专业的课程内容设计师，请为以下课时生成详细内容。

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
  ],
  "summary": "本课时摘要（用于下一课时衔接）"
}}
```

【重要提示】
1. 严格按照推荐的教学形式生成 steps
2. 每个 step 必须包含完整的规格信息
3. 内容要与学习目标紧密对应
4. 保持与上一课时的连贯性
"""

    def _generate_rationale(self, analysis: ContentAnalysis) -> str:
        """生成分析理由"""
        reasons = []

        if analysis.has_dynamic_process:
            if analysis.is_physical_action:
                reasons.append("内容涉及身体动作，需要视频演示")
            else:
                reasons.append("内容有动态过程，需要可视化展示")

        if analysis.has_structural_relationship:
            reasons.append("内容有结构/层级关系，适合图文展示")

        if analysis.requires_hands_on_practice:
            if analysis.has_parameter_feedback_loop:
                reasons.append("需要动手实践且有参数反馈，适合模拟器")
            else:
                reasons.append("需要简单练习巩固")

        if analysis.has_common_misconceptions:
            reasons.append("存在常见误区，可能需要 AI 个性化纠正")

        if not reasons:
            reasons.append("纯概念内容，文字足够表达")

        return "；".join(reasons)

    def _build_form_instructions(self, forms: List[str]) -> str:
        """构建教学形式的详细说明"""
        form_specs = {
            "text_content": """
【text_content 规格】
{
  "step_id": "S00X",
  "type": "text_content",
  "title": "步骤标题",
  "content": {
    "body": "正文内容（支持 Markdown）",
    "key_points": ["要点1", "要点2"]
  }
}""",
            "illustrated_content": """
【illustrated_content 规格】
{
  "step_id": "S00X",
  "type": "illustrated_content",
  "title": "步骤标题",
  "content": {"text": "说明文字"},
  "diagram_spec": {
    "diagram_id": "DIAG-XXX",
    "type": "static_diagram/flowchart/line_chart",
    "description": "图表描述"
  }
}""",
            "video": """
【video 规格】
{
  "step_id": "S00X",
  "type": "video",
  "title": "步骤标题",
  "video_spec": {
    "video_id": "VID-XXX",
    "duration": "3:00",
    "script": {"scenes": [{"timecode": "00:00-00:30", "scene": "场景描述", "narration": "旁白"}]}
  }
}""",
            "simulator": """
【simulator 规格 - 简化版交互模拟器】

模拟器分为两大类：
1. 理科模拟器（滑块调参、计算演示）
2. 文科模拟器（时间线、决策、对比、概念图）

AI 应根据内容特性智能选择合适的类型。

=== 理科模拟器（参数计算型）===
适用：物理公式演示、参数调节可视化、数据计算

{
  "step_id": "S00X",
  "type": "simulator",
  "title": "XXX计算器",
  "simulator_spec": {
    "simulator_id": "SIM-XXX",
    "name": "模拟器名称",
    "description": "模拟器描述",
    "type": "custom",
    "inputs": [
      {
        "id": "input1",
        "name": "force",
        "label": "力 (N)",
        "type": "slider",
        "defaultValue": 100,
        "min": 0,
        "max": 500,
        "step": 10,
        "unit": "N"
      }
    ],
    "outputs": [
      {
        "id": "output1",
        "name": "acceleration",
        "label": "加速度",
        "type": "number",
        "unit": "m/s²",
        "formula": "input.force / 50"
      }
    ],
    "instructions": ["调整滑块观察结果变化"]
  }
}

=== 文科模拟器 - 时间线 ===
适用：历史事件、发展历程、演变过程

{
  "step_id": "S00X",
  "type": "simulator",
  "title": "XXX发展历程",
  "simulator_spec": {
    "simulator_id": "SIM-XXX",
    "name": "时间线名称",
    "description": "时间线描述",
    "type": "timeline",
    "timeline": {
      "title": "时间线标题",
      "events": [
        {"id": "e1", "year": "1949", "title": "事件标题", "description": "事件描述", "category": "分类", "highlight": false}
      ]
    }
  }
}

=== 文科模拟器 - 决策情景 ===
适用：案例分析、决策训练、情景模拟

{
  "step_id": "S00X",
  "type": "simulator",
  "title": "XXX决策",
  "simulator_spec": {
    "simulator_id": "SIM-XXX",
    "name": "决策名称",
    "description": "决策描述",
    "type": "decision",
    "decision": {
      "title": "决策标题",
      "scenario": "情景描述",
      "question": "你会如何选择？",
      "options": [
        {"id": "opt1", "label": "选项A", "result": "选择A的结果", "isOptimal": true},
        {"id": "opt2", "label": "选项B", "result": "选择B的结果", "isOptimal": false}
      ],
      "analysis": "综合分析"
    }
  }
}

=== 文科模拟器 - 对比分析 ===
适用：概念对比、方案比较、特征分析

{
  "step_id": "S00X",
  "type": "simulator",
  "title": "XXX对比",
  "simulator_spec": {
    "simulator_id": "SIM-XXX",
    "name": "对比名称",
    "description": "对比描述",
    "type": "comparison",
    "comparison": {
      "title": "对比标题",
      "dimensions": ["维度1", "维度2", "维度3"],
      "items": [
        {"id": "item1", "name": "对象A", "attributes": {"维度1": "值1", "维度2": "值2", "维度3": "值3"}},
        {"id": "item2", "name": "对象B", "attributes": {"维度1": "值1", "维度2": "值2", "维度3": "值3"}}
      ],
      "conclusion": "对比结论"
    }
  }
}

=== 文科模拟器 - 概念关系图 ===
适用：知识结构、概念关系、因果链条

{
  "step_id": "S00X",
  "type": "simulator",
  "title": "XXX概念图",
  "simulator_spec": {
    "simulator_id": "SIM-XXX",
    "name": "概念图名称",
    "description": "概念图描述",
    "type": "concept-map",
    "concept_map": {
      "title": "概念图标题",
      "nodes": [
        {"id": "n1", "label": "概念A", "description": "概念描述", "category": "分类"}
      ],
      "relations": [
        {"from": "n1", "to": "n2", "label": "关系描述"}
      ]
    }
  }
}

【类型选择指南】
- 有数值计算、公式演示 → custom（理科）
- 有时间顺序、历史发展 → timeline
- 有选择决策、案例分析 → decision
- 有多对象比较、特征分析 → comparison
- 有概念关系、知识结构 → concept-map
""",
            "ai_tutor": """
【ai_tutor 规格】
{
  "step_id": "S00X",
  "type": "ai_tutor",
  "title": "AI 导师考察",
  "ai_spec": {
    "opening_message": "开场白",
    "conversation_goals": [{"goal": "目标", "examples": ["示例"]}],
    "max_turns": 6
  }
}""",
            "assessment": """
【assessment 规格】
{
  "step_id": "S00X",
  "type": "assessment",
  "title": "测验标题",
  "assessment_spec": {
    "type": "quick_check",
    "questions": [{"question": "问题", "options": ["A", "B", "C"], "correct": "A", "explanation": "解释"}],
    "pass_required": true
  }
}""",
            "quick_check": """
【quick_check 规格】
{
  "step_id": "S00X",
  "type": "assessment",
  "title": "快速检测",
  "assessment_spec": {
    "type": "quick_check",
    "questions": [{"question": "问题", "options": ["A", "B", "C"], "correct": "A"}],
    "pass_required": false
  }
}""",
            "practice": """
【practice 规格】
{
  "step_id": "S00X",
  "type": "practice",
  "title": "练习",
  "content": {"instructions": "练习说明", "tasks": ["任务1", "任务2"]}
}"""
        }

        instructions = []
        for form in forms:
            if form in form_specs:
                instructions.append(form_specs[form])

        return "\n".join(instructions)

    def get_style_prompt(self) -> str:
        return """使用智能教学规划风格：
- 根据内容特性选择最合适的教学形式
- 遵循"最小充分原则"，不堆砌形式
- 确保每个教学形式的选择都有明确理由
- 保持内容的连贯性和渐进性"""
