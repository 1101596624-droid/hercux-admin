# 体育模板 Part 6 - 武术和格斗

TAEKWONDO_KICK_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_taekwondo_kick",
    "name": "跆拳道踢腿技术",
    "description": "展示跆拳道前踢、横踢、后踢等基本腿法",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e1b4b", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "mat", "name": "垫子", "type": "shape", "transform": {"position": {"x": 400, "y": 400}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 600, "height": 150, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 8}},
        {"id": "athlete", "name": "运动员", "type": "shape", "transform": {"position": {"x": 300, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 30, "fill": {"type": "solid", "color": "#ffffff"}, "stroke": {"color": "#ef4444", "width": 4}}},
        {"id": "leg", "name": "腿", "type": "shape", "transform": {"position": {"x": 300, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 15, "height": 60, "fill": {"type": "solid", "color": "#ffffff"}, "cornerRadius": 6}},
        {"id": "target", "name": "靶子", "type": "shape", "transform": {"position": {"x": 500, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "circle", "radius": 40, "fill": {"type": "solid", "color": "#ef4444"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "跆拳道踢腿技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "kick_name", "name": "踢法名称", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "前踢 (Ap Chagi)", "fontFamily": "Arial", "fontSize": 18, "color": "#22c55e", "align": "center"}},
        {"id": "btn_front", "name": "前踢按钮", "type": "shape", "transform": {"position": {"x": 150, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_front_text", "name": "前踢文字", "type": "text", "transform": {"position": {"x": 150, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "前踢", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_round", "name": "横踢按钮", "type": "shape", "transform": {"position": {"x": 290, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_round_text", "name": "横踢文字", "type": "text", "transform": {"position": {"x": 290, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "横踢", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_side", "name": "侧踢按钮", "type": "shape", "transform": {"position": {"x": 430, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_side_text", "name": "侧踢文字", "type": "text", "transform": {"position": {"x": 430, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "侧踢", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_back", "name": "后踢按钮", "type": "shape", "transform": {"position": {"x": 570, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_back_text", "name": "后踢文字", "type": "text", "transform": {"position": {"x": 570, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "后踢", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_spin", "name": "旋踢按钮", "type": "shape", "transform": {"position": {"x": 710, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_spin_text", "name": "旋踢文字", "type": "text", "transform": {"position": {"x": 710, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "旋踢", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "front_kick", "name": "前踢动画", "duration": 1000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "leg", "property": "rotation", "value": 0, "easing": "linear"},
            {"time": 300, "targetId": "leg", "property": "rotation", "value": -90, "easing": "easeOut"},
            {"time": 700, "targetId": "leg", "property": "rotation", "value": -90, "easing": "linear"},
            {"time": 1000, "targetId": "leg", "property": "rotation", "value": 0, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_front", "name": "点击前踢", "enabled": True, "trigger": {"type": "click", "targetId": "btn_front"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "front_kick"}}]}
    ],
    "variables": [{"id": "kick_type", "name": "踢法类型", "type": "string", "defaultValue": "front"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "跆拳道", "踢腿"], "category": "sports"}
}

BOXING_PUNCH_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_boxing_punch",
    "name": "拳击出拳技术",
    "description": "展示拳击直拳、勾拳、摆拳等基本拳法",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1c1917", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "ring", "name": "拳台", "type": "shape", "transform": {"position": {"x": 400, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 600, "height": 180, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ef4444", "width": 4}, "cornerRadius": 4}},
        {"id": "boxer", "name": "拳击手", "type": "shape", "transform": {"position": {"x": 300, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 35, "fill": {"type": "solid", "color": "#fbbf24"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "glove_left", "name": "左拳套", "type": "shape", "transform": {"position": {"x": 260, "y": 330}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 11, "interactive": False, "shape": {"shapeType": "circle", "radius": 18, "fill": {"type": "solid", "color": "#ef4444"}}},
        {"id": "glove_right", "name": "右拳套", "type": "shape", "transform": {"position": {"x": 340, "y": 330}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 11, "interactive": False, "shape": {"shapeType": "circle", "radius": 18, "fill": {"type": "solid", "color": "#ef4444"}}},
        {"id": "punching_bag", "name": "沙袋", "type": "shape", "transform": {"position": {"x": 550, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "rectangle", "width": 60, "height": 150, "fill": {"type": "solid", "color": "#78350f"}, "cornerRadius": 30}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "拳击出拳技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "punch_name", "name": "拳法名称", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "直拳 (Jab)", "fontFamily": "Arial", "fontSize": 18, "color": "#22c55e", "align": "center"}},
        {"id": "btn_jab", "name": "直拳按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_jab_text", "name": "直拳文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "直拳", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_cross", "name": "后手直拳按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_cross_text", "name": "后手直拳文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "后手直拳", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_hook", "name": "勾拳按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_hook_text", "name": "勾拳文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "勾拳", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_uppercut", "name": "上勾拳按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_uppercut_text", "name": "上勾拳文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "上勾拳", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_combo", "name": "组合拳按钮", "type": "shape", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_combo_text", "name": "组合拳文字", "type": "text", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "组合拳", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "jab_punch", "name": "直拳动画", "duration": 600, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "glove_left", "property": "position", "value": {"x": 260, "y": 330}, "easing": "linear"},
            {"time": 200, "targetId": "glove_left", "property": "position", "value": {"x": 450, "y": 300}, "easing": "easeOut"},
            {"time": 400, "targetId": "glove_left", "property": "position", "value": {"x": 450, "y": 300}, "easing": "linear"},
            {"time": 600, "targetId": "glove_left", "property": "position", "value": {"x": 260, "y": 330}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_jab", "name": "点击直拳", "enabled": True, "trigger": {"type": "click", "targetId": "btn_jab"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "jab_punch"}}]}
    ],
    "variables": [{"id": "punch_type", "name": "拳法类型", "type": "string", "defaultValue": "jab"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "拳击", "出拳"], "category": "sports"}
}
