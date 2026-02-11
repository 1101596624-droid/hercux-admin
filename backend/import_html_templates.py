#!/usr/bin/env python3
"""
导入HTML模拟器模板到数据库
将15个benchmark案例导入到simulator_templates表
"""

import asyncio
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

# 数据库连接配置
DATABASE_URL = "postgresql://hercu:Hercu2026Secure@106.14.180.66:5432/hercu_db"

# 15个案例的映射
TEMPLATES = [
    # 物理 (3个)
    {
        "file": "benchmark_cases/physics/circular_motion.html",
        "subject": "physics",
        "name": "圆周运动",
        "description": "展示物体做圆周运动的轨迹、向心力和角速度的关系",
        "difficulty": "medium",
        "quality_score": 95
    },
    {
        "file": "benchmark_cases/physics/projectile_motion.html",
        "subject": "physics",
        "name": "抛体运动",
        "description": "模拟抛体运动轨迹，展示初速度、角度对射程和高度的影响",
        "difficulty": "medium",
        "quality_score": 95
    },
    {
        "file": "benchmark_cases/physics/spring_oscillator.html",
        "subject": "physics",
        "name": "弹簧振子",
        "description": "弹簧振子的简谐运动，展示弹性势能和动能的转换",
        "difficulty": "medium",
        "quality_score": 95
    },
    # 生物 (3个)
    {
        "file": "benchmark_cases/biology/cell_division.html",
        "subject": "biology",
        "name": "细胞分裂",
        "description": "细胞有丝分裂过程的动态展示",
        "difficulty": "medium",
        "quality_score": 90
    },
    {
        "file": "benchmark_cases/biology/dna_replication.html",
        "subject": "biology",
        "name": "DNA复制",
        "description": "DNA双螺旋结构的解旋和复制过程",
        "difficulty": "hard",
        "quality_score": 90
    },
    {
        "file": "benchmark_cases/biology/enzyme_activity.html",
        "subject": "biology",
        "name": "酶活性与米氏方程",
        "description": "酶催化反应的动力学模拟，展示底物浓度对反应速率的影响",
        "difficulty": "medium",
        "quality_score": 92
    },
    # 化学 (3个)
    {
        "file": "benchmark_cases/chemistry/electron_orbitals.html",
        "subject": "chemistry",
        "name": "电子轨道",
        "description": "原子电子轨道的3D可视化，展示不同能级的轨道形状",
        "difficulty": "hard",
        "quality_score": 92
    },
    {
        "file": "benchmark_cases/chemistry/molecular_structure.html",
        "subject": "chemistry",
        "name": "分子结构",
        "description": "分子的3D结构展示和旋转",
        "difficulty": "medium",
        "quality_score": 90
    },
    {
        "file": "benchmark_cases/chemistry/reaction_equilibrium.html",
        "subject": "chemistry",
        "name": "化学平衡",
        "description": "可逆反应的化学平衡状态模拟",
        "difficulty": "medium",
        "quality_score": 90
    },
    # 医学 (2个)
    {
        "file": "benchmark_cases/medicine/blood_circulation.html",
        "subject": "medicine",
        "name": "血液循环",
        "description": "心血管系统的血液循环路径和心脏泵血过程",
        "difficulty": "medium",
        "quality_score": 90
    },
    {
        "file": "benchmark_cases/medicine/immune_response.html",
        "subject": "medicine",
        "name": "免疫应答",
        "description": "免疫系统对病原体的识别和清除过程",
        "difficulty": "hard",
        "quality_score": 90
    },
    # 计算机 (2个)
    {
        "file": "benchmark_cases/computer_science/binary_tree.html",
        "subject": "computer_science",
        "name": "二叉树遍历",
        "description": "二叉树的前序、中序、后序遍历可视化",
        "difficulty": "medium",
        "quality_score": 88
    },
    {
        "file": "benchmark_cases/computer_science/sorting_visualization.html",
        "subject": "computer_science",
        "name": "排序算法可视化",
        "description": "冒泡排序、快速排序等算法的动态演示",
        "difficulty": "easy",
        "quality_score": 88
    },
    # 数学 (2个)
    {
        "file": "benchmark_cases/mathematics/fourier_transform.html",
        "subject": "mathematics",
        "name": "傅里叶变换",
        "description": "傅里叶级数的图形展示，展示不同频率波形的叠加",
        "difficulty": "hard",
        "quality_score": 92
    },
    {
        "file": "benchmark_cases/mathematics/parametric_curves.html",
        "subject": "mathematics",
        "name": "参数曲线",
        "description": "参数方程生成的各种美丽曲线（心形线、玫瑰线等）",
        "difficulty": "medium",
        "quality_score": 90
    },
]


async def import_templates():
    """导入HTML模板到数据库"""

    # 创建数据库引擎
    engine = create_engine(DATABASE_URL, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    base_path = Path("F:/9/hercu-agent")

    success_count = 0
    failed_count = 0

    print("\n" + "="*60)
    print("开始导入HTML模拟器模板")
    print("="*60 + "\n")

    for idx, template in enumerate(TEMPLATES, 1):
        file_path = base_path / template["file"]

        print(f"[{idx}/{len(TEMPLATES)}] 处理: {template['name']}")
        print(f"   文件: {file_path}")

        # 检查文件是否存在
        if not file_path.exists():
            print(f"   ❌ 文件不存在，跳过")
            failed_count += 1
            continue

        # 读取HTML内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except Exception as e:
            print(f"   ❌ 读取文件失败: {e}")
            failed_count += 1
            continue

        # 插入数据库
        try:
            sql = text("""
                INSERT INTO simulator_templates
                (name, description, subject, difficulty, quality_score, html_content,
                 render_mode, created_at, updated_at)
                VALUES
                (:name, :description, :subject, :difficulty, :quality_score, :html_content,
                 'html', NOW(), NOW())
                RETURNING id
            """)

            result = session.execute(sql, {
                "name": template["name"],
                "description": template["description"],
                "subject": template["subject"],
                "difficulty": template["difficulty"],
                "quality_score": template["quality_score"],
                "html_content": html_content
            })

            template_id = result.fetchone()[0]
            session.commit()

            print(f"   ✅ 导入成功 (ID: {template_id}, {len(html_content)} 字符)")
            success_count += 1

        except Exception as e:
            session.rollback()
            print(f"   ❌ 插入数据库失败: {e}")
            failed_count += 1

    session.close()

    print("\n" + "="*60)
    print("导入完成")
    print("="*60)
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {failed_count} 个")
    print(f"📊 总计: {len(TEMPLATES)} 个")
    print("")


if __name__ == "__main__":
    asyncio.run(import_templates())
