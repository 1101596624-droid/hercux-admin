# 物理模板 Part 1 - 力学

FORCE_COMPOSITION_TEMPLATE = {
    "version": "1.0.0",
    "id": "physics_force_composition",
    "name": "力的合成与分解",
    "description": "通过拖拽调整两个力的大小和方向，观察合力的变化",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#f8fafc", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "grid_bg", "name": "网格背景", "type": "shape", "transform": {"position": {"x": 400, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 760, "height": 460, "fill": {"type": "solid", "color": "#f1f5f9"}, "stroke": {"color": "#e2e8f0", "width": 1}, "cornerRadius": 8}},
        {"id": "origin", "name": "原点", "type": "shape", "transform": {"position": {"x": 400, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 8, "fill": {"type": "solid", "color": "#1e293b"}}},
        {"id": "axis_x", "name": "X轴", "type": "shape", "transform": {"position": {"x": 400, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.3, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": -350, "y": 0}, {"x": 350, "y": 0}], "stroke": {"color": "#64748b", "width": 1}}},
        {"id": "axis_y", "name": "Y轴", "type": "shape", "transform": {"position": {"x": 400, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.3, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": 0, "y": -200}, {"x": 0, "y": 200}], "stroke": {"color": "#64748b", "width": 1}}},
        {"id": "force_f1", "name": "力F1", "type": "shape", "transform": {"position": {"x": 400, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": 0, "y": 0}, {"x": 150, "y": 0}], "stroke": {"color": "#ef4444", "width": 5, "lineCap": "round"}}},
        {"id": "force_f1_arrow", "name": "F1箭头", "type": "shape", "transform": {"position": {"x": 550, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 6, "interactive": True, "shape": {"shapeType": "circle", "radius": 14, "fill": {"type": "solid", "color": "#ef4444"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "force_f1_label", "name": "F1标签", "type": "text", "transform": {"position": {"x": 570, "y": 235}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "F₁ = 150N", "fontFamily": "Arial", "fontSize": 16, "fontWeight": "bold", "color": "#ef4444", "align": "left"}},
        {"id": "force_f2", "name": "力F2", "type": "shape", "transform": {"position": {"x": 400, "y": 250}, "rotation": -60, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": 0, "y": 0}, {"x": 120, "y": 0}], "stroke": {"color": "#3b82f6", "width": 5, "lineCap": "round"}}},
        {"id": "force_f2_arrow", "name": "F2箭头", "type": "shape", "transform": {"position": {"x": 460, "y": 146}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 6, "interactive": True, "shape": {"shapeType": "circle", "radius": 14, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "force_f2_label", "name": "F2标签", "type": "text", "transform": {"position": {"x": 480, "y": 130}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "F₂ = 120N", "fontFamily": "Arial", "fontSize": 16, "fontWeight": "bold", "color": "#3b82f6", "align": "left"}},
        {"id": "resultant", "name": "合力", "type": "shape", "transform": {"position": {"x": 400, "y": 250}, "rotation": -25, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 4, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": 0, "y": 0}, {"x": 220, "y": 0}], "stroke": {"color": "#22c55e", "width": 6, "lineCap": "round", "dashArray": [12, 6]}}},
        {"id": "resultant_label", "name": "合力标签", "type": "text", "transform": {"position": {"x": 580, "y": 180}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "R = 234N", "fontFamily": "Arial", "fontSize": 18, "fontWeight": "bold", "color": "#22c55e", "align": "left"}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 30}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "力的合成与分解", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#1e293b", "align": "center"}},
        {"id": "instructions", "name": "说明", "type": "text", "transform": {"position": {"x": 400, "y": 480}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.7, "zIndex": 20, "interactive": False, "text": {"content": "拖拽红色和蓝色控制点调整力的大小和方向", "fontFamily": "Arial", "fontSize": 14, "color": "#64748b", "align": "center"}},
        {"id": "angle_display", "name": "夹角显示", "type": "text", "transform": {"position": {"x": 100, "y": 100}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "夹角: 60°", "fontFamily": "Arial", "fontSize": 16, "color": "#8b5cf6", "align": "center"}}
    ],
    "timelines": [],
    "interactions": [
        {"id": "drag_f1", "name": "拖拽F1", "enabled": True, "trigger": {"type": "drag", "targetId": "force_f1_arrow"}, "actions": [{"type": "log", "params": {"message": "F1被拖拽"}}]},
        {"id": "drag_f2", "name": "拖拽F2", "enabled": True, "trigger": {"type": "drag", "targetId": "force_f2_arrow"}, "actions": [{"type": "log", "params": {"message": "F2被拖拽"}}]}
    ],
    "variables": [
        {"id": "f1_magnitude", "name": "F1大小", "type": "number", "defaultValue": 150},
        {"id": "f1_angle", "name": "F1角度", "type": "number", "defaultValue": 0},
        {"id": "f2_magnitude", "name": "F2大小", "type": "number", "defaultValue": 120},
        {"id": "f2_angle", "name": "F2角度", "type": "number", "defaultValue": 60},
        {"id": "resultant_magnitude", "name": "合力大小", "type": "number", "defaultValue": 234}
    ],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["物理", "力学", "力的合成"], "category": "physics"}
}

PROJECTILE_MOTION_TEMPLATE = {
    "version": "1.0.0",
    "id": "physics_projectile_motion",
    "name": "抛体运动模拟",
    "description": "展示不同角度和初速度下的抛体运动轨迹",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "sky", "name": "天空", "type": "shape", "transform": {"position": {"x": 400, "y": 200}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 800, "height": 400, "fill": {"type": "solid", "color": "#1e3a5f"}}},
        {"id": "ground", "name": "地面", "type": "shape", "transform": {"position": {"x": 400, "y": 450}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 800, "height": 100, "fill": {"type": "solid", "color": "#166534"}}},
        {"id": "cannon", "name": "发射器", "type": "shape", "transform": {"position": {"x": 80, "y": 380}, "rotation": -45, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "rectangle", "width": 60, "height": 20, "fill": {"type": "solid", "color": "#475569"}, "cornerRadius": 4}},
        {"id": "projectile", "name": "抛射物", "type": "shape", "transform": {"position": {"x": 100, "y": 360}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 12, "fill": {"type": "solid", "color": "#ef4444"}, "stroke": {"color": "#ffffff", "width": 2}}},
        {"id": "trajectory_45", "name": "45度轨迹", "type": "shape", "transform": {"position": {"x": 100, "y": 360}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 0.5, "zIndex": 3, "interactive": False, "shape": {"shapeType": "circle", "radius": 280, "fill": {"type": "none"}, "stroke": {"color": "#22c55e", "width": 3, "dashArray": [8, 4]}}},
        {"id": "trajectory_30", "name": "30度轨迹", "type": "shape", "transform": {"position": {"x": 100, "y": 360}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": False, "opacity": 0.5, "zIndex": 3, "interactive": False, "shape": {"shapeType": "circle", "radius": 240, "fill": {"type": "none"}, "stroke": {"color": "#f59e0b", "width": 3, "dashArray": [8, 4]}}},
        {"id": "trajectory_60", "name": "60度轨迹", "type": "shape", "transform": {"position": {"x": 100, "y": 360}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": False, "opacity": 0.5, "zIndex": 3, "interactive": False, "shape": {"shapeType": "circle", "radius": 240, "fill": {"type": "none"}, "stroke": {"color": "#3b82f6", "width": 3, "dashArray": [8, 4]}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 30}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "抛体运动模拟", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "info_panel", "name": "信息面板", "type": "shape", "transform": {"position": {"x": 680, "y": 120}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.9, "zIndex": 15, "interactive": False, "shape": {"shapeType": "rectangle", "width": 180, "height": 160, "fill": {"type": "solid", "color": "#1e293b"}, "stroke": {"color": "#475569", "width": 1}, "cornerRadius": 10}},
        {"id": "angle_text", "name": "角度", "type": "text", "transform": {"position": {"x": 680, "y": 70}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "发射角度: 45°", "fontFamily": "Arial", "fontSize": 14, "color": "#22c55e", "align": "center"}},
        {"id": "velocity_text", "name": "速度", "type": "text", "transform": {"position": {"x": 680, "y": 100}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "初速度: 20 m/s", "fontFamily": "Arial", "fontSize": 14, "color": "#f59e0b", "align": "center"}},
        {"id": "range_text", "name": "射程", "type": "text", "transform": {"position": {"x": 680, "y": 130}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "射程: 40.8 m", "fontFamily": "Arial", "fontSize": 14, "color": "#3b82f6", "align": "center"}},
        {"id": "height_text", "name": "高度", "type": "text", "transform": {"position": {"x": 680, "y": 160}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "最大高度: 10.2 m", "fontFamily": "Arial", "fontSize": 14, "color": "#8b5cf6", "align": "center"}},
        {"id": "btn_30", "name": "30度按钮", "type": "shape", "transform": {"position": {"x": 150, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_30_text", "name": "30度文字", "type": "text", "transform": {"position": {"x": 150, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "30°", "fontFamily": "Arial", "fontSize": 16, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_45", "name": "45度按钮", "type": "shape", "transform": {"position": {"x": 300, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_45_text", "name": "45度文字", "type": "text", "transform": {"position": {"x": 300, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "45°", "fontFamily": "Arial", "fontSize": 16, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_60", "name": "60度按钮", "type": "shape", "transform": {"position": {"x": 450, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_60_text", "name": "60度文字", "type": "text", "transform": {"position": {"x": 450, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "60°", "fontFamily": "Arial", "fontSize": 16, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_launch", "name": "发射按钮", "type": "shape", "transform": {"position": {"x": 620, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 120, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_launch_text", "name": "发射文字", "type": "text", "transform": {"position": {"x": 620, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "发射", "fontFamily": "Arial", "fontSize": 16, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "launch_45", "name": "45度发射", "duration": 2000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "projectile", "property": "position", "value": {"x": 100, "y": 360}, "easing": "linear"},
            {"time": 500, "targetId": "projectile", "property": "position", "value": {"x": 280, "y": 200}, "easing": "easeOut"},
            {"time": 1000, "targetId": "projectile", "property": "position", "value": {"x": 460, "y": 160}, "easing": "linear"},
            {"time": 1500, "targetId": "projectile", "property": "position", "value": {"x": 640, "y": 240}, "easing": "easeIn"},
            {"time": 2000, "targetId": "projectile", "property": "position", "value": {"x": 700, "y": 400}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_launch", "name": "点击发射", "enabled": True, "trigger": {"type": "click", "targetId": "btn_launch"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "launch_45"}}]}
    ],
    "variables": [
        {"id": "angle", "name": "发射角度", "type": "number", "defaultValue": 45},
        {"id": "velocity", "name": "初速度", "type": "number", "defaultValue": 20},
        {"id": "range", "name": "射程", "type": "number", "defaultValue": 40.8}
    ],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["物理", "力学", "抛体运动"], "category": "physics"}
}
