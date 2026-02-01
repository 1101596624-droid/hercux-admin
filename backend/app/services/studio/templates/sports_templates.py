"""
体育学科 SDL 场景模板
"""

from .sports_part1 import SPRINT_START_TEMPLATE
from .sports_part2 import BASKETBALL_SHOOTING_TEMPLATE, FOOTBALL_KICK_TEMPLATE
from .sports_part3 import SWIMMING_STROKE_TEMPLATE, GYMNASTICS_VAULT_TEMPLATE
from .sports_part4 import TENNIS_SERVE_TEMPLATE, VOLLEYBALL_SPIKE_TEMPLATE
from .sports_part5 import LONG_JUMP_TEMPLATE, SHOT_PUT_TEMPLATE
from .sports_part6 import TAEKWONDO_KICK_TEMPLATE, BOXING_PUNCH_TEMPLATE
from .sports_part7 import BADMINTON_SMASH_TEMPLATE, TABLE_TENNIS_SERVE_TEMPLATE
from .sports_part8 import GOLF_SWING_TEMPLATE, HOCKEY_SHOT_TEMPLATE
from .sports_part9 import SKIING_SLALOM_TEMPLATE, FIGURE_SKATING_SPIN_TEMPLATE
from .sports_part10 import DIVING_PLATFORM_TEMPLATE, ROWING_TECHNIQUE_TEMPLATE
from .sports_part11 import ARCHERY_SHOT_TEMPLATE, FENCING_LUNGE_TEMPLATE
from .sports_part12 import CYCLING_SPRINT_TEMPLATE, WEIGHTLIFTING_SNATCH_TEMPLATE
from .sports_part13 import YOGA_POSE_TEMPLATE, HURDLES_TEMPLATE
from .sports_part14 import RELAY_RACE_TEMPLATE, DISCUS_THROW_TEMPLATE
from .sports_part15 import POLE_VAULT_TEMPLATE, JAVELIN_THROW_TEMPLATE
from .sports_part16 import GYMNASTICS_FLOOR_FLIP_TEMPLATE, GYMNASTICS_HIGH_BAR_TEMPLATE
from .sports_part17 import DIVING_TWIST_TEMPLATE, FIGURE_SKATING_JUMP_TEMPLATE
from .sports_part18 import BASKETBALL_DUNK_TEMPLATE, FOOTBALL_BICYCLE_KICK_TEMPLATE

# J形助跑跳高模板
JUMP_APPROACH_TEMPLATE = {
    "version": "1.0.0",
    "id": "sports_jump_approach",
    "name": "J形助跑路线模拟",
    "description": "模拟跳高运动员的J形助跑路线，展示弧线跑技术要点",
    "canvas": {"width": 800, "height": 500, "backgroundColor": "#0f172a", "renderer": "pixi", "antialias": True},
    "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
    "elements": [
        {"id": "field_bg", "name": "场地背景", "type": "shape", "transform": {"position": {"x": 400, "y": 250}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 0, "interactive": False, "shape": {"shapeType": "rectangle", "width": 760, "height": 460, "fill": {"type": "solid", "color": "#1e3a5f"}, "stroke": {"color": "#3b82f6", "width": 2}, "cornerRadius": 12}},
        {"id": "landing_mat", "name": "跳高垫", "type": "shape", "transform": {"position": {"x": 650, "y": 200}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 1, "interactive": False, "shape": {"shapeType": "rectangle", "width": 180, "height": 120, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 8}},
        {"id": "crossbar", "name": "横杆", "type": "shape", "transform": {"position": {"x": 560, "y": 200}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 5, "interactive": False, "shape": {"shapeType": "rectangle", "width": 8, "height": 100, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 4}},
        {"id": "athlete_marker", "name": "运动员", "type": "shape", "transform": {"position": {"x": 150, "y": 400}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 10, "interactive": True, "shape": {"shapeType": "circle", "radius": 20, "fill": {"type": "solid", "color": "#22c55e"}, "stroke": {"color": "#ffffff", "width": 3}}},
        {"id": "title", "name": "标题", "type": "text", "transform": {"position": {"x": 400, "y": 30}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 20, "interactive": False, "text": {"content": "J形助跑路线模拟", "fontFamily": "Arial", "fontSize": 24, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_phase1", "name": "阶段一按钮", "type": "shape", "transform": {"position": {"x": 150, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#3b82f6"}, "cornerRadius": 20}},
        {"id": "btn_phase1_text", "name": "阶段一文字", "type": "text", "transform": {"position": {"x": 150, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "阶段一", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_phase2", "name": "阶段二按钮", "type": "shape", "transform": {"position": {"x": 280, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}},
        {"id": "btn_phase2_text", "name": "阶段二文字", "type": "text", "transform": {"position": {"x": 280, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "阶段二", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_phase3", "name": "阶段三按钮", "type": "shape", "transform": {"position": {"x": 410, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"type": "solid", "color": "#f59e0b"}, "cornerRadius": 20}},
        {"id": "btn_phase3_text", "name": "阶段三文字", "type": "text", "transform": {"position": {"x": 410, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "阶段三", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}},
        {"id": "btn_full", "name": "完整演示按钮", "type": "shape", "transform": {"position": {"x": 560, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 15, "interactive": True, "shape": {"shapeType": "rectangle", "width": 120, "height": 40, "fill": {"type": "solid", "color": "#8b5cf6"}, "cornerRadius": 20}},
        {"id": "btn_full_text", "name": "完整演示文字", "type": "text", "transform": {"position": {"x": 560, "y": 470}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}}, "visible": True, "opacity": 1, "zIndex": 16, "interactive": False, "text": {"content": "完整演示", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}}
    ],
    "timelines": [
        {"id": "phase1_animation", "name": "阶段一动画", "duration": 2000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "athlete_marker", "property": "position", "value": {"x": 150, "y": 400}, "easing": "linear"},
            {"time": 2000, "targetId": "athlete_marker", "property": "position", "value": {"x": 350, "y": 340}, "easing": "easeOut"}
        ]},
        {"id": "phase2_animation", "name": "阶段二动画", "duration": 1500, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "athlete_marker", "property": "position", "value": {"x": 350, "y": 340}, "easing": "linear"},
            {"time": 1500, "targetId": "athlete_marker", "property": "position", "value": {"x": 480, "y": 250}, "easing": "easeInOut"}
        ]},
        {"id": "phase3_animation", "name": "阶段三动画", "duration": 1000, "loop": False, "autoPlay": False, "keyframes": [
            {"time": 0, "targetId": "athlete_marker", "property": "position", "value": {"x": 480, "y": 250}, "easing": "linear"},
            {"time": 500, "targetId": "athlete_marker", "property": "position", "value": {"x": 540, "y": 150}, "easing": "easeIn"},
            {"time": 1000, "targetId": "athlete_marker", "property": "position", "value": {"x": 620, "y": 200}, "easing": "easeOut"}
        ]}
    ],
    "interactions": [
        {"id": "click_phase1", "name": "点击阶段一", "enabled": True, "trigger": {"type": "click", "targetId": "btn_phase1"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "phase1_animation"}}]},
        {"id": "click_phase2", "name": "点击阶段二", "enabled": True, "trigger": {"type": "click", "targetId": "btn_phase2"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "phase2_animation"}}]},
        {"id": "click_phase3", "name": "点击阶段三", "enabled": True, "trigger": {"type": "click", "targetId": "btn_phase3"}, "actions": [{"type": "playTimeline", "params": {"timelineId": "phase3_animation"}}]}
    ],
    "variables": [{"id": "current_phase", "name": "当前阶段", "type": "number", "defaultValue": 0}],
    "metadata": {"author": "HERCU", "version": "1.0.0", "tags": ["体育", "跳高", "助跑"], "category": "sports"}
}

# 导出所有体育模板
SPORTS_TEMPLATES = {
    # 田径
    "sports_jump_approach": JUMP_APPROACH_TEMPLATE,
    "sports_sprint_start": SPRINT_START_TEMPLATE,
    "sports_long_jump": LONG_JUMP_TEMPLATE,
    "sports_shot_put": SHOT_PUT_TEMPLATE,
    "sports_hurdles": HURDLES_TEMPLATE,
    "sports_relay_race": RELAY_RACE_TEMPLATE,
    "sports_discus_throw": DISCUS_THROW_TEMPLATE,
    "sports_pole_vault": POLE_VAULT_TEMPLATE,
    "sports_javelin_throw": JAVELIN_THROW_TEMPLATE,

    # 球类运动
    "sports_basketball_shooting": BASKETBALL_SHOOTING_TEMPLATE,
    "sports_basketball_dunk": BASKETBALL_DUNK_TEMPLATE,
    "sports_football_kick": FOOTBALL_KICK_TEMPLATE,
    "sports_football_bicycle_kick": FOOTBALL_BICYCLE_KICK_TEMPLATE,
    "sports_tennis_serve": TENNIS_SERVE_TEMPLATE,
    "sports_volleyball_spike": VOLLEYBALL_SPIKE_TEMPLATE,
    "sports_badminton_smash": BADMINTON_SMASH_TEMPLATE,
    "sports_table_tennis_serve": TABLE_TENNIS_SERVE_TEMPLATE,
    "sports_golf_swing": GOLF_SWING_TEMPLATE,
    "sports_hockey_shot": HOCKEY_SHOT_TEMPLATE,

    # 游泳和体操
    "sports_swimming_stroke": SWIMMING_STROKE_TEMPLATE,
    "sports_gymnastics_vault": GYMNASTICS_VAULT_TEMPLATE,
    "sports_gymnastics_floor_flip": GYMNASTICS_FLOOR_FLIP_TEMPLATE,
    "sports_gymnastics_high_bar": GYMNASTICS_HIGH_BAR_TEMPLATE,

    # 武术和格斗
    "sports_taekwondo_kick": TAEKWONDO_KICK_TEMPLATE,
    "sports_boxing_punch": BOXING_PUNCH_TEMPLATE,
    "sports_fencing_lunge": FENCING_LUNGE_TEMPLATE,

    # 冬季运动
    "sports_skiing_slalom": SKIING_SLALOM_TEMPLATE,
    "sports_figure_skating_spin": FIGURE_SKATING_SPIN_TEMPLATE,
    "sports_figure_skating_jump": FIGURE_SKATING_JUMP_TEMPLATE,

    # 水上运动
    "sports_diving_platform": DIVING_PLATFORM_TEMPLATE,
    "sports_diving_twist": DIVING_TWIST_TEMPLATE,
    "sports_rowing_technique": ROWING_TECHNIQUE_TEMPLATE,

    # 射击和射箭
    "sports_archery_shot": ARCHERY_SHOT_TEMPLATE,

    # 自行车和举重
    "sports_cycling_sprint": CYCLING_SPRINT_TEMPLATE,
    "sports_weightlifting_snatch": WEIGHTLIFTING_SNATCH_TEMPLATE,

    # 瑜伽和健身
    "sports_yoga_pose": YOGA_POSE_TEMPLATE,
}
