# ============================================
# enums.py - HERCU Studio 枚举定义
# 基于 HERCU 课程包标准规范 v2.0
# ============================================

from enum import Enum


class TeachingFormType(str, Enum):
    """教学形式类型"""
    TEXT_CONTENT = "text_content"           # 文字内容
    ILLUSTRATED_CONTENT = "illustrated_content"  # 图文内容
    VIDEO = "video"                         # 视频
    SIMULATOR = "simulator"                 # 模拟器
    AI_TUTOR = "ai_tutor"                   # AI 导师
    ASSESSMENT = "assessment"               # 测验
    QUICK_CHECK = "quick_check"             # 快速检测
    PRACTICE = "practice"                   # 简单练习


class ComplexityLevel(str, Enum):
    """课时复杂度等级"""
    SIMPLE = "simple"           # 1-2 steps
    STANDARD = "standard"       # 3-4 steps
    RICH = "rich"               # 4-5 steps
    COMPREHENSIVE = "comprehensive"  # 5-6 steps


class DiagramType(str, Enum):
    """图表类型"""
    STATIC_DIAGRAM = "static_diagram"
    FLOWCHART = "flowchart"
    LINE_CHART = "line_chart"
    ANALYSIS_DIAGRAM = "analysis_diagram"
    PYRAMID = "pyramid"
    COMPARISON = "comparison"


class AssessmentType(str, Enum):
    """测验类型"""
    QUICK_CHECK = "quick_check"
    SCENARIO_QUIZ = "scenario_quiz"
    OPEN_ENDED = "open_ended"
    MULTIPLE_CHOICE = "multiple_choice"


class AITutorMode(str, Enum):
    """AI 导师模式"""
    PROACTIVE_ASSESSMENT = "proactive_assessment"  # 主动评估（苏格拉底式）
    REACTIVE_QA = "reactive_qa"                    # 被动问答
    GUIDED_PRACTICE = "guided_practice"            # 引导练习


class StepTrigger(str, Enum):
    """Step 触发条件"""
    DEFAULT = ""                            # 默认
    REQUIRED = "required"                   # 必须完成
    OPTIONAL_USER_REQUEST = "optional_user_request"  # 用户可选请求
    AUTO_AFTER_SIMULATOR = "auto_after_simulator"    # 模拟器后自动触发
