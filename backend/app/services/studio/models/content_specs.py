# ============================================
# content_specs.py - HERCU Studio 内容规格定义
# 基于 HERCU 课程包标准规范 v2.0
# ============================================

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class TextContentSpec:
    """文字内容规格"""
    body: str
    key_points: List[str] = field(default_factory=list)


@dataclass
class DiagramAnnotation:
    """图表标注"""
    position: str  # top, bottom, left, right, center
    text: str


@dataclass
class DiagramSpec:
    """图表规格"""
    diagram_id: str
    type: str  # DiagramType
    description: str
    annotations: List[DiagramAnnotation] = field(default_factory=list)
    design_notes: str = ""
    data_series: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class IllustratedContentSpec:
    """图文内容规格"""
    text: str
    diagram_spec: Optional[DiagramSpec] = None


@dataclass
class VideoScene:
    """视频场景"""
    timecode: str
    scene: str
    narration: str


@dataclass
class VideoScript:
    """视频脚本"""
    scenes: List[VideoScene] = field(default_factory=list)


@dataclass
class EmbeddedInteraction:
    """嵌入式互动"""
    timestamp: str
    type: str  # pause_and_ask, highlight, checkpoint
    question: str = ""
    options: List[str] = field(default_factory=list)
    correct: str = ""


@dataclass
class VideoSpec:
    """视频规格"""
    video_id: str
    duration: str
    script: VideoScript = field(default_factory=VideoScript)
    production_notes: str = ""
    video_url: str = ""  # 实际视频URL（如果已上传）
    embedded_interactions: List[EmbeddedInteraction] = field(default_factory=list)


@dataclass
class SimulatorInput:
    """模拟器输入参数"""
    id: str
    name: str
    label: str
    type: str  # number, slider, boolean, select
    defaultValue: Any = 0
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    unit: str = ""
    options: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SimulatorOutput:
    """模拟器输出"""
    id: str
    name: str
    label: str
    type: str  # number, text, chart, animation
    unit: str = ""
    formula: str = ""  # 计算公式，如 "input.force / input.mass"


@dataclass
class EvaluationCriterion:
    """评估标准"""
    id: str
    name: str
    description: str = ""
    targetValue: Optional[float] = None
    tolerance: Optional[float] = None


# ============================================
# 文科模拟器数据类型
# ============================================

@dataclass
class TimelineEvent:
    """时间线事件"""
    id: str
    year: str
    title: str
    description: str
    category: str = ""
    highlight: bool = False


@dataclass
class TimelineData:
    """时间线数据"""
    title: str
    events: List[TimelineEvent] = field(default_factory=list)


@dataclass
class DecisionOption:
    """决策选项"""
    id: str
    label: str
    result: str
    isOptimal: bool = False


@dataclass
class DecisionData:
    """决策情景数据"""
    title: str
    scenario: str
    question: str
    options: List[DecisionOption] = field(default_factory=list)
    analysis: str = ""


@dataclass
class ComparisonItem:
    """对比项"""
    id: str
    name: str
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class ComparisonData:
    """对比分析数据"""
    title: str
    dimensions: List[str] = field(default_factory=list)
    items: List[ComparisonItem] = field(default_factory=list)
    conclusion: str = ""


@dataclass
class ConceptNode:
    """概念节点"""
    id: str
    label: str
    description: str = ""
    category: str = ""


@dataclass
class ConceptRelation:
    """概念关系"""
    from_id: str  # 使用 from_id 避免 Python 关键字
    to: str
    label: str = ""


@dataclass
class ConceptMapData:
    """概念关系图数据"""
    title: str
    nodes: List[ConceptNode] = field(default_factory=list)
    relations: List[ConceptRelation] = field(default_factory=list)


@dataclass
class SimulatorSpec:
    """模拟器规格 - 支持理科和文科模拟器"""
    simulator_id: str
    name: str
    description: str
    type: str  # preset, custom, iframe, timeline, decision, comparison, concept-map

    # 预设模拟器 ID
    preset_id: str = ""

    # 自定义模拟器代码 (mode=custom 时使用)
    mode: str = ""  # custom, preset
    custom_code: str = ""  # JavaScript 代码
    variables: List[Dict[str, Any]] = field(default_factory=list)  # 变量配置

    # 理科模拟器配置
    inputs: List[SimulatorInput] = field(default_factory=list)
    outputs: List[SimulatorOutput] = field(default_factory=list)

    # 文科模拟器数据
    timeline: Optional[TimelineData] = None
    decision: Optional[DecisionData] = None
    comparison: Optional[ComparisonData] = None
    concept_map: Optional[ConceptMapData] = None

    # iframe 嵌入
    iframe_url: str = ""
    iframe_width: Optional[int] = None
    iframe_height: Optional[int] = None

    # 场景说明
    instructions: List[str] = field(default_factory=list)

    # 评估配置
    evaluation: Optional[Dict[str, Any]] = None


@dataclass
class ProbingQuestion:
    """探测问题"""
    question: str
    intent: str
    expected_elements: List[str] = field(default_factory=list)
    follow_ups: Dict[str, str] = field(default_factory=dict)


@dataclass
class DiagnosticFocus:
    """诊断焦点"""
    key_concepts: List[str] = field(default_factory=list)
    common_misconceptions: List[str] = field(default_factory=list)
    transfer_scenarios: List[str] = field(default_factory=list)


@dataclass
class ConversationGoal:
    """对话目标"""
    goal: str
    examples: List[str] = field(default_factory=list)


@dataclass
class AITutorSpec:
    """AI 导师规格"""
    opening_message: str = ""
    mode: str = "proactive_assessment"  # AITutorMode
    probing_questions: List[ProbingQuestion] = field(default_factory=list)
    conversation_goals: List[ConversationGoal] = field(default_factory=list)
    diagnostic_focus: Optional[DiagnosticFocus] = None
    mastery_criteria: str = ""
    max_turns: int = 6


@dataclass
class AssessmentQuestion:
    """测验问题"""
    question: str
    options: List[str] = field(default_factory=list)
    correct: str = ""
    explanation: str = ""
    scenario: str = ""  # 用于场景化测验


@dataclass
class AssessmentRubric:
    """开放题评分标准"""
    criterion: str
    points: int


@dataclass
class AssessmentSpec:
    """测验规格"""
    type: str  # AssessmentType
    questions: List[AssessmentQuestion] = field(default_factory=list)
    pass_required: bool = False
    rubric: List[str] = field(default_factory=list)  # 开放题评分标准
    min_words: int = 0  # 开放题最少字数
    ai_grading: bool = False  # 是否使用 AI 评分
