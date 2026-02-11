#!/usr/bin/env python3
"""
生成SQL插入语句用于导入HTML模板
24个S-tier基础模板，质量分数75分
"""

import os
from pathlib import Path

# 24个案例 - 8个学科 × 3个 = 24个，全部75分
TEMPLATES = [
    # 物理 (3个)
    {
        "file": "benchmark_cases/physics/circular_motion.html",
        "subject": "physics",
        "name": "圆周运动",
        "description": "展示物体做圆周运动的轨迹、向心力和角速度的关系",
        "difficulty": "medium",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/physics/projectile_motion.html",
        "subject": "physics",
        "name": "抛体运动",
        "description": "模拟抛体运动轨迹，展示初速度、角度对射程和高度的影响",
        "difficulty": "medium",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/physics/spring_oscillator.html",
        "subject": "physics",
        "name": "弹簧振子",
        "description": "弹簧振子的简谐运动，展示弹性势能和动能的转换",
        "difficulty": "medium",
        "quality_score": 75
    },
    # 生物 (3个)
    {
        "file": "benchmark_cases/biology/cell_division.html",
        "subject": "biology",
        "name": "细胞分裂",
        "description": "细胞有丝分裂过程的动态展示",
        "difficulty": "medium",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/biology/dna_replication.html",
        "subject": "biology",
        "name": "DNA复制",
        "description": "DNA双螺旋结构的解旋和复制过程",
        "difficulty": "hard",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/biology/enzyme_activity.html",
        "subject": "biology",
        "name": "酶活性与米氏方程",
        "description": "酶催化反应的动力学模拟，展示底物浓度对反应速率的影响",
        "difficulty": "medium",
        "quality_score": 75
    },
    # 化学 (3个)
    {
        "file": "benchmark_cases/chemistry/electron_orbitals.html",
        "subject": "chemistry",
        "name": "电子轨道",
        "description": "原子电子轨道的3D可视化，展示不同能级的轨道形状",
        "difficulty": "hard",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/chemistry/molecular_structure.html",
        "subject": "chemistry",
        "name": "分子结构",
        "description": "分子的3D结构展示和旋转",
        "difficulty": "medium",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/chemistry/reaction_equilibrium.html",
        "subject": "chemistry",
        "name": "化学平衡",
        "description": "可逆反应的化学平衡状态模拟",
        "difficulty": "medium",
        "quality_score": 75
    },
    # 医学 (3个)
    {
        "file": "benchmark_cases/medicine/blood_circulation.html",
        "subject": "medicine",
        "name": "血液循环",
        "description": "心血管系统的血液循环路径和心脏泵血过程",
        "difficulty": "medium",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/medicine/immune_response.html",
        "subject": "medicine",
        "name": "免疫应答",
        "description": "免疫系统对病原体的识别和清除过程",
        "difficulty": "hard",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/medicine/neural_signal.html",
        "subject": "medicine",
        "name": "神经信号传导",
        "description": "神经元之间的电信号和化学信号传递过程",
        "difficulty": "hard",
        "quality_score": 75
    },
    # 计算机 (3个)
    {
        "file": "benchmark_cases/computer_science/binary_tree.html",
        "subject": "computer_science",
        "name": "二叉树遍历",
        "description": "二叉树的前序、中序、后序遍历可视化",
        "difficulty": "medium",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/computer_science/sorting_visualization.html",
        "subject": "computer_science",
        "name": "排序算法可视化",
        "description": "冒泡排序、快速排序等算法的动态演示",
        "difficulty": "easy",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/computer_science/graph_pathfinding.html",
        "subject": "computer_science",
        "name": "图路径搜索",
        "description": "图搜索算法（BFS、DFS、Dijkstra）的可视化演示",
        "difficulty": "hard",
        "quality_score": 75
    },
    # 数学 (3个)
    {
        "file": "benchmark_cases/mathematics/fourier_transform.html",
        "subject": "mathematics",
        "name": "傅里叶变换",
        "description": "傅里叶级数的图形展示，展示不同频率波形的叠加",
        "difficulty": "hard",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/mathematics/parametric_curves.html",
        "subject": "mathematics",
        "name": "参数曲线",
        "description": "参数方程生成的各种美丽曲线（心形线、玫瑰线等）",
        "difficulty": "medium",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/mathematics/matrix_operations.html",
        "subject": "mathematics",
        "name": "矩阵运算",
        "description": "矩阵乘法、变换的几何意义可视化",
        "difficulty": "medium",
        "quality_score": 75
    },
    # 历史 (3个)
    {
        "file": "benchmark_cases/history/event_causality.html",
        "subject": "history",
        "name": "历史事件因果关系",
        "description": "重大历史事件的因果链条和相互影响关系图",
        "difficulty": "medium",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/history/trade_routes.html",
        "subject": "history",
        "name": "贸易路线",
        "description": "古代丝绸之路等重要贸易路线的地理分布和商品流动",
        "difficulty": "medium",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/history/dynasty_timeline.html",
        "subject": "history",
        "name": "朝代时间轴",
        "description": "中国历史朝代更替的时间线和重要事件",
        "difficulty": "easy",
        "quality_score": 75
    },
    # 地理 (3个)
    {
        "file": "benchmark_cases/geography/water_cycle.html",
        "subject": "geography",
        "name": "水循环",
        "description": "地球水循环过程：蒸发、降水、径流的动态展示",
        "difficulty": "medium",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/geography/climate_zones.html",
        "subject": "geography",
        "name": "气候带分布",
        "description": "全球气候带的分布和特征，受纬度和地形影响",
        "difficulty": "medium",
        "quality_score": 75
    },
    {
        "file": "benchmark_cases/geography/plate_tectonics.html",
        "subject": "geography",
        "name": "板块运动",
        "description": "地球板块的运动、碰撞和分离过程",
        "difficulty": "hard",
        "quality_score": 75
    },
]

def escape_sql_string(s):
    """SQL字符串转义"""
    return s.replace("'", "''")

def generate_sql():
    import os
    import json
    import sys
    # 使用绝对路径，兼容Windows
    base_path = Path(r"F:\9\hercu-agent")
    sql_statements = []

    sys.stderr.write("-- " + "="*40 + "\n")
    sys.stderr.write("-- 导入24个HTML模拟器基础模板（75分）\n")
    sys.stderr.write("-- " + "="*40 + "\n")
    sys.stderr.write("\n")

    for idx, template in enumerate(TEMPLATES, 1):
        file_path = base_path / template["file"]

        if not file_path.exists():
            sys.stderr.write(f"-- 警告: 文件不存在 {file_path}\n")
            continue

        # 读取HTML内容
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 计算指标
        line_count = html_content.count('\n')
        # 简单估算Canvas绘制指令数量 (ctx.xxx 调用)
        visual_elements = html_content.count('ctx.')

        # 创建metadata JSON
        metadata = {
            "name": template['name'],
            "description": template['description'],
            "difficulty": template['difficulty'],
            "render_mode": "html"
        }
        metadata_json = json.dumps(metadata, ensure_ascii=False).replace("'", "''")

        # 生成INSERT语句 - 匹配实际表结构
        sql = f"""-- [{idx}/24] {template['name']} ({template['subject']}, {template['quality_score']}分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('{template['subject']}',
 '{escape_sql_string(template['name'])}',
 $HTML${html_content}$HTML$,
 {template['quality_score']},
 {visual_elements},
 {line_count},
 false,
 0,
 NOW(),
 '{metadata_json}');
"""
        sql_statements.append(sql)

    return "\n\n".join(sql_statements)

if __name__ == "__main__":
    import sys

    sql = generate_sql()

    # 保存到文件
    output_file = "F:/9/hercux-admin/backend/import_templates.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql)

    # 输出到stderr，避免污染SQL内容
    sys.stderr.write(f"\n[SUCCESS] SQL file generated: {output_file}\n")
    sys.stderr.write(f"[INFO] Total: {len(TEMPLATES)} templates (75 points)\n")
    sys.stderr.write(f"[INFO] Distribution: 8 subjects x 3 templates\n")
    sys.stderr.write("\nUse the following command to import:\n")
    sys.stderr.write(f"PGPASSWORD='Hercu2026Secure' psql -U hercu -d hercu_db -h 106.14.180.66 -f {output_file}\n")
