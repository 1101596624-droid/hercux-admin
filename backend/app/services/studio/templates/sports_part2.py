# 体育模板 Part 2 - 球类运动

BASKETBALL_SHOOTING_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_basketball_shooting",
    "name": "篮球投篮弧线模拟",
    "description": "展示篮球投篮的最佳弧线和入射角度",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1a1a2e", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "court_bg", "name": "球场", "type": "shape", "transform": {"position": {"x": 400, "y": 400}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 760, "height": 150, "fill": {"type": "solid", "color": "#8b4513"}, "cornerRadius": 4}},
        {"id": "backboard", "name": "篮板", "type": "shape", "transform": {"position": {"x": 700, "y": 200}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 15, "height": 100, "fill": {"type": "solid", "color": "#ffffff"}, "stroke": {"color": "#ef4444", "width": 2}}},
        {"id": "rim", "name": "篮筐", "type": "shape", "transform": {"position": {"x": 660, "y": 220}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 3, "interactive": False, "shape": {"shapeType": "circle", "radius": 20, "fill": {"type": "none"}, "stroke": {"color": "#ef4444", "width": 4}}},
        {"id": "pole", "name": "篮架", "type": "shape", "transform": {"position": {"x": 720, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 10, "height": 200, "fill": {"type": "solid", "color": "#475569"}}},
        {"id": "player", "name": "球员", "type": "shape", "transform": {"position": {"x": 200, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "circle", "radius": 30, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "ball", "name": "篮球", "type": "shape", "transform": {"position": {"x": 220, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": True, "shape": {"shapeType": "circle", "radius": 15, "fill": {"type": "solid", "color": "#f97316"}, "stroke": {"color": "#000000", "width": 2}}},
        {"id": "arc_high", "name": "高弧线", "type": "shape", "transform": {"position": {"x": 440, "y": 150}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.6, "zIndex": 4, "interactive": False, "shape": {"shapeType": "circle", "radius": 200, "fill": {"type": "none"}, "stroke": {"color": "#22c55e", "width": 3, "dashArray": [8, 4]}}},
        {"id": "arc_low", "name": "低弧线", "type": "shape", "transform": {"position": {"x": 440, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.6, "zIndex": 4, "interactive": False, "shape": {"shapeType": "circle", "radius": 150, "fill": {"type": "none"}, "stroke": {"color": "#ef4444", "width": 3, "dashArray": [8, 4]}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "篮球投篮弧线分析", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "angle_panel", "name": "角度面板", "type": "shape", "transform": {"position": {"x": 100, "y": 150}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.9, "zIndex": 8, "interactive": False, "shape": {"shapeType": "rectangle", "width": 160, "height": 100, "fill": {"type": "solid", "color": "#1e293b"}, "stroke": {"color": "#475569", "width": 1}, "cornerRadius": 10}},
        {"id": "angle_label", "name": "角度标签", "type": "text", "transform": {"position": {"x": 100, "y": 120}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "text": {"content": "出手角度: 52°", "fontFamily": "Arial", "fontSize": 14, "color": "#22c55e", "align": "center"}},
        {"id": "entry_label", "name": "入射标签", "type": "text", "transform": {"position": {"x": 100, "y": 150}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "text": {"content": "入射角度: 45°", "fontFamily": "Arial", "fontSize": 14, "color": "#f59e0b", "align": "center"}},
        {"id": "success_label", "name": "命中率", "type": "text", "transform": {"position": {"x": 100, "y": 180}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "text": {"content": "命中率: 高", "fontFamily": "Arial", "fontSize": 14, "color": "#3b82f6", "align": "center"}},
        {"id": "btn_high", "name": "高弧线按钮", "type": "shape", "transform": {"position": {"x": 250, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 140, "height": 44, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 22}},
        {"id": "btn_high_text", "name": "高弧线文字", "type": "text", "transform": {"position": {"x": 250, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "高弧线投篮", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_low", "name": "低弧线按钮", "type": "shape", "transform": {"position": {"x": 450, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 140, "height": 44, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 22}},
        {"id": "btn_low_text", "name": "低弧线文字", "type": "text", "transform": {"position": {"x": 450, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "低弧线投篮", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_reset", "name": "重置按钮", "type": "shape", "transform": {"position": {"x": 650, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 44, "fill": {"type": "solid", "color": "#6366f1"}, "cornerRadius": 22}},
        {"id": "btn_reset_text", "name": "重置文字", "type": "text", "transform": {"position": {"x": 650, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "重置", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "high_arc_shot", "name": "高弧线投篮", "duration": 1500, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "ball", "property": "position", "value": {"x": 220, "y": 300}, "easing": "linear"},
            {"time": 500, "targetId": "ball", "property": "position", "value": {"x": 400, "y": 100}, "easing": "easeOut"},
            {"time": 1000, "targetId": "ball", "property": "position", "value": {"x": 580, "y": 150}, "easing": "easeInOut"},
            {"time": 1500, "targetId": "ball", "property": "position", "value": {"x": 660, "y": 220}, "easing": "easeIn"}
        ]},
        {"id": "low_arc_shot", "name": "低弧线投篮", "duration": 1200, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "ball", "property": "position", "value": {"x": 220, "y": 300}, "easing": "linear"},
            {"time": 400, "targetId": "ball", "property": "position", "value": {"x": 400, "y": 200}, "easing": "easeOut"},
            {"time": 800, "targetId": "ball", "property": "position", "value": {"x": 580, "y": 200}, "easing": "linear"},
            {"time": 1200, "targetId": "ball", "property": "position", "value": {"x": 700, "y": 200}, "easing": "easeIn"}
        ]},
        {"id": "reset_ball", "name": "重置球", "duration": 300, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "ball", "property": "position", "value": {"x": 660, "y": 220}, "easing": "linear"},
            {"time": 300, "targetId": "ball", "property": "position", "value": {"x": 220, "y": 300}, "easing": "easeOut"}
        ]}
    ],
    "interactions": [
        {"id": "click_high", "name": "点击高弧线", "enabled": True, "trigger": {"type": "click", "targetId": "btn_high"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "high_arc_shot"}}]},
        {"id": "click_low", "name": "点击低弧线", "enabled": True, "trigger": {"type": "click", "targetId": "btn_low"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "low_arc_shot"}}]},
        {"id": "click_reset", "name": "点击重置", "enabled": True, "trigger": {"type": "click", "targetId": "btn_reset"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "reset_ball"}}]}
    ],
    "variables": [{"id": "shot_angle", "name": "出手角度", "type": "number", "defaultValue": 52}, {"id": "entry_angle", "name": "入射角度", "type": "number", "defaultValue": 45}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "篮球", "投篮"], "category": "sports"}
}

FOOTBALL_KICK_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_football_kick",
    "name": "足球踢球技术模拟",
    "description": "展示足球不同踢法的球路轨迹",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "field", "name": "球场", "type": "shape", "transform": {"position": {"x": 400, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 760, "height": 250, "fill": {"type": "solid", "color": "#166534"}, "cornerRadius": 4}},
        {"id": "goal", "name": "球门", "type": "shape", "transform": {"position": {"x": 700, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 20, "height": 120, "fill": {"type": "none"}, "stroke": {"color": "#ffffff", "width": 4}}},
        {"id": "ball", "name": "足球", "type": "shape", "transform": {"position": {"x": 150, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": True, "shape": {"shapeType": "circle", "radius": 15, "fill": {"type": "solid", "color": "#ffffff"}, "stroke": {"color": "#000000", "width": 2}}},
        {"id": "player", "name": "球员", "type": "shape", "transform": {"position": {"x": 100, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "足球踢球技术分析", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_straight", "name": "直线按钮", "type": "shape", "transform": {"position": {"x": 150, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 120, "height": 44, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 22}},
        {"id": "btn_straight_text", "name": "直线文字", "type": "text", "transform": {"position": {"x": 150, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "正脚背", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_curve", "name": "弧线按钮", "type": "shape", "transform": {"position": {"x": 320, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 120, "height": 44, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 22}},
        {"id": "btn_curve_text", "name": "弧线文字", "type": "text", "transform": {"position": {"x": 320, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "内脚背弧线", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_chip", "name": "挑射按钮", "type": "shape", "transform": {"position": {"x": 490, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 120, "height": 44, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 22}},
        {"id": "btn_chip_text", "name": "挑射文字", "type": "text", "transform": {"position": {"x": 490, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "挑射", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_reset", "name": "重置按钮", "type": "shape", "transform": {"position": {"x": 660, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 44, "fill": {"type": "solid", "color": "#6366f1"}, "cornerRadius": 22}},
        {"id": "btn_reset_text", "name": "重置文字", "type": "text", "transform": {"position": {"x": 660, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "重置", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "straight_kick", "name": "直线踢球", "duration": 1000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "ball", "property": "position", "value": {"x": 150, "y": 380}, "easing": "linear"},
            {"time": 1000, "targetId": "ball", "property": "position", "value": {"x": 700, "y": 300}, "easing": "easeOut"}
        ]},
        {"id": "curve_kick", "name": "弧线踢球", "duration": 1200, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "ball", "property": "position", "value": {"x": 150, "y": 380}, "easing": "linear"},
            {"time": 400, "targetId": "ball", "property": "position", "value": {"x": 350, "y": 320}, "easing": "easeOut"},
            {"time": 800, "targetId": "ball", "property": "position", "value": {"x": 550, "y": 280}, "easing": "easeInOut"},
            {"time": 1200, "targetId": "ball", "property": "position", "value": {"x": 700, "y": 320}, "easing": "easeIn"}
        ]},
        {"id": "chip_kick", "name": "挑射", "duration": 1500, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "ball", "property": "position", "value": {"x": 150, "y": 380}, "easing": "linear"},
            {"time": 500, "targetId": "ball", "property": "position", "value": {"x": 350, "y": 200}, "easing": "easeOut"},
            {"time": 1000, "targetId": "ball", "property": "position", "value": {"x": 550, "y": 180}, "easing": "easeInOut"},
            {"time": 1500, "targetId": "ball", "property": "position", "value": {"x": 700, "y": 280}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_straight", "name": "点击直线", "enabled": True, "trigger": {"type": "click", "targetId": "btn_straight"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "straight_kick"}}]},
        {"id": "click_curve", "name": "点击弧线", "enabled": True, "trigger": {"type": "click", "targetId": "btn_curve"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "curve_kick"}}]},
        {"id": "click_chip", "name": "点击挑射", "enabled": True, "trigger": {"type": "click", "targetId": "btn_chip"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "chip_kick"}}]}
    ],
    "variables": [{"id": "kick_type", "name": "踢法类型", "type": "string", "defaultValue": "straight"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "足球", "踢球"], "category": "sports"}
}
