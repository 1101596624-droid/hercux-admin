# 体育模板 Part 11 - 射箭和击剑

ARCHERY_SHOT_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_archery_shot",
    "name": "射箭技术分析",
    "description": "展示射箭的站位、搭箭、拉弓、瞄准、释放技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e3a5f", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "target", "name": "靶子", "type": "shape", "transform": {"position": {"x": 650, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "circle", "radius": 80, "fill": {"type": "solid", "color": "#ffffff"}, "stroke": {"color": "#1f2937", "width": 2}}},
        {"id": "target_red", "name": "红环", "type": "shape", "transform": {"position": {"x": 650, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 3, "interactive": False, "shape": {"shapeType": "circle", "radius": 55, "fill": {"type": "solid", "color": "#ef4444"}}},
        {"id": "target_blue", "name": "蓝环", "type": "shape", "transform": {"position": {"x": 650, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 4, "interactive": False, "shape": {"shapeType": "circle", "radius": 35, "fill": {"type": "solid", "color": "#3b82f6"}}},
        {"id": "target_yellow", "name": "黄心", "type": "shape", "transform": {"position": {"x": 650, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "circle", "radius": 15, "fill": {"type": "solid", "color": "#fbbf24"}}},
        {"id": "archer", "name": "射手", "type": "shape", "transform": {"position": {"x": 150, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#22c55e"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "bow", "name": "弓", "type": "shape", "transform": {"position": {"x": 180, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 10, "height": 100, "fill": {"type": "solid", "color": "#78350f"}, "cornerRadius": 5}},
        {"id": "arrow", "name": "箭", "type": "shape", "transform": {"position": {"x": 200, "y": 280}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 11, "interactive": False, "shape": {"shapeType": "rectangle", "width": 80, "height": 4, "fill": {"type": "solid", "color": "#6b7280"}, "cornerRadius": 2}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "射箭技术分析", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "score_text", "name": "得分", "type": "text", "transform": {"position": {"x": 650, "y": 400}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "得分: 0", "fontFamily": "Arial", "fontSize": 20, "fontWeight": "bold", "color": "#fbbf24", "align": "center"}},
        {"id": "btn_stance", "name": "站位按钮", "type": "shape", "transform": {"position": {"x": 100, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_stance_text", "name": "站位文字", "type": "text", "transform": {"position": {"x": 100, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "站位", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_nock", "name": "搭箭按钮", "type": "shape", "transform": {"position": {"x": 220, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_nock_text", "name": "搭箭文字", "type": "text", "transform": {"position": {"x": 220, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "搭箭", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_draw", "name": "拉弓按钮", "type": "shape", "transform": {"position": {"x": 340, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_draw_text", "name": "拉弓文字", "type": "text", "transform": {"position": {"x": 340, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "拉弓", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_aim", "name": "瞄准按钮", "type": "shape", "transform": {"position": {"x": 460, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_aim_text", "name": "瞄准文字", "type": "text", "transform": {"position": {"x": 460, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "瞄准", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_release", "name": "释放按钮", "type": "shape", "transform": {"position": {"x": 580, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_release_text", "name": "释放文字", "type": "text", "transform": {"position": {"x": 580, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "释放", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 700, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#ec4899"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 700, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "shot_full", "name": "完整射箭", "duration": 2000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "arrow", "property": "position", "value": {"x": 200, "y": 280}, "easing": "linear"},
            {"time": 500, "targetId": "bow", "property": "scale", "value": {"x": 1.1, "y": 0.9}, "easing": "easeIn"},
            {"time": 800, "targetId": "arrow", "property": "position", "value": {"x": 400, "y": 280}, "easing": "easeOut"},
            {"time": 1200, "targetId": "arrow", "property": "position", "value": {"x": 600, "y": 280}, "easing": "linear"},
            {"time": 1500, "targetId": "arrow", "property": "position", "value": {"x": 650, "y": 280}, "easing": "easeIn"},
            {"time": 2000, "targetId": "bow", "property": "scale", "value": {"x": 1, "y": 1}, "easing": "easeOut"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "shot_full"}}]}
    ],
    "variables": [{"id": "score", "name": "得分", "type": "number", "defaultValue": 0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "射箭", "瞄准"], "category": "sports"}
}

FENCING_LUNGE_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_fencing_lunge",
    "name": "击剑弓步刺技术",
    "description": "展示击剑的准备姿势、弓步、刺击、收回技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1f2937", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "piste", "name": "剑道", "type": "shape", "transform": {"position": {"x": 400, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 700, "height": 80, "fill": {"type": "solid", "color": "#6b7280"}, "stroke": {"color": "#ffffff", "width": 2}, "cornerRadius": 4}},
        {"id": "center_line", "name": "中线", "type": "shape", "transform": {"position": {"x": 400, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.5, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": 0, "y": -40}, {"x": 0, "y": 40}], "stroke": {"color": "#ffffff", "width": 2}}},
        {"id": "fencer", "name": "击剑手", "type": "shape", "transform": {"position": {"x": 250, "y": 320}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#ffffff"}, "stroke": {"color": "#3b82f6", "width": 3}}},
        {"id": "foil", "name": "花剑", "type": "shape", "transform": {"position": {"x": 280, "y": 310}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 11, "interactive": False, "shape": {"shapeType": "rectangle", "width": 100, "height": 4, "fill": {"type": "solid", "color": "#9ca3af"}, "cornerRadius": 2}},
        {"id": "opponent", "name": "对手", "type": "shape", "transform": {"position": {"x": 550, "y": 320}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#ffffff"}, "stroke": {"color": "#ef4444", "width": 3}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "击剑弓步刺技术", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "score_text", "name": "比分", "type": "text", "transform": {"position": {"x": 400, "y": 80}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "0 : 0", "fontFamily": "Arial", "fontSize": 24, "fontWeight": "bold", "color": "#22c55e", "align": "center"}},
        {"id": "btn_guard", "name": "准备按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_guard_text", "name": "准备文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "准备", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_advance", "name": "前进按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_advance_text", "name": "前进文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "前进", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_lunge", "name": "弓步按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_lunge_text", "name": "弓步文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "弓步刺", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_recover", "name": "收回按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_recover_text", "name": "收回文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "收回", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 680, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "lunge_full", "name": "完整弓步刺", "duration": 1500, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "fencer", "property": "position", "value": {"x": 250, "y": 320}, "easing": "linear"},
            {"time": 300, "targetId": "fencer", "property": "position", "value": {"x": 320, "y": 320}, "easing": "easeIn"},
            {"time": 600, "targetId": "fencer", "property": "position", "value": {"x": 450, "y": 320}, "easing": "easeOut"},
            {"time": 600, "targetId": "foil", "property": "scale", "value": {"x": 1.5, "y": 1}, "easing": "easeOut"},
            {"time": 1000, "targetId": "fencer", "property": "position", "value": {"x": 350, "y": 320}, "easing": "easeIn"},
            {"time": 1000, "targetId": "foil", "property": "scale", "value": {"x": 1, "y": 1}, "easing": "easeIn"},
            {"time": 1500, "targetId": "fencer", "property": "position", "value": {"x": 250, "y": 320}, "easing": "easeOut"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "lunge_full"}}]}
    ],
    "variables": [{"id": "score_left", "name": "左方得分", "type": "number", "defaultValue": 0}, {"id": "score_right", "name": "右方得分", "type": "number", "defaultValue": 0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "击剑", "弓步刺"], "category": "sports"}
}
