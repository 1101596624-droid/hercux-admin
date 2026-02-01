# ============================================
# analysis.py - HERCU Studio 内容分析模型
# ============================================

from dataclasses import dataclass, field
from typing import List
from .enums import ComplexityLevel


@dataclass
class ContentAnalysis:
    """内容特性分析结果 - 用于决定教学形式"""
    has_dynamic_process: bool = False       # 需要看到动态过程
    is_physical_action: bool = False        # 是身体动作/操作技能
    has_structural_relationship: bool = False  # 有结构/层级/因果关系
    requires_hands_on_practice: bool = False   # 需要动手实践
    has_parameter_feedback_loop: bool = False  # 有参数调整→结果反馈循环
    has_common_misconceptions: bool = False    # 有常见误区
    needs_personalized_guidance: bool = False  # 需要个性化引导
    is_gateway_to_next: bool = False           # 是进入下一课的关卡
    complexity_level: ComplexityLevel = ComplexityLevel.STANDARD
    recommended_forms: List[str] = field(default_factory=list)
    rationale: str = ""
