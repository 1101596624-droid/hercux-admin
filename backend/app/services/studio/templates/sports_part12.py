# 体育模板 Part 12 - 自行车和举重

CYCLING_SPRINT_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_cycling_sprint",
    "name": "自行车冲刺技术",
    "description": "展示自行车冲刺的踏频、姿势、发力技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e3a5f", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "track", "name": "赛道", "type": "shape", "transform": {"position": {"x": 400, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 760, "height": 100, "fill": {"type": "solid", "color": "#78350f"}, "stroke": {"color": "#ffffff", "width": 2}, "cornerRadius": 4}},
        {"id": "lane_line", "name": "车道线", "type": "shape", "transform": {"position": {"x": 400, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.5, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": -380, "y": 0}, {"x": 380, "y": 0}], "stroke": {"color": "#ffffff", "width": 2, "dashArray": [30, 15]}}},
        {"id": "cyclist", "name": "自行车手", "type": "shape", "transform": {"position": {"x": 200, "y": 340}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 20, "fill": {"type": "solid", "color": "#ef4444"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "bike_frame", "name": "车架", "type": "shape", "transform": {"position": {"x": 200, "y": 360}, "rotation": -10, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 8, "interactive": False, "shape": {"shapeType": "rectangle", "width": 80, "height": 8, "fill": {"type": "solid", "color": "#1f2937"}, "cornerRadius": 4}},
        {"id": "wheel_front", "name": "前轮", "type": "shape", "transform": {"position": {"x": 240, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "transparent"}, "stroke": {"color": "#1f2937", "width": 4}}},
        {"id": "wheel_rear", "name": "后轮", "type": "shape", "transform": {"position": {"x": 160, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "transparent"}, "stroke": {"color": "#1f2937", "width": 4}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "自行车冲刺技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "speed_text", "name": "速度", "type": "text", "transform": {"position": {"x": 700, "y": 80}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "速度: 0 km/h", "fontFamily": "Arial", "fontSize": 18, "fontWeight": "bold", "color": "#22c55e", "align": "center"}},
        {"id": "btn_start", "name": "起步按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_start_text", "name": "起步文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "起步", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_accelerate", "name": "加速按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_accelerate_text", "name": "加速文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "加速", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_sprint", "name": "冲刺按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_sprint_text", "name": "冲刺文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "冲刺", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "sprint_full", "name": "完整冲刺", "duration": 3000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "cyclist", "property": "position", "value": {"x": 200, "y": 340}, "easing": "linear"},
            {"time": 0, "targetId": "bike_frame", "property": "position", "value": {"x": 200, "y": 360}, "easing": "linear"},
            {"time": 0, "targetId": "wheel_front", "property": "position", "value": {"x": 240, "y": 380}, "easing": "linear"},
            {"time": 0, "targetId": "wheel_rear", "property": "position", "value": {"x": 160, "y": 380}, "easing": "linear"},
            {"time": 1500, "targetId": "cyclist", "property": "position", "value": {"x": 450, "y": 340}, "easing": "easeIn"},
            {"time": 1500, "targetId": "bike_frame", "property": "position", "value": {"x": 450, "y": 360}, "easing": "easeIn"},
            {"time": 1500, "targetId": "wheel_front", "property": "position", "value": {"x": 490, "y": 380}, "easing": "easeIn"},
            {"time": 1500, "targetId": "wheel_rear", "property": "position", "value": {"x": 410, "y": 380}, "easing": "easeIn"},
            {"time": 3000, "targetId": "cyclist", "property": "position", "value": {"x": 700, "y": 340}, "easing": "easeOut"},
            {"time": 3000, "targetId": "bike_frame", "property": "position", "value": {"x": 700, "y": 360}, "easing": "easeOut"},
            {"time": 3000, "targetId": "wheel_front", "property": "position", "value": {"x": 740, "y": 380}, "easing": "easeOut"},
            {"time": 3000, "targetId": "wheel_rear", "property": "position", "value": {"x": 660, "y": 380}, "easing": "easeOut"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "sprint_full"}}]}
    ],
    "variables": [{"id": "speed", "name": "速度", "type": "number", "defaultValue": 0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "自行车", "冲刺"], "category": "sports"}
}

WEIGHTLIFTING_SNATCH_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_weightlifting_snatch",
    "name": "举重抓举技术",
    "description": "展示举重抓举的准备、提铃、发力、支撑技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1f2937", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "platform", "name": "举重台", "type": "shape", "transform": {"position": {"x": 400, "y": 420}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 400, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 4}},
        {"id": "lifter", "name": "举重运动员", "type": "shape", "transform": {"position": {"x": 400, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 30, "fill": {"type": "solid", "color": "#ef4444"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "barbell", "name": "杠铃杆", "type": "shape", "transform": {"position": {"x": 400, "y": 390}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 8, "interactive": False, "shape": {"shapeType": "rectangle", "width": 200, "height": 8, "fill": {"type": "solid", "color": "#9ca3af"}, "cornerRadius": 4}},
        {"id": "plate_left", "name": "左杠铃片", "type": "shape", "transform": {"position": {"x": 300, "y": 390}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 15, "height": 50, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 2}},
        {"id": "plate_right", "name": "右杠铃片", "type": "shape", "transform": {"position": {"x": 500, "y": 390}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 15, "height": 50, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 2}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "举重抓举技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "weight_text", "name": "重量", "type": "text", "transform": {"position": {"x": 400, "y": 80}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "重量: 100kg", "fontFamily": "Arial", "fontSize": 20, "fontWeight": "bold", "color": "#fbbf24", "align": "center"}},
        {"id": "btn_setup", "name": "准备按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_setup_text", "name": "准备文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "准备", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_pull", "name": "提铃按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_pull_text", "name": "提铃文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "提铃", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_explode", "name": "发力按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_explode_text", "name": "发力文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "发力", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_catch", "name": "支撑按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_catch_text", "name": "支撑文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "支撑", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "snatch_full", "name": "完整抓举", "duration": 2500, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "barbell", "property": "position", "value": {"x": 400, "y": 390}, "easing": "linear"},
            {"time": 0, "targetId": "plate_left", "property": "position", "value": {"x": 300, "y": 390}, "easing": "linear"},
            {"time": 0, "targetId": "plate_right", "property": "position", "value": {"x": 500, "y": 390}, "easing": "linear"},
            {"time": 600, "targetId": "barbell", "property": "position", "value": {"x": 400, "y": 300}, "easing": "easeIn"},
            {"time": 600, "targetId": "plate_left", "property": "position", "value": {"x": 300, "y": 300}, "easing": "easeIn"},
            {"time": 600, "targetId": "plate_right", "property": "position", "value": {"x": 500, "y": 300}, "easing": "easeIn"},
            {"time": 1200, "targetId": "barbell", "property": "position", "value": {"x": 400, "y": 150}, "easing": "easeOut"},
            {"time": 1200, "targetId": "plate_left", "property": "position", "value": {"x": 300, "y": 150}, "easing": "easeOut"},
            {"time": 1200, "targetId": "plate_right", "property": "position", "value": {"x": 500, "y": 150}, "easing": "easeOut"},
            {"time": 1200, "targetId": "lifter", "property": "position", "value": {"x": 400, "y": 280}, "easing": "easeOut"},
            {"time": 2000, "targetId": "lifter", "property": "position", "value": {"x": 400, "y": 350}, "easing": "easeIn"},
            {"time": 2500, "targetId": "barbell", "property": "position", "value": {"x": 400, "y": 150}, "easing": "linear"},
            {"time": 2500, "targetId": "plate_left", "property": "position", "value": {"x": 300, "y": 150}, "easing": "linear"},
            {"time": 2500, "targetId": "plate_right", "property": "position", "value": {"x": 500, "y": 150}, "easing": "linear"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "snatch_full"}}]}
    ],
    "variables": [{"id": "weight", "name": "重量", "type": "number", "defaultValue": 100}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "举重", "抓举"], "category": "sports"}
}
