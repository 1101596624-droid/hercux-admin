import sqlite3
import json
import sys

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

# 连接数据库
conn = sqlite3.connect(r'H:\Users\hercu.db')
cursor = conn.cursor()

# 查询最新的课程包
cursor.execute("SELECT id, title, status, lessons FROM studio_packages ORDER BY created_at DESC LIMIT 1")
row = cursor.fetchone()

if row:
    pkg_id, title, status, lessons_json = row
    print(f"课程ID: {pkg_id}")
    print(f"标题: {title}")
    print(f"状态: {status}")
    print("-" * 50)

    if lessons_json:
        lessons = json.loads(lessons_json)
        print(f"课时数量: {len(lessons)}")

        for i, lesson in enumerate(lessons[:3]):  # 只看前3个
            print(f"\n=== 课时 {i+1}: {lesson.get('title', 'N/A')} ===")
            steps = lesson.get('steps', [])
            print(f"步骤数: {len(steps)}")

            for j, step in enumerate(steps):
                step_type = step.get('type', 'unknown')
                step_title = step.get('title', 'N/A')
                print(f"  步骤 {j+1}: [{step_type}] {step_title}")

                if step_type == 'simulator':
                    sim_spec = step.get('simulator_spec', {})
                    sdl = sim_spec.get('sdl')
                    if sdl:
                        elements = sdl.get('elements', [])
                        interactions = sdl.get('interactions', [])
                        timelines = sdl.get('timelines', [])
                        print(f"    SDL: {len(elements)} 元素, {len(interactions)} 交互, {len(timelines)} 动画")
                        print(f"    场景名: {sdl.get('name', 'N/A')}")
                    else:
                        print(f"    警告: 没有 SDL 配置!")
                        print(f"    simulator_spec keys: {list(sim_spec.keys())}")
else:
    print("没有找到课程")

conn.close()
