# 体育模板 Part 16 - 高难度体操动作

# 体操自由操空翻
GYMNASTICS_FLOOR_FLIP_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_gymnastics_floor_flip",
    "name": "体操自由操空翻技术",
    "description": "展示前空翻、后空翻、侧空翻等高难度空翻动作",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e1b4b", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "floor", "name": "地板", "type": "shape", "transform": {"position": {"x": 400, "y": 420}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 760, "height": 60, "fill": {"type": "solid", "color": "#3730a3"}, "cornerRadius": 4}},
        {"id": "gymnast", "name": "体操运动员", "type": "shape", "transform": {"position": {"x": 150, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 22, "fill": {"type": "solid", "color": "#ec4899"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "trail1", "name": "轨迹1", "type": "shape", "transform": {"position": {"x": 300, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.3, "zIndex": 5, "interactive": False, "shape": {"shapeType": "circle", "radius": 15, "fill": {"type": "solid", "color": "#ec4899"}}},
        {"id": "trail2", "name": "轨迹2", "type": "shape", "transform": {"position": {"x": 400, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.3, "zIndex": 5, "interactive": False, "shape": {"shapeType": "circle", "radius": 15, "fill": {"type": "solid", "color": "#ec4899"}}},
        {"id": "trail3", "name": "轨迹3", "type": "shape", "transform": {"position": {"x": 500, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.3, "zIndex": 5, "interactive": False, "shape": {"shapeType": "circle", "radius": 15, "fill": {"type": "solid", "color": "#ec4899"}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "体操自由操空翻技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "flip_name", "name": "空翻名称", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "前空翻", "fontFamily": "Arial", "fontSize": 18, "color": "#ec4899", "align": "center"}},
        {"id": "btn_front", "name": "前空翻按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_front_text", "name": "前空翻文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "前空翻", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_back", "name": "后空翻按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_back_text", "name": "后空翻文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "后空翻", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_side", "name": "侧空翻按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_side_text", "name": "侧空翻文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "侧空翻", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_twist", "name": "转体按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_twist_text", "name": "转体文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "转体空翻", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_play", "name": "播放按钮", "type": "shape", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_play_text", "name": "播放文字", "type": "text", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "播放", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "front_flip", "name": "前空翻动画", "duration": 1500, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "gymnast", "property": "position", "value": {"x": 150, "y": 380}, "easing": "linear"},
            {"time": 0, "targetId": "gymnast", "property": "rotation", "value": 0, "easing": "linear"},
            {"time": 300, "targetId": "gymnast", "property": "position", "value": {"x": 250, "y": 300}, "easing": "easeOut"},
            {"time": 300, "targetId": "gymnast", "property": "rotation", "value": 180, "easing": "linear"},
            {"time": 600, "targetId": "gymnast", "property": "position", "value": {"x": 350, "y": 250}, "easing": "easeInOut"},
            {"time": 600, "targetId": "gymnast", "property": "rotation", "value": 360, "easing": "linear"},
            {"time": 900, "targetId": "gymnast", "property": "position", "value": {"x": 450, "y": 300}, "easing": "easeInOut"},
            {"time": 900, "targetId": "gymnast", "property": "rotation", "value": 540, "easing": "linear"},
            {"time": 1200, "targetId": "gymnast", "property": "position", "value": {"x": 550, "y": 380}, "easing": "easeIn"},
            {"time": 1200, "targetId": "gymnast", "property": "rotation", "value": 720, "easing": "linear"},
            {"time": 1500, "targetId": "gymnast", "property": "rotation", "value": 720, "easing": "linear"}
        ]}
    ],
    "interactions": [
        {"id": "click_play", "name": "点击播放", "enabled": True, "trigger": {"type": "click", "targetId": "btn_play"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "front_flip"}}]}
    ],
    "variables": [{"id": "flip_type", "name": "空翻类型", "type": "string", "defaultValue": "front"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "体操", "空翻"], "category": "sports"}
}

# 体操单杠大回环
GYMNASTICS_HIGH_BAR_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_gymnastics_high_bar",
    "name": "体操单杠大回环技术",
    "description": "展示单杠大回环、飞行动作、下法等高难度技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e1b4b", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "mat", "name": "落地垫", "type": "shape", "transform": {"position": {"x": 400, "y": 440}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 400, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 4}},
        {"id": "bar", "name": "单杠", "type": "shape", "transform": {"position": {"x": 400, "y": 180}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "rectangle", "width": 200, "height": 8, "fill": {"type": "solid", "color": "#9ca3af"}, "cornerRadius": 4}},
        {"id": "pole_left", "name": "左立柱", "type": "shape", "transform": {"position": {"x": 300, "y": 310}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 4, "interactive": False, "shape": {"shapeType": "rectangle", "width": 15, "height": 260, "fill": {"type": "solid", "color": "#6b7280"}}},
        {"id": "pole_right", "name": "右立柱", "type": "shape", "transform": {"position": {"x": 500, "y": 310}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 4, "interactive": False, "shape": {"shapeType": "rectangle", "width": 15, "height": 260, "fill": {"type": "solid", "color": "#6b7280"}}},
        {"id": "gymnast", "name": "体操运动员", "type": "shape", "transform": {"position": {"x": 400, "y": 220}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 20, "fill": {"type": "solid", "color": "#ef4444"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "body", "name": "身体", "type": "shape", "transform": {"position": {"x": 400, "y": 260}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 12, "height": 60, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 6}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "体操单杠大回环技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "move_name", "name": "动作名称", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "大回环", "fontFamily": "Arial", "fontSize": 18, "color": "#ef4444", "align": "center"}},
        {"id": "btn_giant", "name": "大回环按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_giant_text", "name": "大回环文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "大回环", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_release", "name": "飞行按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_release_text", "name": "飞行文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "飞行动作", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_dismount", "name": "下法按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_dismount_text", "name": "下法文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "下法", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_play", "name": "播放按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_play_text", "name": "播放文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "播放", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "giant_swing", "name": "大回环动画", "duration": 2000, "loop": True, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "gymnast", "property": "position", "value": {"x": 400, "y": 220}, "easing": "linear"},
            {"time": 0, "targetId": "body", "property": "rotation", "value": 0, "easing": "linear"},
            {"time": 500, "targetId": "gymnast", "property": "position", "value": {"x": 400, "y": 80}, "easing": "easeOut"},
            {"time": 500, "targetId": "body", "property": "rotation", "value": 180, "easing": "linear"},
            {"time": 1000, "targetId": "gymnast", "property": "position", "value": {"x": 400, "y": 140}, "easing": "easeIn"},
            {"time": 1000, "targetId": "body", "property": "rotation", "value": 180, "easing": "linear"},
            {"time": 1500, "targetId": "gymnast", "property": "position", "value": {"x": 400, "y": 280}, "easing": "easeOut"},
            {"time": 1500, "targetId": "body", "property": "rotation", "value": 360, "easing": "linear"},
            {"time": 2000, "targetId": "gymnast", "property": "position", "value": {"x": 400, "y": 220}, "easing": "easeIn"},
            {"time": 2000, "targetId": "body", "property": "rotation", "value": 360, "easing": "linear"}
        ]}
    ],
    "interactions": [
        {"id": "click_play", "name": "点击播放", "enabled": True, "trigger": {"type": "click", "targetId": "btn_play"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "giant_swing"}}]}
    ],
    "variables": [{"id": "move_type", "name": "动作类型", "type": "string", "defaultValue": "giant"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "体操", "单杠"], "category": "sports"}
}
