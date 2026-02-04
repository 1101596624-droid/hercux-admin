"""
勋章安装脚本 - 独立版本，直接使用 sqlite3
"""
import json
import sqlite3
from pathlib import Path

def install_badges():
    """安装所有勋章到数据库"""
    # 数据库路径
    db_path = "C:/Users/11015/Desktop/9/hercux-admin/backend/hercu_dev.db"

    # 加载勋章配置
    script_dir = Path(__file__).parent
    badges_file = script_dir / "all_badges.json"

    with open(badges_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    badges = data['badges']
    print(f"Loading {len(badges)} badges...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    inserted = 0
    updated = 0

    for badge in badges:
        # 检查是否存在
        cursor.execute("SELECT id FROM badge_configs WHERE id = ?", (badge['id'],))
        existing = cursor.fetchone()

        condition_json = json.dumps(badge['condition'], ensure_ascii=False)
        animation = badge.get('unlock_animation', '') or ''
        icon_url = badge.get('icon_url', '') or ''

        if existing:
            # 更新
            cursor.execute("""
                UPDATE badge_configs SET
                    name = ?,
                    name_en = ?,
                    icon = ?,
                    icon_url = ?,
                    description = ?,
                    category = ?,
                    rarity = ?,
                    points = ?,
                    condition = ?,
                    unlock_animation = ?,
                    is_active = 1
                WHERE id = ?
            """, (
                badge['name'],
                badge.get('name_en', ''),
                badge['icon'],
                icon_url,
                badge.get('description', ''),
                badge['category'],
                badge['rarity'],
                badge['points'],
                condition_json,
                animation,
                badge['id']
            ))
            updated += 1
        else:
            # 插入
            cursor.execute("""
                INSERT INTO badge_configs (id, name, name_en, icon, icon_url, description, category, rarity, points, condition, unlock_animation, is_active, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
            """, (
                badge['id'],
                badge['name'],
                badge.get('name_en', ''),
                badge['icon'],
                icon_url,
                badge.get('description', ''),
                badge['category'],
                badge['rarity'],
                badge['points'],
                condition_json,
                animation
            ))
            inserted += 1

        # 打印进度
        total = inserted + updated
        if total % 20 == 0:
            print(f"  Progress: {total}/{len(badges)}")

    conn.commit()
    conn.close()

    print(f"\nCompleted!")
    print(f"  Inserted: {inserted}")
    print(f"  Updated: {updated}")
    print(f"  Total: {inserted + updated}")


if __name__ == '__main__':
    print("=" * 50)
    print("Badge Installation Script (Standalone)")
    print("=" * 50)
    install_badges()
