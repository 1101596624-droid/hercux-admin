# 体育模板 Part 18 - 高难度球类动作

# 篮球扣篮
BASKETBALL_DUNK_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_basketball_dunk",
    "name": "篮球扣篮技术",
    "description": "展示单手扣篮、双手扣篮、战斧扣篮、风车扣篮等高难度扣篮",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e3a5f", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "court", "name": "球场", "type": "shape", "transform": {"position": {"x": 400, "y": 400}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 760, "height": 150, "fill": {"type": "solid", "color": "#78350f"}, "cornerRadius": 4}},
        {"id": "backboard", "name": "篮板", "type": "shape", "transform": {"position": {"x": 650, "y": 180}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 3, "interactive": False, "shape": {"shapeType": "rectangle", "width": 100, "height": 70, "fill": {"type": "solid", "color": "#ffffff"}, "stroke": {"color": "#ef4444", "width": 3}}},
        {"id": "rim", "name": "篮筐", "type": "shape", "transform": {"position": {"x": 600, "y": 200}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 4, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "transparent"}, "stroke": {"color": "#ef4444", "width": 4}}},
        {"id": "pole", "name": "篮架", "type": "shape", "transform": {"position": {"x": 700, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 15, "height": 180, "fill": {"type": "solid", "color": "#6b7280"}}},
        {"id": "player", "name": "球员", "type": "shape", "transform": {"position": {"x": 200, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "ball", "name": "篮球", "type": "shape", "transform": {"position": {"x": 230, "y": 330}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 11, "interactive": False, "shape": {"shapeType": "circle", "radius": 15, "fill": {"type": "solid", "color": "#f97316"}, "stroke": {"color": "#1f2937", "width": 2}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "篮球扣篮技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "dunk_name", "name": "扣篮名称", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "战斧扣篮", "fontFamily": "Arial", "fontSize": 18, "color": "#f97316", "align": "center"}},
        {"id": "btn_one_hand", "name": "单手按钮", "type": "shape", "transform": {"position": {"x": 100, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_one_hand_text", "name": "单手文字", "type": "text", "transform": {"position": {"x": 100, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "单手扣", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_two_hand", "name": "双手按钮", "type": "shape", "transform": {"position": {"x": 220, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_two_hand_text", "name": "双手文字", "type": "text", "transform": {"position": {"x": 220, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "双手扣", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_tomahawk", "name": "战斧按钮", "type": "shape", "transform": {"position": {"x": 340, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_tomahawk_text", "name": "战斧文字", "type": "text", "transform": {"position": {"x": 340, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "战斧扣", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_windmill", "name": "风车按钮", "type": "shape", "transform": {"position": {"x": 460, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_windmill_text", "name": "风车文字", "type": "text", "transform": {"position": {"x": 460, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "风车扣", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_360", "name": "360按钮", "type": "shape", "transform": {"position": {"x": 580, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#ec4899"}, "cornerRadius": 20}},
        {"id": "btn_360_text", "name": "360文字", "type": "text", "transform": {"position": {"x": 580, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "360扣", "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_play", "name": "播放按钮", "type": "shape", "transform": {"position": {"x": 700, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_play_text", "name": "播放文字", "type": "text", "transform": {"position": {"x": 700, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "播放", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "tomahawk_dunk", "name": "战斧扣篮", "duration": 2000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "player", "property": "position", "value": {"x": 200, "y": 350}, "easing": "linear"},
            {"time": 0, "targetId": "ball", "property": "position", "value": {"x": 230, "y": 330}, "easing": "linear"},
            {"time": 500, "targetId": "player", "property": "position", "value": {"x": 400, "y": 350}, "easing": "easeIn"},
            {"time": 500, "targetId": "ball", "property": "position", "value": {"x": 430, "y": 330}, "easing": "easeIn"},
            {"time": 800, "targetId": "player", "property": "position", "value": {"x": 500, "y": 250}, "easing": "easeOut"},
            {"time": 800, "targetId": "ball", "property": "position", "value": {"x": 530, "y": 180}, "easing": "easeOut"},
            {"time": 1200, "targetId": "player", "property": "position", "value": {"x": 570, "y": 180}, "easing": "easeInOut"},
            {"time": 1200, "targetId": "ball", "property": "position", "value": {"x": 600, "y": 120}, "easing": "easeOut"},
            {"time": 1500, "targetId": "ball", "property": "position", "value": {"x": 600, "y": 200}, "easing": "easeIn"},
            {"time": 1800, "targetId": "player", "property": "position", "value": {"x": 580, "y": 350}, "easing": "easeIn"},
            {"time": 2000, "targetId": "ball", "property": "position", "value": {"x": 600, "y": 350}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_play", "name": "点击播放", "enabled": True, "trigger": {"type": "click", "targetId": "btn_play"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "tomahawk_dunk"}}]}
    ],
    "variables": [{"id": "dunk_type", "name": "扣篮类型", "type": "string", "defaultValue": "tomahawk"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "篮球", "扣篮"], "category": "sports"}
}

# 足球倒钩射门
FOOTBALL_BICYCLE_KICK_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_football_bicycle_kick",
    "name": "足球倒钩射门技术",
    "description": "展示倒钩射门的起跳、腾空、击球、落地技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#065f46", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "field", "name": "球场", "type": "shape", "transform": {"position": {"x": 400, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 760, "height": 180, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 4}},
        {"id": "goal", "name": "球门", "type": "shape", "transform": {"position": {"x": 700, "y": 320}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 30, "height": 150, "fill": {"type": "solid", "color": "#ffffff"}, "stroke": {"color": "#1f2937", "width": 3}}},
        {"id": "goal_net", "name": "球网", "type": "shape", "transform": {"position": {"x": 720, "y": 320}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.5, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 40, "height": 140, "fill": {"type": "solid", "color": "#9ca3af"}}},
        {"id": "player", "name": "球员", "type": "shape", "transform": {"position": {"x": 300, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 22, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "ball", "name": "足球", "type": "shape", "transform": {"position": {"x": 350, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 11, "interactive": False, "shape": {"shapeType": "circle", "radius": 15, "fill": {"type": "solid", "color": "#ffffff"}, "stroke": {"color": "#1f2937", "width": 2}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "足球倒钩射门技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_jump", "name": "起跳按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_jump_text", "name": "起跳文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "起跳", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_flip", "name": "翻转按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_flip_text", "name": "翻转文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "翻转", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_kick", "name": "击球按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_kick_text", "name": "击球文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "击球", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "bicycle_kick", "name": "倒钩射门", "duration": 2000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "player", "property": "position", "value": {"x": 300, "y": 350}, "easing": "linear"},
            {"time": 0, "targetId": "player", "property": "rotation", "value": 0, "easing": "linear"},
            {"time": 300, "targetId": "player", "property": "position", "value": {"x": 350, "y": 280}, "easing": "easeOut"},
            {"time": 300, "targetId": "player", "property": "rotation", "value": -45, "easing": "linear"},
            {"time": 600, "targetId": "player", "property": "position", "value": {"x": 380, "y": 220}, "easing": "easeOut"},
            {"time": 600, "targetId": "player", "property": "rotation", "value": -90, "easing": "linear"},
            {"time": 900, "targetId": "player", "property": "position", "value": {"x": 400, "y": 200}, "easing": "easeInOut"},
            {"time": 900, "targetId": "player", "property": "rotation", "value": -180, "easing": "linear"},
            {"time": 900, "targetId": "ball", "property": "position", "value": {"x": 500, "y": 250}, "easing": "easeOut"},
            {"time": 1200, "targetId": "ball", "property": "position", "value": {"x": 620, "y": 300}, "easing": "linear"},
            {"time": 1400, "targetId": "player", "property": "position", "value": {"x": 420, "y": 280}, "easing": "easeIn"},
            {"time": 1400, "targetId": "player", "property": "rotation", "value": -270, "easing": "linear"},
            {"time": 1500, "targetId": "ball", "property": "position", "value": {"x": 700, "y": 320}, "easing": "easeIn"},
            {"time": 1800, "targetId": "player", "property": "position", "value": {"x": 430, "y": 350}, "easing": "easeIn"},
            {"time": 1800, "targetId": "player", "property": "rotation", "value": -360, "easing": "linear"},
            {"time": 2000, "targetId": "player", "property": "rotation", "value": -360, "easing": "linear"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "bicycle_kick"}}]}
    ],
    "variables": [{"id": "phase", "name": "阶段", "type": "string", "defaultValue": "ready"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "足球", "倒钩"], "category": "sports"}
}
