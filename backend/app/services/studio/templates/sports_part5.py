# 体育模板 Part 5 - 田径（跳远、铅球、标枪）

LONG_JUMP_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_long_jump",
    "name": "跳远技术分析",
    "description": "展示跳远的助跑、起跳、腾空、落地四个阶段",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "runway", "name": "助跑道", "type": "shape", "transform": {"position": {"x": 250, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 400, "height": 60, "fill": {"type": "solid", "color": "#dc2626"}, "cornerRadius": 4}},
        {"id": "takeoff_board", "name": "起跳板", "type": "shape", "transform": {"position": {"x": 450, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 30, "height": 60, "fill": {"type": "solid", "color": "#ffffff"}}},
        {"id": "sand_pit", "name": "沙坑", "type": "shape", "transform": {"position": {"x": 620, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 280, "height": 60, "fill": {"type": "solid", "color": "#fbbf24"}, "cornerRadius": 4}},
        {"id": "athlete", "name": "运动员", "type": "shape", "transform": {"position": {"x": 100, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 22, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "跳远技术分析", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "distance_text", "name": "距离显示", "type": "text", "transform": {"position": {"x": 620, "y": 320}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": False, "text": {"content": "距离: 0.00m", "fontFamily": "Arial", "fontSize": 18, "color": "#22c55e", "align": "center"}},
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
        {"id": "jump_full", "name": "完整跳远", "duration": 3000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "athlete", "property": "position", "value": {"x": 100, "y": 350}, "easing": "linear"},
            {"time": 800, "targetId": "athlete", "property": "position", "value": {"x": 420, "y": 350}, "easing": "easeIn"},
            {"time": 1200, "targetId": "athlete", "property": "position", "value": {"x": 500, "y": 200}, "easing": "easeOut"},
            {"time": 1800, "targetId": "athlete", "property": "position", "value": {"x": 600, "y": 180}, "easing": "easeInOut"},
            {"time": 2400, "targetId": "athlete", "property": "position", "value": {"x": 680, "y": 280}, "easing": "easeIn"},
            {"time": 3000, "targetId": "athlete", "property": "position", "value": {"x": 700, "y": 350}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "jump_full"}}]}
    ],
    "variables": [{"id": "distance", "name": "距离", "type": "number", "defaultValue": 0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "田径", "跳远"], "category": "sports"}
}

SHOT_PUT_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_shot_put",
    "name": "铅球投掷技术分析",
    "description": "展示铅球的握球、滑步、转体、推球技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "circle", "name": "投掷圈", "type": "shape", "transform": {"position": {"x": 200, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "circle", "radius": 100, "fill": {"type": "solid", "color": "#475569"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "toe_board", "name": "抵趾板", "type": "shape", "transform": {"position": {"x": 300, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 15, "height": 80, "fill": {"type": "solid", "color": "#ffffff"}, "cornerRadius": 4}},
        {"id": "sector_line1", "name": "扇形线1", "type": "shape", "transform": {"position": {"x": 300, "y": 350}, "rotation": 20, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 0.5, "zIndex": 0, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": 0, "y": 0}, {"x": 450, "y": 0}], "stroke": {"color": "#ffffff", "width": 2}}},
        {"id": "sector_line2", "name": "扇形线2", "type": "shape", "transform": {"position": {"x": 300, "y": 350}, "rotation": -20, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 0.5, "zIndex": 0, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": 0, "y": 0}, {"x": 450, "y": 0}], "stroke": {"color": "#ffffff", "width": 2}}},
        {"id": "athlete", "name": "运动员", "type": "shape", "transform": {"position": {"x": 150, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 28, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "shot", "name": "铅球", "type": "shape", "transform": {"position": {"x": 180, "y": 330}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 11, "interactive": False, "shape": {"shapeType": "circle", "radius": 15, "fill": {"type": "solid", "color": "#6b7280"}, "stroke": {"color": "#374151", "width": 2}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "铅球投掷技术分析", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "distance_text", "name": "距离显示", "type": "text", "transform": {"position": {"x": 600, "y": 200}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": False, "text": {"content": "距离: 0.00m", "fontFamily": "Arial", "fontSize": 20, "color": "#22c55e", "align": "center"}},
        {"id": "btn_grip", "name": "握球按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_grip_text", "name": "握球文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "握球", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_glide", "name": "滑步按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_glide_text", "name": "滑步文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "滑步", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_turn", "name": "转体按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_turn_text", "name": "转体文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "转体", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_push", "name": "推球按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_push_text", "name": "推球文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "推球", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "put_full", "name": "完整投掷", "duration": 2500, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "athlete", "property": "position", "value": {"x": 150, "y": 350}, "easing": "linear"},
            {"time": 600, "targetId": "athlete", "property": "position", "value": {"x": 220, "y": 350}, "easing": "easeIn"},
            {"time": 1200, "targetId": "athlete", "property": "position", "value": {"x": 260, "y": 350}, "easing": "easeInOut"},
            {"time": 1800, "targetId": "shot", "property": "position", "value": {"x": 400, "y": 200}, "easing": "easeOut"},
            {"time": 2500, "targetId": "shot", "property": "position", "value": {"x": 650, "y": 350}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "put_full"}}]}
    ],
    "variables": [{"id": "distance", "name": "距离", "type": "number", "defaultValue": 0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "田径", "铅球"], "category": "sports"}
}
