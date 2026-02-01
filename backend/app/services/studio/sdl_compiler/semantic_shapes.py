# -*- coding: utf-8 -*-
"""
语义形状库
将语义类型映射为具体的基础形状组合
支持关节动画系统
"""

from typing import Dict, List, Any


# 语义形状定义
SEMANTIC_SHAPES: Dict[str, Dict[str, Any]] = {
    # ==================== 人物类 ====================
    "swimmer": {
        "description": "游泳者（俯视，完整关节）",
        "parts": [
            # 头部
            {"id": "head", "type": "circle", "offset": {"x": 50, "y": 0}, "size": {"radius": 10}, "colorKey": "primary"},
            # 脊椎（上下两段）
            {"id": "spine_upper", "type": "ellipse", "offset": {"x": 20, "y": 0}, "size": {"radiusX": 20, "radiusY": 10}, "colorKey": "primary"},
            {"id": "spine_lower", "type": "ellipse", "offset": {"x": -15, "y": 0}, "size": {"radiusX": 18, "radiusY": 9}, "colorKey": "primary"},
            # 左臂（上臂+前臂）
            {"id": "upper_arm_left", "type": "ellipse", "offset": {"x": 25, "y": -15}, "size": {"radiusX": 12, "radiusY": 4}, "rotation": -15, "colorKey": "secondary"},
            {"id": "lower_arm_left", "type": "ellipse", "offset": {"x": 40, "y": -20}, "size": {"radiusX": 10, "radiusY": 3}, "rotation": -30, "colorKey": "secondary"},
            # 右臂（上臂+前臂）
            {"id": "upper_arm_right", "type": "ellipse", "offset": {"x": 25, "y": 15}, "size": {"radiusX": 12, "radiusY": 4}, "rotation": 15, "colorKey": "secondary"},
            {"id": "lower_arm_right", "type": "ellipse", "offset": {"x": 40, "y": 20}, "size": {"radiusX": 10, "radiusY": 3}, "rotation": 30, "colorKey": "secondary"},
            # 左腿（大腿+小腿）
            {"id": "upper_leg_left", "type": "ellipse", "offset": {"x": -35, "y": -8}, "size": {"radiusX": 12, "radiusY": 4}, "colorKey": "secondary"},
            {"id": "lower_leg_left", "type": "ellipse", "offset": {"x": -52, "y": -8}, "size": {"radiusX": 10, "radiusY": 3}, "colorKey": "secondary"},
            # 右腿（大腿+小腿）
            {"id": "upper_leg_right", "type": "ellipse", "offset": {"x": -35, "y": 8}, "size": {"radiusX": 12, "radiusY": 4}, "colorKey": "secondary"},
            {"id": "lower_leg_right", "type": "ellipse", "offset": {"x": -52, "y": 8}, "size": {"radiusX": 10, "radiusY": 3}, "colorKey": "secondary"}
        ],
        "joints": {
            # 脊椎关节
            "spine_upper": {"pivot": {"x": -18, "y": 0}, "range": {"min": -20, "max": 20}},
            "spine_lower": {"pivot": {"x": 15, "y": 0}, "range": {"min": -15, "max": 15}},
            # 肩关节
            "upper_arm_left": {"pivot": {"x": -10, "y": 0}, "range": {"min": -60, "max": 60}},
            "upper_arm_right": {"pivot": {"x": -10, "y": 0}, "range": {"min": -60, "max": 60}},
            # 肘关节
            "lower_arm_left": {"pivot": {"x": -8, "y": 0}, "range": {"min": -45, "max": 45}},
            "lower_arm_right": {"pivot": {"x": -8, "y": 0}, "range": {"min": -45, "max": 45}},
            # 髋关节
            "upper_leg_left": {"pivot": {"x": 10, "y": 0}, "range": {"min": -30, "max": 30}},
            "upper_leg_right": {"pivot": {"x": 10, "y": 0}, "range": {"min": -30, "max": 30}},
            # 膝关节
            "lower_leg_left": {"pivot": {"x": 8, "y": 0}, "range": {"min": -20, "max": 20}},
            "lower_leg_right": {"pivot": {"x": 8, "y": 0}, "range": {"min": -20, "max": 20}}
        },
        "defaultColors": {"primary": "#fbbf24", "secondary": "#f59e0b"}
    },

    "runner": {
        "description": "跑步者（侧视，完整关节）",
        "parts": [
            # 头部
            {"id": "head", "type": "circle", "offset": {"x": 0, "y": -55}, "size": {"radius": 11}, "colorKey": "primary"},
            # 脊椎（上下两段）
            {"id": "spine_upper", "type": "ellipse", "offset": {"x": 0, "y": -35}, "size": {"radiusX": 10, "radiusY": 14}, "colorKey": "primary"},
            {"id": "spine_lower", "type": "ellipse", "offset": {"x": 0, "y": -12}, "size": {"radiusX": 9, "radiusY": 10}, "colorKey": "primary"},
            # 前臂（上臂+前臂）
            {"id": "upper_arm_front", "type": "ellipse", "offset": {"x": 12, "y": -32}, "size": {"radiusX": 4, "radiusY": 11}, "rotation": -45, "colorKey": "secondary"},
            {"id": "lower_arm_front", "type": "ellipse", "offset": {"x": 20, "y": -20}, "size": {"radiusX": 3, "radiusY": 9}, "rotation": -90, "colorKey": "secondary"},
            # 后臂（上臂+前臂）
            {"id": "upper_arm_back", "type": "ellipse", "offset": {"x": -12, "y": -32}, "size": {"radiusX": 4, "radiusY": 11}, "rotation": 45, "colorKey": "secondary"},
            {"id": "lower_arm_back", "type": "ellipse", "offset": {"x": -20, "y": -20}, "size": {"radiusX": 3, "radiusY": 9}, "rotation": 90, "colorKey": "secondary"},
            # 前腿（大腿+小腿）
            {"id": "upper_leg_front", "type": "ellipse", "offset": {"x": 10, "y": 10}, "size": {"radiusX": 5, "radiusY": 14}, "rotation": -30, "colorKey": "secondary"},
            {"id": "lower_leg_front", "type": "ellipse", "offset": {"x": 15, "y": 35}, "size": {"radiusX": 4, "radiusY": 12}, "rotation": -10, "colorKey": "secondary"},
            # 后腿（大腿+小腿）
            {"id": "upper_leg_back", "type": "ellipse", "offset": {"x": -10, "y": 10}, "size": {"radiusX": 5, "radiusY": 14}, "rotation": 30, "colorKey": "secondary"},
            {"id": "lower_leg_back", "type": "ellipse", "offset": {"x": -15, "y": 35}, "size": {"radiusX": 4, "radiusY": 12}, "rotation": 60, "colorKey": "secondary"}
        ],
        "joints": {
            # 脊椎关节
            "spine_upper": {"pivot": {"x": 0, "y": 12}, "range": {"min": -25, "max": 25}},
            "spine_lower": {"pivot": {"x": 0, "y": 8}, "range": {"min": -15, "max": 15}},
            # 肩关节
            "upper_arm_front": {"pivot": {"x": 0, "y": -9}, "range": {"min": -90, "max": 45}},
            "upper_arm_back": {"pivot": {"x": 0, "y": -9}, "range": {"min": -45, "max": 90}},
            # 肘关节
            "lower_arm_front": {"pivot": {"x": 0, "y": -7}, "range": {"min": -120, "max": 0}},
            "lower_arm_back": {"pivot": {"x": 0, "y": -7}, "range": {"min": 0, "max": 120}},
            # 髋关节
            "upper_leg_front": {"pivot": {"x": 0, "y": -12}, "range": {"min": -60, "max": 30}},
            "upper_leg_back": {"pivot": {"x": 0, "y": -12}, "range": {"min": -30, "max": 60}},
            # 膝关节
            "lower_leg_front": {"pivot": {"x": 0, "y": -10}, "range": {"min": 0, "max": 130}},
            "lower_leg_back": {"pivot": {"x": 0, "y": -10}, "range": {"min": 0, "max": 130}}
        },
        "defaultColors": {"primary": "#3b82f6", "secondary": "#60a5fa"}
    },

    "jumper": {
        "description": "跳跃者（完整关节）",
        "parts": [
            # 头部
            {"id": "head", "type": "circle", "offset": {"x": 0, "y": -55}, "size": {"radius": 11}, "colorKey": "primary"},
            # 脊椎（上下两段）
            {"id": "spine_upper", "type": "ellipse", "offset": {"x": 0, "y": -35}, "size": {"radiusX": 10, "radiusY": 14}, "colorKey": "primary"},
            {"id": "spine_lower", "type": "ellipse", "offset": {"x": 0, "y": -12}, "size": {"radiusX": 9, "radiusY": 10}, "colorKey": "primary"},
            # 左臂（上臂+前臂）
            {"id": "upper_arm_left", "type": "ellipse", "offset": {"x": -16, "y": -32}, "size": {"radiusX": 4, "radiusY": 11}, "rotation": -60, "colorKey": "secondary"},
            {"id": "lower_arm_left", "type": "ellipse", "offset": {"x": -25, "y": -22}, "size": {"radiusX": 3, "radiusY": 9}, "rotation": -80, "colorKey": "secondary"},
            # 右臂（上臂+前臂）
            {"id": "upper_arm_right", "type": "ellipse", "offset": {"x": 16, "y": -32}, "size": {"radiusX": 4, "radiusY": 11}, "rotation": 60, "colorKey": "secondary"},
            {"id": "lower_arm_right", "type": "ellipse", "offset": {"x": 25, "y": -22}, "size": {"radiusX": 3, "radiusY": 9}, "rotation": 80, "colorKey": "secondary"},
            # 左腿（大腿+小腿）
            {"id": "upper_leg_left", "type": "ellipse", "offset": {"x": -7, "y": 10}, "size": {"radiusX": 5, "radiusY": 14}, "colorKey": "secondary"},
            {"id": "lower_leg_left", "type": "ellipse", "offset": {"x": -7, "y": 35}, "size": {"radiusX": 4, "radiusY": 12}, "colorKey": "secondary"},
            # 右腿（大腿+小腿）
            {"id": "upper_leg_right", "type": "ellipse", "offset": {"x": 7, "y": 10}, "size": {"radiusX": 5, "radiusY": 14}, "colorKey": "secondary"},
            {"id": "lower_leg_right", "type": "ellipse", "offset": {"x": 7, "y": 35}, "size": {"radiusX": 4, "radiusY": 12}, "colorKey": "secondary"}
        ],
        "joints": {
            # 脊椎关节
            "spine_upper": {"pivot": {"x": 0, "y": 12}, "range": {"min": -30, "max": 30}},
            "spine_lower": {"pivot": {"x": 0, "y": 8}, "range": {"min": -20, "max": 20}},
            # 肩关节
            "upper_arm_left": {"pivot": {"x": 0, "y": -9}, "range": {"min": -180, "max": 90}},
            "upper_arm_right": {"pivot": {"x": 0, "y": -9}, "range": {"min": -90, "max": 180}},
            # 肘关节
            "lower_arm_left": {"pivot": {"x": 0, "y": -7}, "range": {"min": -150, "max": 0}},
            "lower_arm_right": {"pivot": {"x": 0, "y": -7}, "range": {"min": 0, "max": 150}},
            # 髋关节
            "upper_leg_left": {"pivot": {"x": 0, "y": -12}, "range": {"min": -90, "max": 90}},
            "upper_leg_right": {"pivot": {"x": 0, "y": -12}, "range": {"min": -90, "max": 90}},
            # 膝关节
            "lower_leg_left": {"pivot": {"x": 0, "y": -10}, "range": {"min": 0, "max": 150}},
            "lower_leg_right": {"pivot": {"x": 0, "y": -10}, "range": {"min": 0, "max": 150}}
        },
        "defaultColors": {"primary": "#22c55e", "secondary": "#4ade80"}
    },

    "person": {
        "description": "站立人物（完整关节）",
        "parts": [
            # 头部
            {"id": "head", "type": "circle", "offset": {"x": 0, "y": -55}, "size": {"radius": 12}, "colorKey": "primary"},
            # 脊椎（上下两段）
            {"id": "spine_upper", "type": "ellipse", "offset": {"x": 0, "y": -35}, "size": {"radiusX": 12, "radiusY": 15}, "colorKey": "primary"},
            {"id": "spine_lower", "type": "ellipse", "offset": {"x": 0, "y": -10}, "size": {"radiusX": 10, "radiusY": 12}, "colorKey": "primary"},
            # 左臂（上臂+前臂）
            {"id": "upper_arm_left", "type": "ellipse", "offset": {"x": -18, "y": -30}, "size": {"radiusX": 4, "radiusY": 12}, "colorKey": "secondary"},
            {"id": "lower_arm_left", "type": "ellipse", "offset": {"x": -18, "y": -8}, "size": {"radiusX": 3, "radiusY": 10}, "colorKey": "secondary"},
            # 右臂（上臂+前臂）
            {"id": "upper_arm_right", "type": "ellipse", "offset": {"x": 18, "y": -30}, "size": {"radiusX": 4, "radiusY": 12}, "colorKey": "secondary"},
            {"id": "lower_arm_right", "type": "ellipse", "offset": {"x": 18, "y": -8}, "size": {"radiusX": 3, "radiusY": 10}, "colorKey": "secondary"},
            # 左腿（大腿+小腿）
            {"id": "upper_leg_left", "type": "ellipse", "offset": {"x": -7, "y": 15}, "size": {"radiusX": 5, "radiusY": 14}, "colorKey": "secondary"},
            {"id": "lower_leg_left", "type": "ellipse", "offset": {"x": -7, "y": 40}, "size": {"radiusX": 4, "radiusY": 12}, "colorKey": "secondary"},
            # 右腿（大腿+小腿）
            {"id": "upper_leg_right", "type": "ellipse", "offset": {"x": 7, "y": 15}, "size": {"radiusX": 5, "radiusY": 14}, "colorKey": "secondary"},
            {"id": "lower_leg_right", "type": "ellipse", "offset": {"x": 7, "y": 40}, "size": {"radiusX": 4, "radiusY": 12}, "colorKey": "secondary"}
        ],
        "joints": {
            # 脊椎关节
            "spine_upper": {"pivot": {"x": 0, "y": 12}, "range": {"min": -30, "max": 30}},
            "spine_lower": {"pivot": {"x": 0, "y": 10}, "range": {"min": -20, "max": 20}},
            # 肩关节（上臂）
            "upper_arm_left": {"pivot": {"x": 0, "y": -10}, "range": {"min": -180, "max": 180}},
            "upper_arm_right": {"pivot": {"x": 0, "y": -10}, "range": {"min": -180, "max": 180}},
            # 肘关节（前臂）
            "lower_arm_left": {"pivot": {"x": 0, "y": -8}, "range": {"min": -150, "max": 0}},
            "lower_arm_right": {"pivot": {"x": 0, "y": -8}, "range": {"min": 0, "max": 150}},
            # 髋关节（大腿）
            "upper_leg_left": {"pivot": {"x": 0, "y": -12}, "range": {"min": -90, "max": 90}},
            "upper_leg_right": {"pivot": {"x": 0, "y": -12}, "range": {"min": -90, "max": 90}},
            # 膝关节（小腿）
            "lower_leg_left": {"pivot": {"x": 0, "y": -10}, "range": {"min": 0, "max": 150}},
            "lower_leg_right": {"pivot": {"x": 0, "y": -10}, "range": {"min": 0, "max": 150}}
        },
        "defaultColors": {"primary": "#6366f1", "secondary": "#818cf8"}
    },

    # ==================== 带关节的运动员 ====================
    "gymnast": {
        "description": "体操运动员",
        "parts": [
            {"id": "body", "type": "ellipse", "offset": {"x": 0, "y": 0}, "size": {"radiusX": 10, "radiusY": 25}, "colorKey": "primary"},
            {"id": "head", "type": "circle", "offset": {"x": 0, "y": -35}, "size": {"radius": 10}, "colorKey": "primary"},
            {"id": "upper_arm_left", "type": "ellipse", "offset": {"x": -15, "y": -15}, "size": {"radiusX": 4, "radiusY": 12}, "rotation": -30, "colorKey": "secondary"},
            {"id": "lower_arm_left", "type": "ellipse", "offset": {"x": -22, "y": -5}, "size": {"radiusX": 3, "radiusY": 10}, "rotation": -60, "colorKey": "secondary"},
            {"id": "upper_arm_right", "type": "ellipse", "offset": {"x": 15, "y": -15}, "size": {"radiusX": 4, "radiusY": 12}, "rotation": 30, "colorKey": "secondary"},
            {"id": "lower_arm_right", "type": "ellipse", "offset": {"x": 22, "y": -5}, "size": {"radiusX": 3, "radiusY": 10}, "rotation": 60, "colorKey": "secondary"},
            {"id": "upper_leg_left", "type": "ellipse", "offset": {"x": -6, "y": 30}, "size": {"radiusX": 5, "radiusY": 15}, "colorKey": "secondary"},
            {"id": "lower_leg_left", "type": "ellipse", "offset": {"x": -6, "y": 52}, "size": {"radiusX": 4, "radiusY": 12}, "colorKey": "secondary"},
            {"id": "upper_leg_right", "type": "ellipse", "offset": {"x": 6, "y": 30}, "size": {"radiusX": 5, "radiusY": 15}, "colorKey": "secondary"},
            {"id": "lower_leg_right", "type": "ellipse", "offset": {"x": 6, "y": 52}, "size": {"radiusX": 4, "radiusY": 12}, "colorKey": "secondary"}
        ],
        "joints": {
            "upper_arm_left": {"pivot": {"x": 0, "y": -10}, "range": {"min": -180, "max": 180}},
            "lower_arm_left": {"pivot": {"x": 0, "y": -8}, "range": {"min": -150, "max": 0}},
            "upper_arm_right": {"pivot": {"x": 0, "y": -10}, "range": {"min": -180, "max": 180}},
            "lower_arm_right": {"pivot": {"x": 0, "y": -8}, "range": {"min": 0, "max": 150}},
            "upper_leg_left": {"pivot": {"x": 0, "y": -12}, "range": {"min": -90, "max": 90}},
            "lower_leg_left": {"pivot": {"x": 0, "y": -10}, "range": {"min": 0, "max": 150}},
            "upper_leg_right": {"pivot": {"x": 0, "y": -12}, "range": {"min": -90, "max": 90}},
            "lower_leg_right": {"pivot": {"x": 0, "y": -10}, "range": {"min": 0, "max": 150}}
        },
        "defaultColors": {"primary": "#ec4899", "secondary": "#f472b6"}
    },

    "diver": {
        "description": "跳水运动员",
        "parts": [
            {"id": "body", "type": "ellipse", "offset": {"x": 0, "y": 0}, "size": {"radiusX": 10, "radiusY": 22}, "colorKey": "primary"},
            {"id": "head", "type": "circle", "offset": {"x": 0, "y": -32}, "size": {"radius": 10}, "colorKey": "primary"},
            {"id": "arm_left", "type": "ellipse", "offset": {"x": -12, "y": -25}, "size": {"radiusX": 4, "radiusY": 18}, "rotation": -15, "colorKey": "secondary"},
            {"id": "arm_right", "type": "ellipse", "offset": {"x": 12, "y": -25}, "size": {"radiusX": 4, "radiusY": 18}, "rotation": 15, "colorKey": "secondary"},
            {"id": "leg_left", "type": "ellipse", "offset": {"x": -5, "y": 30}, "size": {"radiusX": 5, "radiusY": 20}, "colorKey": "secondary"},
            {"id": "leg_right", "type": "ellipse", "offset": {"x": 5, "y": 30}, "size": {"radiusX": 5, "radiusY": 20}, "colorKey": "secondary"}
        ],
        "joints": {
            "arm_left": {"pivot": {"x": 0, "y": -15}, "range": {"min": -180, "max": 180}},
            "arm_right": {"pivot": {"x": 0, "y": -15}, "range": {"min": -180, "max": 180}},
            "leg_left": {"pivot": {"x": 0, "y": -18}, "range": {"min": -90, "max": 90}},
            "leg_right": {"pivot": {"x": 0, "y": -18}, "range": {"min": -90, "max": 90}}
        },
        "defaultColors": {"primary": "#0ea5e9", "secondary": "#38bdf8"}
    },

    "kicker": {
        "description": "踢球者",
        "parts": [
            {"id": "body", "type": "ellipse", "offset": {"x": 0, "y": -5}, "size": {"radiusX": 12, "radiusY": 25}, "colorKey": "primary"},
            {"id": "head", "type": "circle", "offset": {"x": 0, "y": -40}, "size": {"radius": 11}, "colorKey": "primary"},
            {"id": "arm_left", "type": "ellipse", "offset": {"x": -18, "y": -10}, "size": {"radiusX": 4, "radiusY": 16}, "rotation": -20, "colorKey": "secondary"},
            {"id": "arm_right", "type": "ellipse", "offset": {"x": 18, "y": -10}, "size": {"radiusX": 4, "radiusY": 16}, "rotation": 20, "colorKey": "secondary"},
            {"id": "leg_stand", "type": "ellipse", "offset": {"x": -6, "y": 30}, "size": {"radiusX": 5, "radiusY": 22}, "colorKey": "secondary"},
            {"id": "leg_kick", "type": "ellipse", "offset": {"x": 15, "y": 20}, "size": {"radiusX": 5, "radiusY": 22}, "rotation": -45, "colorKey": "secondary"}
        ],
        "joints": {
            "arm_left": {"pivot": {"x": 0, "y": -14}, "range": {"min": -90, "max": 90}},
            "arm_right": {"pivot": {"x": 0, "y": -14}, "range": {"min": -90, "max": 90}},
            "leg_stand": {"pivot": {"x": 0, "y": -20}, "range": {"min": -20, "max": 20}},
            "leg_kick": {"pivot": {"x": 0, "y": -20}, "range": {"min": -120, "max": 60}}
        },
        "defaultColors": {"primary": "#22c55e", "secondary": "#4ade80"}
    },
    "ball": {
        "description": "通用球",
        "parts": [
            {"id": "ball", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 20}, "colorKey": "primary"}
        ],
        "defaultColors": {"primary": "#ef4444"}
    },

    "football": {
        "description": "足球",
        "parts": [
            {"id": "ball", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 22}, "colorKey": "primary"},
            {"id": "pattern1", "type": "polygon", "offset": {"x": 0, "y": 0}, "size": {"points": [{"x": 0, "y": -10}, {"x": 9, "y": -3}, {"x": 5, "y": 8}, {"x": -5, "y": 8}, {"x": -9, "y": -3}]}, "colorKey": "secondary"}
        ],
        "defaultColors": {"primary": "#ffffff", "secondary": "#1f2937"}
    },

    "basketball": {
        "description": "篮球",
        "parts": [
            {"id": "ball", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 24}, "colorKey": "primary"},
            {"id": "line_h", "type": "line", "offset": {"x": 0, "y": 0}, "size": {"points": [{"x": -24, "y": 0}, {"x": 24, "y": 0}]}, "colorKey": "secondary"},
            {"id": "line_v", "type": "line", "offset": {"x": 0, "y": 0}, "size": {"points": [{"x": 0, "y": -24}, {"x": 0, "y": 24}]}, "colorKey": "secondary"}
        ],
        "defaultColors": {"primary": "#f97316", "secondary": "#1f2937"}
    },

    "volleyball": {
        "description": "排球",
        "parts": [
            {"id": "ball", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 22}, "colorKey": "primary"}
        ],
        "defaultColors": {"primary": "#fef3c7"}
    },

    # ==================== 器械类 ====================
    "barbell": {
        "description": "杠铃",
        "parts": [
            {"id": "bar", "type": "rectangle", "offset": {"x": 0, "y": 0}, "size": {"width": 120, "height": 6}, "colorKey": "secondary"},
            {"id": "weight_left", "type": "rectangle", "offset": {"x": -50, "y": 0}, "size": {"width": 15, "height": 35}, "colorKey": "primary"},
            {"id": "weight_right", "type": "rectangle", "offset": {"x": 50, "y": 0}, "size": {"width": 15, "height": 35}, "colorKey": "primary"}
        ],
        "defaultColors": {"primary": "#374151", "secondary": "#9ca3af"}
    },

    "hurdle": {
        "description": "跨栏架",
        "parts": [
            {"id": "bar", "type": "rectangle", "offset": {"x": 0, "y": -20}, "size": {"width": 80, "height": 8}, "colorKey": "primary"},
            {"id": "leg_left", "type": "rectangle", "offset": {"x": -35, "y": 10}, "size": {"width": 6, "height": 50}, "colorKey": "secondary"},
            {"id": "leg_right", "type": "rectangle", "offset": {"x": 35, "y": 10}, "size": {"width": 6, "height": 50}, "colorKey": "secondary"}
        ],
        "defaultColors": {"primary": "#ef4444", "secondary": "#fbbf24"}
    },

    "diving_board": {
        "description": "跳板",
        "parts": [
            {"id": "board", "type": "rectangle", "offset": {"x": 0, "y": 0}, "size": {"width": 100, "height": 12}, "colorKey": "primary"},
            {"id": "support", "type": "rectangle", "offset": {"x": -40, "y": 20}, "size": {"width": 20, "height": 30}, "colorKey": "secondary"}
        ],
        "defaultColors": {"primary": "#60a5fa", "secondary": "#374151"}
    },

    "goal": {
        "description": "球门",
        "parts": [
            {"id": "top", "type": "rectangle", "offset": {"x": 0, "y": -40}, "size": {"width": 120, "height": 8}, "colorKey": "primary"},
            {"id": "left", "type": "rectangle", "offset": {"x": -56, "y": 0}, "size": {"width": 8, "height": 80}, "colorKey": "primary"},
            {"id": "right", "type": "rectangle", "offset": {"x": 56, "y": 0}, "size": {"width": 8, "height": 80}, "colorKey": "primary"}
        ],
        "defaultColors": {"primary": "#ffffff", "secondary": "#9ca3af"}
    },

    "basket": {
        "description": "篮筐",
        "parts": [
            {"id": "backboard", "type": "rectangle", "offset": {"x": 0, "y": -30}, "size": {"width": 60, "height": 40}, "colorKey": "secondary"},
            {"id": "rim", "type": "circle", "offset": {"x": 0, "y": 10}, "size": {"radius": 18}, "colorKey": "primary"}
        ],
        "defaultColors": {"primary": "#ef4444", "secondary": "#ffffff"}
    },

    # ==================== 轨迹类 ====================
    "arrow": {
        "description": "箭头",
        "parts": [
            {"id": "arrow", "type": "polygon", "offset": {"x": 0, "y": 0}, "size": {"points": [{"x": -30, "y": -8}, {"x": 10, "y": -8}, {"x": 10, "y": -16}, {"x": 30, "y": 0}, {"x": 10, "y": 16}, {"x": 10, "y": 8}, {"x": -30, "y": 8}]}, "colorKey": "primary"}
        ],
        "defaultColors": {"primary": "#22c55e"}
    },

    "trajectory": {
        "description": "运动轨迹线",
        "parts": [
            {"id": "line", "type": "line", "offset": {"x": 0, "y": 0}, "size": {"points": [{"x": -50, "y": 0}, {"x": 50, "y": 0}]}, "colorKey": "primary", "stroke": {"width": 3}}
        ],
        "defaultColors": {"primary": "#f59e0b"}
    },

    "arc_trajectory": {
        "description": "弧形轨迹",
        "parts": [
            {"id": "arc", "type": "polygon", "offset": {"x": 0, "y": 0}, "size": {"points": [{"x": -40, "y": 20}, {"x": -30, "y": 0}, {"x": -15, "y": -15}, {"x": 0, "y": -20}, {"x": 15, "y": -15}, {"x": 30, "y": 0}, {"x": 40, "y": 20}]}, "colorKey": "primary", "stroke": {"width": 3}, "noFill": True}
        ],
        "defaultColors": {"primary": "#8b5cf6"}
    },

    # ==================== 场地类 ====================
    "pool_lane": {
        "description": "泳道",
        "parts": [
            {"id": "lane", "type": "rectangle", "offset": {"x": 0, "y": 0}, "size": {"width": 600, "height": 60}, "colorKey": "primary"},
            {"id": "line_top", "type": "line", "offset": {"x": 0, "y": -30}, "size": {"points": [{"x": -300, "y": 0}, {"x": 300, "y": 0}]}, "colorKey": "secondary", "stroke": {"width": 2}},
            {"id": "line_bottom", "type": "line", "offset": {"x": 0, "y": 30}, "size": {"points": [{"x": -300, "y": 0}, {"x": 300, "y": 0}]}, "colorKey": "secondary", "stroke": {"width": 2}}
        ],
        "defaultColors": {"primary": "#0ea5e9", "secondary": "#ffffff"}
    },

    "track_lane": {
        "description": "跑道",
        "parts": [
            {"id": "lane", "type": "rectangle", "offset": {"x": 0, "y": 0}, "size": {"width": 500, "height": 40}, "colorKey": "primary"},
            {"id": "line", "type": "line", "offset": {"x": 0, "y": 0}, "size": {"points": [{"x": -250, "y": 0}, {"x": 250, "y": 0}]}, "colorKey": "secondary", "stroke": {"width": 2, "dash": [10, 5]}}
        ],
        "defaultColors": {"primary": "#dc2626", "secondary": "#ffffff"}
    },

    "water": {
        "description": "水面",
        "parts": [
            {"id": "water", "type": "rectangle", "offset": {"x": 0, "y": 0}, "size": {"width": 700, "height": 200}, "colorKey": "primary"}
        ],
        "defaultColors": {"primary": "#0369a1"}
    },

    # ==================== 标注类 ====================
    "label_box": {
        "description": "标签框",
        "parts": [
            {"id": "box", "type": "rectangle", "offset": {"x": 0, "y": 0}, "size": {"width": 80, "height": 30, "cornerRadius": 5}, "colorKey": "primary"}
        ],
        "defaultColors": {"primary": "#1f2937"}
    },

    "highlight_circle": {
        "description": "高亮圆圈",
        "parts": [
            {"id": "circle", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 30}, "colorKey": "primary", "stroke": {"width": 3}, "noFill": True}
        ],
        "defaultColors": {"primary": "#fbbf24"}
    },

    "marker": {
        "description": "标记点",
        "parts": [
            {"id": "outer", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 12}, "colorKey": "primary"},
            {"id": "inner", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 5}, "colorKey": "secondary"}
        ],
        "defaultColors": {"primary": "#ef4444", "secondary": "#ffffff"}
    },

    # ==================== 变量关系展示类 ====================
    "slider": {
        "description": "可拖动滑块（自变量控制器）",
        "interactive": True,
        "controlType": "slider",
        "parts": [
            # 滑轨背景
            {"id": "track_bg", "type": "rectangle", "offset": {"x": 0, "y": 0}, "size": {"width": 200, "height": 8, "cornerRadius": 4}, "colorKey": "track"},
            # 滑轨填充（显示当前值）
            {"id": "track_fill", "type": "rectangle", "offset": {"x": -50, "y": 0}, "size": {"width": 100, "height": 8, "cornerRadius": 4}, "colorKey": "primary"},
            # 滑块手柄
            {"id": "handle", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 14}, "colorKey": "handle"},
            {"id": "handle_inner", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 8}, "colorKey": "primary"}
        ],
        "defaultColors": {"primary": "#3b82f6", "track": "#e5e7eb", "handle": "#ffffff"},
        "config": {
            "min": 0,
            "max": 100,
            "step": 1,
            "defaultValue": 50,
            "width": 200
        }
    },

    "value_display": {
        "description": "数值显示框（因变量显示）",
        "parts": [
            # 背景框
            {"id": "bg", "type": "rectangle", "offset": {"x": 0, "y": 0}, "size": {"width": 120, "height": 50, "cornerRadius": 8}, "colorKey": "background"},
            # 标签区域
            {"id": "label_bg", "type": "rectangle", "offset": {"x": 0, "y": -12}, "size": {"width": 120, "height": 20, "cornerRadius": 0}, "colorKey": "primary"}
        ],
        "defaultColors": {"primary": "#3b82f6", "background": "#1f2937", "text": "#ffffff"},
        "config": {
            "label": "变量",
            "unit": "",
            "decimals": 2
        }
    },

    "axis_x": {
        "description": "X轴（水平坐��轴）",
        "parts": [
            # 主轴线
            {"id": "line", "type": "line", "offset": {"x": 0, "y": 0}, "size": {"points": [{"x": -200, "y": 0}, {"x": 200, "y": 0}]}, "colorKey": "primary", "stroke": {"width": 2}},
            # 箭头
            {"id": "arrow", "type": "polygon", "offset": {"x": 200, "y": 0}, "size": {"points": [{"x": 0, "y": -6}, {"x": 12, "y": 0}, {"x": 0, "y": 6}]}, "colorKey": "primary"},
            # 刻度线（5个）
            {"id": "tick1", "type": "line", "offset": {"x": -160, "y": 0}, "size": {"points": [{"x": 0, "y": -5}, {"x": 0, "y": 5}]}, "colorKey": "primary", "stroke": {"width": 1}},
            {"id": "tick2", "type": "line", "offset": {"x": -80, "y": 0}, "size": {"points": [{"x": 0, "y": -5}, {"x": 0, "y": 5}]}, "colorKey": "primary", "stroke": {"width": 1}},
            {"id": "tick3", "type": "line", "offset": {"x": 0, "y": 0}, "size": {"points": [{"x": 0, "y": -5}, {"x": 0, "y": 5}]}, "colorKey": "primary", "stroke": {"width": 1}},
            {"id": "tick4", "type": "line", "offset": {"x": 80, "y": 0}, "size": {"points": [{"x": 0, "y": -5}, {"x": 0, "y": 5}]}, "colorKey": "primary", "stroke": {"width": 1}},
            {"id": "tick5", "type": "line", "offset": {"x": 160, "y": 0}, "size": {"points": [{"x": 0, "y": -5}, {"x": 0, "y": 5}]}, "colorKey": "primary", "stroke": {"width": 1}}
        ],
        "defaultColors": {"primary": "#9ca3af"}
    },

    "axis_y": {
        "description": "Y轴（垂直坐标轴）",
        "parts": [
            # 主轴线
            {"id": "line", "type": "line", "offset": {"x": 0, "y": 0}, "size": {"points": [{"x": 0, "y": 150}, {"x": 0, "y": -150}]}, "colorKey": "primary", "stroke": {"width": 2}},
            # 箭头
            {"id": "arrow", "type": "polygon", "offset": {"x": 0, "y": -150}, "size": {"points": [{"x": -6, "y": 0}, {"x": 0, "y": -12}, {"x": 6, "y": 0}]}, "colorKey": "primary"},
            # 刻度线（5个）
            {"id": "tick1", "type": "line", "offset": {"x": 0, "y": 120}, "size": {"points": [{"x": -5, "y": 0}, {"x": 5, "y": 0}]}, "colorKey": "primary", "stroke": {"width": 1}},
            {"id": "tick2", "type": "line", "offset": {"x": 0, "y": 60}, "size": {"points": [{"x": -5, "y": 0}, {"x": 5, "y": 0}]}, "colorKey": "primary", "stroke": {"width": 1}},
            {"id": "tick3", "type": "line", "offset": {"x": 0, "y": 0}, "size": {"points": [{"x": -5, "y": 0}, {"x": 5, "y": 0}]}, "colorKey": "primary", "stroke": {"width": 1}},
            {"id": "tick4", "type": "line", "offset": {"x": 0, "y": -60}, "size": {"points": [{"x": -5, "y": 0}, {"x": 5, "y": 0}]}, "colorKey": "primary", "stroke": {"width": 1}},
            {"id": "tick5", "type": "line", "offset": {"x": 0, "y": -120}, "size": {"points": [{"x": -5, "y": 0}, {"x": 5, "y": 0}]}, "colorKey": "primary", "stroke": {"width": 1}}
        ],
        "defaultColors": {"primary": "#9ca3af"}
    },

    "vector_arrow": {
        "description": "向量箭头（带方向和大小）",
        "parts": [
            # 箭杆
            {"id": "shaft", "type": "rectangle", "offset": {"x": 0, "y": 0}, "size": {"width": 60, "height": 6, "cornerRadius": 2}, "colorKey": "primary"},
            # 箭头
            {"id": "head", "type": "polygon", "offset": {"x": 35, "y": 0}, "size": {"points": [{"x": 0, "y": -10}, {"x": 20, "y": 0}, {"x": 0, "y": 10}]}, "colorKey": "primary"}
        ],
        "defaultColors": {"primary": "#ef4444"},
        "config": {
            "scalable": True,
            "minLength": 30,
            "maxLength": 150
        }
    },

    "data_point": {
        "description": "数据点（用于图表）",
        "parts": [
            {"id": "point", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 8}, "colorKey": "primary"},
            {"id": "glow", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 12}, "colorKey": "glow"}
        ],
        "defaultColors": {"primary": "#3b82f6", "glow": "rgba(59, 130, 246, 0.3)"}
    },

    "progress_bar": {
        "description": "进度条（显示比例关系）",
        "parts": [
            {"id": "track", "type": "rectangle", "offset": {"x": 0, "y": 0}, "size": {"width": 200, "height": 20, "cornerRadius": 10}, "colorKey": "track"},
            {"id": "fill", "type": "rectangle", "offset": {"x": -50, "y": 0}, "size": {"width": 100, "height": 20, "cornerRadius": 10}, "colorKey": "primary"}
        ],
        "defaultColors": {"primary": "#22c55e", "track": "#374151"}
    },

    "gauge": {
        "description": "仪表盘（显示数值范围）",
        "parts": [
            # 外圈
            {"id": "outer_ring", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 50}, "colorKey": "track", "stroke": {"width": 8}, "noFill": True},
            # 填充弧（通过旋转和遮罩实现）
            {"id": "fill_ring", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 50}, "colorKey": "primary", "stroke": {"width": 8}, "noFill": True},
            # 中心点
            {"id": "center", "type": "circle", "offset": {"x": 0, "y": 0}, "size": {"radius": 8}, "colorKey": "primary"},
            # 指针
            {"id": "needle", "type": "rectangle", "offset": {"x": 0, "y": -20}, "size": {"width": 4, "height": 40, "cornerRadius": 2}, "colorKey": "needle"}
        ],
        "defaultColors": {"primary": "#3b82f6", "track": "#374151", "needle": "#ef4444"}
    },

    "formula_box": {
        "description": "公式展示框",
        "parts": [
            {"id": "bg", "type": "rectangle", "offset": {"x": 0, "y": 0}, "size": {"width": 180, "height": 60, "cornerRadius": 8}, "colorKey": "background"},
            {"id": "border", "type": "rectangle", "offset": {"x": 0, "y": 0}, "size": {"width": 180, "height": 60, "cornerRadius": 8}, "colorKey": "primary", "stroke": {"width": 2}, "noFill": True}
        ],
        "defaultColors": {"primary": "#6366f1", "background": "#1e1b4b"}
    },

    "comparison_bar": {
        "description": "对比条（展示两个变量对比）",
        "parts": [
            # 左侧条
            {"id": "bar_left", "type": "rectangle", "offset": {"x": -55, "y": 0}, "size": {"width": 100, "height": 30, "cornerRadius": 4}, "colorKey": "primary"},
            # 右侧条
            {"id": "bar_right", "type": "rectangle", "offset": {"x": 55, "y": 0}, "size": {"width": 100, "height": 30, "cornerRadius": 4}, "colorKey": "secondary"},
            # 中间分隔
            {"id": "divider", "type": "rectangle", "offset": {"x": 0, "y": 0}, "size": {"width": 4, "height": 40}, "colorKey": "divider"}
        ],
        "defaultColors": {"primary": "#3b82f6", "secondary": "#ef4444", "divider": "#ffffff"}
    }
}


# 粒子特效定义
PARTICLE_EFFECTS: Dict[str, Dict[str, Any]] = {
    "water_splash": {
        "description": "水花飞溅",
        "particleConfig": {
            "type": "burst",
            "count": 15,
            "lifetime": 800,
            "speed": {"min": 50, "max": 150},
            "direction": {"min": -90, "max": 90},
            "gravity": 200,
            "size": {"start": 8, "end": 2},
            "color": {"start": "#60a5fa", "end": "#0ea5e9"},
            "opacity": {"start": 0.8, "end": 0}
        }
    },
    "dust": {
        "description": "尘土飞扬",
        "particleConfig": {
            "type": "burst",
            "count": 10,
            "lifetime": 600,
            "speed": {"min": 20, "max": 80},
            "direction": {"min": -180, "max": 0},
            "gravity": 50,
            "size": {"start": 6, "end": 12},
            "color": {"start": "#a3a3a3", "end": "#737373"},
            "opacity": {"start": 0.6, "end": 0}
        }
    },
    "trail": {
        "description": "运动轨迹",
        "particleConfig": {
            "type": "continuous",
            "emitRate": 30,
            "lifetime": 400,
            "speed": {"min": 0, "max": 10},
            "size": {"start": 6, "end": 2},
            "color": {"start": "#fbbf24", "end": "#f59e0b"},
            "opacity": {"start": 0.7, "end": 0}
        }
    },
    "glow": {
        "description": "发光效果",
        "particleConfig": {
            "type": "continuous",
            "emitRate": 5,
            "lifetime": 1000,
            "speed": {"min": 0, "max": 5},
            "size": {"start": 20, "end": 30},
            "color": {"start": "#fef3c7", "end": "#fbbf24"},
            "opacity": {"start": 0.3, "end": 0},
            "blendMode": "add"
        }
    },
    "ripple": {
        "description": "水面涟漪",
        "particleConfig": {
            "type": "burst",
            "count": 3,
            "lifetime": 1200,
            "speed": {"min": 0, "max": 0},
            "size": {"start": 10, "end": 60},
            "color": {"start": "#ffffff", "end": "#0ea5e9"},
            "opacity": {"start": 0.5, "end": 0},
            "shape": "ring"
        }
    },
    "bubbles": {
        "description": "气泡",
        "particleConfig": {
            "type": "continuous",
            "emitRate": 8,
            "lifetime": 1500,
            "speed": {"min": 30, "max": 60},
            "direction": {"min": -100, "max": -80},
            "gravity": -50,
            "size": {"start": 4, "end": 8},
            "color": {"start": "#bfdbfe", "end": "#60a5fa"},
            "opacity": {"start": 0.6, "end": 0}
        }
    },
    "sparkle": {
        "description": "闪光",
        "particleConfig": {
            "type": "burst",
            "count": 8,
            "lifetime": 500,
            "speed": {"min": 50, "max": 100},
            "direction": {"min": 0, "max": 360},
            "size": {"start": 4, "end": 1},
            "color": {"start": "#fef3c7", "end": "#fbbf24"},
            "opacity": {"start": 1, "end": 0}
        }
    },
    "smoke": {
        "description": "烟雾",
        "particleConfig": {
            "type": "continuous",
            "emitRate": 15,
            "lifetime": 2000,
            "speed": {"min": 10, "max": 30},
            "direction": {"min": -100, "max": -80},
            "gravity": -20,
            "size": {"start": 15, "end": 40},
            "color": {"start": "#9ca3af", "end": "#6b7280"},
            "opacity": {"start": 0.4, "end": 0}
        }
    },

    # ==================== 变量关系特效 ====================
    "energy_pulse": {
        "description": "能量脉冲（表示能量/力的变化）",
        "particleConfig": {
            "type": "burst",
            "count": 12,
            "lifetime": 600,
            "speed": {"min": 80, "max": 150},
            "direction": {"min": 0, "max": 360},
            "size": {"start": 6, "end": 2},
            "color": {"start": "#fbbf24", "end": "#f97316"},
            "opacity": {"start": 1, "end": 0}
        }
    },
    "speed_lines": {
        "description": "速度线（表示速度/加速度）",
        "particleConfig": {
            "type": "continuous",
            "emitRate": 20,
            "lifetime": 300,
            "speed": {"min": 100, "max": 200},
            "direction": {"min": 175, "max": 185},
            "size": {"start": 3, "end": 1},
            "color": {"start": "#60a5fa", "end": "#3b82f6"},
            "opacity": {"start": 0.8, "end": 0},
            "shape": "line"
        }
    },
    "value_change": {
        "description": "数值变化（表示变量增减）",
        "particleConfig": {
            "type": "burst",
            "count": 5,
            "lifetime": 800,
            "speed": {"min": 20, "max": 50},
            "direction": {"min": -100, "max": -80},
            "gravity": -30,
            "size": {"start": 10, "end": 6},
            "color": {"start": "#22c55e", "end": "#16a34a"},
            "opacity": {"start": 0.9, "end": 0}
        }
    },
    "impact": {
        "description": "碰撞效果（表示力的作用）",
        "particleConfig": {
            "type": "burst",
            "count": 20,
            "lifetime": 400,
            "speed": {"min": 100, "max": 200},
            "direction": {"min": 0, "max": 360},
            "gravity": 100,
            "size": {"start": 5, "end": 2},
            "color": {"start": "#ffffff", "end": "#fbbf24"},
            "opacity": {"start": 1, "end": 0}
        }
    },
    "flow": {
        "description": "流动效果（表示连续变化）",
        "particleConfig": {
            "type": "continuous",
            "emitRate": 15,
            "lifetime": 1000,
            "speed": {"min": 30, "max": 60},
            "direction": {"min": -10, "max": 10},
            "size": {"start": 8, "end": 4},
            "color": {"start": "#06b6d4", "end": "#0891b2"},
            "opacity": {"start": 0.6, "end": 0}
        }
    },
    "highlight_pulse": {
        "description": "高亮脉冲（强调关键变化点）",
        "particleConfig": {
            "type": "burst",
            "count": 1,
            "lifetime": 1000,
            "speed": {"min": 0, "max": 0},
            "size": {"start": 20, "end": 80},
            "color": {"start": "#fbbf24", "end": "#fbbf24"},
            "opacity": {"start": 0.6, "end": 0},
            "shape": "ring"
        }
    }
}


def get_semantic_shape(shape_type: str) -> Dict[str, Any]:
    """获取语义形状定义"""
    return SEMANTIC_SHAPES.get(shape_type)


def list_semantic_shapes() -> List[str]:
    """列出所有可用的语义形状类型"""
    return list(SEMANTIC_SHAPES.keys())


def get_shape_description(shape_type: str) -> str:
    """获取形状描述"""
    shape = SEMANTIC_SHAPES.get(shape_type)
    if shape:
        return shape.get("description", "")
    return ""


def get_particle_effect(effect_type: str) -> Dict[str, Any]:
    """获取粒子特效定义"""
    return PARTICLE_EFFECTS.get(effect_type)


def list_particle_effects() -> List[str]:
    """列出所有可用的粒子特效类型"""
    return list(PARTICLE_EFFECTS.keys())
