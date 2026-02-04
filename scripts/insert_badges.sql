-- 勋章配置初始化 SQL
-- Generated at 2026-02-02T21:48:34.701320
-- Total badges: 120

-- 清空现有勋章配置（谨慎使用）
-- DELETE FROM badge_configs;

-- 插入勋章配置
INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('first_step', '初次启程', 'First Step', '🚀', '完成第一个学习节点', 'learning', 'common', 10, '{"type": "counter", "metric": "completed_nodes", "target": 1}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('getting_started', '渐入佳境', 'Getting Started', '📖', '完成5个学习节点', 'learning', 'common', 15, '{"type": "counter", "metric": "completed_nodes", "target": 5}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('steady_learner', '稳步前行', 'Steady Learner', '📚', '完成10个学习节点', 'learning', 'common', 20, '{"type": "counter", "metric": "completed_nodes", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('knowledge_seeker', '求知若渴', 'Knowledge Seeker', '🔍', '完成20个学习节点', 'learning', 'common', 25, '{"type": "counter", "metric": "completed_nodes", "target": 20}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('diligent_student', '勤奋学子', 'Diligent Student', '✏️', '完成30个学习节点', 'learning', 'common', 30, '{"type": "counter", "metric": "completed_nodes", "target": 30}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('half_century', '半百之路', 'Half Century', '🎯', '完成50个学习节点', 'learning', 'rare', 50, '{"type": "counter", "metric": "completed_nodes", "target": 50}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('century_milestone', '百节里程碑', 'Century Milestone', '💯', '完成100个学习节点', 'learning', 'rare', 80, '{"type": "counter", "metric": "completed_nodes", "target": 100}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('knowledge_collector', '知识收藏家', 'Knowledge Collector', '📦', '完成150个学习节点', 'learning', 'rare', 100, '{"type": "counter", "metric": "completed_nodes", "target": 150}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('learning_expert', '学习专家', 'Learning Expert', '🎓', '完成200个学习节点', 'learning', 'epic', 150, '{"type": "counter", "metric": "completed_nodes", "target": 200}', '/* 勋章解锁动画 - 学习专家 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🎓</span>
  </div>
  <div class="epic-title">学习专家</div>
  <div class="epic-points">+150 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('knowledge_master', '知识大师', 'Knowledge Master', '👨‍🎓', '完成300个学习节点', 'learning', 'epic', 200, '{"type": "counter", "metric": "completed_nodes", "target": 300}', '/* 勋章解锁动画 - 知识大师 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">👨‍🎓</span>
  </div>
  <div class="epic-title">知识大师</div>
  <div class="epic-points">+200 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('learning_legend', '学习传奇', 'Learning Legend', '🏛️', '完成500个学习节点', 'learning', 'legendary', 500, '{"type": "counter", "metric": "completed_nodes", "target": 500}', '/* 勋章解锁动画 - 学习传奇 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">🏛️</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">学习传奇</div>
  <div class="legendary-points">+500 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('first_course', '课程入门', 'First Course', '📗', '完成第一门课程', 'learning', 'common', 30, '{"type": "courses", "target": 1}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('course_explorer', '课程探索者', 'Course Explorer', '🗺️', '完成3门课程', 'learning', 'common', 50, '{"type": "courses", "target": 3}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('course_enthusiast', '课程爱好者', 'Course Enthusiast', '💝', '完成5门课程', 'learning', 'rare', 80, '{"type": "courses", "target": 5}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('course_collector', '课程收藏家', 'Course Collector', '🏆', '完成10门课程', 'learning', 'rare', 120, '{"type": "courses", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('course_conqueror', '课程征服者', 'Course Conqueror', '⚔️', '完成15门课程', 'learning', 'epic', 180, '{"type": "courses", "target": 15}', '/* 勋章解锁动画 - 课程征服者 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">⚔️</span>
  </div>
  <div class="epic-title">课程征服者</div>
  <div class="epic-points">+180 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('course_champion', '课程冠军', 'Course Champion', '👑', '完成20门课程', 'learning', 'epic', 250, '{"type": "courses", "target": 20}', '/* 勋章解锁动画 - 课程冠军 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">👑</span>
  </div>
  <div class="epic-title">课程冠军</div>
  <div class="epic-points">+250 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('course_grandmaster', '课程宗师', 'Course Grandmaster', '🐉', '完成30门课程', 'learning', 'legendary', 500, '{"type": "courses", "target": 30}', '/* 勋章解锁动画 - 课程宗师 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">🐉</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">课程宗师</div>
  <div class="legendary-points">+500 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('first_hour', '初尝学习', 'First Hour', '⏰', '累计学习1小时', 'learning', 'common', 10, '{"type": "time_based", "target": 1}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('five_hours', '小有积累', 'Five Hours', '⏱️', '累计学习5小时', 'learning', 'common', 20, '{"type": "time_based", "target": 5}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('ten_hours', '十小时达人', 'Ten Hours', '🕐', '累计学习10小时', 'learning', 'common', 30, '{"type": "time_based", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('twenty_hours', '学习投入者', 'Twenty Hours', '🕑', '累计学习20小时', 'learning', 'common', 40, '{"type": "time_based", "target": 20}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('fifty_hours', '半百时光', 'Fifty Hours', '🕒', '累计学习50小时', 'learning', 'rare', 60, '{"type": "time_based", "target": 50}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('hundred_hours', '百小时学者', 'Hundred Hours', '🕓', '累计学习100小时', 'learning', 'rare', 100, '{"type": "time_based", "target": 100}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('two_hundred_hours', '时间富翁', 'Time Millionaire', '🕔', '累计学习200小时', 'learning', 'epic', 180, '{"type": "time_based", "target": 200}', '/* 勋章解锁动画 - 时间富翁 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🕔</span>
  </div>
  <div class="epic-title">时间富翁</div>
  <div class="epic-points">+180 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('five_hundred_hours', '学习巨匠', 'Learning Giant', '🕕', '累计学习500小时', 'learning', 'legendary', 500, '{"type": "time_based", "target": 500}', '/* 勋章解锁动画 - 学习巨匠 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">🕕</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">学习巨匠</div>
  <div class="legendary-points">+500 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('streak_3', '三日坚持', '3-Day Streak', '🔥', '连续学习3天', 'persistence', 'common', 15, '{"type": "streak", "target": 3}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('streak_7', '一周坚持', 'Week Warrior', '💪', '连续学习7天', 'persistence', 'common', 30, '{"type": "streak", "target": 7}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('streak_14', '两周坚持', 'Fortnight Fighter', '⚡', '连续学习14天', 'persistence', 'rare', 50, '{"type": "streak", "target": 14}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('streak_21', '习惯养成', 'Habit Former', '🌟', '连续学习21天，习惯已养成', 'persistence', 'rare', 80, '{"type": "streak", "target": 21}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('streak_30', '月度坚持', 'Monthly Master', '🌙', '连续学习30天', 'persistence', 'rare', 100, '{"type": "streak", "target": 30}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('streak_60', '双月坚持', 'Two Month Titan', '🌕', '连续学习60天', 'persistence', 'epic', 180, '{"type": "streak", "target": 60}', '/* 勋章解锁动画 - 双月坚持 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🌕</span>
  </div>
  <div class="epic-title">双月坚持</div>
  <div class="epic-points">+180 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('streak_90', '季度坚持', 'Quarter Champion', '☀️', '连续学习90天', 'persistence', 'epic', 250, '{"type": "streak", "target": 90}', '/* 勋章解锁动画 - 季度坚持 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">☀️</span>
  </div>
  <div class="epic-title">季度坚持</div>
  <div class="epic-points">+250 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('streak_180', '半年坚持', 'Half Year Hero', '🌈', '连续学习180天', 'persistence', 'legendary', 500, '{"type": "streak", "target": 180}', '/* 勋章解锁动画 - 半年坚持 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">🌈</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">半年坚持</div>
  <div class="legendary-points">+500 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('streak_365', '全年无休', 'Year Round Legend', '🎆', '连续学习365天', 'persistence', 'legendary', 1000, '{"type": "streak", "target": 365}', '/* 勋章解锁动画 - 全年无休 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">🎆</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">全年无休</div>
  <div class="legendary-points">+1000 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('days_7', '一周学员', 'Week Learner', '📅', '累计学习7天', 'persistence', 'common', 15, '{"type": "days", "target": 7}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('days_14', '两周学员', 'Fortnight Learner', '📆', '累计学习14天', 'persistence', 'common', 25, '{"type": "days", "target": 14}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('days_30', '月度学员', 'Monthly Learner', '🗓️', '累计学习30天', 'persistence', 'common', 40, '{"type": "days", "target": 30}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('days_60', '双月学员', 'Two Month Learner', '📋', '累计学习60天', 'persistence', 'rare', 60, '{"type": "days", "target": 60}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('days_90', '季度学员', 'Quarter Learner', '📊', '累计学习90天', 'persistence', 'rare', 80, '{"type": "days", "target": 90}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('days_180', '半年学员', 'Half Year Learner', '📈', '累计学习180天', 'persistence', 'epic', 150, '{"type": "days", "target": 180}', '/* 勋章解锁动画 - 半年学员 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">📈</span>
  </div>
  <div class="epic-title">半年学员</div>
  <div class="epic-points">+150 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('days_365', '年度学员', 'Year Learner', '🎊', '累计学习365天', 'persistence', 'legendary', 300, '{"type": "days", "target": 365}', '/* 勋章解锁动画 - 年度学员 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">🎊</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">年度学员</div>
  <div class="legendary-points">+300 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('max_streak_7', '周冠记录', 'Week Record', '🏅', '历史最长连续学习达到7天', 'persistence', 'common', 20, '{"type": "max_streak", "target": 7}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('max_streak_30', '月冠记录', 'Month Record', '🥇', '历史最长连续学习达到30天', 'persistence', 'rare', 60, '{"type": "max_streak", "target": 30}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('max_streak_90', '季冠记录', 'Quarter Record', '🏆', '历史最长连续学习达到90天', 'persistence', 'epic', 150, '{"type": "max_streak", "target": 90}', '/* 勋章解锁动画 - 季冠记录 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🏆</span>
  </div>
  <div class="epic-title">季冠记录</div>
  <div class="epic-points">+150 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('first_quiz', '初试牛刀', 'First Quiz', '📝', '完成第一次测验', 'quiz', 'common', 10, '{"type": "counter", "metric": "completed_quizzes", "target": 1}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('quiz_5', '测验新手', 'Quiz Novice', '✍️', '完成5次测验', 'quiz', 'common', 20, '{"type": "counter", "metric": "completed_quizzes", "target": 5}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('quiz_10', '测验达人', 'Quiz Expert', '📋', '完成10次测验', 'quiz', 'common', 30, '{"type": "counter", "metric": "completed_quizzes", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('quiz_25', '测验高手', 'Quiz Master', '🎯', '完成25次测验', 'quiz', 'rare', 50, '{"type": "counter", "metric": "completed_quizzes", "target": 25}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('quiz_50', '测验专家', 'Quiz Specialist', '🏅', '完成50次测验', 'quiz', 'rare', 80, '{"type": "counter", "metric": "completed_quizzes", "target": 50}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('quiz_100', '百题斩', 'Century Quizzer', '💯', '完成100次测验', 'quiz', 'epic', 150, '{"type": "counter", "metric": "completed_quizzes", "target": 100}', '/* 勋章解锁动画 - 百题斩 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">💯</span>
  </div>
  <div class="epic-title">百题斩</div>
  <div class="epic-points">+150 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('quiz_200', '做题机器', 'Quiz Machine', '🤖', '完成200次测验', 'quiz', 'legendary', 300, '{"type": "counter", "metric": "completed_quizzes", "target": 200}', '/* 勋章解锁动画 - 做题机器 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">🤖</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">做题机器</div>
  <div class="legendary-points">+300 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('first_simulator', '模拟初体验', 'First Simulation', '🎮', '完成第一个模拟器', 'quiz', 'common', 15, '{"type": "counter", "metric": "completed_simulators", "target": 1}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('simulator_5', '模拟新手', 'Simulator Novice', '🕹️', '完成5个模拟器', 'quiz', 'common', 30, '{"type": "counter", "metric": "completed_simulators", "target": 5}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('simulator_10', '模拟达人', 'Simulator Expert', '🎲', '完成10个模拟器', 'quiz', 'rare', 50, '{"type": "counter", "metric": "completed_simulators", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('simulator_25', '模拟高手', 'Simulator Master', '🎰', '完成25个模拟器', 'quiz', 'rare', 80, '{"type": "counter", "metric": "completed_simulators", "target": 25}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('simulator_50', '模拟专家', 'Simulator Specialist', '🔬', '完成50个模拟器', 'quiz', 'epic', 150, '{"type": "counter", "metric": "completed_simulators", "target": 50}', '/* 勋章解锁动画 - 模拟专家 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🔬</span>
  </div>
  <div class="epic-title">模拟专家</div>
  <div class="epic-points">+150 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('simulator_100', '模拟大师', 'Simulator Grandmaster', '🧪', '完成100个模拟器', 'quiz', 'epic', 200, '{"type": "counter", "metric": "completed_simulators", "target": 100}', '/* 勋章解锁动画 - 模拟大师 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🧪</span>
  </div>
  <div class="epic-title">模拟大师</div>
  <div class="epic-points">+200 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('simulator_legend', '模拟传奇', 'Simulator Legend', '⚗️', '完成200个模拟器', 'quiz', 'legendary', 400, '{"type": "counter", "metric": "completed_simulators", "target": 200}', '/* 勋章解锁动画 - 模拟传奇 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">⚗️</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">模拟传奇</div>
  <div class="legendary-points">+400 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('mini_lesson_1', '小课堂初体验', 'First Mini Lesson', '🎬', '完成第一个小课堂', 'practice', 'common', 10, '{"type": "counter", "metric": "mini_lessons_completed", "target": 1}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('mini_lesson_5', '小课堂新手', 'Mini Lesson Novice', '📺', '完成5个小课堂', 'practice', 'common', 20, '{"type": "counter", "metric": "mini_lessons_completed", "target": 5}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('mini_lesson_10', '小课堂达人', 'Mini Lesson Expert', '📱', '完成10个小课堂', 'practice', 'common', 30, '{"type": "counter", "metric": "mini_lessons_completed", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('mini_lesson_25', '小课堂高手', 'Mini Lesson Master', '💡', '完成25个小课堂', 'practice', 'rare', 50, '{"type": "counter", "metric": "mini_lessons_completed", "target": 25}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('mini_lesson_50', '小课堂专家', 'Mini Lesson Specialist', '🌟', '完成50个小课堂', 'practice', 'rare', 80, '{"type": "counter", "metric": "mini_lessons_completed", "target": 50}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('mini_lesson_100', '小课堂大师', 'Mini Lesson Grandmaster', '✨', '完成100个小课堂', 'practice', 'epic', 150, '{"type": "counter", "metric": "mini_lessons_completed", "target": 100}', '/* 勋章解锁动画 - 小课堂大师 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">✨</span>
  </div>
  <div class="epic-title">小课堂大师</div>
  <div class="epic-points">+150 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('mini_lesson_200', '小课堂传奇', 'Mini Lesson Legend', '🎯', '完成200个小课堂', 'practice', 'legendary', 300, '{"type": "counter", "metric": "mini_lessons_completed", "target": 200}', '/* 勋章解锁动画 - 小课堂传奇 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">🎯</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">小课堂传奇</div>
  <div class="legendary-points">+300 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('knowledge_point_10', '知识点收集者', 'Knowledge Collector', '📌', '掌握10个知识点', 'practice', 'common', 15, '{"type": "counter", "metric": "knowledge_points_mastered", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('knowledge_point_30', '知识点积累者', 'Knowledge Accumulator', '📍', '掌握30个知识点', 'practice', 'common', 30, '{"type": "counter", "metric": "knowledge_points_mastered", "target": 30}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('knowledge_point_50', '知识点达人', 'Knowledge Expert', '🎯', '掌握50个知识点', 'practice', 'rare', 50, '{"type": "counter", "metric": "knowledge_points_mastered", "target": 50}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('knowledge_point_100', '知识点专家', 'Knowledge Specialist', '🧠', '掌握100个知识点', 'practice', 'rare', 80, '{"type": "counter", "metric": "knowledge_points_mastered", "target": 100}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('knowledge_point_200', '知识点大师', 'Knowledge Master', '🎓', '掌握200个知识点', 'practice', 'epic', 150, '{"type": "counter", "metric": "knowledge_points_mastered", "target": 200}', '/* 勋章解锁动画 - 知识点大师 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🎓</span>
  </div>
  <div class="epic-title">知识点大师</div>
  <div class="epic-points">+150 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('knowledge_point_500', '知识点宗师', 'Knowledge Grandmaster', '👨‍🎓', '掌握500个知识点', 'practice', 'epic', 250, '{"type": "counter", "metric": "knowledge_points_mastered", "target": 500}', '/* 勋章解锁动画 - 知识点宗师 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">👨‍🎓</span>
  </div>
  <div class="epic-title">知识点宗师</div>
  <div class="epic-points">+250 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('knowledge_point_1000', '知识点传奇', 'Knowledge Legend', '🏛️', '掌握1000个知识点', 'practice', 'legendary', 500, '{"type": "counter", "metric": "knowledge_points_mastered", "target": 1000}', '/* 勋章解锁动画 - 知识点传奇 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">🏛️</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">知识点传奇</div>
  <div class="legendary-points">+500 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('ai_chat_1', 'AI初次对话', 'First AI Chat', '🤖', '与AI助手进行第一次对话', 'special', 'common', 10, '{"type": "counter", "metric": "ai_conversations", "target": 1}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('ai_chat_10', 'AI对话新手', 'AI Chat Novice', '💬', '与AI助手进行10次对话', 'special', 'common', 20, '{"type": "counter", "metric": "ai_conversations", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('ai_chat_50', 'AI对话达人', 'AI Chat Expert', '🗣️', '与AI助手进行50次对话', 'special', 'rare', 50, '{"type": "counter", "metric": "ai_conversations", "target": 50}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('ai_chat_100', 'AI对话专家', 'AI Chat Specialist', '🎙️', '与AI助手进行100次对话', 'special', 'rare', 80, '{"type": "counter", "metric": "ai_conversations", "target": 100}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('ai_chat_500', 'AI对话大师', 'AI Chat Master', '🎤', '与AI助手进行500次对话', 'special', 'epic', 200, '{"type": "counter", "metric": "ai_conversations", "target": 500}', '/* 勋章解锁动画 - AI对话大师 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🎤</span>
  </div>
  <div class="epic-title">AI对话大师</div>
  <div class="epic-points">+200 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('training_plan_1', '训练计划启动', 'First Training Plan', '📋', '完成第一个AI训练计划', 'special', 'common', 20, '{"type": "counter", "metric": "training_plans_completed", "target": 1}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('training_plan_5', '训练计划新手', 'Training Novice', '📊', '完成5个AI训练计划', 'special', 'common', 40, '{"type": "counter", "metric": "training_plans_completed", "target": 5}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('training_plan_10', '训练计划达人', 'Training Expert', '📈', '完成10个AI训练计划', 'special', 'rare', 80, '{"type": "counter", "metric": "training_plans_completed", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('training_plan_25', '训练计划专家', 'Training Specialist', '🏋️', '完成25个AI训练计划', 'special', 'epic', 150, '{"type": "counter", "metric": "training_plans_completed", "target": 25}', '/* 勋章解锁动画 - 训练计划专家 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🏋️</span>
  </div>
  <div class="epic-title">训练计划专家</div>
  <div class="epic-points">+150 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('training_plan_50', '训练计划大师', 'Training Master', '🏆', '完成50个AI训练计划', 'special', 'legendary', 300, '{"type": "counter", "metric": "training_plans_completed", "target": 50}', '/* 勋章解锁动画 - 训练计划大师 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">🏆</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">训练计划大师</div>
  <div class="legendary-points">+300 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('ai_question_10', '好奇宝宝', 'Curious Mind', '❓', '向AI提出10个问题', 'special', 'common', 15, '{"type": "counter", "metric": "ai_questions_asked", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('ai_question_50', '求知探索者', 'Knowledge Seeker', '🔍', '向AI提出50个问题', 'special', 'rare', 50, '{"type": "counter", "metric": "ai_questions_asked", "target": 50}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('ai_question_200', '问题专家', 'Question Expert', '💭', '向AI提出200个问题', 'special', 'epic', 150, '{"type": "counter", "metric": "ai_questions_asked", "target": 200}', '/* 勋章解锁动画 - 问题专家 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">💭</span>
  </div>
  <div class="epic-title">问题专家</div>
  <div class="epic-points">+150 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('ai_question_500', '问题大师', 'Question Master', '🧐', '向AI提出500个问题', 'special', 'legendary', 300, '{"type": "counter", "metric": "ai_questions_asked", "target": 500}', '/* 勋章解锁动画 - 问题大师 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">🧐</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">问题大师</div>
  <div class="legendary-points">+300 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('early_bird', '早起鸟儿', 'Early Bird', '🌅', '在早上6点前开始学习', 'special', 'rare', 30, '{"type": "special", "metric": "early_morning_study", "target": 1}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('night_owl', '夜猫子', 'Night Owl', '🦉', '在晚上11点后��习', 'special', 'rare', 30, '{"type": "special", "metric": "late_night_study", "target": 1}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('weekend_warrior', '周末战士', 'Weekend Warrior', '⚔️', '连续4个周末都有学习', 'special', 'rare', 50, '{"type": "special", "metric": "weekend_study_streak", "target": 4}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('perfect_week', '完美一周', 'Perfect Week', '💎', '一周内每天学习超过2小时', 'special', 'epic', 100, '{"type": "special", "metric": "perfect_week", "target": 1}', '/* 勋章解锁动画 - 完美一周 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">💎</span>
  </div>
  <div class="epic-title">完美一周</div>
  <div class="epic-points">+100 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('marathon_learner', '马拉松学习者', 'Marathon Learner', '🏃', '单日学习超过5小时', 'special', 'epic', 80, '{"type": "special", "metric": "daily_hours", "target": 5}', '/* 勋章解锁动画 - 马拉松学习者 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🏃</span>
  </div>
  <div class="epic-title">马拉松学习者</div>
  <div class="epic-points">+80 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('speed_learner', '速学达人', 'Speed Learner', '⚡', '单日完成10个学习节点', 'special', 'rare', 50, '{"type": "special", "metric": "daily_nodes", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('comeback_king', '王者归来', 'Comeback King', '👑', '中断学习7天后重新开始', 'special', 'common', 20, '{"type": "special", "metric": "comeback_after_break", "target": 7}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('accuracy_90', '精准射手', 'Sharpshooter', '🎯', '测验正确率达到90%以上（至少20题）', 'quiz', 'rare', 60, '{"type": "threshold", "metric": "quiz_accuracy", "target": 90}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('accuracy_95', '神射手', 'Marksman', '🏹', '测验正确率达到95%以上（至少50题）', 'quiz', 'epic', 120, '{"type": "threshold", "metric": "quiz_accuracy", "target": 95}', '/* 勋章解锁动画 - 神射手 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🏹</span>
  </div>
  <div class="epic-title">神射手</div>
  <div class="epic-points">+120 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('accuracy_99', '完美主义者', 'Perfectionist', '💯', '测验正确率达到99%以上（至少100题）', 'quiz', 'legendary', 300, '{"type": "threshold", "metric": "quiz_accuracy", "target": 99}', '/* 勋章解锁动画 - 完美主义者 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">💯</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">完美主义者</div>
  <div class="legendary-points">+300 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('error_learner_10', '错题收集者', 'Error Collector', '📕', '收集10道错题并复习', 'quiz', 'common', 15, '{"type": "counter", "metric": "wrong_questions_reviewed", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('error_learner_50', '错题克星', 'Error Buster', '📗', '收集50道错题并复习', 'quiz', 'rare', 50, '{"type": "counter", "metric": "wrong_questions_reviewed", "target": 50}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('error_learner_100', '错题终结者', 'Error Terminator', '📘', '收集100道错题并复习', 'quiz', 'epic', 100, '{"type": "counter", "metric": "wrong_questions_reviewed", "target": 100}', '/* 勋章解锁动画 - 错题终结者 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">📘</span>
  </div>
  <div class="epic-title">错题终结者</div>
  <div class="epic-points">+100 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('error_master_rate', '错题掌握者', 'Error Master', '✅', '错题复习后正确率达到80%', 'quiz', 'rare', 60, '{"type": "threshold", "metric": "error_review_accuracy", "target": 80}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('social_first_share', '分享达人', 'First Share', '📤', '第一次分享学习成果', 'special', 'common', 10, '{"type": "counter", "metric": "shares", "target": 1}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('note_taker_10', '笔记新手', 'Note Novice', '📝', '创建10条学习笔记', 'learning', 'common', 15, '{"type": "counter", "metric": "notes_created", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('note_taker_50', '笔记达人', 'Note Expert', '📒', '创建50条学习笔记', 'learning', 'rare', 50, '{"type": "counter", "metric": "notes_created", "target": 50}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('note_taker_100', '笔记大师', 'Note Master', '📓', '创建100条学习笔记', 'learning', 'epic', 100, '{"type": "counter", "metric": "notes_created", "target": 100}', '/* 勋章解锁动画 - 笔记大师 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">📓</span>
  </div>
  <div class="epic-title">笔记大师</div>
  <div class="epic-points">+100 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('bookmark_collector', '收藏家', 'Bookmark Collector', '🔖', '收藏20个学习内容', 'learning', 'common', 15, '{"type": "counter", "metric": "bookmarks", "target": 20}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('domain_explorer', '领域探索者', 'Domain Explorer', '🌐', '学习3个不同领域的课程', 'learning', 'rare', 50, '{"type": "counter", "metric": "domains_explored", "target": 3}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('domain_master', '领域大师', 'Domain Master', '🌍', '学习5个不同领域的课程', 'learning', 'epic', 100, '{"type": "counter", "metric": "domains_explored", "target": 5}', '/* 勋章解锁动画 - 领域大师 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🌍</span>
  </div>
  <div class="epic-title">领域大师</div>
  <div class="epic-points">+100 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('first_badge', '勋章收集者', 'Badge Collector', '🎖️', '获得第一枚勋章', 'special', 'common', 5, '{"type": "counter", "metric": "badges_earned", "target": 1}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('badge_10', '勋章达人', 'Badge Expert', '🏅', '获得10枚勋章', 'special', 'common', 20, '{"type": "counter", "metric": "badges_earned", "target": 10}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('badge_30', '勋章专家', 'Badge Specialist', '🥇', '获得30枚勋章', 'special', 'rare', 50, '{"type": "counter", "metric": "badges_earned", "target": 30}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('badge_60', '勋章大师', 'Badge Master', '🏆', '获得60枚勋章', 'special', 'epic', 100, '{"type": "counter", "metric": "badges_earned", "target": 60}', '/* 勋章解锁动画 - 勋章大师 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🏆</span>
  </div>
  <div class="epic-title">勋章大师</div>
  <div class="epic-points">+100 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('badge_100', '勋章传奇', 'Badge Legend', '👑', '获得100枚勋章', 'special', 'legendary', 300, '{"type": "counter", "metric": "badges_earned", "target": 100}', '/* 勋章解锁动画 - 勋章传奇 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">👑</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">勋章传奇</div>
  <div class="legendary-points">+300 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('total_points_100', '积分新手', 'Points Novice', '⭐', '累计获得100积分', 'special', 'common', 10, '{"type": "threshold", "metric": "total_points", "target": 100}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('total_points_500', '积分达人', 'Points Expert', '🌟', '累计获得500积分', 'special', 'common', 20, '{"type": "threshold", "metric": "total_points", "target": 500}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('total_points_1000', '积分专家', 'Points Specialist', '💫', '累计获得1000积分', 'special', 'rare', 50, '{"type": "threshold", "metric": "total_points", "target": 1000}', '', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('total_points_3000', '积分大师', 'Points Master', '✨', '累计获得3000积分', 'special', 'epic', 100, '{"type": "threshold", "metric": "total_points", "target": 3000}', '/* 勋章解锁动画 - 积分大师 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">✨</span>
  </div>
  <div class="epic-title">积分大师</div>
  <div class="epic-points">+100 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('total_points_10000', '积分传奇', 'Points Legend', '🌠', '累计获得10000积分', 'special', 'legendary', 500, '{"type": "threshold", "metric": "total_points", "target": 10000}', '/* 勋章解锁动画 - 积分传奇 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">🌠</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">积分传奇</div>
  <div class="legendary-points">+500 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('wrong_to_right_50', '知错能改', 'Learn From Mistakes', '🔄', '将50道错题重新答对', 'quiz', 'epic', 120, '{"type": "counter", "metric": "wrong_questions_corrected", "target": 50}', '/* 勋章解锁动画 - 知错能改 (Epic) */

/* HTML */
<div class="epic-unlock-container">
  <div class="epic-particles"></div>
  <div class="epic-glow"></div>
  <div class="epic-badge">
    <span class="epic-icon">🔄</span>
  </div>
  <div class="epic-title">知错能改</div>
  <div class="epic-points">+120 积分</div>
</div>

/* CSS */
<style>
.epic-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
  z-index: 1000;
}

.epic-particles {
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
}

@keyframes epicParticles {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.epic-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: epicGlow 2s ease-in-out infinite;
}

@keyframes epicGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 0.9; }
}

.epic-badge {
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
}

@keyframes epicBadgeIn {
  0% { opacity: 0; transform: scale(0) rotate(-180deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.epic-icon {
  font-size: 56px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.epic-title {
  margin-top: 24px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  animation: epicFadeIn 0.5s ease-out 0.5s forwards;
  opacity: 0;
}

.epic-points {
  margin-top: 12px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  animation: epicFadeIn 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

@keyframes epicFadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 3500);
</script>', 1, 0, datetime('now'))
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

INSERT INTO badge_configs (id, name, name_en, icon, description, category, rarity, points, condition, unlock_animation, is_active, sort_order, created_at)
VALUES ('improvement_master', '进步大师', 'Improvement Master', '📈', '错题正确率从50%提升到90%', 'quiz', 'legendary', 300, '{"type": "special", "metric": "error_rate_improvement", "target": 40}', '/* 勋章解锁动画 - 进步大师 (Legendary) */

/* HTML */
<div class="legendary-unlock-container">
  <div class="legendary-lightning"></div>
  <div class="legendary-rays"></div>
  <div class="legendary-particles"></div>
  <div class="legendary-badge">
    <div class="legendary-ring"></div>
    <span class="legendary-icon">📈</span>
  </div>
  <div class="legendary-title">传说成就</div>
  <div class="legendary-name">进步大师</div>
  <div class="legendary-points">+300 积分</div>
</div>

/* CSS */
<style>
.legendary-unlock-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.98) 60%);
  z-index: 1000;
  overflow: hidden;
}

.legendary-lightning {
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
}

@keyframes legendaryLightning {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

.legendary-rays {
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
}

@keyframes legendaryRays {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legendary-particles {
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
}

@keyframes legendaryParticles {
  0%, 100% { background-position: 0% 0%; opacity: 0.8; }
  50% { background-position: 100% 100%; opacity: 1; }
}

.legendary-badge {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: legendaryBadgeIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
  opacity: 0;
  transform: scale(0);
}

.legendary-ring {
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
}

@keyframes legendaryRing {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes legendaryBadgeIn {
  0% { opacity: 0; transform: scale(0) translateY(-50px); }
  60% { opacity: 1; transform: scale(1.1) translateY(0); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.legendary-badge::before {
  content: '''';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.9), 0 0 100px rgba(245, 158, 11, 0.5), inset 0 0 30px rgba(255, 255, 255, 0.3);
}

.legendary-icon {
  position: relative;
  font-size: 64px;
  filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
  animation: legendaryIconPulse 1.5s ease-in-out infinite;
}

@keyframes legendaryIconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.legendary-title {
  margin-top: 24px;
  font-size: 16px;
  font-weight: bold;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 4px;
  animation: legendaryFadeIn 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

.legendary-name {
  margin-top: 8px;
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
  animation: legendaryFadeIn 0.5s ease-out 1s forwards;
  opacity: 0;
}

.legendary-points {
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
}

@keyframes legendaryFadeIn {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>

/* JavaScript */
<script>
// 触发闪电效果
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 100);
setTimeout(function() {
  document.querySelector(''.legendary-lightning'').style.animation = ''legendaryLightning 0.2s ease-out'';
}, 400);

setTimeout(function() {
  if (window.onAnimationComplete) window.onAnimationComplete();
}, 4000);
</script>', 1, 0, datetime('now'))
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
