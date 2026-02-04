"""
勋章初始化脚本
将所有勋章配置合并并导入数据库
同时为 epic 和 legendary 勋章生成解锁动画
"""
import json
import asyncio
from pathlib import Path
from datetime import datetime

# 解锁动画模板 - Epic 级别 (紫色主题)
EPIC_ANIMATION_TEMPLATE = '''/* 勋章解锁动画 - {badge_name} (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">{icon}</span>
  </div>
  <div class="epic-title">{badge_name}</div>
  <div class="epic-points">+{points} 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {{
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}}

.epic-particles {{
  position: absolute;
  width: 100%;
  height: 100%;
  background-image:
    radial-gradient(2px 2px at 20% 30%, #a78bfa, transparent),
    radial-gradient(2px 2px at 40% 70%, #c4b5fd, transparent),
    radial-gradient(2px 2px at 60% 40%, #8b5cf6, transparent),
    radial-gradient(2px 2px at 80% 60%, #a78bfa, transparent),
    radial-gradient(3px 3px at 10% 80%, #c4b5fd, transparent),
    radial-gradient(3px 3px at 90% 20%, #8b5cf6, transparent);
  background-size: 200% 200%;
  animation: epicParticles 3s ease-in-out infinite;
}}

@keyframes epicParticles {{
  0%, 100% {{ background-position: 0% 0%; }}
  50% {{ background-position: 100% 100%; }}
}}

.epic-glow {{
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}}

@keyframes epicGlow {{
  0%, 100% {{ transform: scale(1); opacity: 0.6; }}
  50% {{ transform: scale(1.3); opacity: 0.9; }}
}}

.epic-badge {{
  position: relative;
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 40px rgba(139, 92, 246, 0.8), inset 0 0 20px rgba(255, 255, 255, 0.2);
  animation: epicBadgeIn 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  opacity: 0;
  transform: scale(0);
}}

@keyframes epicBadgeIn {{
  0% {{ opacity: 0; transform: scale(0) rotate(-180deg); }}
  100% {{ opacity: 1; transform: scale(1) rotate(0deg); }}
}}

.epic-icon {{
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}}

.epic-title {{
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}}

.epic-points {{
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}}

@keyframes epicFadeIn {{
  0% {{ opacity: 0; transform: translateY(20px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}
</style>

/* JavaScript */
<script>
setTimeout(function() {{
  if (window.onAnimationComplete) window.onAnimationComplete();
}}, 3500);
</script>'''

# 解锁动画模板 - Legendary 级别 (金色主题 + 闪电效果)
LEGENDARY_ANIMATION_TEMPLATE = '''/* 勋章解锁动画 - {badge_name} (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">{icon}</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">{badge_name}</div>
  <div class="legendary-points">+{points} 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {{
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}}

.legendary-lightning {{
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg,
    transparent 0%,
    rgba(245, 158, 11, 0.1) 45%,
    rgba(245, 158, 11, 0.4) 50%,
    rgba(245, 158, 11, 0.1) 55%,
    transparent 100%);
  animation: legendaryLightning 0.2s ease-out;
  opacity: 0;
}}

@keyframes legendaryLightning {{
  0% {{ opacity: 1; }}
  100% {{ opacity: 0; }}
}}

.legendary-rays {{
  position: absolute;
  width: 400px;
  height: 400px;
  background: conic-gradient(from 0deg,
    transparent 0deg, rgba(245, 158, 11, 0.3) 10deg, transparent 20deg,
    transparent 40deg, rgba(245, 158, 11, 0.3) 50deg, transparent 60deg,
    transparent 80deg, rgba(245, 158, 11, 0.3) 90deg, transparent 100deg,
    transparent 120deg, rgba(245, 158, 11, 0.3) 130deg, transparent 140deg,
    transparent 160deg, rgba(245, 158, 11, 0.3) 170deg, transparent 180deg,
    transparent 200deg, rgba(245, 158, 11, 0.3) 210deg, transparent 220deg,
    transparent 240deg, rgba(245, 158, 11, 0.3) 250deg, transparent 260deg,
    transparent 280deg, rgba(245, 158, 11, 0.3) 290deg, transparent 300deg,
    transparent 320deg, rgba(245, 158, 11, 0.3) 330deg, transparent 340deg,
    transparent 360deg);
  animation: legendaryRays 10s linear infinite;
}}

@keyframes legendaryRays {{
  0% {{ transform: rotate(0deg); }}
  100% {{ transform: rotate(360deg); }}
}}

.legendary-particles {{
  position: absolute;
  width: 100%;
  height: 100%;
  background-image:
    radial-gradient(2px 2px at 15% 25%, #fbbf24, transparent),
    radial-gradient(3px 3px at 35% 65%, #f59e0b, transparent),
    radial-gradient(2px 2px at 55% 35%, #fcd34d, transparent),
    radial-gradient(3px 3px at 75% 55%, #fbbf24, transparent),
    radial-gradient(2px 2px at 25% 75%, #f59e0b, transparent),
    radial-gradient(3px 3px at 85% 15%, #fcd34d, transparent),
    radial-gradient(2px 2px at 45% 85%, #fbbf24, transparent),
    radial-gradient(3px 3px at 65% 5%, #f59e0b, transparent);
  background-size: 150% 150%;
  animation: legendaryParticles 4s ease-in-out infinite;
}}

@keyframes legendaryParticles {{
  0%, 100% {{ background-position: 0% 0%; opacity: 0.8; }}
  50% {{ background-position: 100% 100%; opacity: 1; }}
}}

.legendary-badge {{
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}}

.legendary-ring {{
  position: absolute;
  inset: -10px;
  border: 4px solid transparent;
  border-radius: 50%;
  background: linear-gradient(135deg, #fbbf24, #f59e0b, #d97706) border-box;
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  animation: legendaryRing 2s linear infinite;
}}

@keyframes legendaryRing {{
  0% {{ transform: rotate(0deg); }}
  100% {{ transform: rotate(360deg); }}
}}

@keyframes legendaryBadgeIn {{
  0% {{ opacity: 0; transform: scale(0) translateY(-50px); }}
  60% {{ opacity: 1; transform: scale(1.1) translateY(0); }}
  100% {{ opacity: 1; transform: scale(1) translateY(0); }}
}}

.legendary-badge::before {{
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}}

.legendary-icon {{
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}}

@keyframes legendaryIconPulse {{
  0%, 100% {{ transform: scale(1); }}
  50% {{ transform: scale(1.1); }}
}}

.legendary-title {{
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}}

.legendary-name {{
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}}

.legendary-points {{
  margin-top: 16px;
  padding: 10px 32px;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 24px;
  color: #1f2937;
  font-weight: bold;
  font-size: 20px;
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.6);
  animation: legendaryFadeIn 0.5s ease-out 1.2s forwards;
  opacity: 0;
}}

@keyframes legendaryFadeIn {{
  0% {{ opacity: 0; transform: translateY(30px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {{
  document.querySelector('.legendary-lightning').style.animation = 'legendaryLightning 0.2s ease-out';
}}, 100);
setTimeout(function() {{
  document.querySelector('.legendary-lightning').style.animation = 'legendaryLightning 0.2s ease-out';
}}, 400);

setTimeout(function() {{
  if (window.onAnimationComplete) window.onAnimationComplete();
}}, 4000);
</script>'''


def generate_animation(badge: dict) -> str:
    """为 epic 和 legendary 勋章生成解锁动画"""
    rarity = badge.get('rarity', 'common')

    if rarity == 'epic':
        return EPIC_ANIMATION_TEMPLATE.format(
            badge_name=badge['name'],
            icon=badge['icon'],
            points=badge['points']
        )
    elif rarity == 'legendary':
        return LEGENDARY_ANIMATION_TEMPLATE.format(
            badge_name=badge['name'],
            icon=badge['icon'],
            points=badge['points']
        )
    return None


def load_and_merge_badges():
    """加载并合并所有勋章配置"""
    script_dir = Path(__file__).parent
    all_badges = []

    # 加载所有 JSON 文件
    json_files = sorted(script_dir.glob('badges_part*.json'))

    for json_file in json_files:
        print(f"Loading {json_file.name}...")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            badges = data.get('badges', [])
            all_badges.extend(badges)

    print(f"\nTotal badges loaded: {len(all_badges)}")

    # 统计
    stats = {
        'common': 0,
        'rare': 0,
        'epic': 0,
        'legendary': 0
    }
    categories = {}

    for badge in all_badges:
        rarity = badge.get('rarity', 'common')
        stats[rarity] = stats.get(rarity, 0) + 1

        category = badge.get('category', 'special')
        categories[category] = categories.get(category, 0) + 1

        # 为 epic 和 legendary 生成动画
        if rarity in ['epic', 'legendary']:
            badge['unlock_animation'] = generate_animation(badge)

    print("\nRarity distribution:")
    for rarity, count in stats.items():
        print(f"  {rarity}: {count}")

    print("\nCategory distribution:")
    for category, count in categories.items():
        print(f"  {category}: {count}")

    return all_badges


def save_merged_badges(badges: list):
    """保存合并后的勋章配置"""
    script_dir = Path(__file__).parent
    output_file = script_dir / 'all_badges.json'

    output = {
        'generated_at': datetime.now().isoformat(),
        'total_count': len(badges),
        'badges': badges
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to {output_file}")
    return output_file


def generate_sql_insert(badges: list):
    """生成 SQL INSERT 语句"""
    script_dir = Path(__file__).parent
    sql_file = script_dir / 'insert_badges.sql'

    lines = [
        "-- 勋章配置初始化 SQL",
        f"-- Generated at {datetime.now().isoformat()}",
        f"-- Total badges: {len(badges)}",
        "",
        "-- 清空现有勋章配置（谨慎使用）",
        "-- DELETE FROM badge_configs;",
        "",
        "-- 插入勋章配置",
    ]

    for badge in badges:
        condition_json = json.dumps(badge['condition'], ensure_ascii=False)
        animation = badge.get('unlock_animation', '')
        animation_escaped = animation.replace("'", "''") if animation else ''

        sql = f"""INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('{badge['id']}', '{badge['name']}', '{badge.get('name_en', '')}', '{badge['icon']}', '{badge.get('description', '')}', '{badge['category']}', '{badge['rarity']}', {badge['points']}, '{condition_json}', '{animation_escaped}', 1, 0, datetime('now'))
ON CONFLICT(id) DO UPDATE SET
  name = excluded.name,
  name_en = excluded.name_en,
  icon = excluded.icon,
  description = excluded.description,
  category = excluded.category,
  rarity = excluded.rarity,
  points = excluded.points,
  condition = excluded.condition,
  unlock_animation = excluded.unlock_animation;
"""
        lines.append(sql)

    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"SQL file saved to {sql_file}")
    return sql_file


async def insert_to_database(badges: list):
    """直接插入数据库"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from app.db.session import async_session_maker
    from app.models.models import BadgeConfig
    from sqlalchemy import text

    async with async_session_maker() as session:
        for badge in badges:
            # 检查是否存在
            result = await session.execute(
                text("SELECT id FROM badge_configs WHERE id = :id"),
                {"id": badge['id']}
            )
            existing = result.scalar_one_or_none()

            if existing:
                # 更新
                await session.execute(
                    text("""
                        UPDATE badge_configs SET
                            name = :name,
                            name_en = :name_en,
                            icon = :icon,
                            description = :description,
                            category = :category,
                            rarity = :rarity,
                            points = :points,
                            condition = :condition,
                            unlock_animation = :unlock_animation
                        WHERE id = :id
                    """),
                    {
                        "id": badge['id'],
                        "name": badge['name'],
                        "name_en": badge.get('name_en', ''),
                        "icon": badge['icon'],
                        "description": badge.get('description', ''),
                        "category": badge['category'],
                        "rarity": badge['rarity'],
                        "points": badge['points'],
                        "condition": json.dumps(badge['condition']),
                        "unlock_animation": badge.get('unlock_animation', '')
                    }
                )
            else:
                # 插入
                await session.execute(
                    text("""
                        INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order)
                        VALUES (:id, :name, :name_en, :icon, :description, :category, :rarity, :points, :condition, :unlock_animation, 1, 0)
                    """),
                    {
                        "id": badge['id'],
                        "name": badge['name'],
                        "name_en": badge.get('name_en', ''),
                        "icon": badge['icon'],
                        "description": badge.get('description', ''),
                        "category": badge['category'],
                        "rarity": badge['rarity'],
                        "points": badge['points'],
                        "condition": json.dumps(badge['condition']),
                        "unlock_animation": badge.get('unlock_animation', '')
                    }
                )

        await session.commit()
        print(f"\nInserted/Updated {len(badges)} badges to database")


if __name__ == '__main__':
    print("=" * 50)
    print("勋章配置初始化脚本")
    print("=" * 50)

    # 加载并合并
    badges = load_and_merge_badges()

    # 保存合并后的 JSON
    save_merged_badges(badges)

    # 生成 SQL
    generate_sql_insert(badges)

    # 可选：直接插入数据库
    # asyncio.run(insert_to_database(badges))

    print("\n" + "=" * 50)
    print("完成！")
    print("=" * 50)
