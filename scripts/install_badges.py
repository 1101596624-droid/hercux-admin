"""
勋章安装脚本 - 将所有勋章配置插入数据库
"""
import json
import asyncio
import sys
from pathlib import Path

# 添加后端路径
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

async def install_badges():
    """安装所有勋章到数据库"""
    from app.db.session import async_session_maker
    from sqlalchemy import text

    # 加载勋章配置
    script_dir = Path(__file__).parent
    badges_file = script_dir / "all_badges.json"

    with open(badges_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    badges = data['badges']
    print(f"Loading {len(badges)} badges...")

    async with async_session_maker() as session:
        inserted = 0
        updated = 0

        for badge in badges:
            # 检查是否存在
            result = await session.execute(
                text("SELECT id FROM badge_configs WHERE id = :id"),
                {"id": badge['id']}
            )
            existing = result.scalar_one_or_none()

            condition_json = json.dumps(badge['condition'], ensure_ascii=False)
            animation = badge.get('unlock_animation', '') or ''

            icon_url = badge.get('icon_url', '') or ''

            if existing:
                # 更新
                await session.execute(
                    text("""
                        UPDATE badge_configs SET
                            name = :name,
                            name_en = :name_en,
                            icon = :icon,
                            icon_url = :icon_url,
                            description = :description,
                            category = :category,
                            rarity = :rarity,
                            points = :points,
                            condition = :condition,
                            unlock_animation = :unlock_animation,
                            is_active = 1
                        WHERE id = :id
                    """),
                    {
                        "id": badge['id'],
                        "name": badge['name'],
                        "name_en": badge.get('name_en', ''),
                        "icon": badge['icon'],
                        "icon_url": icon_url,
                        "description": badge.get('description', ''),
                        "category": badge['category'],
                        "rarity": badge['rarity'],
                        "points": badge['points'],
                        "condition": condition_json,
                        "unlock_animation": animation
                    }
                )
                updated += 1
            else:
                # 插入
                await session.execute(
                    text("""
                        INSERT INTO badge_configs (id, name, name_en, icon, icon_url, description, category, rarity, points, condition, unlock_animation, is_active, sort_order)
                        VALUES (:id, :name, :name_en, :icon, :icon_url, :description, :category, :rarity, :points, :condition, :unlock_animation, 1, 0)
                    """),
                    {
                        "id": badge['id'],
                        "name": badge['name'],
                        "name_en": badge.get('name_en', ''),
                        "icon": badge['icon'],
                        "icon_url": icon_url,
                        "description": badge.get('description', ''),
                        "category": badge['category'],
                        "rarity": badge['rarity'],
                        "points": badge['points'],
                        "condition": condition_json,
                        "unlock_animation": animation
                    }
                )
                inserted += 1

            # 打印进度
            total = inserted + updated
            if total % 20 == 0:
                print(f"  Progress: {total}/{len(badges)}")

        await session.commit()
        print(f"\nCompleted!")
        print(f"  Inserted: {inserted}")
        print(f"  Updated: {updated}")
        print(f"  Total: {inserted + updated}")


if __name__ == '__main__':
    print("=" * 50)
    print("Badge Installation Script")
    print("=" * 50)
    asyncio.run(install_badges())
