"""
交互式通用模板
"""

from .art_templates import COLOR_WHEEL_TEMPLATE, COMPOSITION_TEMPLATE

# 交互式计数器模板
INTERACTIVE_COUNTER_TEMPLATE = {
    "version": "1.0.0",
    "id": "interactive_counter",
    "name": "交互式计数器",
    "description": "点击按钮增加或减少计数，拖拽滑块调整数值",
    "canvas": {"width": 500, "height": 400, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 250, "y": 40}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "text": {"content": "交互式计数器", "fontFamily": "Arial", "fontSize": 28, "fontWeight": "bold", "color": "#f8fafc", "align": "center"}},
        {"id": "counter_bg", "name": "计数背景", "type": "shape", "transform": {"position": {"x": 250, "y": 150}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 200, "height": 80, "fill": {"type": "solid", "color": "#1e293b"}, "stroke": {"color": "#3b82f6", "width": 2}, "cornerRadius": 12}},
        {"id": "counter_display", "name": "计数显示", "type": "text", "transform": {"position": {"x": 250, "y": 150}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "text": {"content": "0", "fontFamily": "Arial", "fontSize": 48, "fontWeight": "bold", "color": "#3b82f6", "align": "center"}},
        {"id": "btn_decrease", "name": "减少按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 260}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": True, "shape": {"shapeType": "circle", "radius": 35, "fill": {"type": "solid", "color": "#ef4444"}}},
        {"id": "btn_decrease_text", "name": "减少文字", "type": "text", "transform": {"position": {"x": 120, "y": 260}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 6, "interactive": False, "text": {"content": "-", "fontFamily": "Arial", "fontSize": 40, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_increase", "name": "增加按钮", "type": "shape", "transform": {"position": {"x": 380, "y": 260}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": True, "shape": {"shapeType": "circle", "radius": 35, "fill": {"type": "solid", "color": "#22c55e"}}},
        {"id": "btn_increase_text", "name": "增加文字", "type": "text", "transform": {"position": {"x": 380, "y": 260}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 6, "interactive": False, "text": {"content": "+", "fontFamily": "Arial", "fontSize": 40, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_reset", "name": "重置按钮", "type": "shape", "transform": {"position": {"x": 250, "y": 260}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": True, "shape": {"shapeType": "rectangle", "width": 80, "height": 50, "fill": {"type": "solid", "color": "#6366f1"}, "cornerRadius": 8}},
        {"id": "btn_reset_text", "name": "重置文字", "type": "text", "transform": {"position": {"x": 250, "y": 260}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 6, "interactive": False, "text": {"content": "重置", "fontFamily": "Arial", "fontSize": 16, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "draggable_ball", "name": "可拖拽球", "type": "shape", "transform": {"position": {"x": 250, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": True, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#f59e0b"}, "stroke": {"color": "#ffffff", "width": 3}}}
    ],
    "timelines": [],
    "interactions": [
        {"id": "click_increase", "name": "点击增加", "enabled": True, "trigger": {"type": "click", "targetId": "btn_increase"}, "actions": [{"type": "incrementVariable", "params": {"name": "counter", "amount": 1}}]},
        {"id": "click_decrease", "name": "点击减少", "enabled": True, "trigger": {"type": "click", "targetId": "btn_decrease"}, "actions": [{"type": "incrementVariable", "params": {"name": "counter", "amount": -1}}]},
        {"id": "click_reset", "name": "点击重置", "enabled": True, "trigger": {"type": "click", "targetId": "btn_reset"}, "actions": [{"type": "setVariable", "params": {"name": "counter", "value": 0}}]},
        {"id": "drag_ball", "name": "拖拽球", "enabled": True, "trigger": {"type": "drag", "targetId": "draggable_ball"}, "actions": [{"type": "moveElement", "params": {"targetId": "draggable_ball"}}]}
    ],
    "variables": [{"id": "counter", "name": "计数器", "type": "number", "defaultValue": 0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["交互", "演示", "计数器"], "category": "interactive"}
}

# 导出所有交互模板
INTERACTIVE_TEMPLATES = {
    "interactive_counter": INTERACTIVE_COUNTER_TEMPLATE,
    "art_color_wheel": COLOR_WHEEL_TEMPLATE,
    "art_composition": COMPOSITION_TEMPLATE,
}
