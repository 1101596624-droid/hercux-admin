"""
为史诗和传说级别勋章生成独特的解锁动画
每个动画都根据勋章内容和解锁方式定制
"""
import sqlite3
import json

# 动画模板 - 根据勋章类型定制
ANIMATION_TEMPLATES = {
    # ========== 史诗级别 ==========

    # 准确率相关 - 靶心/精准效果
    "accuracy_95": {
        "type": "target_lock",
        "colors": ["#8B5CF6", "#EC4899"],
        "effect": "crosshair_zoom",
        "particles": "precision_dots",
        "description": "十字准星锁定，精准命中效果"
    },

    # AI对话相关 - 数据流/对话气泡
    "ai_chat_500": {
        "type": "data_stream",
        "colors": ["#06B6D4", "#8B5CF6"],
        "effect": "chat_bubbles_spiral",
        "particles": "binary_rain",
        "description": "对话气泡螺旋上升，数据流环绕"
    },
    "ai_question_200": {
        "type": "question_burst",
        "colors": ["#F59E0B", "#8B5CF6"],
        "effect": "question_marks_explode",
        "particles": "light_bulbs",
        "description": "问号爆发，灯泡闪烁"
    },

    # 勋章收集 - 奖章雨/光环
    "badge_60": {
        "type": "medal_shower",
        "colors": ["#8B5CF6", "#EC4899"],
        "effect": "medals_falling",
        "particles": "sparkle_trail",
        "description": "奖章从天而降，闪光轨迹"
    },

    # 课程完成 - 书本/毕业帽
    "course_champion": {
        "type": "graduation",
        "colors": ["#10B981", "#8B5CF6"],
        "effect": "books_stack_glow",
        "particles": "confetti",
        "description": "书本堆叠发光，彩带飘落"
    },
    "course_conqueror": {
        "type": "conquest",
        "colors": ["#EF4444", "#8B5CF6"],
        "effect": "flag_plant",
        "particles": "victory_sparks",
        "description": "旗帜插入，胜利火花"
    },

    # 天数相关 - 日历/时钟
    "days_180": {
        "type": "calendar_flip",
        "colors": ["#F59E0B", "#8B5CF6"],
        "effect": "pages_flip_fast",
        "particles": "time_dust",
        "description": "日历快速翻页，时间尘埃"
    },

    # 领域探索 - 地球/星图
    "domain_master": {
        "type": "world_map",
        "colors": ["#3B82F6", "#8B5CF6"],
        "effect": "globe_spin_highlight",
        "particles": "location_pins",
        "description": "地球旋转，区域高亮"
    },

    # 错题相关 - 修复/转化
    "error_learner_100": {
        "type": "error_fix",
        "colors": ["#EF4444", "#10B981"],
        "effect": "x_to_check",
        "particles": "correction_sparks",
        "description": "错误标记转为正确，修复火花"
    },

    # 知识节点 - 神经网络/连接
    "knowledge_master": {
        "type": "neural_network",
        "colors": ["#8B5CF6", "#06B6D4"],
        "effect": "nodes_connect",
        "particles": "synapse_pulse",
        "description": "神经节点连接，突触脉冲"
    },
    "knowledge_point_200": {
        "type": "knowledge_tree",
        "colors": ["#10B981", "#8B5CF6"],
        "effect": "tree_grow",
        "particles": "leaf_burst",
        "description": "知识树生长，叶片绽放"
    },
    "knowledge_point_500": {
        "type": "knowledge_galaxy",
        "colors": ["#8B5CF6", "#EC4899"],
        "effect": "stars_form_constellation",
        "particles": "cosmic_dust",
        "description": "星星形成星座，宇宙尘埃"
    },

    # 学习专家 - 书本/光芒
    "learning_expert": {
        "type": "enlightenment",
        "colors": ["#F59E0B", "#8B5CF6"],
        "effect": "book_open_light",
        "particles": "wisdom_rays",
        "description": "书本打开放光，智慧光芒"
    },

    # 马拉松学习 - 跑道/冲刺
    "marathon_learner": {
        "type": "marathon",
        "colors": ["#EF4444", "#F59E0B"],
        "effect": "finish_line_cross",
        "particles": "speed_lines",
        "description": "冲过终点线，速度线条"
    },

    # 连续记录 - 火焰/链条
    "max_streak_90": {
        "type": "streak_fire",
        "colors": ["#F59E0B", "#EF4444"],
        "effect": "flame_chain",
        "particles": "ember_rise",
        "description": "火焰链条，余烬上升"
    },

    # 小课堂 - 灯泡/闪光
    "mini_lesson_100": {
        "type": "lightbulb_array",
        "colors": ["#F59E0B", "#8B5CF6"],
        "effect": "bulbs_light_up",
        "particles": "idea_sparks",
        "description": "灯泡阵列点亮，创意火花"
    },

    # 笔记 - 笔/纸张
    "note_taker_100": {
        "type": "writing_flow",
        "colors": ["#3B82F6", "#8B5CF6"],
        "effect": "pen_write_glow",
        "particles": "ink_splash",
        "description": "笔尖发光书写，墨水飞溅"
    },

    # 完美一周 - 钻石/完美
    "perfect_week": {
        "type": "diamond_form",
        "colors": ["#06B6D4", "#8B5CF6"],
        "effect": "crystal_assemble",
        "particles": "prism_light",
        "description": "水晶组装成型，棱镜折射"
    },

    # 测验 - 勾选/答题
    "quiz_100": {
        "type": "check_cascade",
        "colors": ["#10B981", "#8B5CF6"],
        "effect": "checkmarks_rain",
        "particles": "score_numbers",
        "description": "勾选标记瀑布，分数飞舞"
    },

    # 模拟器 - 齿轮/机械
    "simulator_100": {
        "type": "gear_system",
        "colors": ["#6B7280", "#8B5CF6"],
        "effect": "gears_interlock",
        "particles": "mechanical_sparks",
        "description": "齿轮咬合运转，机械火花"
    },
    "simulator_50": {
        "type": "hologram",
        "colors": ["#06B6D4", "#8B5CF6"],
        "effect": "hologram_project",
        "particles": "scan_lines",
        "description": "全息投影展开，扫描线条"
    },

    # 连续学习 - 链条/火焰
    "streak_60": {
        "type": "chain_link",
        "colors": ["#F59E0B", "#8B5CF6"],
        "effect": "chain_forge",
        "particles": "forge_sparks",
        "description": "链条锻造成型，锻造火花"
    },
    "streak_90": {
        "type": "phoenix_rise",
        "colors": ["#EF4444", "#F59E0B"],
        "effect": "phoenix_wings",
        "particles": "feather_embers",
        "description": "凤凰展翅，羽毛余烬"
    },

    # 积分 - 金币/宝箱
    "total_points_3000": {
        "type": "treasure_chest",
        "colors": ["#F59E0B", "#8B5CF6"],
        "effect": "chest_open_gold",
        "particles": "coin_fountain",
        "description": "宝箱打开，金币喷涌"
    },

    # 训练计划 - 日程/进度
    "training_plan_25": {
        "type": "progress_bar",
        "colors": ["#10B981", "#8B5CF6"],
        "effect": "bar_fill_glow",
        "particles": "milestone_stars",
        "description": "进度条填满发光，里程碑星星"
    },

    # 学习时长 - 沙漏/时钟
    "two_hundred_hours": {
        "type": "hourglass",
        "colors": ["#8B5CF6", "#EC4899"],
        "effect": "sand_flow_reverse",
        "particles": "time_crystals",
        "description": "沙漏倒流，时间水晶"
    },

    # 错题纠正 - 转化/蜕变
    "wrong_to_right_50": {
        "type": "transformation",
        "colors": ["#EF4444", "#10B981"],
        "effect": "morph_x_to_check",
        "particles": "metamorphosis_dust",
        "description": "错误蜕变为正确，蜕变尘埃"
    },

    # ========== 传说级别 ==========

    # 完美准确率 - 神级精准
    "accuracy_99": {
        "type": "perfect_aim",
        "colors": ["#FFD700", "#FF6B6B"],
        "effect": "bullseye_explosion",
        "particles": "golden_precision",
        "description": "靶心爆炸，金色精准光芒"
    },

    # AI问题大师 - 智慧之眼
    "ai_question_500": {
        "type": "wisdom_eye",
        "colors": ["#FFD700", "#8B5CF6"],
        "effect": "all_seeing_eye",
        "particles": "knowledge_streams",
        "description": "全知之眼开启，知识流涌入"
    },

    # 勋章传奇 - 王冠加冕
    "badge_100": {
        "type": "coronation",
        "colors": ["#FFD700", "#FF6B6B"],
        "effect": "crown_descend",
        "particles": "royal_sparkles",
        "description": "王冠从天降下，皇家闪光"
    },

    # 课程宗师 - 学院殿堂
    "course_grandmaster": {
        "type": "grand_hall",
        "colors": ["#FFD700", "#8B5CF6"],
        "effect": "pillars_rise",
        "particles": "marble_dust",
        "description": "殿堂柱子升起，大理石尘埃"
    },

    # 年度学员 - 四季轮回
    "days_365": {
        "type": "seasons_cycle",
        "colors": ["#10B981", "#F59E0B", "#EF4444", "#3B82F6"],
        "effect": "four_seasons_spin",
        "particles": "seasonal_elements",
        "description": "四季轮回旋转，季节元素飞舞"
    },

    # 学习巨匠 - 时间领主
    "five_hundred_hours": {
        "type": "time_lord",
        "colors": ["#FFD700", "#8B5CF6"],
        "effect": "clock_shatter_reform",
        "particles": "time_fragments",
        "description": "时钟碎裂重组，时间碎片"
    },

    # 进步大师 - 蝴蝶蜕变
    "improvement_master": {
        "type": "butterfly_emerge",
        "colors": ["#EC4899", "#8B5CF6"],
        "effect": "cocoon_break",
        "particles": "wing_scales",
        "description": "破茧成蝶，翅膀鳞片飞舞"
    },

    # 知识点传奇 - 宇宙大爆炸
    "knowledge_point_1000": {
        "type": "big_bang",
        "colors": ["#FFD700", "#FF6B6B", "#8B5CF6"],
        "effect": "universe_expand",
        "particles": "star_birth",
        "description": "宇宙大爆炸，星星诞生"
    },

    # 学习传奇 - 神殿升起
    "learning_legend": {
        "type": "temple_ascend",
        "colors": ["#FFD700", "#8B5CF6"],
        "effect": "temple_rise_clouds",
        "particles": "divine_light",
        "description": "神殿从云中升起，神圣光芒"
    },

    # 小课堂传奇 - 星云汇聚
    "mini_lesson_200": {
        "type": "nebula_form",
        "colors": ["#EC4899", "#8B5CF6", "#06B6D4"],
        "effect": "nebula_swirl",
        "particles": "cosmic_gas",
        "description": "星云旋转汇聚，宇宙气体"
    },

    # 做题机器 - 矩阵代码
    "quiz_200": {
        "type": "matrix_code",
        "colors": ["#10B981", "#FFD700"],
        "effect": "code_rain_golden",
        "particles": "digital_numbers",
        "description": "金色代码雨，数字矩阵"
    },

    # 模拟传奇 - 虚拟现实
    "simulator_legend": {
        "type": "vr_world",
        "colors": ["#06B6D4", "#8B5CF6", "#FFD700"],
        "effect": "reality_shatter",
        "particles": "pixel_fragments",
        "description": "现实碎裂，像素碎片重组"
    },

    # 半年坚持 - 不灭火焰
    "streak_180": {
        "type": "eternal_flame",
        "colors": ["#FF6B6B", "#FFD700"],
        "effect": "flame_pillar",
        "particles": "sacred_embers",
        "description": "永恒火焰柱，神圣余烬"
    },

    # 全年无休 - 太阳升起
    "streak_365": {
        "type": "sun_rise",
        "colors": ["#FFD700", "#FF6B6B", "#F59E0B"],
        "effect": "sun_corona",
        "particles": "solar_flares",
        "description": "太阳升起，日冕喷发"
    },

    # 积分传奇 - 龙腾宝库
    "total_points_10000": {
        "type": "dragon_treasure",
        "colors": ["#FFD700", "#EF4444"],
        "effect": "dragon_circle",
        "particles": "gold_rain",
        "description": "金龙环绕宝库，黄金雨"
    },

    # 训练计划大师 - 星际航行
    "training_plan_50": {
        "type": "starship_launch",
        "colors": ["#3B82F6", "#8B5CF6", "#FFD700"],
        "effect": "warp_speed",
        "particles": "star_trails",
        "description": "星舰跃迁，星轨拖尾"
    },
}

def generate_animation_code(badge_id: str, config: dict) -> str:
    """根据配置生成动画代码"""
    colors = config["colors"]
    effect = config["effect"]
    anim_type = config["type"]

    # 生成CSS动画代码
    animation_code = f"""{{
  "type": "{anim_type}",
  "effect": "{effect}",
  "colors": {json.dumps(colors)},
  "particles": "{config['particles']}",
  "duration": 3000,
  "easing": "cubic-bezier(0.4, 0, 0.2, 1)"
}}"""

    return animation_code

def main():
    db_path = "C:/Users/11015/Desktop/9/hercux-admin/backend/hercu_dev.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    updated = 0

    for badge_id, config in ANIMATION_TEMPLATES.items():
        animation_code = generate_animation_code(badge_id, config)

        cursor.execute(
            "UPDATE badge_configs SET unlock_animation = ? WHERE id = ?",
            (animation_code, badge_id)
        )

        if cursor.rowcount > 0:
            updated += 1
            print(f"Updated: {badge_id} - {config['description']}")

    conn.commit()
    conn.close()

    print(f"\nTotal updated: {updated}")

if __name__ == "__main__":
    main()
