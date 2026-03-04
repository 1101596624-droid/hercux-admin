"""
课程生成数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import re


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
class HTMLSimulatorQualityStandards:
    """HTML模拟器质量标准 (2026-02-11)

    HTML格式模拟器使用标准Canvas 2D API，不再使用ctx.createCircle等专有API
    基础模板75分，优质模板85-95分
    """

    # === 代码质量标准 ===
    min_code_lines: int = 100                   # 最少代码行数（HTML格式较长）
    # max_code_lines 已移除 - 不限制代码上限,鼓励生成丰富内容
    must_have_html_structure: bool = True       # 必须有完整HTML结构
    must_have_doctype: bool = True              # 必须有 <!DOCTYPE html>
    must_have_canvas: bool = True               # 必须有 <canvas> 元素
    must_have_style: bool = True                # 必须有 <style> 标签
    must_have_script: bool = True               # 必须有 <script> 标签
    must_use_variables: bool = True             # 必须使用变量
    min_variables: int = 2                      # 最少变量数量
    max_variables: int = 4                      # 最多变量数量
    min_comments: int = 5                       # 最少注释行数

    # === Canvas API 使用标准 ===
    min_canvas_api_calls: int = 30              # 最少Canvas API调用数（ctx.）
    must_use_animation_frame: bool = True       # 必须使用 requestAnimationFrame
    recommended_canvas_apis: List[str] = field(default_factory=lambda: [
        'ctx.fillRect',
        'ctx.strokeRect',
        'ctx.arc',
        'ctx.beginPath',
        'ctx.lineTo',
        'ctx.fill',
        'ctx.stroke',
        'ctx.fillText',
        'ctx.save',
        'ctx.restore',
    ])

    # === 视觉质量标准 ===
    min_colors_used: int = 5                    # 最少使用颜色数量
    must_have_title: bool = True                # 必须有标题
    must_have_labels: bool = True               # 必须有文字标签
    must_have_data_display: bool = True         # 必须有数据显示
    must_have_animation: bool = True            # 必须有动画效果
    recommended_colors: List[str] = field(default_factory=lambda: [
        '#3B82F6', '#60A5FA', '#93C5FD',       # 蓝色系
        '#8B5CF6', '#A78BFA', '#C4B5FD',       # 紫色系
        '#F59E0B', '#FBBF24', '#FCD34D',       # 橙黄系
        '#10B981', '#34D399', '#6EE7B7',       # 绿色系
        '#EF4444', '#F87171', '#FCA5A5',       # 红色系
        '#F1F5F9', '#E2E8F0', '#CBD5E1',       # 文本色
    ])

    # === HTML控件标准 ===
    min_input_controls: int = 2                 # 最少input range控件数量
    must_show_control_values: bool = True       # 必须显示控件当前值
    must_have_event_listeners: bool = True      # 必须有事件监听器

    # === 交互质量标准 ===
    variable_must_affect_visual: bool = True    # 变量必须影响视觉效果
    must_show_real_time_values: bool = True     # 必须实时显示数值
    smooth_animation: bool = True               # 动画必须流畅

    # === 教学质量标准 ===
    must_demonstrate_concept: bool = True       # 必须演示核心概念
    must_have_clear_cause_effect: bool = True   # 必须有清晰的因果关系
    variables_must_be_meaningful: bool = True   # 变量必须有实际意义
    must_have_visual_feedback: bool = True      # 变量变化必须有视觉反馈

    # === 禁止项 ===
    forbidden_patterns: List[str] = field(default_factory=lambda: [
        'eval(',
        'Function(',
        'console.log',
        'alert(',
        'confirm(',
        'prompt(',
        'setTimeout',
        'setInterval',
        'fetch(',
        'XMLHttpRequest',
        'localStorage',
        'sessionStorage',
        'debugger',
        'document.write',
        'innerHTML',
        'outerHTML',
    ])

    # === 质量评分权重 ===
    score_weights: Dict[str, int] = field(default_factory=lambda: {
        'structure': 20,        # HTML结构完整性
        'canvas_usage': 25,     # Canvas API使用质量
        'visual_quality': 20,   # 视觉效果质量
        'interactivity': 20,    # 交互性
        'education': 15,        # 教学价值
    })


@dataclass
class ChapterQualityStandards:
    """章节质量标准 - 专业级高标准 (2026-02-06 全面升级版)"""

    # === 内容标准（严格）===
    # 步骤数量不设硬编码限制，由AI监督者根据章节内容和课程风格决定
    min_text_length: int = 200                  # 每步最少字数（提高到200）
    min_key_points: int = 4                     # 每步最少要点数（提高到4）
    min_total_words: int = 1500                 # 整章最少字数（提高到1500）
    min_step_title_length: int = 5              # 步骤标题最少字数（新增）
    max_step_title_length: int = 25             # 步骤标题最多字数（新增）

    # === 结构标准（强化）===
    must_have_text_content: bool = True         # 必须有文本内容
    # 模拟器和图文数量不设硬限制，由AI监督者根据内容需要决定
    # 但同一课程内的图片和模拟器必须有明显区别

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
    simulator_standards: HTMLSimulatorQualityStandards = field(
        default_factory=HTMLSimulatorQualityStandards
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
class HTMLSimulatorSpec:
    """HTML模拟器规格 (2026-02-11)"""
    name: str
    description: str
    html_content: str = ""
    mode: str = "html"

    def validate(self, standards: HTMLSimulatorQualityStandards) -> List[str]:
        """验证HTML模拟器是否符合质量标准，返回问题列表"""
        issues = []
        code = self.html_content

        # 检查HTML结构
        if standards.must_have_doctype and '<!DOCTYPE html>' not in code:
            issues.append("缺少 <!DOCTYPE html> 声明")

        if standards.must_have_html_structure:
            if '<html' not in code:
                issues.append("缺少 <html> 标签")
            if '<head>' not in code:
                issues.append("缺少 <head> 标签")
            if '<body>' not in code:
                issues.append("缺少 <body> 标签")

        if standards.must_have_canvas and '<canvas' not in code:
            issues.append("缺少 <canvas> 元素")

        if standards.must_have_style and '<style>' not in code:
            issues.append("缺少 <style> 标签")

        if standards.must_have_script and '<script>' not in code:
            issues.append("缺少 <script> 标签")

        # 检查代码行数
        code_lines = len([l for l in code.split('\n') if l.strip()])
        if code_lines < standards.min_code_lines:
            issues.append(f"代码太短，只有{code_lines}行，至少需要{standards.min_code_lines}行")
        # 不再检查代码上限 - 鼓励生成丰富内容

        # 检查Canvas API使用
        canvas_api_count = code.count('ctx.')
        if canvas_api_count < standards.min_canvas_api_calls:
            issues.append(f"Canvas API调用太少，只有{canvas_api_count}处，至少需要{standards.min_canvas_api_calls}处")

        # 检查动画
        if standards.must_use_animation_frame and 'requestAnimationFrame' not in code:
            issues.append("没有使用 requestAnimationFrame 实现动画循环")

        # 检查变量
        if standards.must_use_variables:
            if 'variables' not in code and 'let ' not in code:
                issues.append("没有定义变量")

        # 检查HTML控件
        input_count = code.count('<input type="range"')
        if input_count < standards.min_input_controls:
            issues.append(f"input range控件太少，只有{input_count}个，至少需要{standards.min_input_controls}个")

        if standards.must_have_event_listeners:
            if 'addEventListener' not in code:
                issues.append("没有事件监听器，控件无法响应用户操作")

        # 检查视觉元素
        if standards.must_have_labels:
            if 'fillText' not in code and 'strokeText' not in code:
                issues.append("没有文字标签，用户无法理解模拟器展示的内容")

        # 检查颜色使用
        color_pattern = r"#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|rgb\([^)]+\)|rgba\([^)]+\)"
        colors_found = set(re.findall(color_pattern, code))
        if len(colors_found) < standards.min_colors_used:
            issues.append(f"颜色使用太少，只用了{len(colors_found)}种颜色，至少需要{standards.min_colors_used}种")

        # 检查禁止项
        for pattern in standards.forbidden_patterns:
            if pattern in code:
                issues.append(f"代码中包含禁止使用的模式：{pattern}")

        return issues

    def calculate_quality_score(self, standards: HTMLSimulatorQualityStandards = None) -> 'HTMLSimulatorQualityScore':
        """
        计算HTML模拟器质量评分 (0-100)

        评分维度:
        - 结构分 (0-20): HTML结构完整性
        - Canvas使用分 (0-25): Canvas API调用质量
        - 视觉分 (0-20): 颜色、标签、数据显示
        - 交互分 (0-20): 变量控件、事件监听
        - 教学分 (0-15): 概念演示、注释

        75分标准: 24个基础模板

        ⚠️ 必要元素检查：缺少任何必要元素直接判0分
        """
        if standards is None:
            standards = HTMLSimulatorQualityStandards()

        score = HTMLSimulatorQualityScore()
        code = self.html_content
        lines = code.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]

        # ========== 必要元素检查 (2026-02-15) ==========
        # 缺少任何必要元素直接判0分，强制重做
        required_elements = {
            'DOCTYPE声明': '<!DOCTYPE html>' in code.upper(),
            'html标签': '<html' in code.lower(),
            'head标签': '<head>' in code.lower(),
            'body标签': '<body>' in code.lower(),
            'canvas标签': '<canvas' in code.lower(),
            'script标签': '<script>' in code.lower(),
        }

        missing_elements = [name for name, exists in required_elements.items() if not exists]

        if missing_elements:
            # 缺少必要元素，直接判0分
            score.structure_score = 0
            score.canvas_score = 0
            score.visual_quality_score = 0
            score.interaction_score = 0
            score.educational_value_score = 0
            score.total_score = 0
            score.passed = False
            score.issues.append(f"❌ 致命错误：缺少必要元素 {', '.join(missing_elements)}")
            score.issues.append("⚠️ 必要元素缺失导致结构不完整，必须重新生成")
            return score

        # ========== 结构分 (0-20) ==========
        structure = 0
        structure_details = {}

        # 1. DOCTYPE (3分)
        has_doctype = '<!DOCTYPE html>' in code
        structure += 3 if has_doctype else 0
        structure_details['has_doctype'] = has_doctype

        # 2. 完整HTML结构 (8分)
        has_html = '<html' in code
        has_head = '<head>' in code
        has_body = '<body>' in code
        has_canvas = '<canvas' in code
        structure += 2 if has_html else 0
        structure += 2 if has_head else 0
        structure += 2 if has_body else 0
        structure += 2 if has_canvas else 0
        structure_details['html_structure'] = {
            'html': has_html, 'head': has_head,
            'body': has_body, 'canvas': has_canvas
        }

        # 3. 必要标签 (6分)
        has_style = '<style>' in code
        has_script = '<script>' in code
        has_controls = '<input type="range"' in code
        structure += 2 if has_style else 0
        structure += 2 if has_script else 0
        structure += 2 if has_controls else 0
        structure_details['required_tags'] = {
            'style': has_style, 'script': has_script, 'controls': has_controls
        }

        # 4. 代码行数 (3分): 最少100行,不限上限
        line_count = len(non_empty_lines)
        if line_count >= standards.min_code_lines:
            structure += 3  # 满足最低要求即得满分
        structure_details['line_count'] = line_count

        score.structure_score = min(20, structure)

        # ========== Canvas使用分 (0-25) ==========
        canvas = 0
        canvas_details = {}

        # 1. Canvas API调用数量 (10分)
        canvas_api_count = code.count('ctx.')
        if canvas_api_count >= 100:
            canvas += 10
        elif canvas_api_count >= 60:
            canvas += 8
        elif canvas_api_count >= 30:
            canvas += 6
        else:
            canvas += max(0, canvas_api_count // 5)
        canvas_details['api_call_count'] = canvas_api_count

        # 2. 动画实现 (8分)
        has_animate_function = 'function animate' in code or 'function draw' in code
        has_request_frame = 'requestAnimationFrame' in code
        uses_time_based = 'Date.now()' in code or 'performance.now()' in code or 'time' in code.lower()
        canvas += 3 if has_animate_function else 0
        canvas += 3 if has_request_frame else 0
        canvas += 2 if uses_time_based else 0
        canvas_details['animation'] = {
            'animate_function': has_animate_function,
            'request_frame': has_request_frame,
            'time_based': uses_time_based
        }

        # 3. Canvas API多样性 (7分)
        canvas_apis = ['fillRect', 'strokeRect', 'arc', 'beginPath', 'lineTo',
                       'fill', 'stroke', 'fillText', 'save', 'restore']
        apis_used = sum(1 for api in canvas_apis if api in code)
        canvas += min(7, apis_used)
        canvas_details['api_diversity'] = apis_used

        score.canvas_score = min(25, canvas)

        # ========== 视觉分 (0-20) ==========
        visual = 0
        visual_details = {}

        # 1. 颜色使用与配色协调性 (7分)
        color_pattern = r"#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|rgb\([^)]+\)|rgba\([^)]+\)"
        colors_found = set(re.findall(color_pattern, code))
        color_count = len(colors_found)

        # 解析颜色为RGB值
        def parse_color_to_rgb(color_str):
            """解析颜色字符串为RGB元组 (0-255)"""
            if color_str.startswith('#'):
                hex_color = color_str[1:]
                if len(hex_color) == 3:
                    hex_color = ''.join([c*2 for c in hex_color])
                if len(hex_color) == 6:
                    try:
                        return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))
                    except:
                        return None
            elif color_str.startswith('rgb'):
                try:
                    nums = re.findall(r'\d+', color_str)
                    if len(nums) >= 3:
                        return (int(nums[0]), int(nums[1]), int(nums[2]))
                except:
                    return None
            return None

        # 分析配色协调性
        high_saturation_count = 0  # 高饱和度颜色数量
        brightness_variance = []   # 亮度方差

        for color in colors_found:
            rgb = parse_color_to_rgb(color)
            if rgb:
                r, g, b = rgb
                # 计算亮度 (0-1)
                luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                brightness_variance.append(luminance)

                # 检测饱和度
                max_rgb = max(r, g, b)
                min_rgb = min(r, g, b)
                saturation = (max_rgb - min_rgb) / max_rgb if max_rgb > 0 else 0

                # 统计高饱和度颜色 (饱和度>0.6)
                if saturation > 0.6:
                    high_saturation_count += 1

        # 配色协调性惩罚
        color_harmony_penalty = 0

        # 1) 过多高饱和度颜色 -> 刺眼 (最多扣8分)
        if high_saturation_count >= 5:
            color_harmony_penalty += 8
            visual_details['issue_high_saturation'] = f"{high_saturation_count}种高饱和度颜色严重过多"
        elif high_saturation_count >= 4:
            color_harmony_penalty += 5
            visual_details['issue_high_saturation'] = f"{high_saturation_count}种高饱和度颜色过多"
        elif high_saturation_count >= 3:
            color_harmony_penalty += 3

        # 2) 亮度差异过大 -> 对比刺眼 (最多扣7分)
        if len(brightness_variance) >= 3:
            import statistics
            variance = statistics.variance(brightness_variance)
            # 方差>0.2说明亮度差异非常大，严重刺眼
            if variance > 0.2:
                color_harmony_penalty += 7
                visual_details['issue_brightness_contrast'] = f"亮度对比严重过强(方差={variance:.2f})"
            # 方差>0.15说明亮度差异很大，可能刺眼
            elif variance > 0.15:
                color_harmony_penalty += 4
                visual_details['issue_brightness_contrast'] = f"亮度对比过强(方差={variance:.2f})"

        # 基础颜色数量分
        if color_count >= 8:
            visual += 7
        elif color_count >= 5:
            visual += 5
        else:
            visual += color_count

        # 应用配色协调性惩罚(最多扣15分)
        visual = max(0, visual - min(15, color_harmony_penalty))
        visual_details['colors_used'] = color_count
        visual_details['high_saturation_count'] = high_saturation_count
        visual_details['color_harmony_penalty'] = color_harmony_penalty

        # 2. 文字标签 (6分)
        has_filltext = 'fillText' in code
        has_title = 'title' in code.lower() or '<h1' in code or '<h2' in code
        filltext_count = code.count('fillText')
        visual += 3 if has_filltext else 0
        visual += 2 if has_title else 0
        visual += min(1, filltext_count // 5)
        visual_details['text_elements'] = {
            'has_filltext': has_filltext,
            'has_title': has_title,
            'filltext_count': filltext_count
        }

        # 3. 数据显示 (7分)
        has_value_display = 'value-display' in code or 'textContent' in code
        has_label_update = 'textContent' in code or 'innerText' in code
        value_display_count = code.count('textContent') + code.count('innerText')
        visual += 3 if has_value_display else 0
        visual += 2 if has_label_update else 0
        visual += min(2, value_display_count // 2)
        visual_details['data_display'] = {
            'has_value_display': has_value_display,
            'has_label_update': has_label_update,
            'update_count': value_display_count
        }

        score.visual_score = min(20, visual)

        # ========== 交互分 (0-20) ==========
        interaction = 0
        interaction_details = {}

        # 1. 变量控件 (6分) - 降低权重，为拖动/点击腾出空间
        input_count = code.count('<input type="range"')
        if input_count >= 3:
            interaction += 6
        elif input_count >= 2:
            interaction += 4
        else:
            interaction += input_count * 2
        interaction_details['input_controls'] = input_count

        # 2. 拖动交互 (7分) - 新增！至少需要2个拖动/点击交互
        # 检测鼠标事件
        has_mousedown = 'mousedown' in code.lower()
        has_mousemove = 'mousemove' in code.lower()
        has_mouseup = 'mouseup' in code.lower()
        has_click = 'click' in code.lower() or 'onclick' in code.lower()

        # 拖动交互 = mousedown + mousemove + mouseup
        has_drag_interaction = has_mousedown and has_mousemove and has_mouseup
        # 点击交互
        click_listener_count = code.count("addEventListener('click'") + code.count('addEventListener("click"')

        # 评分
        if has_drag_interaction:
            interaction += 4  # 拖动交互4分
            interaction_details['has_drag'] = True
        else:
            interaction_details['has_drag'] = False

        if click_listener_count >= 2:
            interaction += 3  # 2个以上点击3分
        elif click_listener_count >= 1:
            interaction += 2  # 1个点击2分

        interaction_details['click_count'] = click_listener_count
        interaction_details['mouse_events'] = {
            'mousedown': has_mousedown,
            'mousemove': has_mousemove,
            'mouseup': has_mouseup
        }

        # 3. 事件监听 (4分) - 降低权重
        listener_count = code.count('addEventListener')
        has_input_listener = 'addEventListener(\'input\'' in code
        if listener_count >= 4:
            interaction += 4
        elif listener_count >= 3:
            interaction += 3
        elif listener_count >= 2:
            interaction += 2
        else:
            interaction += listener_count
        interaction_details['event_listeners'] = {
            'listener_count': listener_count,
            'has_input_listener': has_input_listener
        }

        # 4. 实时更新与动画响应 (3分)
        updates_variables = 'variables.' in code or 'variables[' in code
        updates_display = 'textContent' in code
        has_animate_loop = 'function animate' in code and 'requestAnimationFrame' in code
        interaction += 1 if updates_variables else 0
        interaction += 1 if updates_display else 0
        interaction += 1 if has_animate_loop else 0
        interaction_details['real_time_update'] = {
            'updates_variables': updates_variables,
            'updates_display': updates_display,
            'animate_loop': has_animate_loop
        }

        score.interaction_score = min(20, interaction)

        # 交互不足严重惩罚(17分) - 至少需要2个拖动或点击交互
        interactive_element_count = (1 if has_drag_interaction else 0) + click_listener_count
        if interactive_element_count < 2:
            score.interaction_score = max(0, score.interaction_score - 17)
            interaction_details['interaction_penalty'] = 17
            interaction_details['interactive_elements'] = interactive_element_count
        # 交互过多惩罚(10分) - 最多4个交互，过多影响学习效果
        elif interactive_element_count > 4:
            score.interaction_score = max(0, score.interaction_score - 10)
            interaction_details['interaction_penalty'] = 10
            interaction_details['interactive_elements'] = interactive_element_count
            interaction_details['too_many_interactions'] = True

        # ========== 教学分 (0-15) ==========
        education = 0
        education_details = {}

        # 1. 注释说明 (6分)
        comment_count = code.count('//') + code.count('/*')
        if comment_count >= 10:
            education += 6
        elif comment_count >= 5:
            education += 4
        else:
            education += min(6, comment_count)
        education_details['comment_count'] = comment_count

        # 2. 概念演示 (5分)
        demonstrates_concept = any(word in code.lower() for word in
                                   ['物理', '数学', '化学', '生物', '算法', '公式', 'formula'])
        has_clear_visualization = 'arc' in code or 'lineTo' in code
        education += 3 if demonstrates_concept else 0
        education += 2 if has_clear_visualization else 0
        education_details['concept_demonstration'] = {
            'demonstrates_concept': demonstrates_concept,
            'has_visualization': has_clear_visualization
        }

        # 3. 变量命名 (4分)
        meaningful_var_names = sum(1 for var in ['velocity', 'acceleration', 'angle',
                                                   'radius', 'frequency', 'amplitude']
                                   if var in code.lower())
        education += min(4, meaningful_var_names)
        education_details['meaningful_vars'] = meaningful_var_names

        score.education_score = min(15, education)

        # ========== 汇总 ==========
        score.details = {
            'structure': structure_details,
            'canvas': canvas_details,
            'visual': visual_details,
            'interaction': interaction_details,
            'education': education_details,
        }

        # 收集问题
        if not has_doctype:
            score.issues.append("缺少 <!DOCTYPE html> 声明")
        if not has_canvas:
            score.issues.append("缺少 <canvas> 元素")
        if not has_request_frame:
            score.issues.append("未使用 requestAnimationFrame 实现动画")
        if input_count < 2:
            score.issues.append(f"input range控件太少 ({input_count}个)")
        if listener_count < 2:
            score.issues.append(f"事件监听器太少 ({listener_count}个)")
        if color_count < 5:
            score.issues.append(f"颜色使用太少 ({color_count}种)")

        # 配色协调性问题
        if high_saturation_count >= 3:
            score.issues.append(f"配色刺眼: {high_saturation_count}种高饱和度颜色过多，建议使用柔和色调")
        if 'issue_brightness_contrast' in visual_details:
            score.issues.append(f"配色刺眼: {visual_details['issue_brightness_contrast']}，建议降低亮度对比")

        # 交互性问题
        if not has_drag_interaction and click_listener_count < 2:
            score.issues.append(f"交互性不足: 缺少拖动交互或点击交互(至少需要2个)，当前拖动={has_drag_interaction}, 点击={click_listener_count}")
        elif not has_drag_interaction:
            score.issues.append("建议添加拖动交互: 使用mousedown/mousemove/mouseup实现可拖动元素")
        elif click_listener_count < 1:
            score.issues.append("建议添加点击交互: 使用click事件监听器")

        # 交互过多问题
        if interaction_details.get('too_many_interactions'):
            score.issues.append(f"交互过多: 当前{interactive_element_count}个交互，最多4个。过多交互会影响学习效果和用户体验")

        # 动画响应问题
        if (has_drag_interaction or click_listener_count > 0) and not has_animate_loop:
            score.issues.append("交互缺少动画响应: 有交互但未使用requestAnimationFrame实现动画反馈")

        score.calculate_total()
        return score


class SyntaxErrorType(Enum):
    """语法错误类型"""
    MISSING_FUNCTION = "missing_function"       # 缺少必要函数
    UNCLOSED_BRACKET = "unclosed_bracket"       # 未闭合括号
    MISMATCHED_BRACKET = "mismatched_bracket"   # 括号不匹配
    INVALID_API = "invalid_api"                 # 无效API调用
    RETURN_OUTSIDE_FUNCTION = "return_outside"  # return在函数外
    UNCLOSED_STRING = "unclosed_string"         # 未闭合字符串
    FORBIDDEN_PATTERN = "forbidden_pattern"     # 禁止的模式
    OUT_OF_BOUNDS = "out_of_bounds"             # 超出画布边界
    LOW_CONTRAST = "low_contrast"               # 颜色对比度不足
    DUPLICATE_DECLARATION = "duplicate_declaration"  # 重复变量声明
    CHINESE_PUNCTUATION = "chinese_punctuation"      # 代码中的中文标点


@dataclass
class CodeSyntaxError:
    """代码语法错误详情"""
    error_type: SyntaxErrorType
    message: str
    line_number: Optional[int] = None           # 错误行号（从1开始）
    column: Optional[int] = None                # 错误列号（从1开始）
    context_before: str = ""                    # 错误行前的上下文（2行）
    error_line: str = ""                        # 错误所在行
    context_after: str = ""                     # 错误行后的上下文（2行）
    suggestion: str = ""                        # 修复建议

    def format_report(self) -> str:
        """生成可读的错误报告"""
        report = [f"[{self.error_type.value}] {self.message}"]

        if self.line_number:
            report.append(f"位置: 第 {self.line_number} 行" + (f", 第 {self.column} 列" if self.column else ""))

        if self.context_before or self.error_line or self.context_after:
            report.append("\n代码上下文:")
            if self.context_before:
                for i, line in enumerate(self.context_before.split('\n')):
                    line_num = self.line_number - len(self.context_before.split('\n')) + i if self.line_number else '?'
                    report.append(f"  {line_num} | {line}")
            if self.error_line:
                report.append(f"→ {self.line_number or '?'} | {self.error_line}")
                if self.column:
                    # 添加指示箭头
                    pointer = " " * (len(str(self.line_number or '?')) + 3 + self.column - 1) + "^"
                    report.append(pointer)
            if self.context_after:
                for i, line in enumerate(self.context_after.split('\n')):
                    line_num = (self.line_number or 0) + i + 1
                    report.append(f"  {line_num} | {line}")

        if self.suggestion:
            report.append(f"\n建议: {self.suggestion}")

        return "\n".join(report)


@dataclass
class HTMLSimulatorQualityScore:
    """HTML模拟器质量评分 (2026-02-11)

    评分维度:
    - 结构分 (0-20): HTML结构完整性、Canvas元素、必要标签
    - Canvas使用分 (0-25): Canvas API调用质量、动画实现
    - 视觉分 (0-20): 颜色使用、标签文字、数据显示
    - 交互分 (0-20): 变量控件、事件监听、实时更新
    - 教学分 (0-15): 概念演示、因果关系、注释说明

    75分: 基础模板标准 (24个标准模板)
    85-95分: 优质模拟器
    """
    total_score: int = 0
    structure_score: int = 0        # HTML结构完整性 (0-20)
    canvas_score: int = 0           # Canvas API使用 (0-25)
    visual_score: int = 0           # 视觉效果质量 (0-20)
    interaction_score: int = 0      # 交互性 (0-20)
    education_score: int = 0        # 教学价值 (0-15)

    # 详细评分项
    details: Dict[str, Any] = field(default_factory=dict)

    # 问题列表
    issues: List[str] = field(default_factory=list)

    # 是否通过质量阈值
    passed: bool = False
    threshold: int = 74             # 质量阈值（监督者通过标准）

    def calculate_total(self):
        """计算总分"""
        self.total_score = (
            self.structure_score +
            self.canvas_score +
            self.visual_score +
            self.interaction_score +
            self.education_score
        )
        self.passed = self.total_score >= self.threshold

    def format_report(self) -> str:
        """生成评分报告"""
        status = "✓ 通过" if self.passed else "✗ 未通过"
        report = [
            f"HTML模拟器质量评分: {self.total_score}/100 ({status})",
            f"  结构分: {self.structure_score}/20 (HTML结构完整性)",
            f"  Canvas使用分: {self.canvas_score}/25 (Canvas API质量)",
            f"  视觉分: {self.visual_score}/20 (视觉效果)",
            f"  交互分: {self.interaction_score}/20 (交互性)",
            f"  教学分: {self.education_score}/15 (教学价值)",
        ]

        if self.issues:
            report.append("\n问题:")
            for issue in self.issues:
                report.append(f"  - {issue}")

        return "\n".join(report)


@dataclass
class ChapterStep:
    """章节步骤"""
    step_id: str
    type: str  # text_content, illustrated_content, simulator, ai_tutor, assessment
    title: str
    content: Optional[Dict[str, Any]] = None
    simulator_spec: Optional['HTMLSimulatorSpec'] = None  # 只支持HTML格式模拟器
    assessment_spec: Optional[Dict[str, Any]] = None
    diagram_spec: Optional[Dict[str, Any]] = None
    ai_spec: Optional[Dict[str, Any]] = None  # AI导师规格


@dataclass
class ChapterResult:
    """章节生成结果"""
    lesson_id: str
    title: str
    order: int
    total_steps: int
    rationale: str
    steps: List[ChapterStep]  # 统一使用steps字段（课程标准2026-02-13）
    estimated_minutes: int
    learning_objectives: List[str]
    complexity_level: str

    # 元数据
    generation_attempts: int = 1
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StepReviewResult:
    """单步审核结果"""
    step_index: int
    step_type: str
    status: ReviewStatus
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    score: int = 0

    def is_approved(self) -> bool:
        return self.status == ReviewStatus.APPROVED


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

    # 每个步骤的详细审核结果（用于单步重做）
    step_reviews: List[StepReviewResult] = field(default_factory=list)

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

    def get_step_issues(self, step_index: int) -> List[str]:
        """获取指定步骤的问题列表"""
        for sr in self.step_reviews:
            if sr.step_index == step_index:
                return sr.issues
        return []


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

    # 学科分类信息（新增）
    subject_classification: Optional[Dict[str, Any]] = None

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

    # 单步重做状态（新增）
    step_retry_counts: Dict[int, int] = field(default_factory=dict)  # {step_index: retry_count}
    max_step_retries: int = 2  # 单步最大重试次数

    # JSON 解析错误信息（用于监督者指导修复）
    last_json_error: Optional[str] = None
    json_fix_guidance: Optional[str] = None

    # 步骤重试错误信息（用于监督者给出针对性重试指导）
    last_step_error: Optional[str] = None
    step_fix_guidance: Optional[str] = None

    # 监督者对话状态
    supervisor_conversation_id: Optional[str] = None
    supervisor_context_compressed: bool = False

    # 时间戳
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_updated_at: datetime = field(default_factory=datetime.utcnow)

    def reset_step_retries(self):
        """重置单步重试计数（新章节时调用）"""
        self.step_retry_counts = {}

    def can_retry_step(self, step_index: int) -> bool:
        """检查指定步骤是否还能重试"""
        return self.step_retry_counts.get(step_index, 0) < self.max_step_retries

    def increment_step_retry(self, step_index: int):
        """增加指定步骤的重试次数"""
        self.step_retry_counts[step_index] = self.step_retry_counts.get(step_index, 0) + 1
        self.last_updated_at = datetime.utcnow()

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
            sim_count = sum(1 for s in ch.steps if s.type == 'simulator')
            lines.append(f"  - 第{ch.order + 1}章：{ch.title}（{ch.total_steps}步，{sim_count}个模拟器）")
        return "\n".join(lines)

    def add_completed_chapter(self, chapter: ChapterResult):
        """添加已完成的章节，同时更新已使用的模拟器和主题"""
        self.completed_chapters.append(chapter)
        self.covered_topics.append(chapter.title)

        # 提取模拟器
        for step in chapter.steps:
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
