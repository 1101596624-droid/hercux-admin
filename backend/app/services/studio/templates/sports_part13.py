# 体育模板 Part 13 - 瑜伽和体操

YOGA_POSE_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_yoga_pose",
    "name": "瑜伽体式分析",
    "description": "展示瑜伽的战士式、树式、下犬式等基本体式",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e1b4b", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "mat", "name": "瑜伽垫", "type": "shape", "transform": {"position": {"x": 400, "y": 400}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 300, "height": 100, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 8}},
        {"id": "yogi", "name": "瑜伽练习者", "type": "shape", "transform": {"position": {"x": 400, "y": 320}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#ec4899"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "arm_left", "name": "左臂", "type": "shape", "transform": {"position": {"x": 375, "y": 310}, "rotation": -90, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 50, "height": 10, "fill": {"type": "solid", "color": "#ec4899"}, "cornerRadius": 5}},
        {"id": "arm_right", "name": "右臂", "type": "shape", "transform": {"position": {"x": 425, "y": 310}, "rotation": 90, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 9, "interactive": False, "shape": {"shapeType": "rectangle", "width": 50, "height": 10, "fill": {"type": "solid", "color": "#ec4899"}, "cornerRadius": 5}},
        {"id": "leg_left", "name": "左腿", "type": "shape", "transform": {"position": {"x": 385, "y": 345}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 8, "interactive": False, "shape": {"shapeType": "rectangle", "width": 12, "height": 60, "fill": {"type": "solid", "color": "#ec4899"}, "cornerRadius": 6}},
        {"id": "leg_right", "name": "右腿", "type": "shape", "transform": {"position": {"x": 415, "y": 345}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 8, "interactive": False, "shape": {"shapeType": "rectangle", "width": 12, "height": 60, "fill": {"type": "solid", "color": "#ec4899"}, "cornerRadius": 6}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "瑜伽体式分析", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "pose_name", "name": "体式名称", "type": "text", "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "山式 (Tadasana)", "fontFamily": "Arial", "fontSize": 18, "color": "#a78bfa", "align": "center"}},
        {"id": "btn_mountain", "name": "山式按钮", "type": "shape", "transform": {"position": {"x": 100, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_mountain_text", "name": "山式文字", "type": "text", "transform": {"position": {"x": 100, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "山式", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_warrior", "name": "战士按钮", "type": "shape", "transform": {"position": {"x": 220, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_warrior_text", "name": "战士文字", "type": "text", "transform": {"position": {"x": 220, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "战士式", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_tree", "name": "树式按钮", "type": "shape", "transform": {"position": {"x": 340, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_tree_text", "name": "树式文字", "type": "text", "transform": {"position": {"x": 340, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "树式", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_downdog", "name": "下犬按钮", "type": "shape", "transform": {"position": {"x": 460, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_downdog_text", "name": "下犬文字", "type": "text", "transform": {"position": {"x": 460, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "下犬式", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_cobra", "name": "眼镜蛇按钮", "type": "shape", "transform": {"position": {"x": 580, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_cobra_text", "name": "眼镜蛇文字", "type": "text", "transform": {"position": {"x": 580, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "眼镜蛇", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_play", "name": "播放按钮", "type": "shape", "transform": {"position": {"x": 700, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#ec4899"}, "cornerRadius": 20}},
        {"id": "btn_play_text", "name": "播放文字", "type": "text", "transform": {"position": {"x": 700, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "播放", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "warrior_pose", "name": "战士式动画", "duration": 2000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "leg_left", "property": "rotation", "value": 0, "easing": "linear"},
            {"time": 0, "targetId": "leg_right", "property": "rotation", "value": 0, "easing": "linear"},
            {"time": 0, "targetId": "arm_left", "property": "rotation", "value": -90, "easing": "linear"},
            {"time": 0, "targetId": "arm_right", "property": "rotation", "value": 90, "easing": "linear"},
            {"time": 1000, "targetId": "leg_left", "property": "rotation", "value": -45, "easing": "easeInOut"},
            {"time": 1000, "targetId": "leg_right", "property": "rotation", "value": 30, "easing": "easeInOut"},
            {"time": 1000, "targetId": "arm_left", "property": "rotation", "value": -180, "easing": "easeInOut"},
            {"time": 1000, "targetId": "arm_right", "property": "rotation", "value": 0, "easing": "easeInOut"},
            {"time": 2000, "targetId": "leg_left", "property": "rotation", "value": -45, "easing": "linear"},
            {"time": 2000, "targetId": "leg_right", "property": "rotation", "value": 30, "easing": "linear"}
        ]}
    ],
    "interactions": [
        {"id": "click_warrior", "name": "点击战士式", "enabled": True, "trigger": {"type": "click", "targetId": "btn_warrior"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "warrior_pose"}}]}
    ],
    "variables": [{"id": "pose", "name": "体式", "type": "string", "defaultValue": "mountain"}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "瑜伽", "体式"], "category": "sports"}
}

HURDLES_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_hurdles",
    "name": "跨栏技术分析",
    "description": "展示跨栏的起跑、跨栏、着地、冲刺技术",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "track", "name": "跑道", "type": "shape", "transform": {"position": {"x": 400, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 760, "height": 80, "fill": {"type": "solid", "color": "#dc2626"}, "cornerRadius": 4}},
        {"id": "hurdle1", "name": "栏架1", "type": "shape", "transform": {"position": {"x": 250, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 1}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 60, "height": 8, "fill": {"type": "solid", "color": "#ffffff"}}},
        {"id": "hurdle1_leg", "name": "栏架1腿", "type": "shape", "transform": {"position": {"x": 250, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 6, "height": 40, "fill": {"type": "solid", "color": "#fbbf24"}}},
        {"id": "hurdle2", "name": "栏架2", "type": "shape", "transform": {"position": {"x": 450, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 1}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 60, "height": 8, "fill": {"type": "solid", "color": "#ffffff"}}},
        {"id": "hurdle2_leg", "name": "栏架2腿", "type": "shape", "transform": {"position": {"x": 450, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 6, "height": 40, "fill": {"type": "solid", "color": "#fbbf24"}}},
        {"id": "hurdle3", "name": "栏架3", "type": "shape", "transform": {"position": {"x": 650, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 1}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "rectangle", "width": 60, "height": 8, "fill": {"type": "solid", "color": "#ffffff"}}},
        {"id": "hurdle3_leg", "name": "栏架3腿", "type": "shape", "transform": {"position": {"x": 650, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 6, "height": 40, "fill": {"type": "solid", "color": "#fbbf24"}}},
        {"id": "athlete", "name": "运动员", "type": "shape", "transform": {"position": {"x": 80, "y": 350}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 22, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "跨栏技术分析", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "time_text", "name": "计时", "type": "text", "transform": {"position": {"x": 700, "y": 80}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "00:00.00", "fontFamily": "Arial", "fontSize": 22, "fontWeight": "bold", "color": "#22c55e", "align": "center"}},
        {"id": "btn_start", "name": "起跑按钮", "type": "shape", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_start_text", "name": "起跑文字", "type": "text", "transform": {"position": {"x": 120, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "起跑", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_hurdle", "name": "跨栏按钮", "type": "shape", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_hurdle_text", "name": "跨栏文字", "type": "text", "transform": {"position": {"x": 260, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "跨栏", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_landing", "name": "着地按钮", "type": "shape", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_landing_text", "name": "着地文字", "type": "text", "transform": {"position": {"x": 400, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "着地", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整按钮", "type": "shape", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整文字", "type": "text", "transform": {"position": {"x": 540, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "hurdles_full", "name": "完整跨栏", "duration": 4000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "athlete", "property": "position", "value": {"x": 80, "y": 350}, "easing": "linear"},
            {"time": 600, "targetId": "athlete", "property": "position", "value": {"x": 200, "y": 350}, "easing": "easeIn"},
            {"time": 1000, "targetId": "athlete", "property": "position", "value": {"x": 250, "y": 280}, "easing": "easeOut"},
            {"time": 1400, "targetId": "athlete", "property": "position", "value": {"x": 320, "y": 350}, "easing": "easeIn"},
            {"time": 2000, "targetId": "athlete", "property": "position", "value": {"x": 400, "y": 350}, "easing": "linear"},
            {"time": 2400, "targetId": "athlete", "property": "position", "value": {"x": 450, "y": 280}, "easing": "easeOut"},
            {"time": 2800, "targetId": "athlete", "property": "position", "value": {"x": 520, "y": 350}, "easing": "easeIn"},
            {"time": 3200, "targetId": "athlete", "property": "position", "value": {"x": 600, "y": 350}, "easing": "linear"},
            {"time": 3500, "targetId": "athlete", "property": "position", "value": {"x": 650, "y": 280}, "easing": "easeOut"},
            {"time": 4000, "targetId": "athlete", "property": "position", "value": {"x": 750, "y": 350}, "easing": "easeIn"}
        ]}
    ],
    "interactions": [
        {"id": "click_full", "name": "点击完整", "enabled": True, "trigger": {"type": "click", "targetId": "btn_full"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "hurdles_full"}}]}
    ],
    "variables": [{"id": "time", "name": "时间", "type": "number", "defaultValue": 0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "田径", "跨栏"], "category": "sports"}
}
