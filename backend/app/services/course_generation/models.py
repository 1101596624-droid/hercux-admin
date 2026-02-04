"""
课程生成数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class ReviewStatus(Enum):
    """审核状态"""
    APPROVED = "approved"       # 通过
    REJECTED = "rejected"       # 拒绝，需重做
    NEEDS_REVISION = "needs_revision"  # 需要修改特定部分


class ChapterType(Enum):
    """章节类型"""
    INTRODUCTION = "introduction"   # 导入
    CORE_CONTENT = "core_content"   # 核心内容
    PRACTICE = "practice"           # 实践
    ASSESSMENT = "assessment"       # 测评
    SUMMARY = "summary"             # 总结


@dataclass
class SimulatorQualityStandards:
    """模拟器质量标准 - 高标准"""

    # === 代码质量标准 ===
    min_code_lines: int = 25                    # 最少代码行数
    must_have_setup: bool = True                # 必须有 setup 函数
    must_have_update: bool = True               # 必须有 update 函数
    must_use_variables: bool = True             # 必须使用变量（与滑块联动）
    min_variables: int = 2                      # 最少变量数量
    max_variables: int = 5                      # 最多变量数量

    # === 视觉质量标准 ===
    min_visual_elements: int = 3                # 最少视觉元素（圆、矩形、文本等）
    must_have_animation: bool = True            # 必须有动画效果
    must_have_labels: bool = True               # 必须有文字标签说明
    recommended_colors: List[str] = field(default_factory=lambda: [
        '#3B82F6',  # 蓝色
        '#10B981',  # 绿色
        '#F59E0B',  # 橙色
        '#EF4444',  # 红色
        '#8B5CF6',  # 紫色
        '#EC4899',  # 粉色
        '#06B6D4',  # 青色
        '#FBBF24',  # 黄色
    ])

    # === 交互质量标准 ===
    variable_must_affect_visual: bool = True    # 变量必须影响视觉效果
    must_show_real_time_values: bool = True     # 必须实时显示数值
    smooth_animation: bool = True               # 动画必须流畅

    # === 教学质量标准 ===
    must_demonstrate_concept: bool = True       # 必须演示核心概念
    must_have_clear_cause_effect: bool = True   # 必须有清晰的因果关系
    variables_must_be_meaningful: bool = True   # 变量必须有实际意义

    # === 禁止项 ===
    forbidden_patterns: List[str] = field(default_factory=lambda: [
        'console.log',      # 不要调试代码
        'alert(',           # 不要弹窗
        'document.',        # 不要操作DOM
        'window.',          # 不要操作window
        'eval(',            # 不要eval
        'setTimeout',       # 不要用setTimeout（用ctx.time）
        'setInterval',      # 不要用setInterval
    ])


@dataclass
class ChapterQualityStandards:
    """章节质量标准"""

    # === 内容标准 ===
    min_steps: int = 5                          # 最少步骤数
    max_steps: int = 8                          # 最多步骤数
    min_text_length: int = 100                  # 每步最少字数
    min_key_points: int = 2                     # 每步最少要点数

    # === 结构标准 ===
    must_have_text_content: bool = True         # 必须有文本内容
    must_have_simulator: bool = True            # 必须有模拟器（核心章节）
    must_have_assessment: bool = True           # 必须有测评

    # === 模拟器标准 ===
    simulator_standards: SimulatorQualityStandards = field(
        default_factory=SimulatorQualityStandards
    )

    # === 禁止项 ===
    forbidden_content: List[str] = field(default_factory=lambda: [
        '待补充',
        '此处省略',
        '...',
        '等等',
        'TODO',
        'FIXME',
    ])


@dataclass
class ChapterOutline:
    """章节大纲"""
    index: int
    title: str
    chapter_type: ChapterType
    recommended_forms: List[str]
    complexity_level: str  # simple, standard, advanced
    key_concepts: List[str]
    learning_objectives: List[str]
    suggested_simulator: Optional[str] = None  # 建议的模拟器主题


@dataclass
class CourseOutline:
    """课程大纲"""
    title: str
    description: str
    total_chapters: int
    estimated_hours: float
    difficulty: str  # beginner, intermediate, advanced
    chapters: List[ChapterOutline]
    core_concepts: List[str]  # 整个课程的核心概念
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SimulatorSpec:
    """模拟器规格"""
    name: str
    description: str
    mode: str = "custom"
    variables: List[Dict[str, Any]] = field(default_factory=list)
    custom_code: str = ""

    def validate(self, standards: SimulatorQualityStandards) -> List[str]:
        """验证模拟器是否符合质量标准，返回问题列表"""
        issues = []

        # 检查代码行数
        code_lines = len([l for l in self.custom_code.split('\n') if l.strip()])
        if code_lines < standards.min_code_lines:
            issues.append(f"代码太短，只有{code_lines}行，至少需要{standards.min_code_lines}行")

        # 检查必要函数
        if standards.must_have_setup and 'function setup' not in self.custom_code:
            issues.append("缺少 setup 函数")
        if standards.must_have_update and 'function update' not in self.custom_code:
            issues.append("缺少 update 函数")

        # 检查变量使用
        if standards.must_use_variables:
            if 'ctx.getVar' not in self.custom_code:
                issues.append("没有使用变量（ctx.getVar），模拟器无法与滑块联动")

        # 检查变量数量
        if len(self.variables) < standards.min_variables:
            issues.append(f"变量太少，只有{len(self.variables)}个，至少需要{standards.min_variables}个")
        if len(self.variables) > standards.max_variables:
            issues.append(f"变量太多，有{len(self.variables)}个，最多{standards.max_variables}个")

        # 检查视觉元素
        visual_methods = ['createCircle', 'createRect', 'createText', 'createLine', 'createCurve', 'createPolygon']
        visual_count = sum(1 for m in visual_methods if m in self.custom_code)
        if visual_count < standards.min_visual_elements:
            issues.append(f"视觉元素太少，只用了{visual_count}种，至少需要{standards.min_visual_elements}种")

        # 检查动画
        if standards.must_have_animation:
            animation_indicators = ['ctx.time', 'ctx.math.sin', 'ctx.math.cos', 'setPosition', 'setRotation', 'setScale']
            has_animation = any(ind in self.custom_code for ind in animation_indicators)
            if not has_animation:
                issues.append("没有动画效果，模拟器应该有动态变化")

        # 检查标签
        if standards.must_have_labels:
            if 'createText' not in self.custom_code:
                issues.append("没有文字标签，用户无法理解模拟器展示的内容")

        # 检查禁止项
        for pattern in standards.forbidden_patterns:
            if pattern in self.custom_code:
                issues.append(f"代码中包含禁止使用的模式：{pattern}")

        return issues


@dataclass
class ChapterStep:
    """章节步骤"""
    step_id: str
    type: str  # text_content, illustrated_content, simulator, assessment
    title: str
    content: Optional[Dict[str, Any]] = None
    simulator_spec: Optional[SimulatorSpec] = None
    assessment_spec: Optional[Dict[str, Any]] = None
    diagram_spec: Optional[Dict[str, Any]] = None


@dataclass
class ChapterResult:
    """章节生成结果"""
    lesson_id: str
    title: str
    order: int
    total_steps: int
    rationale: str
    script: List[ChapterStep]
    estimated_minutes: int
    learning_objectives: List[str]
    complexity_level: str

    # 元数据
    generation_attempts: int = 1
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ReviewResult:
    """审核结果"""
    status: ReviewStatus
    chapter_index: int
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    simulator_issues: List[str] = field(default_factory=list)

    # 具体问题定位
    problematic_steps: List[int] = field(default_factory=list)

    # 审核评分 (0-100)
    content_score: int = 0
    simulator_score: int = 0
    overall_score: int = 0

    # 审核意见
    review_comment: str = ""

    def is_approved(self) -> bool:
        return self.status == ReviewStatus.APPROVED

    def get_rejection_reason(self) -> str:
        reasons = []
        if self.issues:
            reasons.append("内容问题：" + "；".join(self.issues))
        if self.simulator_issues:
            reasons.append("模拟器问题：" + "；".join(self.simulator_issues))
        return "\n".join(reasons)


@dataclass
class GenerationState:
    """生成状态 - 监督者需要维护的状态"""

    # 课程信息
    course_title: str
    source_material: str
    source_info: str
    processor_id: str

    # 大纲
    outline: Optional[CourseOutline] = None

    # 已完成的章节
    completed_chapters: List[ChapterResult] = field(default_factory=list)

    # 已使用的模拟器（防止重复）
    used_simulators: List[str] = field(default_factory=list)

    # 已讲解的主题（防止重复）
    covered_topics: List[str] = field(default_factory=list)

    # 已使用的测验题目（防止重复）
    used_questions: List[str] = field(default_factory=list)

    # 当前进度
    current_chapter_index: int = 0
    current_attempt: int = 0
    max_attempts: int = 3  # 每章最多重试次数

    # 监督者对话状态
    supervisor_conversation_id: Optional[str] = None
    supervisor_context_compressed: bool = False

    # 时间戳
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_updated_at: datetime = field(default_factory=datetime.utcnow)

    def get_context_summary(self) -> str:
        """获取上下文摘要，用于监督者上下文被压缩时重新发送"""
        summary = f"""
=== 课程生成状态摘要 ===

【课程信息】
标题：{self.course_title}
处理器：{self.processor_id}

【大纲】
{self._format_outline()}

【已完成章节】({len(self.completed_chapters)}/{self.outline.total_chapters if self.outline else '?'})
{self._format_completed_chapters()}

【已使用的模拟器】
{', '.join(self.used_simulators) if self.used_simulators else '无'}

【已讲解的主题】
{', '.join(self.covered_topics) if self.covered_topics else '无'}

【当前进度】
正在生成第 {self.current_chapter_index + 1} 章，第 {self.current_attempt + 1} 次尝试
"""
        return summary.strip()

    def _format_outline(self) -> str:
        if not self.outline:
            return "尚未生成"

        lines = [f"共 {self.outline.total_chapters} 章，预计 {self.outline.estimated_hours} 小时"]
        for ch in self.outline.chapters:
            status = "✓" if ch.index < len(self.completed_chapters) else "○"
            lines.append(f"  {status} 第{ch.index + 1}章：{ch.title}")
        return "\n".join(lines)

    def _format_completed_chapters(self) -> str:
        if not self.completed_chapters:
            return "无"

        lines = []
        for ch in self.completed_chapters:
            sim_count = sum(1 for s in ch.script if s.type == 'simulator')
            lines.append(f"  - 第{ch.order + 1}章：{ch.title}（{ch.total_steps}步，{sim_count}个模拟器）")
        return "\n".join(lines)

    def add_completed_chapter(self, chapter: ChapterResult):
        """添加已完成的章节，同时更新已使用的模拟器和主题"""
        self.completed_chapters.append(chapter)
        self.covered_topics.append(chapter.title)

        # 提取模拟器
        for step in chapter.script:
            if step.type == 'simulator' and step.simulator_spec:
                self.used_simulators.append(step.simulator_spec.name)

            # 提取测验题目
            if step.type == 'assessment' and step.assessment_spec:
                questions = step.assessment_spec.get('questions', [])
                for q in questions:
                    self.used_questions.append(q.get('question', ''))

        self.current_chapter_index = len(self.completed_chapters)
        self.current_attempt = 0
        self.last_updated_at = datetime.utcnow()

    def increment_attempt(self):
        """增加尝试次数"""
        self.current_attempt += 1
        self.last_updated_at = datetime.utcnow()

    def can_retry(self) -> bool:
        """是否还能重试"""
        return self.current_attempt < self.max_attempts
