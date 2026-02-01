"""
SDL 场景模板库
高质量预设模板，用于课程生成时选择
"""

from .sports_templates import SPORTS_TEMPLATES
from .physics_templates import PHYSICS_TEMPLATES
from .interactive_templates import INTERACTIVE_TEMPLATES

# 所有模板
ALL_TEMPLATES = {
    **SPORTS_TEMPLATES,
    **PHYSICS_TEMPLATES,
    **INTERACTIVE_TEMPLATES,
}

def get_template(template_id: str) -> dict:
    """获取模板"""
    return ALL_TEMPLATES.get(template_id)

def get_template_by_category(category: str) -> list:
    """按分类获取模板"""
    if category == "sports":
        return list(SPORTS_TEMPLATES.values())
    elif category == "physics":
        return list(PHYSICS_TEMPLATES.values())
    elif category == "interactive":
        return list(INTERACTIVE_TEMPLATES.values())
    return []

def list_templates() -> list:
    """列出所有模板"""
    return [
        {"id": k, "name": v["name"], "description": v["description"], "category": v.get("metadata", {}).get("category", "general")}
        for k, v in ALL_TEMPLATES.items()
    ]
