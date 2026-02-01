# 体育模板 Part 7 - 羽毛球和乒乓球

BADMINTON_SMASH_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_badminton_smash",
    "name": "羽毛球扣杀技术",
    "description": "展示羽毛球扣杀的准备、起跳、挥拍、击球技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e3a5f", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "court", "name": "球场", "type": "shape", "transform": {"position": {"x": 400, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 700, "height": 200, "fill": {"type": "solid", "color": "#22c55e"}, "stroke": {"color": "#ffffff", "width": 3}, "cornerRadius": 4}},
        {"id": "net", "name": "球网", "type": "shape", "transform": {"position": {"x": 400, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "rectangle", "width": 6, "height": 120, "fill": {"type": "solid", "color": "#ffffff"}}},
        {"id": "player", "name": "球员", "type": "shape", "transform": {"position": {"x": 200, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "racket", "name": "球拍", "type": "shape", "transform": {"position": {"x": 220, "y": 330}, "rotation": -30, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 11, "interactive": False, "shape": {"shapeType": "rectangle", "width": 70, "height": 10, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 5}},
        {"id": "shuttlecock", "name": "羽毛球", "type": "shape", "transform": {"position": {"x": 300, "y": 150}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 12, "interactive": False, "shape": {"shapeType": "circle", "radius": 10, "fill": {"type": "solid", "color": "#ffffff"}, "stroke": {"color": "#e5e7eb", "width": 2}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "羽毛球扣杀技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "phase_text", "name": "阶段", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "准备姿势", "fontFamily": "Arial", "fontSize": 18, "color": "#22c55e", "align": "center"}},
        {"id": "btn_ready", "name": "准备按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_ready_text", "name": "准备文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "准备", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_jump", "name": "起跳按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_jump_text", "name": "起跳文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "起跳", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_swing", "name": "挥拍按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_swing_text", "name": "挥拍文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "挥拍", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_smash", "name": "扣杀按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_smash_text", "name": "扣杀文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "扣杀", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "smash_full", "name": "完整扣杀", "duration": 2000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "player", "property": "position", "value": {"x": 200, "y": 350}, "easing": "linear"},
            {"time": 400, "targetId": "player", "property": "position", "value": {"x": 250, "y": 350}, "easing": "easeIn"},
            {"time": 800, "targetId": "player", "property": "position", "value": {"x": 280, "y": 200}, "easing": "easeOut"},
            {"time": 1000, "targetId": "racket", "property": "rotation", "value": -120, "easing": "easeIn"},
            {"time": 1200, "targetId": "shuttlecock", "property": "position", "value": {"x": 500, "y": 350}, "easing": "easeIn"},
            {"time": 1600, "targetId": "player", "property": "position", "value": {"x": 280, "y": 350}, "easing": "easeIn"},
            {"time": 2000, "targetId": "racket", "property": "rotation", "value": -30, "easing": "easeOut"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "smash_full"}}]}
    ],
    "variables": [{"id": "phase", "name": "阶段", "type": "string", "defaultValue": "ready"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "羽毛球", "扣杀"], "category": "sports"}
}

TABLE_TENNIS_SERVE_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_table_tennis_serve",
    "name": "乒乓球发球技术",
    "description": "展示乒乓球发球的抛球、引拍、击球、落点控制",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e3a5f", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "table", "name": "球台", "type": "shape", "transform": {"position": {"x": 400, "y": 320}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 500, "height": 180, "fill": {"type": "solid", "color": "#1d4ed8"}, "stroke": {"color": "#ffffff", "width": 3}, "cornerRadius": 4}},
        {"id": "net", "name": "球网", "type": "shape", "transform": {"position": {"x": 400, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "rectangle", "width": 6, "height": 40, "fill": {"type": "solid", "color": "#ffffff"}}},
        {"id": "center_line", "name": "中线", "type": "shape", "transform": {"position": {"x": 400, "y": 320}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.8, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": 0, "y": -90}, {"x": 0, "y": 90}], "stroke": {"color": "#ffffff", "width": 2}}},
        {"id": "player", "name": "球员", "type": "shape", "transform": {"position": {"x": 150, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 22, "fill": {"type": "solid", "color": "#ef4444"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "paddle", "name": "球拍", "type": "shape", "transform": {"position": {"x": 175, "y": 340}, "rotation": -20, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 11, "interactive": False, "shape": {"shapeType": "circle", "radius": 20, "fill": {"type": "solid", "color": "#dc2626"}, "stroke": {"color": "#1f2937", "width": 3}}},
        {"id": "ball", "name": "乒乓球", "type": "shape", "transform": {"position": {"x": 180, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 12, "interactive": False, "shape": {"shapeType": "circle", "radius": 10, "fill": {"type": "solid", "color": "#f97316"}, "stroke": {"color": "#ffffff", "width": 1}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "乒乓球发球技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "serve_type", "name": "发球类型", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "正手发球", "fontFamily": "Arial", "fontSize": 18, "color": "#22c55e", "align": "center"}},
        {"id": "btn_toss", "name": "抛球按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_toss_text", "name": "抛球文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "抛球", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_backswing", "name": "引拍按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_backswing_text", "name": "引拍文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "引拍", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_hit", "name": "击球按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_hit_text", "name": "击球文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "击球", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_spin", "name": "旋转按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_spin_text", "name": "旋转文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "旋转", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "serve_full", "name": "完整发球", "duration": 1500, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "ball", "property": "position", "value": {"x": 180, "y": 280}, "easing": "linear"},
            {"time": 300, "targetId": "ball", "property": "position", "value": {"x": 180, "y": 200}, "easing": "easeOut"},
            {"time": 500, "targetId": "paddle", "property": "rotation", "value": -60, "easing": "easeIn"},
            {"time": 700, "targetId": "ball", "property": "position", "value": {"x": 300, "y": 300}, "easing": "easeIn"},
            {"time": 1000, "targetId": "ball", "property": "position", "value": {"x": 500, "y": 280}, "easing": "easeOut"},
            {"time": 1200, "targetId": "ball", "property": "position", "value": {"x": 600, "y": 350}, "easing": "easeIn"},
            {"time": 1500, "targetId": "paddle", "property": "rotation", "value": -20, "easing": "easeOut"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "serve_full"}}]}
    ],
    "variables": [{"id": "serve_type", "name": "发球类型", "type": "string", "defaultValue": "forehand"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "乒乓球", "发球"], "category": "sports"}
}
