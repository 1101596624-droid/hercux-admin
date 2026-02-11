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
    """模拟器质量标准 - 专业级高标准 (2026-02-06 全面升级版)"""

    # === 代码质量标准（严格）===
    min_code_lines: int = 200                   # 最少代码行数（提高到200行）
    max_code_lines: int = 600                   # 最多代码行数
    must_have_setup: bool = True                # 必须有 setup 函数
    must_have_update: bool = True               # 必须有 update 函数
    must_use_variables: bool = True             # 必须使用变量（与滑块联动）
    min_variables: int = 4                      # 最少变量数量（提高到4个）
    max_variables: int = 8                      # 最多变量数量（提高到8个）
    min_functions: int = 3                      # 最少自定义函数数量（提高到3个）
    min_comments: int = 10                      # 最少注释行数（新增）

    # === 视觉质量标准（专业级）===
    min_visual_elements: int = 7                # 最少视觉元素类型（提高到7种）
    min_total_shapes: int = 25                  # 最少图形总数（提高到25个）
    must_have_animation: bool = True            # 必须有动画效果
    must_have_labels: bool = True               # 必须有文字标签说明
    must_have_legend: bool = True               # 必须有图例
    must_have_data_display: bool = True         # 必须有数据显示面板
    must_have_background: bool = True           # 必须有背景装饰（网格/渐变等）
    must_have_title: bool = True                # 必须有标题
    must_have_axis: bool = True                 # 必须有坐标轴或刻度（新增）
    must_have_tooltip: bool = True              # 必须有提示信息（新增）
    min_colors_used: int = 6                    # 最少使用颜色数量（提高到6种）
    min_text_elements: int = 8                  # 最少文字元素数量（新增）
    recommended_colors: List[str] = field(default_factory=lambda: [
        '#3B82F6',  # 蓝色
        '#10B981',  # 绿色
        '#F59E0B',  # 橙色
        '#EF4444',  # 红色
        '#8B5CF6',  # 紫色
        '#EC4899',  # 粉色
        '#06B6D4',  # 青色
        '#FBBF24',  # 黄色
        '#14B8A6',  # 青绿色
        '#F97316',  # 深橙色
    ])

    # === 交互质量标准（增强）===
    variable_must_affect_visual: bool = True    # 变量必须影响视觉效果
    must_show_real_time_values: bool = True     # 必须实时显示数值
    smooth_animation: bool = True               # 动画必须流畅
    must_have_state_panel: bool = True          # 必须有状态面板
    must_have_progress_indicator: bool = True   # 必须有进度/状态指示器（新增）
    min_animation_types: int = 2                # 最少动画类型数量（新增）

    # === 教学质量标准（强化）===
    must_demonstrate_concept: bool = True       # 必须演示核心概念
    must_have_clear_cause_effect: bool = True   # 必须有清晰的因果关系
    variables_must_be_meaningful: bool = True   # 变量必须有实际意义
    must_have_visual_feedback: bool = True      # 变量变化必须有视觉反馈
    must_have_educational_value: bool = True    # 必须有教学价值（新增）
    must_show_formula: bool = False             # 建议显示相关公式（可选）

    # === 复杂对象标准（提高）===
    min_composite_objects: int = 3              # 最少组合对象数量（提高到3个）
    min_shapes_per_object: int = 4              # 每个组合对象最少图形数量（提高到4个）
    must_have_layered_objects: bool = True      # 必须有层次感的对象（新增）

    # === 禁止项 ===
    forbidden_patterns: List[str] = field(default_factory=lambda: [
        'console.log',      # 不要调试代码
        'alert(',           # 不要弹窗
        'document.',        # 不要操作DOM
        'window.',          # 不要操作window
        'eval(',            # 不要eval
        'setTimeout',       # 不要用setTimeout（用ctx.time）
        'setInterval',      # 不要用setInterval
        'fetch(',           # 不要网络请求
        'XMLHttpRequest',   # 不要网络请求
        'localStorage',     # 不要本地存储
        'sessionStorage',   # 不要会话存储
        'debugger',         # 不要调试语句
        'throw ',           # 不要抛出异常
    ])

    # === 简陋图形禁止项 ===
    forbidden_simple_representations: List[str] = field(default_factory=lambda: [
        '单个圆形代表人物',
        '单个矩形代表建筑',
        '单个圆形代表动物',
        '单个矩形代表车辆',
        '纯色背景无装饰',
        '无标签的图形',
        '无动画的静态图',
    ])


@dataclass
class ChapterQualityStandards:
    """章节质量标准 - 专业级高标准 (2026-02-06 全面升级版)"""

    # === 内容标准（严格）===
    min_steps: int = 7                          # 最少步骤数（提高到7）
    max_steps: int = 12                         # 最多步骤数（提高到12）
    min_text_length: int = 200                  # 每步最少字数（提高到200）
    min_key_points: int = 4                     # 每步最少要点数（提高到4）
    min_total_words: int = 1500                 # 整章最少字数（提高到1500）
    min_step_title_length: int = 5              # 步骤标题最少字数（新增）
    max_step_title_length: int = 25             # 步骤标题最多字数（新增）

    # === 结构标准（强化）===
    must_have_text_content: bool = True         # 必须有文本内容
    must_have_simulator: bool = True            # 必须有模拟器（核心章节）
    must_have_assessment: bool = True           # 测评必须有（必须）
    must_have_illustrated: bool = True          # 必须有图文内容（必须）
    must_have_summary: bool = True              # 必须有总结步骤（新增）
    min_illustrated_steps: int = 2              # 最少图文步骤数（提高到2）
    min_assessment_questions: int = 3           # 最少测验题目数（提高到3）
    min_simulators_per_chapter: int = 1         # 每章最少模拟器数（新增）
    max_simulators_per_chapter: int = 2         # 每章最多模拟器数（新增）

    # === 教学质量标准（新增）===
    must_have_learning_objectives: bool = True  # 必须有学习目标
    min_learning_objectives: int = 3            # 最少学习目标数
    must_have_rationale: bool = True            # 必须有设计理念
    min_rationale_length: int = 50              # 设计理念最少字数

    # === 图文内容标准（新增）===
    min_diagram_description: int = 80           # 图片描述最少字数
    must_have_diagram_elements: bool = True     # 必须有图片元素列表
    min_diagram_elements: int = 3               # 最少图片元素数

    # === 模拟器标准 ===
    simulator_standards: SimulatorQualityStandards = field(
        default_factory=SimulatorQualityStandards
    )

    # === 禁止项（扩展）===
    forbidden_content: List[str] = field(default_factory=lambda: [
        '待补充',
        '此处省略',
        '...',
        '等等',
        'TODO',
        'FIXME',
        '暂无',
        '略',
        '以此类推',
        '详见',
        '参考资料',
        '请参考',
        '如上所述',
        '不再赘述',
        '见上文',
        '同上',
        '此处略过',
        '篇幅有限',
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
        if hasattr(standards, 'max_code_lines') and code_lines > standards.max_code_lines:
            issues.append(f"代码过长，有{code_lines}行，最多{standards.max_code_lines}行")

        # 检查必要函数
        if standards.must_have_setup and 'function setup' not in self.custom_code:
            issues.append("缺少 setup 函数")
        if standards.must_have_update and 'function update' not in self.custom_code:
            issues.append("缺少 update 函数")

        # 检查自定义函数数量（新增）
        if hasattr(standards, 'min_functions'):
            function_count = self.custom_code.count('function ') - 2  # 减去 setup 和 update
            if function_count < standards.min_functions:
                issues.append(f"自定义函数太少，只有{max(0, function_count)}个，建议至少{standards.min_functions}个辅助函数")

        # 检查变量使用
        if standards.must_use_variables:
            if 'ctx.getVar' not in self.custom_code:
                issues.append("没有使用变量（ctx.getVar），模拟器无法与滑块联动")

        # 检查变量数量
        if len(self.variables) < standards.min_variables:
            issues.append(f"变量太少，只有{len(self.variables)}个，至少需要{standards.min_variables}个")
        if len(self.variables) > standards.max_variables:
            issues.append(f"变量太多，有{len(self.variables)}个，最多{standards.max_variables}个")

        # 检查视觉元素类型
        visual_methods = ['createCircle', 'createRect', 'createText', 'createLine', 'createCurve', 'createPolygon', 'createArc', 'createPath']
        visual_count = sum(1 for m in visual_methods if m in self.custom_code)
        if visual_count < standards.min_visual_elements:
            issues.append(f"视觉元素类型太少，只用了{visual_count}种，至少需要{standards.min_visual_elements}种")

        # 检查图形总数（新增）
        if hasattr(standards, 'min_total_shapes'):
            total_shapes = sum(self.custom_code.count(m) for m in visual_methods)
            if total_shapes < standards.min_total_shapes:
                issues.append(f"图形总数太少，只有{total_shapes}个，至少需要{standards.min_total_shapes}个图形元素")

        # 检查颜色使用（新增）
        if hasattr(standards, 'min_colors_used'):
            import re
            color_pattern = r"#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|rgb\([^)]+\)|rgba\([^)]+\)"
            colors_found = set(re.findall(color_pattern, self.custom_code))
            if len(colors_found) < standards.min_colors_used:
                issues.append(f"颜色使用太少，只用了{len(colors_found)}种颜色，至少需要{standards.min_colors_used}种")

        # 检查动画
        if standards.must_have_animation:
            animation_indicators = ['ctx.time', 'ctx.math.sin', 'ctx.math.cos', 'setPosition', 'setRotation', 'setScale', 'math.lerp']
            has_animation = any(ind in self.custom_code for ind in animation_indicators)
            if not has_animation:
                issues.append("没有动画效果，模拟器应该有动态变化（使用 ctx.time 或 math 函数）")

        # 检查标签
        if standards.must_have_labels:
            if 'createText' not in self.custom_code:
                issues.append("没有文字标签，用户无法理解模拟器展示的内容")

        # 检查标题（新增）
        if hasattr(standards, 'must_have_title') and standards.must_have_title:
            # 检查是否有大字号的标题文本
            if self.custom_code.count('createText') < 2:
                issues.append("缺少标题，模拟器应该有明显的标题说明")

        # 检查背景装饰（新增）
        if hasattr(standards, 'must_have_background') and standards.must_have_background:
            background_indicators = ['for (let', 'for(let', 'grid', 'background', '网格']
            has_background = any(ind in self.custom_code.lower() for ind in background_indicators)
            if not has_background and self.custom_code.count('createLine') < 5:
                issues.append("缺少背景装饰（如网格线、刻度线等），视觉效果单调")

        # 检查状态面板（新增）
        if hasattr(standards, 'must_have_state_panel') and standards.must_have_state_panel:
            panel_indicators = ['Label', 'status', 'panel', '状态', '数据', 'setText']
            has_panel = any(ind in self.custom_code for ind in panel_indicators)
            if not has_panel:
                issues.append("缺少状态/数据显示面板，用户无法看到实时数值变化")

        # 检查注释数量（新增）
        if hasattr(standards, 'min_comments') and standards.min_comments > 0:
            comment_count = self.custom_code.count('//') + self.custom_code.count('/*')
            if comment_count < standards.min_comments:
                issues.append(f"注释太少，只有{comment_count}处，至少需要{standards.min_comments}处注释说明")

        # 检查文字元素数量（新增）
        if hasattr(standards, 'min_text_elements') and standards.min_text_elements > 0:
            text_count = self.custom_code.count('createText')
            if text_count < standards.min_text_elements:
                issues.append(f"文字元素太少，只有{text_count}个，至少需要{standards.min_text_elements}个文字标签")

        # 检查坐标轴/刻度（新增）
        if hasattr(standards, 'must_have_axis') and standards.must_have_axis:
            axis_indicators = ['axis', '坐标', '刻度', 'scale', 'tick', 'grid', 'for (let', 'for(let']
            has_axis = any(ind in self.custom_code.lower() for ind in axis_indicators)
            if not has_axis and self.custom_code.count('createLine') < 8:
                issues.append("缺少坐标轴或刻度线，建议添加网格或刻度增强可读性")

        # 检查提示信息（新增）
        if hasattr(standards, 'must_have_tooltip') and standards.must_have_tooltip:
            tooltip_indicators = ['tooltip', 'hint', '提示', 'info', 'setText', 'Label']
            has_tooltip = any(ind in self.custom_code for ind in tooltip_indicators)
            if not has_tooltip:
                issues.append("缺少提示信息或动态文字更新，建议添加实时数据显示")

        # 检查动画类型数量（新增）
        if hasattr(standards, 'min_animation_types') and standards.min_animation_types > 0:
            animation_types = {
                'position': any(x in self.custom_code for x in ['setPosition', 'wolf.x', 'prey.x', '.x =', '.y =']),
                'rotation': 'setRotation' in self.custom_code or 'rotate' in self.custom_code.lower(),
                'scale': 'setScale' in self.custom_code or 'scale' in self.custom_code.lower(),
                'color': any(x in self.custom_code for x in ['setColor', 'barColor', 'color =']),
                'opacity': 'setOpacity' in self.custom_code or 'opacity' in self.custom_code.lower(),
                'time_based': 'ctx.time' in self.custom_code or 'math.sin' in self.custom_code.lower(),
            }
            animation_count = sum(1 for v in animation_types.values() if v)
            if animation_count < standards.min_animation_types:
                issues.append(f"动画类型太少，只有{animation_count}种，至少需要{standards.min_animation_types}种动画效果")

        # 检查层次感对象（新增）
        if hasattr(standards, 'must_have_layered_objects') and standards.must_have_layered_objects:
            # 检查是否有组合对象（多个图形组成一个对象）
            object_indicators = ['body', 'head', 'legs', 'tail', 'ears', 'eyes', 'arms', 'wheels']
            layered_count = sum(1 for ind in object_indicators if ind in self.custom_code.lower())
            if layered_count < 3:
                issues.append("缺少层次感的组合对象，主要元素应由多个图形组合而成（如身体、头部、四肢等）")

        # 检查进度/状态指示器（新增）
        if hasattr(standards, 'must_have_progress_indicator') and standards.must_have_progress_indicator:
            progress_indicators = ['bar', 'progress', 'energy', 'health', 'status', '进度', '状态', '能量']
            has_progress = any(ind in self.custom_code.lower() for ind in progress_indicators)
            if not has_progress:
                issues.append("缺少进度或状态指示器（如能量条、进度条等）")

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

    # JSON 解析错误信息（用于监督者指导修复）
    last_json_error: Optional[str] = None
    json_fix_guidance: Optional[str] = None

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
