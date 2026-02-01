# 体育模板 Part 3 - 游泳和体操

SWIMMING_STROKE_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_swimming_stroke",
    "name": "游泳泳姿分析",
    "description": "展示自由泳、蛙泳、蝶泳、仰泳四种泳姿的动作要领",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0c4a6e", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "pool_bg", "name": "泳池", "type": "shape", "transform": {"position": {"x": 400, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 760, "height": 300, "fill": {"type": "solid", "color": "#0369a1"}, "stroke": {"color": "#0ea5e9", "width": 3}, "cornerRadius": 8}},
        {"id": "lane_line1", "name": "泳道线1", "type": "shape", "transform": {"position": {"x": 400, "y": 200}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.5, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": -350, "y": 0}, {"x": 350, "y": 0}], "stroke": {"color": "#ffffff", "width": 2, "dashArray": [20, 10]}}},
        {"id": "lane_line2", "name": "泳道线2", "type": "shape", "transform": {"position": {"x": 400, "y": 360}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.5, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": -350, "y": 0}, {"x": 350, "y": 0}], "stroke": {"color": "#ffffff", "width": 2, "dashArray": [20, 10]}}},
        {"id": "swimmer", "name": "游泳者", "type": "shape", "transform": {"position": {"x": 150, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#fbbf24"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "arm_left", "name": "左臂", "type": "shape", "transform": {"position": {"x": 130, "y": 260}, "rotation": -30, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 50, "height": 12, "fill": {"type": "solid", "color": "#fbbf24"}, "cornerRadius": 6}},
        {"id": "arm_right", "name": "右臂", "type": "shape", "transform": {"position": {"x": 170, "y": 260}, "rotation": 30, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 50, "height": 12, "fill": {"type": "solid", "color": "#fbbf24"}, "cornerRadius": 6}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "游泳泳姿技术分析", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "stroke_name", "name": "泳姿名称", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "自由泳 (Freestyle)", "fontFamily": "Arial", "fontSize": 18, "color": "#22c55e", "align": "center"}},
        {"id": "btn_freestyle", "name": "自由泳按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 110, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_freestyle_text", "name": "自由泳文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "自由泳", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_breaststroke", "name": "蛙泳按钮", "type": "shape", "transform": {"position": {"x": 270, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 110, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_breaststroke_text", "name": "蛙泳文字", "type": "text", "transform": {"position": {"x": 270, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "蛙泳", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_butterfly", "name": "蝶泳按钮", "type": "shape", "transform": {"position": {"x": 420, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 110, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_butterfly_text", "name": "蝶泳文字", "type": "text", "transform": {"position": {"x": 420, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "蝶泳", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_backstroke", "name": "仰泳按钮", "type": "shape", "transform": {"position": {"x": 570, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 110, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_backstroke_text", "name": "仰泳文字", "type": "text", "transform": {"position": {"x": 570, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "仰泳", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_play", "name": "播放按钮", "type": "shape", "transform": {"position": {"x": 720, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_play_text", "name": "播放文字", "type": "text", "transform": {"position": {"x": 720, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "播放", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "freestyle_swim", "name": "自由泳动画", "duration": 2000, "loop": True, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "swimmer", "property": "position", "value": {"x": 150, "y": 280}, "easing": "linear"},
            {"time": 500, "targetId": "arm_left", "property": "rotation", "value": -60, "easing": "easeInOut"},
            {"time": 1000, "targetId": "swimmer", "property": "position", "value": {"x": 400, "y": 280}, "easing": "linear"},
            {"time": 1500, "targetId": "arm_right", "property": "rotation", "value": 60, "easing": "easeInOut"},
            {"time": 2000, "targetId": "swimmer", "property": "position", "value": {"x": 650, "y": 280}, "easing": "linear"}
        ]}
    ],
    "interactions": [
        {"id": "click_freestyle", "name": "点击自由泳", "enabled": True, "trigger": {"type": "click", "targetId": "btn_freestyle"}, "actions": [{"type": "log", "params": {"message": "自由泳"}}]},
        {"id": "click_play", "name": "点击播放", "enabled": True, "trigger": {"type": "click", "targetId": "btn_play"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "freestyle_swim"}}]}
    ],
    "variables": [{"id": "stroke_type", "name": "泳姿类型", "type": "string", "defaultValue": "freestyle"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "游泳", "泳姿"], "category": "sports"}
}

GYMNASTICS_VAULT_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_gymnastics_vault",
    "name": "体操跳马技术分析",
    "description": "展示跳马的助跑、起跳、腾空、落地四个阶段",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e1b4b", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "floor", "name": "地板", "type": "shape", "transform": {"position": {"x": 400, "y": 420}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 760, "height": 60, "fill": {"type": "solid", "color": "#3730a3"}, "cornerRadius": 4}},
        {"id": "springboard", "name": "跳板", "type": "shape", "transform": {"position": {"x": 300, "y": 380}, "rotation": -10, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 80, "height": 20, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 4}},
        {"id": "vault_table", "name": "跳马", "type": "shape", "transform": {"position": {"x": 450, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 3, "interactive": False, "shape": {"shapeType": "rectangle", "width": 120, "height": 30, "fill": {"type": "solid", "color": "#dc2626"}, "cornerRadius": 4}},
        {"id": "vault_leg", "name": "跳马腿", "type": "shape", "transform": {"position": {"x": 450, "y": 375}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 20, "height": 40, "fill": {"type": "solid", "color": "#991b1b"}}},
        {"id": "landing_mat", "name": "落地垫", "type": "shape", "transform": {"position": {"x": 650, "y": 385}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 150, "height": 30, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 4}},
        {"id": "gymnast", "name": "体操运动员", "type": "shape", "transform": {"position": {"x": 100, "y": 360}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 20, "fill": {"type": "solid", "color": "#ec4899"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "体操跳马技术分析", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "phase_text", "name": "阶段文字", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "阶段: 助跑", "fontFamily": "Arial", "fontSize": 18, "color": "#22c55e", "align": "center"}},
        {"id": "btn_run", "name": "助跑按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_run_text", "name": "助跑文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "助跑", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_takeoff", "name": "起跳按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_takeoff_text", "name": "起跳文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "起跳", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_flight", "name": "腾空按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_flight_text", "name": "腾空文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "腾空", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_landing", "name": "落地按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_landing_text", "name": "落地文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "落地", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "vault_full", "name": "完整动作", "duration": 3000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "gymnast", "property": "position", "value": {"x": 100, "y": 360}, "easing": "linear"},
            {"time": 800, "targetId": "gymnast", "property": "position", "value": {"x": 280, "y": 360}, "easing": "easeIn"},
            {"time": 1200, "targetId": "gymnast", "property": "position", "value": {"x": 350, "y": 250}, "easing": "easeOut"},
            {"time": 1600, "targetId": "gymnast", "property": "position", "value": {"x": 450, "y": 200}, "easing": "easeInOut"},
            {"time": 2200, "targetId": "gymnast", "property": "position", "value": {"x": 550, "y": 150}, "easing": "easeOut"},
            {"time": 2600, "targetId": "gymnast", "property": "position", "value": {"x": 620, "y": 250}, "easing": "easeIn"},
            {"time": 3000, "targetId": "gymnast", "property": "position", "value": {"x": 650, "y": 365}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "vault_full"}}]}
    ],
    "variables": [{"id": "phase", "name": "阶段", "type": "string", "defaultValue": "run"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "体操", "跳马"], "category": "sports"}
}
