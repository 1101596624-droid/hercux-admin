# 物理模板 Part 2 - 电磁学和光学

CIRCUIT_TEMPLATE = {
    "version": "1.0.0",
    "id": "physics_circuit",
    "name": "简单电路模拟",
    "description": "展示串联和并联电路的电流电压关系",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "circuit_bg", "name": "电路板", "type": "shape", "transform": {"position": {"x": 400, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 700, "height": 350, "fill": {"type": "solid", "color": "#1e293b"}, "stroke": {"color": "#475569", "width": 2}, "cornerRadius": 12}},
        {"id": "battery", "name": "电池", "type": "shape", "transform": {"position": {"x": 100, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "rectangle", "width": 40, "height": 80, "fill": {"type": "solid", "color": "#22c55e"}, "stroke": {"color": "#ffffff", "width": 2}, "cornerRadius": 4}},
        {"id": "battery_plus", "name": "正极", "type": "text", "transform": {"position": {"x": 100, "y": 200}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 6, "interactive": False, "text": {"content": "+", "fontFamily": "Arial", "fontSize": 24, "fontWeight": "bold", "color": "#ef4444", "align": "center"}},
        {"id": "battery_minus", "name": "负极", "type": "text", "transform": {"position": {"x": 100, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 6, "interactive": False, "text": {"content": "-", "fontFamily": "Arial", "fontSize": 24, "fontWeight": "bold", "color": "#3b82f6", "align": "center"}},
        {"id": "wire_top", "name": "上导线", "type": "shape", "transform": {"position": {"x": 350, "y": 120}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": -230, "y": 0}, {"x": 230, "y": 0}], "stroke": {"color": "#f59e0b", "width": 4}}},
        {"id": "wire_bottom", "name": "下导线", "type": "shape", "transform": {"position": {"x": 350, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": -230, "y": 0}, {"x": 230, "y": 0}], "stroke": {"color": "#f59e0b", "width": 4}}},
        {"id": "resistor1", "name": "电阻R1", "type": "shape", "transform": {"position": {"x": 300, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": True, "shape": {"shapeType": "rectangle", "width": 80, "height": 30, "fill": {"type": "solid", "color": "#8b5cf6"}, "stroke": {"color": "#ffffff", "width": 2}, "cornerRadius": 4}},
        {"id": "resistor1_label", "name": "R1标签", "type": "text", "transform": {"position": {"x": 300, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 6, "interactive": False, "text": {"content": "R₁", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "resistor2", "name": "电阻R2", "type": "shape", "transform": {"position": {"x": 500, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": True, "shape": {"shapeType": "rectangle", "width": 80, "height": 30, "fill": {"type": "solid", "color": "#ec4899"}, "stroke": {"color": "#ffffff", "width": 2}, "cornerRadius": 4}},
        {"id": "resistor2_label", "name": "R2标签", "type": "text", "transform": {"position": {"x": 500, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 6, "interactive": False, "text": {"content": "R₂", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "bulb", "name": "灯泡", "type": "shape", "transform": {"position": {"x": 650, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "circle", "radius": 25, "fill": {"type": "solid", "color": "#fbbf24"}, "stroke": {"color": "#ffffff", "width": 2}}},
        {"id": "electron1", "name": "电子1", "type": "shape", "transform": {"position": {"x": 150, "y": 120}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 8, "fill": {"type": "solid", "color": "#3b82f6"}}},
        {"id": "electron2", "name": "电子2", "type": "shape", "transform": {"position": {"x": 300, "y": 120}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 8, "fill": {"type": "solid", "color": "#3b82f6"}}},
        {"id": "electron3", "name": "电子3", "type": "shape", "transform": {"position": {"x": 450, "y": 120}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": False, "shape": {"shapeType": "circle", "radius": 8, "fill": {"type": "solid", "color": "#3b82f6"}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 35}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "简单电路模拟", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "voltage_panel", "name": "电压面板", "type": "shape", "transform": {"position": {"x": 100, "y": 420}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.9, "zIndex": 15, "interactive": False, "shape": {"shapeType": "rectangle", "width": 140, "height": 60, "fill": {"type": "solid", "color": "#1e293b"}, "stroke": {"color": "#22c55e", "width": 1}, "cornerRadius": 8}},
        {"id": "voltage_text", "name": "电压", "type": "text", "transform": {"position": {"x": 100, "y": 420}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "电压: 12V", "fontFamily": "Arial", "fontSize": 16, "color": "#22c55e", "align": "center"}},
        {"id": "current_panel", "name": "电流面板", "type": "shape", "transform": {"position": {"x": 280, "y": 420}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.9, "zIndex": 15, "interactive": False, "shape": {"shapeType": "rectangle", "width": 140, "height": 60, "fill": {"type": "solid", "color": "#1e293b"}, "stroke": {"color": "#f59e0b", "width": 1}, "cornerRadius": 8}},
        {"id": "current_text", "name": "电流", "type": "text", "transform": {"position": {"x": 280, "y": 420}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "电流: 2A", "fontFamily": "Arial", "fontSize": 16, "color": "#f59e0b", "align": "center"}},
        {"id": "btn_series", "name": "串联按钮", "type": "shape", "transform": {"position": {"x": 500, "y": 450}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 120, "height": 44, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 22}},
        {"id": "btn_series_text", "name": "串联文字", "type": "text", "transform": {"position": {"x": 500, "y": 450}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "串联电路", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_parallel", "name": "并联按钮", "type": "shape", "transform": {"position": {"x": 660, "y": 450}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 120, "height": 44, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 22}},
        {"id": "btn_parallel_text", "name": "并联文字", "type": "text", "transform": {"position": {"x": 660, "y": 450}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "并联电路", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "electron_flow", "name": "电子流动", "duration": 3000, "loop": True, "autoPlay": True, "keyframes": [
            {"time": 0, "targetId": "electron1", "property": "position", "value": {"x": 150, "y": 120}, "easing": "linear"},
            {"time": 1000, "targetId": "electron1", "property": "position", "value": {"x": 400, "y": 120}, "easing": "linear"},
            {"time": 2000, "targetId": "electron1", "property": "position", "value": {"x": 580, "y": 250}, "easing": "linear"},
            {"time": 3000, "targetId": "electron1", "property": "position", "value": {"x": 150, "y": 380}, "easing": "linear"}
        ]}
    ],
    "interactions": [
        {"id": "click_series", "name": "点击串联", "enabled": True, "trigger": {"type": "click", "targetId": "btn_series"}, "actions": [{"type": "log", "params": {"message": "切换到串联电路"}}]},
        {"id": "click_parallel", "name": "点击并联", "enabled": True, "trigger": {"type": "click", "targetId": "btn_parallel"}, "actions": [{"type": "log", "params": {"message": "切换到并联电路"}}]}
    ],
    "variables": [
        {"id": "voltage", "name": "电压", "type": "number", "defaultValue": 12},
        {"id": "current", "name": "电流", "type": "number", "defaultValue": 2},
        {"id": "circuit_type", "name": "电路类型", "type": "string", "defaultValue": "series"}
    ],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["物理", "电学", "电路"], "category": "physics"}
}

PENDULUM_TEMPLATE = {
    "version": "1.0.0",
    "id": "physics_pendulum",
    "name": "单摆运动模拟",
    "description": "展示单摆的周期性运动和能量转换",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "support", "name": "支架", "type": "shape", "transform": {"position": {"x": 400, "y": 50}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 200, "height": 20, "fill": {"type": "solid", "color": "#475569"}, "cornerRadius": 4}},
        {"id": "pivot", "name": "支点", "type": "shape", "transform": {"position": {"x": 400, "y": 60}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "circle", "radius": 8, "fill": {"type": "solid", "color": "#ef4444"}}},
        {"id": "string", "name": "摆线", "type": "shape", "transform": {"position": {"x": 400, "y": 60}, "rotation": 30, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 1, "zIndex": 2, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": 0, "y": 0}, {"x": 0, "y": 250}], "stroke": {"color": "#94a3b8", "width": 3}}},
        {"id": "bob", "name": "摆球", "type": "shape", "transform": {"position": {"x": 525, "y": 277}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": True, "shape": {"shapeType": "circle", "radius": 30, "fill": {"type": "solid", "color": "#3b82f6"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "equilibrium_line", "name": "平衡位置", "type": "shape", "transform": {"position": {"x": 400, "y": 200}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0}}, "visible": True, "opacity": 0.3, "zIndex": 1, "interactive": False, "shape": {"shapeType": "line", "points": [{"x": 0, "y": 0}, {"x": 0, "y": 200}], "stroke": {"color": "#22c55e", "width": 2, "dashArray": [8, 4]}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 25}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "单摆运动模拟", "fontFamily": "Arial", "fontSize": 26, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "energy_panel", "name": "能量面板", "type": "shape", "transform": {"position": {"x": 120, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 0.9, "zIndex": 15, "interactive": False, "shape": {"shapeType": "rectangle", "width": 180, "height": 200, "fill": {"type": "solid", "color": "#1e293b"}, "stroke": {"color": "#475569", "width": 1}, "cornerRadius": 12}},
        {"id": "ke_label", "name": "动能标签", "type": "text", "transform": {"position": {"x": 120, "y": 230}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "动能 KE", "fontFamily": "Arial", "fontSize": 14, "color": "#ef4444", "align": "center"}},
        {"id": "ke_bar", "name": "动能条", "type": "shape", "transform": {"position": {"x": 120, "y": 260}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "shape": {"shapeType": "rectangle", "width": 140, "height": 20, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 4}},
        {"id": "pe_label", "name": "势能标签", "type": "text", "transform": {"position": {"x": 120, "y": 300}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "势能 PE", "fontFamily": "Arial", "fontSize": 14, "color": "#22c55e", "align": "center"}},
        {"id": "pe_bar", "name": "势能条", "type": "shape", "transform": {"position": {"x": 120, "y": 330}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "shape": {"shapeType": "rectangle", "width": 100, "height": 20, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 4}},
        {"id": "period_text", "name": "周期", "type": "text", "transform": {"position": {"x": 120, "y": 380}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "周期 T = 1.0s", "fontFamily": "Arial", "fontSize": 14, "color": "#f59e0b", "align": "center"}},
        {"id": "btn_start", "name": "开始按钮", "type": "shape", "transform": {"position": {"x": 550, "y": 450}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 120, "height": 44, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 22}},
        {"id": "btn_start_text", "name": "开始文字", "type": "text", "transform": {"position": {"x": 550, "y": 450}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "开始摆动", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_reset", "name": "重置按钮", "type": "shape", "transform": {"position": {"x": 700, "y": 450}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 44, "fill": {"type": "solid", "color": "#6366f1"}, "cornerRadius": 22}},
        {"id": "btn_reset_text", "name": "重置文字", "type": "text", "transform": {"position": {"x": 700, "y": 450}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "重置", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "swing", "name": "摆动", "duration": 2000, "loop": True, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "bob", "property": "position", "value": {"x": 525, "y": 277}, "easing": "easeInOut"},
            {"time": 500, "targetId": "bob", "property": "position", "value": {"x": 400, "y": 310}, "easing": "easeInOut"},
            {"time": 1000, "targetId": "bob", "property": "position", "value": {"x": 275, "y": 277}, "easing": "easeInOut"},
            {"time": 1500, "targetId": "bob", "property": "position", "value": {"x": 400, "y": 310}, "easing": "easeInOut"},
            {"time": 2000, "targetId": "bob", "property": "position", "value": {"x": 525, "y": 277}, "easing": "easeInOut"}
        ]}
    ],
    "interactions": [
        {"id": "click_start", "name": "点击开始", "enabled": True, "trigger": {"type": "click", "targetId": "btn_start"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "swing"}}]},
        {"id": "drag_bob", "name": "拖拽摆球", "enabled": True, "trigger": {"type": "drag", "targetId": "bob"}, "actions": [{"type": "log", "params": {"message": "摆球被拖拽"}}]}
    ],
    "variables": [
        {"id": "angle", "name": "摆角", "type": "number", "defaultValue": 30},
        {"id": "length", "name": "摆长", "type": "number", "defaultValue": 1},
        {"id": "period", "name": "周期", "type": "number", "defaultValue": 2}
    ],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["物理", "力学", "单摆"], "category": "physics"}
}
