# 体育模板 Part 10 - 水上运动（跳水、赛艇）

DIVING_PLATFORM_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_diving_platform",
    "name": "跳水技术分析",
    "description": "展示跳水的起跳、空中动作、入水技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0c4a6e", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "pool", "name": "泳池", "type": "shape", "transform": {"position": {"x": 500, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 500, "height": 180, "fill": {"type": "solid", "color": "#0369a1"}, "stroke": {"color": "#0ea5e9", "width": 3}, "cornerRadius": 4}},
        {"id": "platform", "name": "跳台", "type": "shape", "transform": {"position": {"x": 100, "y": 150}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 120, "height": 20, "fill": {"type": "solid", "color": "#6b7280"}}},
        {"id": "platform_support", "name": "支架", "type": "shape", "transform": {"position": {"x": 60, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 30, "height": 200, "fill": {"type": "solid", "color": "#4b5563"}}},
        {"id": "diver", "name": "跳水运动员", "type": "shape", "transform": {"position": {"x": 140, "y": 130}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 20, "fill": {"type": "solid", "color": "#ef4444"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "splash", "name": "水花", "type": "shape", "transform": {"position": {"x": 500, "y": 300}, "rotation": 0, "scale": {"x": 0, "y": 0}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.8, "zIndex": 15, "interactive": False, "shape": {"shapeType": "circle", "radius": 40, "fill": {"type": "solid", "color": "#ffffff"}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "跳水技术分析", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "score_text", "name": "得分", "type": "text", "transform": {"position": {"x": 700, "y": 80}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "得分: 0.0", "fontFamily": "Arial", "fontSize": 20, "fontWeight": "bold", "color": "#22c55e", "align": "center"}},
        {"id": "btn_takeoff", "name": "起跳按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_takeoff_text", "name": "起跳文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "起跳", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_tuck", "name": "抱膝按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_tuck_text", "name": "抱膝文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "抱膝", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_pike", "name": "屈体按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_pike_text", "name": "屈体文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "屈体", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_entry", "name": "入水按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_entry_text", "name": "入水文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "入水", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "dive_full", "name": "完整跳水", "duration": 2500, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "diver", "property": "position", "value": {"x": 140, "y": 130}, "easing": "linear"},
            {"time": 300, "targetId": "diver", "property": "position", "value": {"x": 200, "y": 80}, "easing": "easeOut"},
            {"time": 800, "targetId": "diver", "property": "position", "value": {"x": 350, "y": 150}, "easing": "easeInOut"},
            {"time": 800, "targetId": "diver", "property": "rotation", "value": 360, "easing": "linear"},
            {"time": 1400, "targetId": "diver", "property": "position", "value": {"x": 450, "y": 250}, "easing": "easeIn"},
            {"time": 1400, "targetId": "diver", "property": "rotation", "value": 720, "easing": "linear"},
            {"time": 2000, "targetId": "diver", "property": "position", "value": {"x": 500, "y": 350}, "easing": "easeIn"},
            {"time": 2500, "targetId": "diver", "property": "position", "value": {"x": 500, "y": 400}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "dive_full"}}]}
    ],
    "variables": [{"id": "score", "name": "得分", "type": "number", "defaultValue": 0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "跳水", "空中动作"], "category": "sports"}
}

ROWING_TECHNIQUE_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_rowing_technique",
    "name": "赛艇划桨技术",
    "description": "展示赛艇的拉桨、推桨、回桨技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0c4a6e", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "water", "name": "水面", "type": "shape", "transform": {"position": {"x": 400, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 800, "height": 200, "fill": {"type": "solid", "color": "#0369a1"}}},
        {"id": "boat", "name": "赛艇", "type": "shape", "transform": {"position": {"x": 400, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "rectangle", "width": 300, "height": 30, "fill": {"type": "solid", "color": "#fbbf24"}, "cornerRadius": 15}},
        {"id": "rower", "name": "划手", "type": "shape", "transform": {"position": {"x": 400, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 20, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "oar_left", "name": "左桨", "type": "shape", "transform": {"position": {"x": 350, "y": 300}, "rotation": -30, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 8, "interactive": False, "shape": {"shapeType": "rectangle", "width": 120, "height": 8, "fill": {"type": "solid", "color": "#78350f"}, "cornerRadius": 4}},
        {"id": "oar_right", "name": "右桨", "type": "shape", "transform": {"position": {"x": 450, "y": 300}, "rotation": 30, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 8, "interactive": False, "shape": {"shapeType": "rectangle", "width": 120, "height": 8, "fill": {"type": "solid", "color": "#78350f"}, "cornerRadius": 4}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "赛艇划桨技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "phase_text", "name": "阶段", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "准备姿势", "fontFamily": "Arial", "fontSize": 18, "color": "#22c55e", "align": "center"}},
        {"id": "btn_catch", "name": "入水按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_catch_text", "name": "入水文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "入水", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_drive", "name": "拉桨按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_drive_text", "name": "拉桨文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "拉桨", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_finish", "name": "出水按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_finish_text", "name": "出水文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "出水", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_recovery", "name": "回桨按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_recovery_text", "name": "回桨文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "回桨", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "row_full", "name": "完整划桨", "duration": 2000, "loop": True, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "oar_left", "property": "rotation", "value": -30, "easing": "linear"},
            {"time": 0, "targetId": "oar_right", "property": "rotation", "value": 30, "easing": "linear"},
            {"time": 500, "targetId": "oar_left", "property": "rotation", "value": -60, "easing": "easeIn"},
            {"time": 500, "targetId": "oar_right", "property": "rotation", "value": 60, "easing": "easeIn"},
            {"time": 1000, "targetId": "oar_left", "property": "rotation", "value": 0, "easing": "easeOut"},
            {"time": 1000, "targetId": "oar_right", "property": "rotation", "value": 0, "easing": "easeOut"},
            {"time": 1500, "targetId": "oar_left", "property": "rotation", "value": -30, "easing": "easeInOut"},
            {"time": 1500, "targetId": "oar_right", "property": "rotation", "value": 30, "easing": "easeInOut"},
            {"time": 2000, "targetId": "boat", "property": "position", "value": {"x": 420, "y": 300}, "easing": "linear"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "row_full"}}]}
    ],
    "variables": [{"id": "phase", "name": "阶段", "type": "string", "defaultValue": "ready"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "赛艇", "划桨"], "category": "sports"}
}
