# 体育模板 Part 9 - 冬季运动（滑雪、滑冰）

SKIING_SLALOM_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_skiing_slalom",
    "name": "高山滑雪回转技术",
    "description": "展示高山滑雪回转的转弯、重心转移、立刃技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0c4a6e", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "slope", "name": "雪坡", "type": "shape", "transform": {"position": {"x": 400, "y": 300}, "rotation": 15, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 800, "height": 400, "fill": {"type": "solid", "color": "#f0f9ff"}}},
        {"id": "gate1", "name": "旗门1", "type": "shape", "transform": {"position": {"x": 250, "y": 150}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 1}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 8, "height": 60, "fill": {"type": "solid", "color": "#ef4444"}}},
        {"id": "gate2", "name": "旗门2", "type": "shape", "transform": {"position": {"x": 450, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 1}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 8, "height": 60, "fill": {"type": "solid", "color": "#3b82f6"}}},
        {"id": "gate3", "name": "旗门3", "type": "shape", "transform": {"position": {"x": 300, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 1}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 8, "height": 60, "fill": {"type": "solid", "color": "#ef4444"}}},
        {"id": "gate4", "name": "旗门4", "type": "shape", "transform": {"position": {"x": 550, "y": 420}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 1}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 8, "height": 60, "fill": {"type": "solid", "color": "#3b82f6"}}},
        {"id": "skier", "name": "滑雪者", "type": "shape", "transform": {"position": {"x": 150, "y": 100}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 20, "fill": {"type": "solid", "color": "#f59e0b"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "ski_left", "name": "左雪板", "type": "shape", "transform": {"position": {"x": 140, "y": 120}, "rotation": 30, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 8, "height": 50, "fill": {"type": "solid", "color": "#1f2937"}, "cornerRadius": 4}},
        {"id": "ski_right", "name": "右雪板", "type": "shape", "transform": {"position": {"x": 160, "y": 120}, "rotation": 30, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 8, "height": 50, "fill": {"type": "solid", "color": "#1f2937"}, "cornerRadius": 4}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "高山滑雪回转技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "time_text", "name": "计时", "type": "text", "transform": {"position": {"x": 700, "y": 80}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "00:00.00", "fontFamily": "Arial", "fontSize": 24, "fontWeight": "bold", "color": "#22c55e", "align": "center"}},
        {"id": "btn_carve", "name": "立刃按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_carve_text", "name": "立刃文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "立刃", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_turn", "name": "转弯按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_turn_text", "name": "转弯文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "转弯", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_weight", "name": "重心按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_weight_text", "name": "重心文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "重心", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "slalom_full", "name": "完整回转", "duration": 4000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "skier", "property": "position", "value": {"x": 150, "y": 100}, "easing": "linear"},
            {"time": 1000, "targetId": "skier", "property": "position", "value": {"x": 280, "y": 180}, "easing": "easeInOut"},
            {"time": 2000, "targetId": "skier", "property": "position", "value": {"x": 420, "y": 280}, "easing": "easeInOut"},
            {"time": 3000, "targetId": "skier", "property": "position", "value": {"x": 330, "y": 370}, "easing": "easeInOut"},
            {"time": 4000, "targetId": "skier", "property": "position", "value": {"x": 520, "y": 450}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "slalom_full"}}]}
    ],
    "variables": [{"id": "time", "name": "时间", "type": "number", "defaultValue": 0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "滑雪", "回转"], "category": "sports"}
}

FIGURE_SKATING_SPIN_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_figure_skating_spin",
    "name": "花样滑冰旋转技术",
    "description": "展示花样滑冰的直立旋转、蹲转、燕式旋转技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e3a5f", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "ice_rink", "name": "冰场", "type": "shape", "transform": {"position": {"x": 400, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 700, "height": 350, "fill": {"type": "solid", "color": "#bfdbfe"}, "stroke": {"color": "#3b82f6", "width": 4}, "cornerRadius": 8}},
        {"id": "center_circle", "name": "中心圆", "type": "shape", "transform": {"position": {"x": 400, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.5, "zIndex": 1, "interactive": False, "shape": {"shapeType": "circle", "radius": 80, "fill": {"type": "solid", "color": "transparent"}, "stroke": {"color": "#ef4444", "width": 2}}},
        {"id": "skater", "name": "滑冰者", "type": "shape", "transform": {"position": {"x": 400, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#ec4899"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "arm_left", "name": "左臂", "type": "shape", "transform": {"position": {"x": 375, "y": 270}, "rotation": -45, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 40, "height": 8, "fill": {"type": "solid", "color": "#ec4899"}, "cornerRadius": 4}},
        {"id": "arm_right", "name": "右臂", "type": "shape", "transform": {"position": {"x": 425, "y": 270}, "rotation": 45, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 40, "height": 8, "fill": {"type": "solid", "color": "#ec4899"}, "cornerRadius": 4}},
        {"id": "leg", "name": "腿", "type": "shape", "transform": {"position": {"x": 400, "y": 305}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 8, "interactive": False, "shape": {"shapeType": "rectangle", "width": 10, "height": 50, "fill": {"type": "solid", "color": "#ec4899"}, "cornerRadius": 5}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "花样滑冰旋转技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "spin_name", "name": "旋转名称", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "直立旋转", "fontFamily": "Arial", "fontSize": 18, "color": "#ec4899", "align": "center"}},
        {"id": "btn_upright", "name": "直立按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_upright_text", "name": "直立文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "直立旋转", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_sit", "name": "蹲转按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_sit_text", "name": "蹲转文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "蹲转", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_camel", "name": "燕式按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_camel_text", "name": "燕式文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "燕式旋转", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_layback", "name": "躺转按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_layback_text", "name": "躺转文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "躺转", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_play", "name": "播放按钮", "type": "shape", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_play_text", "name": "播放文字", "type": "text", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "播放", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "spin_upright", "name": "直立旋转", "duration": 2000, "loop": True, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "skater", "property": "rotation", "value": 0, "easing": "linear"},
            {"time": 500, "targetId": "skater", "property": "rotation", "value": 360, "easing": "linear"},
            {"time": 1000, "targetId": "skater", "property": "rotation", "value": 720, "easing": "linear"},
            {"time": 1500, "targetId": "skater", "property": "rotation", "value": 1080, "easing": "linear"},
            {"time": 2000, "targetId": "skater", "property": "rotation", "value": 1440, "easing": "linear"}
        ]}
    ],
    "interactions": [
        {"id": "click_play", "name": "点击播放", "enabled": True, "trigger": {"type": "click", "targetId": "btn_play"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "spin_upright"}}]}
    ],
    "variables": [{"id": "spin_type", "name": "旋转类型", "type": "string", "defaultValue": "upright"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "花样滑冰", "旋转"], "category": "sports"}
}
