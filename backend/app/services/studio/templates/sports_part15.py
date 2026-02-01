# 体育模板 Part 15 - 高难度田径动作

# 撑杆跳高
POLE_VAULT_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_pole_vault",
    "name": "撑杆跳高技术",
    "description": "展示撑杆跳高的持杆助跑、插杆起跳、摆体过杆、落地技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "runway", "name": "助跑道", "type": "shape", "transform": {"position": {"x": 200, "y": 400}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 350, "height": 60, "fill": {"type": "solid", "color": "#dc2626"}, "cornerRadius": 4}},
        {"id": "box", "name": "插斗", "type": "shape", "transform": {"position": {"x": 380, "y": 400}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 30, "height": 30, "fill": {"type": "solid", "color": "#6b7280"}}},
        {"id": "mat", "name": "落地垫", "type": "shape", "transform": {"position": {"x": 550, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 250, "height": 150, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 8}},
        {"id": "crossbar", "name": "横杆", "type": "shape", "transform": {"position": {"x": 450, "y": 180}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "rectangle", "width": 150, "height": 6, "fill": {"type": "solid", "color": "#ef4444"}}},
        {"id": "pole_left", "name": "左立柱", "type": "shape", "transform": {"position": {"x": 375, "y": 290}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 1}}, "visible": True, "opacity": 1, "zIndex": 4, "interactive": False, "shape": {"shapeType": "rectangle", "width": 10, "height": 220, "fill": {"type": "solid", "color": "#9ca3af"}}},
        {"id": "pole_right", "name": "右立柱", "type": "shape", "transform": {"position": {"x": 525, "y": 290}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 1}}, "visible": True, "opacity": 1, "zIndex": 4, "interactive": False, "shape": {"shapeType": "rectangle", "width": 10, "height": 220, "fill": {"type": "solid", "color": "#9ca3af"}}},
        {"id": "athlete", "name": "运动员", "type": "shape", "transform": {"position": {"x": 100, "y": 370}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 20, "fill": {"type": "solid", "color": "#22c55e"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "pole", "name": "撑杆", "type": "shape", "transform": {"position": {"x": 120, "y": 350}, "rotation": -70, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 150, "height": 6, "fill": {"type": "solid", "color": "#fbbf24"}, "cornerRadius": 3}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "撑杆跳高技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "height_text", "name": "高度", "type": "text", "transform": {"position": {"x": 700, "y": 80}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "高度: 5.00m", "fontFamily": "Arial", "fontSize": 18, "fontWeight": "bold", "color": "#22c55e", "align": "center"}},
        {"id": "btn_approach", "name": "助跑按钮", "type": "shape", "transform": {"position": {"x": 100, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_approach_text", "name": "助跑文字", "type": "text", "transform": {"position": {"x": 100, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "助跑", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_plant", "name": "插杆按钮", "type": "shape", "transform": {"position": {"x": 220, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_plant_text", "name": "插杆文字", "type": "text", "transform": {"position": {"x": 220, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "插杆", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_swing", "name": "摆体按钮", "type": "shape", "transform": {"position": {"x": 340, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_swing_text", "name": "摆体文字", "type": "text", "transform": {"position": {"x": 340, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "摆体", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_clear", "name": "过杆按钮", "type": "shape", "transform": {"position": {"x": 460, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_clear_text", "name": "过杆文字", "type": "text", "transform": {"position": {"x": 460, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "过杆", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 580, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 580, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "vault_full", "name": "完整撑杆跳", "duration": 4000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "athlete", "property": "position", "value": {"x": 100, "y": 370}, "easing": "linear"},
            {"time": 0, "targetId": "pole", "property": "rotation", "value": -70, "easing": "linear"},
            {"time": 800, "targetId": "athlete", "property": "position", "value": {"x": 350, "y": 370}, "easing": "easeIn"},
            {"time": 800, "targetId": "pole", "property": "rotation", "value": -45, "easing": "easeIn"},
            {"time": 1200, "targetId": "athlete", "property": "position", "value": {"x": 400, "y": 300}, "easing": "easeOut"},
            {"time": 1200, "targetId": "pole", "property": "rotation", "value": 0, "easing": "easeOut"},
            {"time": 1800, "targetId": "athlete", "property": "position", "value": {"x": 430, "y": 180}, "easing": "easeOut"},
            {"time": 2400, "targetId": "athlete", "property": "position", "value": {"x": 470, "y": 120}, "easing": "easeOut"},
            {"time": 3000, "targetId": "athlete", "property": "position", "value": {"x": 500, "y": 150}, "easing": "easeIn"},
            {"time": 3600, "targetId": "athlete", "property": "position", "value": {"x": 530, "y": 280}, "easing": "easeIn"},
            {"time": 4000, "targetId": "athlete", "property": "position", "value": {"x": 550, "y": 350}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "vault_full"}}]}
    ],
    "variables": [{"id": "height", "name": "高度", "type": "number", "defaultValue": 5.0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "田径", "撑杆跳"], "category": "sports"}
}

# 标枪投掷
JAVELIN_THROW_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_javelin_throw",
    "name": "标枪投掷技术",
    "description": "展示标枪投掷的持枪助跑、交叉步、投掷、跟随技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "runway", "name": "助跑道", "type": "shape", "transform": {"position": {"x": 200, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 350, "height": 60, "fill": {"type": "solid", "color": "#dc2626"}, "cornerRadius": 4}},
        {"id": "foul_line", "name": "犯规线", "type": "shape", "transform": {"position": {"x": 380, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 8, "height": 80, "fill": {"type": "solid", "color": "#ffffff"}}},
        {"id": "sector", "name": "落地区", "type": "shape", "transform": {"position": {"x": 580, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.3, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 350, "height": 300, "fill": {"type": "solid", "color": "#22c55e"}}},
        {"id": "athlete", "name": "运动员", "type": "shape", "transform": {"position": {"x": 100, "y": 320}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 22, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "javelin", "name": "标枪", "type": "shape", "transform": {"position": {"x": 130, "y": 310}, "rotation": -15, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 11, "interactive": False, "shape": {"shapeType": "rectangle", "width": 120, "height": 4, "fill": {"type": "solid", "color": "#fbbf24"}, "cornerRadius": 2}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "标枪投掷技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "distance_text", "name": "距离", "type": "text", "transform": {"position": {"x": 650, "y": 80}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "距离: 0.00m", "fontFamily": "Arial", "fontSize": 18, "fontWeight": "bold", "color": "#22c55e", "align": "center"}},
        {"id": "btn_approach", "name": "助跑按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_approach_text", "name": "助跑文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "助跑", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_cross", "name": "交叉步按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_cross_text", "name": "交叉步文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "交叉步", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_throw", "name": "投掷按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_throw_text", "name": "投掷文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "投掷", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "throw_full", "name": "完整投掷", "duration": 3000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "athlete", "property": "position", "value": {"x": 100, "y": 320}, "easing": "linear"},
            {"time": 0, "targetId": "javelin", "property": "position", "value": {"x": 130, "y": 310}, "easing": "linear"},
            {"time": 800, "targetId": "athlete", "property": "position", "value": {"x": 280, "y": 320}, "easing": "easeIn"},
            {"time": 800, "targetId": "javelin", "property": "position", "value": {"x": 310, "y": 310}, "easing": "easeIn"},
            {"time": 1200, "targetId": "athlete", "property": "position", "value": {"x": 350, "y": 320}, "easing": "easeOut"},
            {"time": 1200, "targetId": "javelin", "property": "rotation", "value": -45, "easing": "easeIn"},
            {"time": 1500, "targetId": "javelin", "property": "position", "value": {"x": 500, "y": 200}, "easing": "easeOut"},
            {"time": 1500, "targetId": "javelin", "property": "rotation", "value": -30, "easing": "linear"},
            {"time": 2200, "targetId": "javelin", "property": "position", "value": {"x": 650, "y": 280}, "easing": "linear"},
            {"time": 2200, "targetId": "javelin", "property": "rotation", "value": 15, "easing": "easeIn"},
            {"time": 3000, "targetId": "javelin", "property": "position", "value": {"x": 720, "y": 380}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "throw_full"}}]}
    ],
    "variables": [{"id": "distance", "name": "距离", "type": "number", "defaultValue": 0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "田径", "标枪"], "category": "sports"}
}
