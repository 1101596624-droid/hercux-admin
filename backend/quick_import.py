"""
快速测试：直接通过 SQL 导入示例课程
"""

import sqlite3
import json
from pathlib import Path

# 连接数据库
db_path = Path(__file__).parent / "hercu_dev.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 读取示例课程包
example_file = Path(__file__).parent / "examples" / "example-package-physiology.json"
with open(example_file, "r", encoding="utf-8") as f:
    package = json.load(f)

print("📦 正在导入示例课程包...")

try:
    # 1. 创建课程
    cursor.execute("""
        INSERT INTO courses (name, description, difficulty, duration_hours, studio_package_id)
        VALUES (?, ?, ?, ?, ?)
    """, (
        package["meta"]["title"],
        package["meta"]["description"],
        "intermediate",
        package["meta"]["estimated_hours"],
        package["id"]
    ))
    course_id = cursor.lastrowid
    print(f"✅ 创建课程: ID={course_id}")

    # 2. 创建节点
    node_id_map = {}
    for node in package["nodes"]:
        cursor.execute("""
            INSERT INTO course_nodes (
                course_id, node_id, type, component_id, title, sequence,
                studio_node_id, learning_objectives,
                content_l1, content_l2, content_l3,
                ai_tutor_config, quiz_data, timeline_config
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            course_id,
            node["id"],
            "content",
            node["id"],
            node["title"],
            node["order"],
            node["id"],
            json.dumps(node.get("learning_objectives", [])),
            json.dumps(node["content"].get("L1_intuition", {})),
            json.dumps(node["content"].get("L2_mechanism", {})),
            json.dumps(node["content"].get("L3_essence", {})),
            json.dumps(node.get("ai_tutor", {})),
            json.dumps(node.get("quiz", {})),
            json.dumps({"steps": [{"type": "video", "timeline_events": node.get("timeline", [])}]})
        ))
        node_id_map[node["id"]] = cursor.lastrowid

    print(f"✅ 创建节点: {len(node_id_map)} 个")

    # 3. 创建课程包记录
    cursor.execute("""
        INSERT INTO course_packages (studio_package_id, course_id, version, style, package_data)
        VALUES (?, ?, ?, ?, ?)
    """, (
        package["id"],
        course_id,
        package.get("version", "1.0.0"),
        package["meta"].get("style", "rcs"),
        json.dumps(package)
    ))

    print(f"✅ 保存课程包记录")

    conn.commit()

    print("\n" + "=" * 60)
    print("✅ 导入完成！")
    print("=" * 60)
    print(f"\n🎓 课程 ID: {course_id}")
    print(f"📚 节点数: {len(node_id_map)}")
    print(f"\n现在可以访问前端开始学习：")
    print(f"   http://localhost:3000/course/{course_id}/learn")

except Exception as e:
    conn.rollback()
    print(f"❌ 导入失败: {str(e)}")
    import traceback
    traceback.print_exc()

finally:
    conn.close()
