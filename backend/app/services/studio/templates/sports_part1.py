# 体育模板 Part 1 - 田径类

SPRINT_START_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_sprint_start",
    "name": "短跑起跑技术模拟",
    "description": "展示短跑起跑的三个阶段：预备、起跑、加速",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "track_bg", "name": "跑道", "type": "shape", "transform": {"position": {"x": 400, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 760, "height": 200, "fill": {"type": "solid", "color": "#dc2626"}, "cornerRadius": 4}},
        {"id": "lane_line1", "name": "跑道线1", "type": "shape", "transform": {"position": {"x": 400, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.8, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": -380, "y": 0}, {"x": 380, "y": 0}], "stroke": {"color": "#ffffff", "width": 2}}},
        {"id": "lane_line2", "name": "跑道线2", "type": "shape", "transform": {"position": {"x": 400, "y": 400}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.8, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": -380, "y": 0}, {"x": 380, "y": 0}], "stroke": {"color": "#ffffff", "width": 2}}},
        {"id": "start_line", "name": "起跑线", "type": "shape", "transform": {"position": {"x": 100, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 8, "height": 200, "fill": {"type": "solid", "color": "#ffffff"}}},
        {"id": "starting_block", "name": "起跑器", "type": "shape", "transform": {"position": {"x": 80, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 3, "interactive": False, "shape": {"shapeType": "rectangle", "width": 30, "height": 60, "fill": {"type": "solid", "color": "#475569"}, "cornerRadius": 4}},
        {"id": "runner", "name": "运动员", "type": "shape", "transform": {"position": {"x": 120, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 40}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "短跑起跑技术分析", "fontFamily": "Arial", "fontSize": 28, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "phase_indicator", "name": "阶段指示", "type": "text", "transform": {"position": {"x": 400, "y": 80}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "当前阶段: 预备", "fontFamily": "Arial", "fontSize": 18, "color": "#22c55e", "align": "center"}},
        {"id": "btn_ready", "name": "预备按钮", "type": "shape", "transform": {"position": {"x": 200, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 120, "height": 44, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 22}},
        {"id": "btn_ready_text", "name": "预备文字", "type": "text", "transform": {"position": {"x": 200, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "预备姿势", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_set", "name": "起跑按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 120, "height": 44, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 22}},
        {"id": "btn_set_text", "name": "起跑文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "起跑反应", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_go", "name": "加速按钮", "type": "shape", "transform": {"position": {"x": 600, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 120, "height": 44, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 22}},
        {"id": "btn_go_text", "name": "加速文字", "type": "text", "transform": {"position": {"x": 600, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "加速冲刺", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "info_panel", "name": "信息面板", "type": "shape", "transform": {"position": {"x": 680, "y": 150}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.95, "zIndex": 8, "interactive": False, "shape": {"shapeType": "rectangle", "width": 180, "height": 140, "fill": {"type": "solid", "color": "#1e293b"}, "stroke": {"color": "#475569", "width": 1}, "cornerRadius": 12}},
        {"id": "speed_text", "name": "速度", "type": "text", "transform": {"position": {"x": 680, "y": 110}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "text": {"content": "速度: 0 m/s", "fontFamily": "Arial", "fontSize": 14, "color": "#22c55e", "align": "center"}},
        {"id": "angle_text", "name": "角度", "type": "text", "transform": {"position": {"x": 680, "y": 140}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "text": {"content": "身体角度: 45°", "fontFamily": "Arial", "fontSize": 14, "color": "#f59e0b", "align": "center"}},
        {"id": "reaction_text", "name": "反应时间", "type": "text", "transform": {"position": {"x": 680, "y": 170}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "text": {"content": "反应: 0.15s", "fontFamily": "Arial", "fontSize": 14, "color": "#3b82f6", "align": "center"}}
    ],
    "timelines": [
        {"id": "ready_anim", "name": "预备动画", "duration": 500, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "runner", "property": "position", "value": {"x": 120, "y": 350}, "easing": "linear"},
            {"time": 500, "targetId": "runner", "property": "position", "value": {"x": 110, "y": 340}, "easing": "easeOut"}
        ]},
        {"id": "set_anim", "name": "起跑动画", "duration": 300, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "runner", "property": "position", "value": {"x": 110, "y": 340}, "easing": "linear"},
            {"time": 300, "targetId": "runner", "property": "position", "value": {"x": 150, "y": 350}, "easing": "easeOut"}
        ]},
        {"id": "go_anim", "name": "加速动画", "duration": 2000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "runner", "property": "position", "value": {"x": 150, "y": 350}, "easing": "linear"},
            {"time": 2000, "targetId": "runner", "property": "position", "value": {"x": 700, "y": 350}, "easing": "easeOut"}
        ]}
    ],
    "interactions": [
        {"id": "click_ready", "name": "点击预备", "enabled": True, "trigger": {"type": "click", "targetId": "btn_ready"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "ready_anim"}}]},
        {"id": "click_set", "name": "点击起跑", "enabled": True, "trigger": {"type": "click", "targetId": "btn_set"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "set_anim"}}]},
        {"id": "click_go", "name": "点击加速", "enabled": True, "trigger": {"type": "click", "targetId": "btn_go"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "go_anim"}}]}
    ],
    "variables": [{"id": "phase", "name": "阶段", "type": "number", "defaultValue": 0}, {"id": "speed", "name": "速度", "type": "number", "defaultValue": 0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "短跑", "起跑"], "category": "sports"}
}
