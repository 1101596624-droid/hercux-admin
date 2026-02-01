# 体育模板 Part 14 - 接力和铁饼

RELAY_RACE_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_relay_race",
    "name": "接力赛跑技术",
    "description": "展示接力赛跑的交接棒技术和配合",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "track", "name": "跑道", "type": "shape", "transform": {"position": {"x": 400, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 760, "height": 120, "fill": {"type": "solid", "color": "#dc2626"}, "stroke": {"color": "#ffffff", "width": 2}, "cornerRadius": 4}},
        {"id": "exchange_zone", "name": "交接区", "type": "shape", "transform": {"position": {"x": 400, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.3, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 100, "height": 120, "fill": {"type": "solid", "color": "#fbbf24"}}},
        {"id": "runner1", "name": "第一棒", "type": "shape", "transform": {"position": {"x": 150, "y": 330}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 22, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "runner2", "name": "第二棒", "type": "shape", "transform": {"position": {"x": 380, "y": 330}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 22, "fill": {"type": "solid", "color": "#22c55e"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "baton", "name": "接力棒", "type": "shape", "transform": {"position": {"x": 175, "y": 330}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 11, "interactive": False, "shape": {"shapeType": "rectangle", "width": 30, "height": 8, "fill": {"type": "solid", "color": "#fbbf24"}, "cornerRadius": 4}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "接力赛跑技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "phase_text", "name": "阶段", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "准备交接", "fontFamily": "Arial", "fontSize": 18, "color": "#fbbf24", "align": "center"}},
        {"id": "btn_approach", "name": "接近按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_approach_text", "name": "接近文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "接近", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_exchange", "name": "交接按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_exchange_text", "name": "交接文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "交接", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_accelerate", "name": "加速按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_accelerate_text", "name": "加速文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "加速", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "relay_full", "name": "完整交接", "duration": 3000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "runner1", "property": "position", "value": {"x": 150, "y": 330}, "easing": "linear"},
            {"time": 0, "targetId": "baton", "property": "position", "value": {"x": 175, "y": 330}, "easing": "linear"},
            {"time": 800, "targetId": "runner1", "property": "position", "value": {"x": 350, "y": 330}, "easing": "easeIn"},
            {"time": 800, "targetId": "baton", "property": "position", "value": {"x": 375, "y": 330}, "easing": "easeIn"},
            {"time": 800, "targetId": "runner2", "property": "position", "value": {"x": 400, "y": 330}, "easing": "easeIn"},
            {"time": 1200, "targetId": "runner1", "property": "position", "value": {"x": 400, "y": 330}, "easing": "linear"},
            {"time": 1200, "targetId": "baton", "property": "position", "value": {"x": 425, "y": 330}, "easing": "linear"},
            {"time": 1600, "targetId": "runner2", "property": "position", "value": {"x": 500, "y": 330}, "easing": "easeIn"},
            {"time": 1600, "targetId": "baton", "property": "position", "value": {"x": 525, "y": 330}, "easing": "easeIn"},
            {"time": 2400, "targetId": "runner2", "property": "position", "value": {"x": 650, "y": 330}, "easing": "easeOut"},
            {"time": 2400, "targetId": "baton", "property": "position", "value": {"x": 675, "y": 330}, "easing": "easeOut"},
            {"time": 3000, "targetId": "runner2", "property": "position", "value": {"x": 750, "y": 330}, "easing": "linear"},
            {"time": 3000, "targetId": "baton", "property": "position", "value": {"x": 775, "y": 330}, "easing": "linear"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "relay_full"}}]}
    ],
    "variables": [{"id": "phase", "name": "阶段", "type": "string", "defaultValue": "ready"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "田径", "接力"], "category": "sports"}
}

DISCUS_THROW_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_discus_throw",
    "name": "铁饼投掷技术",
    "description": "展示铁饼投掷的握饼、旋转、出手技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "circle", "name": "投掷圈", "type": "shape", "transform": {"position": {"x": 200, "y": 320}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "circle", "radius": 110, "fill": {"type": "solid", "color": "#475569"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "sector_line1", "name": "扇形线1", "type": "shape", "transform": {"position": {"x": 200, "y": 320}, "rotation": 17, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 0.5, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": 0, "y": 0}, {"x": 550, "y": 0}], "stroke": {"color": "#ffffff", "width": 2}}},
        {"id": "sector_line2", "name": "扇形线2", "type": "shape", "transform": {"position": {"x": 200, "y": 320}, "rotation": -17, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 0.5, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": 0, "y": 0}, {"x": 550, "y": 0}], "stroke": {"color": "#ffffff", "width": 2}}},
        {"id": "athlete", "name": "运动员", "type": "shape", "transform": {"position": {"x": 200, "y": 320}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 28, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "discus", "name": "铁饼", "type": "shape", "transform": {"position": {"x": 230, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 11, "interactive": False, "shape": {"shapeType": "circle", "radius": 18, "fill": {"type": "solid", "color": "#f59e0b"}, "stroke": {"color": "#78350f", "width": 3}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "铁饼投掷技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "distance_text", "name": "距离", "type": "text", "transform": {"position": {"x": 600, "y": 200}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "距离: 0.00m", "fontFamily": "Arial", "fontSize": 20, "fontWeight": "bold", "color": "#22c55e", "align": "center"}},
        {"id": "btn_grip", "name": "握饼按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_grip_text", "name": "握饼文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "握饼", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_spin", "name": "旋转按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_spin_text", "name": "旋转文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "旋转", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_release", "name": "出手按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_release_text", "name": "出手文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "出手", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "throw_full", "name": "完整投掷", "duration": 2500, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "athlete", "property": "rotation", "value": 0, "easing": "linear"},
            {"time": 0, "targetId": "discus", "property": "position", "value": {"x": 230, "y": 300}, "easing": "linear"},
            {"time": 600, "targetId": "athlete", "property": "rotation", "value": 360, "easing": "easeIn"},
            {"time": 1200, "targetId": "athlete", "property": "rotation", "value": 720, "easing": "easeOut"},
            {"time": 1400, "targetId": "discus", "property": "position", "value": {"x": 400, "y": 250}, "easing": "easeOut"},
            {"time": 1800, "targetId": "discus", "property": "position", "value": {"x": 550, "y": 280}, "easing": "linear"},
            {"time": 2200, "targetId": "discus", "property": "position", "value": {"x": 680, "y": 320}, "easing": "easeIn"},
            {"time": 2500, "targetId": "discus", "property": "position", "value": {"x": 720, "y": 350}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "throw_full"}}]}
    ],
    "variables": [{"id": "distance", "name": "距离", "type": "number", "defaultValue": 0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "田径", "铁饼"], "category": "sports"}
}
