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
【simulator 规格 - 高质量交互模拟器】

⚠️ 重要：模拟器内容必须完整、详细、有教育价值！

模拟器分为两大类：
1. 理科模拟器（滑块调参、计算演示）
2. 文科模拟器（时间线、决策、对比、概念图）

AI 应根据内容特性智能选择合适的类型。

=== 理科模拟器（参数计算型）===
适用：物理公式演示、参数调节可视化、数据计算

【质量要求】
- inputs: 至少 2-3 个输入参数，每个都要有完整的 min/max/step/unit
- outputs: 至少 1-2 个输出结果，每个都要有正确的计算公式
- description: 至少 30 字，说明模拟器的教学目的
- instructions: 至少 2-3 条使用说明

{
  "step_id": "S00X",
  "type": "simulator",
  "title": "牛顿第二定律计算器",
  "simulator_spec": {
    "simulator_id": "SIM-XXX",
    "name": "牛顿第二定律交互演示",
    "description": "通过调整力和质量参数，直观观察加速度的变化规律，深入理解 F=ma 公式的物理含义",
    "type": "custom",
    "inputs": [
      {
        "id": "force",
        "name": "force",
        "label": "作用力",
        "type": "slider",
        "defaultValue": 100,
        "min": 0,
        "max": 500,
        "step": 10,
        "unit": "N"
      },
      {
        "id": "mass",
        "name": "mass",
        "label": "物体质量",
        "type": "slider",
        "defaultValue": 50,
        "min": 10,
        "max": 200,
        "step": 5,
        "unit": "kg"
      }
    ],
    "outputs": [
      {
        "id": "acceleration",
        "name": "acceleration",
        "label": "加速度",
        "type": "number",
        "unit": "m/s²",
        "formula": "input.force / input.mass"
      },
      {
        "id": "momentum",
        "name": "momentum",
        "label": "动量变化率",
        "type": "number",
        "unit": "kg·m/s²",
        "formula": "input.force"
      }
    ],
    "instructions": [
      "拖动力滑块，观察加速度如何随力的增大而增大",
      "拖动质量滑块，观察加速度如何随质量的增大而减小",
      "尝试找出使加速度等于 10 m/s² 的力和质量组合"
    ]
  }
}

=== 文科模拟器 - 时间线 ===
适用：历史事件、发展历程、演变过程

【质量要求】
- events: 至少 4-6 个事件，按时间顺序排列
- 每个事件都要有详细的 description（至少 20 字）
- 标记 1-2 个关键事件为 highlight: true
- 使用 category 对事件进行分类

{
  "step_id": "S00X",
  "type": "simulator",
  "title": "人工智能发展历程",
  "simulator_spec": {
    "simulator_id": "SIM-XXX",
    "name": "AI发展里程碑时间线",
    "description": "探索人工智能从诞生到今天的关键发展节点，了解每个时代的突破性进展",
    "type": "timeline",
    "timeline": {
      "title": "人工智能发展史",
      "events": [
        {"id": "e1", "year": "1956", "title": "达特茅斯会议", "description": "人工智能作为一门学科正式诞生，麦卡锡首次提出'人工智能'这一术语", "category": "起源", "highlight": true},
        {"id": "e2", "year": "1966", "title": "ELIZA诞生", "description": "第一个聊天机器人ELIZA问世，展示了自然语言处理的可能性", "category": "早期探索", "highlight": false},
        {"id": "e3", "year": "1997", "title": "深蓝战胜卡斯帕罗夫", "description": "IBM深蓝计算机击败国际象棋世界冠军，标志着AI在特定领域超越人类", "category": "里程碑", "highlight": true},
        {"id": "e4", "year": "2012", "title": "深度学习突破", "description": "AlexNet在ImageNet竞赛中大幅领先，开启深度学习革命", "category": "技术突破", "highlight": false},
        {"id": "e5", "year": "2022", "title": "ChatGPT发布", "description": "OpenAI发布ChatGPT，大语言模型进入公众视野，引发AI应用热潮", "category": "大模型时代", "highlight": true}
      ]
    },
    "instructions": [
      "点击时间线上的节点查看详细信息",
      "注意观察高亮标记的关键转折点",
      "思考每个阶段的技术特点和局限性"
    ]
  }
}

=== 文科模拟器 - 决策情景 ===
适用：案例分析、决策训练、情景模拟

【质量要求】
- scenario: 至少 50 字的详细情景描述
- options: 至少 3-4 个选项，每个都要有详细的 result 说明
- 必须标记一个 isOptimal: true 的最优选项
- analysis: 至少 30 字的综合分析

{
  "step_id": "S00X",
  "type": "simulator",
  "title": "创业融资决策",
  "simulator_spec": {
    "simulator_id": "SIM-XXX",
    "name": "创业融资策略选择",
    "description": "模拟创业公司在不同发展阶段面临的融资决策，学习评估各种融资方式的利弊",
    "type": "decision",
    "decision": {
      "title": "A轮融资方案选择",
      "scenario": "你的科技创业公司已完成产品开发，用户增长良好，现需要A轮融资扩大规模。目前有三家投资机构表示兴趣：一家顶级VC愿意投资2000万但要求35%股权；一家产业资本愿意投资1500万要求25%股权并提供行业资源；一家政府引导基金愿意投资1000万要求15%股权但审批流程较长。",
      "question": "作为创始人，你会选择哪个融资方案？",
      "options": [
        {"id": "opt1", "label": "选择顶级VC", "result": "获得充足资金和品牌背书，但股权稀释较多，后续融资估值压力大", "isOptimal": false},
        {"id": "opt2", "label": "选择产业资本", "result": "资金适中，获得行业资源和渠道支持，有利于业务拓展，股权稀释合理", "isOptimal": true},
        {"id": "opt3", "label": "选择政府引导基金", "result": "股权稀释最少，但资金较少且到账慢，可能错过市场窗口期", "isOptimal": false},
        {"id": "opt4", "label": "继续等待更好的条件", "result": "保持灵活性，但可能面临资金链断裂风险，竞争对手可能抢先", "isOptimal": false}
      ],
      "analysis": "在这个案例中，产业资本是最优选择。虽然资金不是最多，但25%的股权稀释合理，更重要的是能获得行业资源支持，这对早期创业公司的业务拓展至关重要。融资不仅是获取资金，更是获取战略资源。"
    },
    "instructions": [
      "仔细阅读情景描述，理解公司当前状况",
      "分析每个选项的利弊",
      "做出你的选择，然后查看分析结果"
    ]
  }
}

=== 文科模拟器 - 对比分析 ===
适用：概念对比、方案比较、特征分析

【质量要求】
- dimensions: 至少 3-4 个对比维度
- items: 至少 2-3 个对比对象
- 每个对象的 attributes 必须覆盖所有维度
- conclusion: 至少 30 字的对比结论

{
  "step_id": "S00X",
  "type": "simulator",
  "title": "编程语言对比",
  "simulator_spec": {
    "simulator_id": "SIM-XXX",
    "name": "主流编程语言特性对比",
    "description": "从多个维度对比主流编程语言的特点，帮助你根据项目需求选择合适的语言",
    "type": "comparison",
    "comparison": {
      "title": "Python vs JavaScript vs Go 对比",
      "dimensions": ["学习难度", "执行性能", "应用领域", "生态系统", "并发支持"],
      "items": [
        {"id": "python", "name": "Python", "attributes": {"学习难度": "简单，语法清晰", "执行性能": "较慢，解释执行", "应用领域": "AI/数据科学/自动化", "生态系统": "丰富，科学计算库强大", "并发支持": "GIL限制，多进程为主"}},
        {"id": "javascript", "name": "JavaScript", "attributes": {"学习难度": "中等，异步概念需理解", "执行性能": "V8引擎优化后较快", "应用领域": "Web前后端/移动应用", "生态系统": "npm最大，更新快", "并发支持": "事件循环，单线程异步"}},
        {"id": "go", "name": "Go", "attributes": {"学习难度": "中等，概念简洁", "执行性能": "快，编译型语言", "应用领域": "云原生/微服务/系统编程", "生态系统": "精简，标准库强大", "并发支持": "goroutine原生支持，优秀"}}
      ],
      "conclusion": "选择编程语言应根据项目需求：AI和数据分析选Python；Web开发选JavaScript；高性能后端服务选Go。没有最好的语言，只有最适合的语言。"
    },
    "instructions": [
      "横向对比同一维度下不同语言的特点",
      "纵向了解每种语言的整体特性",
      "思考你的项目最需要哪些特性"
    ]
  }
}

=== 文科模拟器 - 概念关系图 ===
适用：知识结构、概念关系、因果链条

【质量要求】
- nodes: 至少 4-6 个概念节点，每个都要有 description
- relations: 至少 3-5 个关系连接，每个都要有 label 说明关系类型
- 使用 category 对节点进行分类

{
  "step_id": "S00X",
  "type": "simulator",
  "title": "机器学习概念图",
  "simulator_spec": {
    "simulator_id": "SIM-XXX",
    "name": "机器学习核心概念关系",
    "description": "可视化展示机器学习领域的核心概念及其相互关系，帮助建立系统的知识框架",
    "type": "concept-map",
    "concept_map": {
      "title": "机器学习知识图谱",
      "nodes": [
        {"id": "ml", "label": "机器学习", "description": "让计算机从数据中学习规律的技术", "category": "核心"},
        {"id": "supervised", "label": "监督学习", "description": "使用标注数据训练模型", "category": "学习范式"},
        {"id": "unsupervised", "label": "无监督学习", "description": "从无标注数据中发现模式", "category": "学习范式"},
        {"id": "dl", "label": "深度学习", "description": "使用多层神经网络的机器学习方法", "category": "技术分支"},
        {"id": "nn", "label": "神经网络", "description": "模拟生物神经元的计算模型", "category": "基础模型"},
        {"id": "cnn", "label": "卷积神经网络", "description": "擅长处理图像数据的神经网络", "category": "网络架构"}
      ],
      "relations": [
        {"from_id": "ml", "to": "supervised", "label": "包含"},
        {"from_id": "ml", "to": "unsupervised", "label": "包含"},
        {"from_id": "ml", "to": "dl", "label": "发展出"},
        {"from_id": "dl", "to": "nn", "label": "基于"},
        {"from_id": "nn", "to": "cnn", "label": "演化为"}
      ]
    },
    "instructions": [
      "从中心概念开始，逐步探索相关概念",
      "注意概念之间的关系类型",
      "尝试在脑中重建这个知识网络"
    ]
  }
}

【类型选择指南】
- 有数值计算、公式演示 → custom（理科）
- 有时间顺序、历史发展 → timeline
- 有选择决策、案例分析 → decision
- 有多对象比较、特征分析 → comparison
- 有概念关系、知识结构 → concept-map

【内容质量检查清单】
✓ 所有必填字段都有值
✓ description 至少 30 字
✓ instructions 至少 2 条
✓ 数据量充足（事件≥4个，选项≥3个，节点≥4个）
✓ 内容有教育价值，不是占位符
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
