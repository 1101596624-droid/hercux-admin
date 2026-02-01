# 体育模板 Part 17 - 高难度跳水和滑冰动作

# 跳水转体动作
DIVING_TWIST_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_diving_twist",
    "name": "跳水转体技术",
    "description": "展示跳水的向前转体、向后转体、向内转体等高难度动作",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0c4a6e", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "pool", "name": "泳池", "type": "shape", "transform": {"position": {"x": 500, "y": 400}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 500, "height": 150, "fill": {"type": "solid", "color": "#0369a1"}, "stroke": {"color": "#0ea5e9", "width": 3}, "cornerRadius": 4}},
        {"id": "platform_10m", "name": "10米台", "type": "shape", "transform": {"position": {"x": 100, "y": 100}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 100, "height": 15, "fill": {"type": "solid", "color": "#6b7280"}}},
        {"id": "platform_support", "name": "支架", "type": "shape", "transform": {"position": {"x": 60, "y": 225}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 25, "height": 250, "fill": {"type": "solid", "color": "#4b5563"}}},
        {"id": "diver", "name": "跳水运动员", "type": "shape", "transform": {"position": {"x": 130, "y": 85}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 18, "fill": {"type": "solid", "color": "#ef4444"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "跳水转体技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "dive_code", "name": "动作代码", "type": "text", "transform": {"position": {"x": 700, "y": 80}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "5253B", "fontFamily": "Arial", "fontSize": 20, "fontWeight": "bold", "color": "#fbbf24", "align": "center"}},
        {"id": "difficulty", "name": "难度系数", "type": "text", "transform": {"position": {"x": 700, "y": 110}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "难度: 3.2", "fontFamily": "Arial", "fontSize": 16, "color": "#22c55e", "align": "center"}},
        {"id": "btn_forward", "name": "向前按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_forward_text", "name": "向前文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "向前转体", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_back", "name": "向后按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_back_text", "name": "向后文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "向后转体", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_inward", "name": "向内按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_inward_text", "name": "向内文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "向内转体", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_play", "name": "播放按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_play_text", "name": "播放文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "播放", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "twist_dive", "name": "转体跳水", "duration": 2500, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "diver", "property": "position", "value": {"x": 130, "y": 85}, "easing": "linear"},
            {"time": 0, "targetId": "diver", "property": "rotation", "value": 0, "easing": "linear"},
            {"time": 300, "targetId": "diver", "property": "position", "value": {"x": 200, "y": 50}, "easing": "easeOut"},
            {"time": 600, "targetId": "diver", "property": "position", "value": {"x": 300, "y": 120}, "easing": "easeIn"},
            {"time": 600, "targetId": "diver", "property": "rotation", "value": 360, "easing": "linear"},
            {"time": 1000, "targetId": "diver", "property": "position", "value": {"x": 380, "y": 200}, "easing": "linear"},
            {"time": 1000, "targetId": "diver", "property": "rotation", "value": 720, "easing": "linear"},
            {"time": 1400, "targetId": "diver", "property": "position", "value": {"x": 450, "y": 280}, "easing": "linear"},
            {"time": 1400, "targetId": "diver", "property": "rotation", "value": 1080, "easing": "linear"},
            {"time": 1800, "targetId": "diver", "property": "position", "value": {"x": 500, "y": 350}, "easing": "easeIn"},
            {"time": 1800, "targetId": "diver", "property": "rotation", "value": 1260, "easing": "linear"},
            {"time": 2200, "targetId": "diver", "property": "position", "value": {"x": 500, "y": 400}, "easing": "easeIn"},
            {"time": 2500, "targetId": "diver", "property": "position", "value": {"x": 500, "y": 420}, "easing": "linear"}
        ]}
    ],
    "interactions": [
        {"id": "click_play", "name": "点击播放", "enabled": True, "trigger": {"type": "click", "targetId": "btn_play"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "twist_dive"}}]}
    ],
    "variables": [{"id": "dive_type", "name": "跳水类型", "type": "string", "defaultValue": "forward_twist"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "跳水", "转体"], "category": "sports"}
}

# 花样滑冰跳跃
FIGURE_SKATING_JUMP_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_figure_skating_jump",
    "name": "花样滑冰跳跃技术",
    "description": "展示阿克塞尔跳、勾手跳、后外点冰跳等高难度跳跃",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e3a5f", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "ice_rink", "name": "冰场", "type": "shape", "transform": {"position": {"x": 400, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 700, "height": 320, "fill": {"type": "solid", "color": "#bfdbfe"}, "stroke": {"color": "#3b82f6", "width": 4}, "cornerRadius": 8}},
        {"id": "skater", "name": "滑冰者", "type": "shape", "transform": {"position": {"x": 200, "y": 320}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 22, "fill": {"type": "solid", "color": "#ec4899"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "trail", "name": "滑行轨迹", "type": "shape", "transform": {"position": {"x": 400, "y": 320}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.3, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": -200, "y": 0}, {"x": 200, "y": 0}], "stroke": {"color": "#ec4899", "width": 3, "dashArray": [10, 5]}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "花样滑冰跳跃技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "jump_name", "name": "跳跃名称", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "三周阿克塞尔 (3A)", "fontFamily": "Arial", "fontSize": 18, "color": "#ec4899", "align": "center"}},
        {"id": "btn_axel", "name": "阿克塞尔按钮", "type": "shape", "transform": {"position": {"x": 100, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_axel_text", "name": "阿克塞尔文字", "type": "text", "transform": {"position": {"x": 100, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "阿克塞尔", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_lutz", "name": "勾手跳按钮", "type": "shape", "transform": {"position": {"x": 220, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_lutz_text", "name": "勾手跳文字", "type": "text", "transform": {"position": {"x": 220, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "勾手跳", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_flip", "name": "后内点冰按钮", "type": "shape", "transform": {"position": {"x": 340, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_flip_text", "name": "后内点冰文字", "type": "text", "transform": {"position": {"x": 340, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "后内点冰", "fontFamily": "Arial", "fontSize": 11, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_toe", "name": "后外点冰按钮", "type": "shape", "transform": {"position": {"x": 460, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_toe_text", "name": "后外点冰文字", "type": "text", "transform": {"position": {"x": 460, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "后外点冰", "fontFamily": "Arial", "fontSize": 11, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_salchow", "name": "后内跳按钮", "type": "shape", "transform": {"position": {"x": 580, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#ec4899"}, "cornerRadius": 20}},
        {"id": "btn_salchow_text", "name": "后内跳文字", "type": "text", "transform": {"position": {"x": 580, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "后内跳", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_play", "name": "播放按钮", "type": "shape", "transform": {"position": {"x": 700, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_play_text", "name": "播放文字", "type": "text", "transform": {"position": {"x": 700, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "播放", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "triple_axel", "name": "三周阿克塞尔", "duration": 2000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "skater", "property": "position", "value": {"x": 200, "y": 320}, "easing": "linear"},
            {"time": 0, "targetId": "skater", "property": "rotation", "value": 0, "easing": "linear"},
            {"time": 400, "targetId": "skater", "property": "position", "value": {"x": 320, "y": 320}, "easing": "easeIn"},
            {"time": 600, "targetId": "skater", "property": "position", "value": {"x": 400, "y": 180}, "easing": "easeOut"},
            {"time": 600, "targetId": "skater", "property": "rotation", "value": 540, "easing": "linear"},
            {"time": 1000, "targetId": "skater", "property": "position", "value": {"x": 480, "y": 160}, "easing": "easeInOut"},
            {"time": 1000, "targetId": "skater", "property": "rotation", "value": 900, "easing": "linear"},
            {"time": 1400, "targetId": "skater", "property": "position", "value": {"x": 550, "y": 220}, "easing": "easeIn"},
            {"time": 1400, "targetId": "skater", "property": "rotation", "value": 1260, "easing": "linear"},
            {"time": 1800, "targetId": "skater", "property": "position", "value": {"x": 600, "y": 320}, "easing": "easeIn"},
            {"time": 1800, "targetId": "skater", "property": "rotation", "value": 1260, "easing": "linear"},
            {"time": 2000, "targetId": "skater", "property": "rotation", "value": 1260, "easing": "linear"}
        ]}
    ],
    "interactions": [
        {"id": "click_play", "name": "点击播放", "enabled": True, "trigger": {"type": "click", "targetId": "btn_play"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "triple_axel"}}]}
    ],
    "variables": [{"id": "jump_type", "name": "跳跃类型", "type": "string", "defaultValue": "axel"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "花样滑冰", "跳跃"], "category": "sports"}
}
