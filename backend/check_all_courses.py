import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect(r'H:\Users\hercu.db')
cursor = conn.cursor()

# 查询所有课程包
cursor.execute("SELECT id, title, status, lessons, created_at FROM studio_packages ORDER BY created_at DESC")
rows = cursor.fetchall()

print(f"共 {len(rows)} 个课程包\n")

for row in rows:
    pkg_id, title, status, lessons_json, created_at = row
    print(f"ID: {pkg_id[:20]}...")
    print(f"标题: {title}")
    print(f"状态: {status}")
    print(f"创建时间: {created_at}")

    if lessons_json:
        lessons = json.loads(lessons_json)
        total_steps = sum(len(lesson.get('steps', [])) for lesson in lessons)
        simulator_count = 0
        sdl_count = 0

        for lesson in lessons:
            for step in lesson.get('steps', []):
                if step.get('type') == 'simulator':
                    simulator_count += 1
                    if step.get('simulator_spec', {}).get('sdl'):
                        sdl_count += 1

        print(f"课时: {len(lessons)}, 步骤: {total_steps}, 模拟器: {simulator_count}, 有SDL: {sdl_count}")
    else:
        print("无课时数据")

    print("-" * 60)

conn.close()
