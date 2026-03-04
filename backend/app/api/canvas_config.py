"""
画布配置API端点
版本: 1.0.0
创建日期: 2026-02-10
"""

from typing import Dict, Any
from app.services.course_generation.standards_loader import get_standards_loader


def get_canvas_config_for_frontend() -> Dict[str, Any]:
    """
    获取画布配置（供前端使用）

    Returns:
        画布配置字典，包含学生端和管理端配置
    """
    loader = get_standards_loader()
    canvas_config = loader.get_canvas_config()

    # 提取关键配置
    return {
        'version': canvas_config.get('version', '1.0.0'),
        'student': {
            'width': canvas_config['canvas_sizes']['student']['width'],
            'height': canvas_config['canvas_sizes']['student']['height'],
            'safeArea': {
                'xMin': canvas_config['safe_area_student']['x_min'],
                'xMax': canvas_config['safe_area_student']['x_max'],
                'yMin': canvas_config['safe_area_student']['y_min'],
                'yMax': canvas_config['safe_area_student']['y_max']
            },
            'mainContentArea': {
                'x': canvas_config['safe_area_student']['main_content_area']['x'],
                'y': canvas_config['safe_area_student']['main_content_area']['y']
            }
        },
        'admin': {
            'width': canvas_config['canvas_sizes']['admin']['width'],
            'height': canvas_config['canvas_sizes']['admin']['height'],
            'safeArea': {
                'xMin': canvas_config['safe_area_admin']['x_min'],
                'xMax': canvas_config['safe_area_admin']['x_max'],
                'yMin': canvas_config['safe_area_admin']['y_min'],
                'yMax': canvas_config['safe_area_admin']['y_max']
            },
            'mainContentArea': {
                'x': canvas_config['safe_area_admin']['main_content_area']['x'],
                'y': canvas_config['safe_area_admin']['main_content_area']['y']
            }
        },
        'responsivePrinciples': canvas_config.get('responsive_principles', []),
        'commonMistakes': canvas_config.get('common_mistakes', [])
    }


def get_subject_color_schemes_for_frontend() -> Dict[str, Any]:
    """
    获取学科配色方案（供前端使用）

    Returns:
        学科配色方案字典
    """
    loader = get_standards_loader()
    color_systems = loader.get_color_systems()

    schemes = {}
    for scheme in color_systems.get('subject_color_schemes', []):
        schemes[scheme['id']] = {
            'name': scheme['name'],
            'philosophy': scheme['philosophy'],
            'colors': {
                'primary': scheme['base_colors']['primary'],
                'primaryName': scheme['base_colors']['primary_name'],
                'secondary': scheme['base_colors']['secondary'],
                'secondaryName': scheme['base_colors']['secondary_name'],
                'accent': scheme['base_colors']['accent'],
                'accentName': scheme['base_colors']['accent_name'],
                'background': scheme['base_colors']['background'],
                'text': scheme['base_colors']['text'],
                'label': scheme['base_colors']['label']
            },
            'useCases': scheme.get('use_cases', {})
        }

    return {
        'version': color_systems.get('version', '1.0.0'),
        'schemes': schemes
    }


def get_visualization_elements_for_frontend() -> Dict[str, Any]:
    """
    获取可视化元素库（供前端使用）

    Returns:
        可视化元素字典
    """
    loader = get_standards_loader()
    viz_elements = loader.get_visualization_elements()

    elements = []
    for elem in viz_elements.get('visualization_elements', []):
        elements.append({
            'id': elem['id'],
            'name': elem['name'],
            'description': elem['description'],
            'apis': elem.get('apis', []),
            'useCases': elem.get('use_cases', []),
            'bestPractices': elem.get('best_practices', [])
        })

    return {
        'version': viz_elements.get('version', '1.0.0'),
        'elements': elements,
        'recommendedCombinations': viz_elements.get('recommended_combinations', [])
    }


def get_interaction_types_for_frontend() -> Dict[str, Any]:
    """
    获取交互类型库（供前端使用）

    Returns:
        交互类型字典
    """
    loader = get_standards_loader()
    interaction_types = loader.get_interaction_types()

    types = []
    for itype in interaction_types.get('interaction_types', []):
        types.append({
            'id': itype['id'],
            'name': itype['name'],
            'description': itype['description'],
            'difficulty': itype.get('difficulty', 'medium'),
            'useCases': itype.get('use_cases', [])
        })

    return {
        'version': interaction_types.get('version', '1.0.0'),
        'types': types
    }


def get_animation_easing_for_frontend() -> Dict[str, Any]:
    """
    获取动画缓动函数（供前端使用）

    Returns:
        缓动函数字典
    """
    loader = get_standards_loader()
    easing = loader.get_animation_easing()

    functions = []
    for func in easing.get('easing_functions', []):
        functions.append({
            'id': func['id'],
            'name': func['name'],
            'formula': func['formula'],
            'description': func['description'],
            'useCases': func.get('use_cases', [])
        })

    return {
        'version': easing.get('version', '1.0.0'),
        'functions': functions
    }


def export_all_standards_for_frontend() -> Dict[str, Any]:
    """
    导出所有标准配置（供前端一次性加载）

    Returns:
        包含所有标准的字典
    """
    return {
        'canvas': get_canvas_config_for_frontend(),
        'colors': get_subject_color_schemes_for_frontend(),
        'visualization': get_visualization_elements_for_frontend(),
        'interactions': get_interaction_types_for_frontend(),
        'animations': get_animation_easing_for_frontend()
    }
