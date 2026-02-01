# 体育模板 Part 4 - 球类运动（网球、排球、乒乓球）

TENNIS_SERVE_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_tennis_serve",
    "name": "网球发球技术分析",
    "description": "展示网球发球的抛球、引拍、击球、随挥四个阶段",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#065f46", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "court", "name": "球场", "type": "shape", "transform": {"position": {"x": 400, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 700, "height": 350, "fill": {"type": "solid", "color": "#047857"}, "stroke": {"color": "#ffffff", "width": 3}, "cornerRadius": 4}},
        {"id": "net", "name": "球网", "type": "shape", "transform": {"position": {"x": 400, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 6, "height": 80, "fill": {"type": "solid", "color": "#ffffff"}}},
        {"id": "service_line", "name": "发球线", "type": "shape", "transform": {"position": {"x": 200, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.8, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": 0, "y": -150}, {"x": 0, "y": 150}], "stroke": {"color": "#ffffff", "width": 2}}},
        {"id": "player", "name": "球员", "type": "shape", "transform": {"position": {"x": 150, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "racket", "name": "球拍", "type": "shape", "transform": {"position": {"x": 180, "y": 330}, "rotation": -45, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 11, "interactive": False, "shape": {"shapeType": "rectangle", "width": 60, "height": 12, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 6}},
        {"id": "ball", "name": "网球", "type": "shape", "transform": {"position": {"x": 150, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 12, "interactive": False, "shape": {"shapeType": "circle", "radius": 12, "fill": {"type": "solid", "color": "#84cc16"}, "stroke": {"color": "#ffffff", "width": 2}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "网球发球技术分析", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_toss", "name": "抛球按钮", "type": "shape", "transform": {"position": {"x": 150, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_toss_text", "name": "抛球文字", "type": "text", "transform": {"position": {"x": 150, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "抛球", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_backswing", "name": "引拍按钮", "type": "shape", "transform": {"position": {"x": 290, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_backswing_text", "name": "引拍文字", "type": "text", "transform": {"position": {"x": 290, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "引拍", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_hit", "name": "击球按钮", "type": "shape", "transform": {"position": {"x": 430, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_hit_text", "name": "击球文字", "type": "text", "transform": {"position": {"x": 430, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "击球", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_follow", "name": "随挥按钮", "type": "shape", "transform": {"position": {"x": 570, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_follow_text", "name": "随挥文字", "type": "text", "transform": {"position": {"x": 570, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "随挥", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 710, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 710, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "serve_full", "name": "完整发球", "duration": 2500, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "ball", "property": "position", "value": {"x": 150, "y": 280}, "easing": "linear"},
            {"time": 500, "targetId": "ball", "property": "position", "value": {"x": 160, "y": 150}, "easing": "easeOut"},
            {"time": 1000, "targetId": "racket", "property": "rotation", "value": -120, "easing": "easeIn"},
            {"time": 1500, "targetId": "ball", "property": "position", "value": {"x": 400, "y": 200}, "easing": "easeOut"},
            {"time": 2000, "targetId": "ball", "property": "position", "value": {"x": 600, "y": 350}, "easing": "easeIn"},
            {"time": 2500, "targetId": "racket", "property": "rotation", "value": 45, "easing": "easeOut"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "serve_full"}}]}
    ],
    "variables": [{"id": "phase", "name": "阶段", "type": "string", "defaultValue": "ready"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "网球", "发球"], "category": "sports"}
}

VOLLEYBALL_SPIKE_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_volleyball_spike",
    "name": "排球扣球技术分析",
    "description": "展示排球扣球的助跑、起跳、挥臂、击球技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e3a5f", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "court", "name": "球场", "type": "shape", "transform": {"position": {"x": 400, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 700, "height": 200, "fill": {"type": "solid", "color": "#f97316"}, "stroke": {"color": "#ffffff", "width": 3}, "cornerRadius": 4}},
        {"id": "net", "name": "球网", "type": "shape", "transform": {"position": {"x": 400, "y": 200}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "rectangle", "width": 400, "height": 8, "fill": {"type": "solid", "color": "#ffffff"}}},
        {"id": "net_pole_left", "name": "左网柱", "type": "shape", "transform": {"position": {"x": 200, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 1}}, "visible": True, "opacity": 1, "zIndex": 4, "interactive": False, "shape": {"shapeType": "rectangle", "width": 10, "height": 160, "fill": {"type": "solid", "color": "#475569"}}},
        {"id": "net_pole_right", "name": "右网柱", "type": "shape", "transform": {"position": {"x": 600, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 1}}, "visible": True, "opacity": 1, "zIndex": 4, "interactive": False, "shape": {"shapeType": "rectangle", "width": 10, "height": 160, "fill": {"type": "solid", "color": "#475569"}}},
        {"id": "player", "name": "球员", "type": "shape", "transform": {"position": {"x": 250, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "ball", "name": "排球", "type": "shape", "transform": {"position": {"x": 350, "y": 150}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 12, "interactive": False, "shape": {"shapeType": "circle", "radius": 18, "fill": {"type": "solid", "color": "#fbbf24"}, "stroke": {"color": "#ffffff", "width": 2}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "排球扣球技术分析", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_approach", "name": "助跑按钮", "type": "shape", "transform": {"position": {"x": 150, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_approach_text", "name": "助跑文字", "type": "text", "transform": {"position": {"x": 150, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "助跑", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_jump", "name": "起跳按钮", "type": "shape", "transform": {"position": {"x": 290, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_jump_text", "name": "起跳文字", "type": "text", "transform": {"position": {"x": 290, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "起跳", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_swing", "name": "挥臂按钮", "type": "shape", "transform": {"position": {"x": 430, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_swing_text", "name": "挥臂文字", "type": "text", "transform": {"position": {"x": 430, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "挥臂", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_spike", "name": "扣球按钮", "type": "shape", "transform": {"position": {"x": 570, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_spike_text", "name": "扣球文字", "type": "text", "transform": {"position": {"x": 570, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "扣球", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 710, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 710, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "spike_full", "name": "完整扣球", "duration": 2000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "player", "property": "position", "value": {"x": 250, "y": 380}, "easing": "linear"},
            {"time": 500, "targetId": "player", "property": "position", "value": {"x": 320, "y": 380}, "easing": "easeIn"},
            {"time": 1000, "targetId": "player", "property": "position", "value": {"x": 350, "y": 200}, "easing": "easeOut"},
            {"time": 1500, "targetId": "ball", "property": "position", "value": {"x": 550, "y": 350}, "easing": "easeIn"},
            {"time": 2000, "targetId": "player", "property": "position", "value": {"x": 350, "y": 380}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "spike_full"}}]}
    ],
    "variables": [{"id": "phase", "name": "阶段", "type": "string", "defaultValue": "ready"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "排球", "扣球"], "category": "sports"}
}
