"""
Phase 13: Agent 强化学习与自适应任务生成
- 奖惩信号计算与策略权重自我优化
- 情感+BKT驱动的自适应任务生成
- 个性化学习路径（整合小课堂/做题家/模拟器/跨学科）
"""
import math
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from sqlalchemy import select, func, and_, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    StudentKnowledgeState, KnowledgeNode, Subject,
    StudentEmotionState, StudentEvent, StudentMisconception,
    ReviewSchedule, StudentAssessment, StudentLearningPath,
    AgentStrategyReward, AgentStrategyWeight,
    CourseRelation, Course,
    StudentGoal, LearningHabit, UserProfile,
)


# ==================== 常量 ====================

# 情感→难度因子
EMOTION_DIFFICULTY = {
    "frustration": 0.5,
    "anxiety": 0.7,
    "boredom": 1.4,
    "focus": 1.0,
    "excitement": 1.2,
}

# 内容类型及基础时长
CONTENT_TYPES = {
    "lecture": {"label": "小课堂", "minutes": 8, "min_mastery": 0, "max_mastery": 0.4},
    "simulator": {"label": "模拟器", "minutes": 10, "min_mastery": 0.2, "max_mastery": 0.7},
    "grinder": {"label": "做题家", "minutes": 6, "min_mastery": 0.3, "max_mastery": 0.8},
    "tutor": {"label": "诊断对话", "minutes": 7, "min_mastery": 0, "max_mastery": 0.6},
    "review": {"label": "间隔复习", "minutes": 4, "min_mastery": 0.5, "max_mastery": 1.0},
    "challenge": {"label": "挑战题", "minutes": 8, "min_mastery": 0.7, "max_mastery": 1.0},
}

# 学习率（策略权重更新速度）
LEARNING_RATE = 0.05

# ε-greedy 探索参数
EPSILON_START = 0.3   # 初始探索率
EPSILON_MIN = 0.05    # 最低探索率
EPSILON_DECAY = 50    # 衰减速度（episodes数）


class AdaptiveAgentService:

    # ==================== 1. 自适应任务生成 ====================

    async def generate_adaptive_tasks(
        self, db: AsyncSession, user_id: int,
        subject_id: Optional[int] = None,
        session_minutes: int = 30,
    ) -> dict:
        """根据情感+BKT状态自适应生成任务列表"""
        # 收集学生状态
        emotion = await self._get_emotion(db, user_id)
        nodes = await self._get_knowledge_states(db, user_id, subject_id)
        review_due = await self._get_review_due(db, user_id)
        misconceptions = await self._get_unresolved_misconceptions(db, user_id)
        strategy_weights = await self._get_strategy_weights(db, "task_generation")
        content_weights = await self._get_strategy_weights(db, "content_type")
        total_episodes = await self._get_total_episodes(db, "content_type")

        # Phase 16: 收集目标和习惯数据
        goal_result = await db.execute(
            select(StudentGoal).where(and_(
                StudentGoal.user_id == user_id,
                StudentGoal.status == "active",
            ))
        )
        active_goals = list(goal_result.scalars().all())
        goal_node_ids = {g.node_id for g in active_goals if g.node_id}
        goal_subject_ids = {g.subject_id for g in active_goals if g.subject_id}

        habit_result = await db.execute(
            select(LearningHabit).where(
                LearningHabit.user_id == user_id,
            ).order_by(LearningHabit.date.desc()).limit(14)
        )
        recent_habits = list(habit_result.scalars().all())
        consistency = len(recent_habits) / 14.0

        # Phase 16: 学习风格
        profile_result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = profile_result.scalars().first()
        learning_style = (profile.learning_style or {}) if profile else {}

        emo_type = emotion.get("type", "focus")
        emo_intensity = emotion.get("intensity", 0.5)
        diff_factor = EMOTION_DIFFICULTY.get(emo_type, 1.0)
        # 高强度负面情感进一步降低难度因子
        if emo_type in ("frustration", "anxiety") and emo_intensity > 0.7:
            diff_factor = max(0.3, diff_factor - (emo_intensity - 0.7) * 0.5)

        # Phase 16: 习惯驱动难度和时长调整（必须在 diff_factor 定义之后）
        if consistency > 0.8:
            diff_factor = min(diff_factor + 0.1, 1.5)
        elif consistency < 0.3:
            diff_factor = max(diff_factor - 0.15, 0.3)
            session_minutes = min(session_minutes, 15)

        # 生成候选任务
        candidates = []

        # 复习到期任务
        for r in review_due[:5]:
            candidates.append({
                "content_type": "review",
                "node_id": r["node_id"],
                "node_name": r["node_name"],
                "mastery": r.get("mastery", 0.5),
                "difficulty": 0.3 * diff_factor,
                "minutes": 4,
                "reason": "复习到期，防止遗忘",
                "priority": 1,
            })

        # 误解纠正任务
        for m in misconceptions[:3]:
            candidates.append({
                "content_type": "tutor",
                "node_id": m["node_id"],
                "node_name": m["node_name"],
                "mastery": m.get("mastery", 0.3),
                "difficulty": 0.4 * diff_factor,
                "minutes": 7,
                "reason": f"纠正误解: {m['misconception'][:30]}",
                "priority": 2,
            })

        # 基于掌握度的学习任务
        for n in nodes:
            mastery = n["mastery"]
            ct = self._select_content_type(mastery, emo_type, content_weights, total_episodes, learning_style)
            cfg = CONTENT_TYPES[ct]
            base_diff = mastery + 0.1
            adj_diff = max(0.1, min(1.0, base_diff * diff_factor))

            # 情感差时降低难度和时长
            minutes = cfg["minutes"]
            if emo_type == "frustration":
                minutes = max(3, minutes - 2)
                adj_diff = min(adj_diff, 0.4)
            elif emo_type == "anxiety":
                minutes = max(3, minutes - 1)
                adj_diff = min(adj_diff, 0.5)
            elif emo_type == "boredom" and mastery > 0.7:
                ct = "challenge"
                minutes = 8
                adj_diff = min(1.0, mastery + 0.2)

            candidates.append({
                "content_type": ct,
                "node_id": n["node_id"],
                "node_name": n["node_name"],
                "mastery": mastery,
                "difficulty": round(adj_diff, 2),
                "minutes": minutes,
                "reason": self._task_reason(ct, mastery, emo_type),
                "priority": 3 if mastery < 0.4 else 4 if mastery < 0.7 else 5,
            })

        # 按优先级排序 + 策略权重加权 + Phase 16 目标对齐
        for c in candidates:
            ct = c["content_type"]
            w = strategy_weights.get(
                {"lecture": "learn", "simulator": "learn", "grinder": "practice",
                 "tutor": "remediate", "review": "review", "challenge": "challenge"
                }.get(ct, "learn"), 0.2
            )
            c["score"] = round((1.0 / c["priority"]) * w * 10, 3)

            # Phase 16: 目标对齐加分
            nid = c.get("node_id")
            if nid in goal_node_ids:
                c["score"] *= 1.5
                c["reason"] += "（目标关联）"

        candidates.sort(key=lambda x: x["score"], reverse=True)

        # 按时间预算选择
        selected = []
        remaining = session_minutes
        seen_nodes = set()
        for c in candidates:
            if remaining < c["minutes"]:
                continue
            if c["node_id"] in seen_nodes:
                continue
            selected.append(c)
            remaining -= c["minutes"]
            seen_nodes.add(c["node_id"])

        # 穿插不同类型防疲劳
        selected = self._interleave_tasks(selected)

        return {
            "tasks": selected,
            "total_tasks": len(selected),
            "total_minutes": session_minutes - remaining,
            "emotion": emotion,
            "difficulty_factor": diff_factor,
            "strategy_weights": strategy_weights,
            "emotion_alert": "情感持续恶化，已自动降低难度" if emotion.get("worsening") else None,
        }

    # ==================== 2. 奖惩信号计算 ====================

    async def compute_reward(
        self, db: AsyncSession, user_id: int,
        strategy_type: str,
        action_taken: dict,
        state_before: dict,
        state_after: dict,
    ) -> dict:
        """计算奖励信号并更新策略权重"""
        components = {}

        # R1: 掌握度提升 (+0.4 max)
        m_before = state_before.get("avg_mastery", 0)
        m_after = state_after.get("avg_mastery", 0)
        mastery_gain = m_after - m_before
        components["mastery_gain"] = round(min(mastery_gain * 4, 0.4), 3)

        # R2: 情感改善 (+0.3 max)
        emo_scores = {"frustration": -1, "anxiety": -0.5, "boredom": -0.3, "focus": 0.3, "excitement": 0.5}
        emo_before = emo_scores.get(state_before.get("emotion", "focus"), 0)
        emo_after = emo_scores.get(state_after.get("emotion", "focus"), 0)
        emotion_improvement = emo_after - emo_before
        components["emotion_improvement"] = round(min(max(emotion_improvement * 0.3, -0.3), 0.3), 3)

        # R3: 正确率 (+0.2 max)
        acc = state_after.get("accuracy", 0.5)
        components["accuracy"] = round((acc - 0.5) * 0.4, 3)

        # R4: 学习时间效率 (+0.1 max)
        time_spent = state_after.get("time_minutes", 0)
        planned = action_taken.get("planned_minutes", 30)
        if planned > 0 and time_spent > 0:
            efficiency = min(time_spent / planned, 1.5)
            components["efficiency"] = round(0.1 * (1.0 - abs(1.0 - efficiency)), 3)
        else:
            components["efficiency"] = 0.0

        # 总奖励
        reward = sum(components.values())
        reward = max(-1.0, min(1.0, reward))

        # 持久化奖惩记录
        record = AgentStrategyReward(
            user_id=user_id,
            strategy_type=strategy_type,
            action_taken=action_taken,
            student_state_before=state_before,
            student_state_after=state_after,
            reward_signal=round(reward, 4),
            reward_components=components,
        )
        db.add(record)

        # 更新策略权重
        await self._update_strategy_weights(db, strategy_type, action_taken, reward)
        await db.commit()

        return {
            "reward": round(reward, 4),
            "components": components,
            "strategy_type": strategy_type,
            "weights_updated": True,
        }

    # ==================== 3. 个性化学习路径 ====================

    async def generate_adaptive_path(
        self, db: AsyncSession, user_id: int,
        subject_id: Optional[int] = None,
        session_minutes: int = 30,
        include_cross_discipline: bool = False,
    ) -> dict:
        """整合小课堂/做题家/模拟器/跨学科的个性化学习路径"""
        emotion = await self._get_emotion(db, user_id)
        nodes = await self._get_knowledge_states(db, user_id, subject_id)
        review_due = await self._get_review_due(db, user_id)
        content_weights = await self._get_strategy_weights(db, "content_type")
        total_episodes = await self._get_total_episodes(db, "content_type")

        # Phase 16: 学习风格
        profile_result2 = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile2 = profile_result2.scalars().first()
        learning_style2 = (profile2.learning_style or {}) if profile2 else {}

        emo_type = emotion.get("type", "focus")
        emo_intensity = emotion.get("intensity", 0.5)
        emo_worsening = emotion.get("worsening", False)
        diff_factor = EMOTION_DIFFICULTY.get(emo_type, 1.0)
        # 强度越高，难度因子偏移越大
        if emo_type in ("frustration", "anxiety") and emo_intensity > 0.7:
            diff_factor = max(0.3, diff_factor - (emo_intensity - 0.7) * 0.5)

        path_items = []
        remaining = session_minutes

        # Phase 1: 情感恢复（强度/恶化驱动动态时长）
        if emo_type in ("frustration", "anxiety") and remaining >= 3:
            # 基础3分钟，高强度+2，恶化中+2
            recovery_min = 3
            if emo_intensity > 0.7:
                recovery_min += 2
            if emo_worsening:
                recovery_min += 2
            recovery_min = min(recovery_min, remaining)
            path_items.append({
                "step": len(path_items) + 1,
                "activity": "emotion_recovery",
                "content_type": "review",
                "description": "复习已掌握内容，恢复信心" if emo_type == "frustration" else "轻松回顾，缓解压力",
                "minutes": recovery_min,
                "difficulty": 0.15 if emo_worsening else 0.2,
                "emotion_alert": "情感持续恶化，已延长恢复时间" if emo_worsening else None,
            })
            remaining -= recovery_min

        # Phase 2: 到期复习
        for r in review_due[:3]:
            if remaining < 4:
                break
            path_items.append({
                "step": len(path_items) + 1,
                "activity": "spaced_review",
                "content_type": "review",
                "node_id": r["node_id"],
                "node_name": r["node_name"],
                "description": f"间隔复习: {r['node_name']}",
                "minutes": 4,
                "difficulty": round(0.3 * diff_factor, 2),
            })
            remaining -= 4

        # Phase 3: 核心学习（按mastery升序，薄弱优先）
        sorted_nodes = sorted(nodes, key=lambda x: x["mastery"])
        for n in sorted_nodes:
            if remaining < 5:
                break
            mastery = n["mastery"]
            ct = self._select_content_type(mastery, emo_type, content_weights, total_episodes, learning_style2)
            cfg = CONTENT_TYPES[ct]
            minutes = min(cfg["minutes"], remaining)

            if emo_type == "frustration":
                minutes = max(3, minutes - 2)

            path_items.append({
                "step": len(path_items) + 1,
                "activity": "core_learning",
                "content_type": ct,
                "node_id": n["node_id"],
                "node_name": n["node_name"],
                "description": f"{cfg['label']}: {n['node_name']}",
                "minutes": minutes,
                "difficulty": round(max(0.1, min(1.0, (mastery + 0.1) * diff_factor)), 2),
                "mastery": mastery,
            })
            remaining -= minutes

        # Phase 4: 挑战/拓展（情感好+掌握度高时）
        if emo_type in ("focus", "excitement", "boredom") and remaining >= 6:
            high_mastery = [n for n in nodes if n["mastery"] >= 0.7]
            if high_mastery:
                n = high_mastery[0]
                path_items.append({
                    "step": len(path_items) + 1,
                    "activity": "challenge",
                    "content_type": "challenge",
                    "node_id": n["node_id"],
                    "node_name": n["node_name"],
                    "description": f"挑战提升: {n['node_name']}",
                    "minutes": min(8, remaining),
                    "difficulty": round(min(1.0, n["mastery"] + 0.2), 2),
                })
                remaining -= min(8, remaining)

        return {
            "path": path_items,
            "total_steps": len(path_items),
            "total_minutes": session_minutes - remaining,
            "emotion": emotion,
            "difficulty_factor": diff_factor,
            "emotion_alert": "情感持续恶化，已延长恢复阶段并降低难度" if emotion.get("worsening") else None,
        }

    # ==================== 4. 策略权重查询 ====================

    async def get_strategy_weights(
        self, db: AsyncSession,
        strategy_type: Optional[str] = None,
    ) -> dict:
        """获取当前策略权重"""
        q = select(AgentStrategyWeight)
        if strategy_type:
            q = q.where(AgentStrategyWeight.strategy_type == strategy_type)
        rows = (await db.execute(q)).scalars().all()
        return {
            r.strategy_type: {
                "weights": r.weights,
                "total_episodes": r.total_episodes,
                "avg_reward": round(r.avg_reward, 4),
                "last_updated": r.last_updated_at.isoformat() if r.last_updated_at else None,
            }
            for r in rows
        }

    # ==================== 5. 奖惩历史 ====================

    async def get_reward_history(
        self, db: AsyncSession, user_id: int,
        strategy_type: Optional[str] = None,
        limit: int = 20,
    ) -> list:
        q = select(AgentStrategyReward).where(
            AgentStrategyReward.user_id == user_id
        )
        if strategy_type:
            q = q.where(AgentStrategyReward.strategy_type == strategy_type)
        q = q.order_by(desc(AgentStrategyReward.created_at)).limit(limit)
        rows = (await db.execute(q)).scalars().all()
        return [
            {
                "id": r.id,
                "strategy_type": r.strategy_type,
                "reward": r.reward_signal,
                "components": r.reward_components,
                "action": r.action_taken,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]

    # ==================== 内部方法 ====================

    async def _get_emotion(self, db: AsyncSession, user_id: int) -> dict:
        q = (
            select(StudentEmotionState)
            .where(StudentEmotionState.user_id == user_id)
            .order_by(desc(StudentEmotionState.created_at))
            .limit(3)
        )
        rows = (await db.execute(q)).scalars().all()
        if not rows:
            return {"type": "focus", "intensity": 0.5, "worsening": False}
        latest = rows[0]
        # 情感恶化检测：最近3条记录中负面情感是否在加剧
        worsening = False
        if len(rows) >= 2:
            neg_types = {"frustration", "anxiety"}
            if latest.emotion_type in neg_types:
                prev_neg = sum(1 for r in rows[1:] if r.emotion_type in neg_types)
                if prev_neg >= 1 and latest.intensity > (rows[1].intensity or 0.5):
                    worsening = True
        return {
            "type": latest.emotion_type,
            "intensity": latest.intensity,
            "worsening": worsening,
        }

    async def _get_knowledge_states(
        self, db: AsyncSession, user_id: int,
        subject_id: Optional[int],
    ) -> list:
        q = (
            select(
                StudentKnowledgeState.knowledge_node_id,
                StudentKnowledgeState.mastery,
                StudentKnowledgeState.stability,
                StudentKnowledgeState.practice_count,
                KnowledgeNode.name,
            )
            .join(KnowledgeNode, KnowledgeNode.id == StudentKnowledgeState.knowledge_node_id)
            .where(StudentKnowledgeState.user_id == user_id)
        )
        if subject_id:
            q = q.where(KnowledgeNode.subject_id == subject_id)
        q = q.order_by(StudentKnowledgeState.mastery).limit(20)
        rows = (await db.execute(q)).all()
        return [
            {
                "node_id": r.knowledge_node_id,
                "node_name": r.name,
                "mastery": float(r.mastery or 0),
                "stability": float(r.stability or 0.5),
                "practice_count": r.practice_count or 0,
            }
            for r in rows
        ]

    async def _get_review_due(self, db: AsyncSession, user_id: int) -> list:
        now = datetime.utcnow()
        q = (
            select(
                ReviewSchedule.knowledge_node_id,
                ReviewSchedule.next_review_at,
                KnowledgeNode.name,
                StudentKnowledgeState.mastery,
            )
            .join(KnowledgeNode, KnowledgeNode.id == ReviewSchedule.knowledge_node_id)
            .outerjoin(
                StudentKnowledgeState,
                and_(
                    StudentKnowledgeState.knowledge_node_id == ReviewSchedule.knowledge_node_id,
                    StudentKnowledgeState.user_id == user_id,
                ),
            )
            .where(and_(
                ReviewSchedule.user_id == user_id,
                ReviewSchedule.next_review_at <= now,
            ))
            .order_by(ReviewSchedule.next_review_at)
            .limit(10)
        )
        rows = (await db.execute(q)).all()
        return [
            {
                "node_id": r.knowledge_node_id,
                "node_name": r.name,
                "mastery": float(r.mastery or 0.5),
            }
            for r in rows
        ]

    async def _get_unresolved_misconceptions(
        self, db: AsyncSession, user_id: int,
    ) -> list:
        q = (
            select(
                StudentMisconception.knowledge_node_id,
                StudentMisconception.misconception,
                KnowledgeNode.name,
                StudentKnowledgeState.mastery,
            )
            .join(KnowledgeNode, KnowledgeNode.id == StudentMisconception.knowledge_node_id)
            .outerjoin(
                StudentKnowledgeState,
                and_(
                    StudentKnowledgeState.knowledge_node_id == StudentMisconception.knowledge_node_id,
                    StudentKnowledgeState.user_id == user_id,
                ),
            )
            .where(and_(
                StudentMisconception.user_id == user_id,
                StudentMisconception.resolved == 0,
            ))
            .order_by(desc(StudentMisconception.frequency))
            .limit(5)
        )
        rows = (await db.execute(q)).all()
        return [
            {
                "node_id": r.knowledge_node_id,
                "node_name": r.name,
                "misconception": r.misconception,
                "mastery": float(r.mastery or 0.3),
            }
            for r in rows
        ]

    async def _get_strategy_weights(
        self, db: AsyncSession, strategy_type: str,
    ) -> dict:
        q = select(AgentStrategyWeight).where(
            AgentStrategyWeight.strategy_type == strategy_type
        )
        row = (await db.execute(q)).scalar_one_or_none()
        if row and row.weights:
            return row.weights
        # 默认权重
        defaults = {
            "task_generation": {"learn": 0.25, "review": 0.2, "practice": 0.2, "remediate": 0.15, "challenge": 0.1, "recover": 0.1},
            "difficulty_selection": {"easy": 0.3, "medium": 0.4, "hard": 0.2, "challenge": 0.1},
            "content_type": {"lecture": 0.25, "simulator": 0.25, "grinder": 0.25, "tutor": 0.25},
        }
        return defaults.get(strategy_type, {})

    async def _get_total_episodes(
        self, db: AsyncSession, strategy_type: str,
    ) -> int:
        """获取策略的总训练轮次（用于ε-greedy衰减）"""
        q = select(AgentStrategyWeight.total_episodes).where(
            AgentStrategyWeight.strategy_type == strategy_type
        )
        result = (await db.execute(q)).scalar_one_or_none()
        return result or 0

    async def _update_strategy_weights(
        self, db: AsyncSession, strategy_type: str,
        action_taken: dict, reward: float,
    ):
        """基于奖励信号更新策略权重（简化版策略梯度）"""
        q = select(AgentStrategyWeight).where(
            AgentStrategyWeight.strategy_type == strategy_type
        )
        row = (await db.execute(q)).scalar_one_or_none()
        if not row:
            return

        weights = dict(row.weights or {})
        action_key = action_taken.get("primary_action", "")

        if action_key and action_key in weights:
            # 正奖励→增加该动作权重，负奖励→减少
            delta = LEARNING_RATE * reward
            weights[action_key] = max(0.01, weights[action_key] + delta)

            # 归一化
            total = sum(weights.values())
            if total > 0:
                weights = {k: round(v / total, 4) for k, v in weights.items()}

        # 更新
        new_episodes = (row.total_episodes or 0) + 1
        new_avg = ((row.avg_reward or 0) * (new_episodes - 1) + reward) / new_episodes

        row.weights = weights
        row.total_episodes = new_episodes
        row.avg_reward = round(new_avg, 4)
        row.last_updated_at = datetime.utcnow()

    def _select_content_type(
        self, mastery: float, emo_type: str, weights: dict,
        total_episodes: int = 0, learning_style: dict = None,
    ) -> str:
        """根据掌握度+情感+学习风格选择最佳内容类型（含ε-greedy探索）"""
        # Phase 16: 学习风格→内容类型权重映射
        style_boost = {}
        if learning_style:
            dominant = max(learning_style, key=learning_style.get, default=None)
            if dominant == "visual":
                style_boost = {"simulator": 1.4}
            elif dominant == "auditory":
                style_boost = {"lecture": 1.3}
            elif dominant == "reading":
                style_boost = {"lecture": 1.3}
            elif dominant == "kinesthetic":
                style_boost = {"grinder": 1.4, "challenge": 1.3}
        # ε-greedy: 随episode增加降低探索率
        epsilon = max(EPSILON_MIN, EPSILON_START * math.exp(-total_episodes / EPSILON_DECAY))
        if random.random() < epsilon:
            # 探索：从掌握度范围内的类型中随机选
            valid = [
                ct for ct, cfg in CONTENT_TYPES.items()
                if cfg["min_mastery"] <= mastery <= cfg["max_mastery"]
            ]
            if valid:
                return random.choice(valid)

        scores = {}
        for ct, cfg in CONTENT_TYPES.items():
            if mastery < cfg["min_mastery"] or mastery > cfg["max_mastery"]:
                score = 0.1
            else:
                # 掌握度在范围内，得分高
                range_width = cfg["max_mastery"] - cfg["min_mastery"]
                center = (cfg["min_mastery"] + cfg["max_mastery"]) / 2
                dist = abs(mastery - center) / (range_width / 2) if range_width > 0 else 0
                score = 1.0 - dist * 0.5

            # 情感调整
            if emo_type == "frustration":
                if ct in ("lecture", "review"):
                    score *= 1.5
                elif ct in ("challenge", "grinder"):
                    score *= 0.3
            elif emo_type == "boredom":
                if ct in ("challenge", "simulator"):
                    score *= 1.5
                elif ct in ("lecture", "review"):
                    score *= 0.5
            elif emo_type == "anxiety":
                if ct in ("lecture", "tutor"):
                    score *= 1.3
                elif ct == "challenge":
                    score *= 0.4

            # 策略权重加成
            w = weights.get(ct, 0.25)
            score *= (0.5 + w)

            # Phase 16: 学习风格加成
            if ct in style_boost:
                score *= style_boost[ct]

            scores[ct] = score

        return max(scores, key=scores.get)

    def _task_reason(self, ct: str, mastery: float, emo_type: str) -> str:
        reasons = {
            "lecture": f"掌握度{mastery:.0%}，通过小课堂学习基础概念",
            "simulator": f"掌握度{mastery:.0%}，通过模拟器直观理解",
            "grinder": f"掌握度{mastery:.0%}，通过练习巩固知识",
            "tutor": f"掌握度{mastery:.0%}，通过诊断对话深入理解",
            "review": f"掌握度{mastery:.0%}，复习巩固已学内容",
            "challenge": f"掌握度{mastery:.0%}，挑战更高难度",
        }
        base = reasons.get(ct, f"掌握度{mastery:.0%}")
        if emo_type == "frustration":
            base += "（已降低难度）"
        elif emo_type == "boredom":
            base += "（已提升挑战性）"
        return base

    def _interleave_tasks(self, tasks: list) -> list:
        """穿插不同类型任务，避免连续3个以上相同类型"""
        if len(tasks) <= 2:
            return tasks
        result = [tasks[0]]
        for t in tasks[1:]:
            if len(result) >= 2:
                if (result[-1]["content_type"] == result[-2]["content_type"] == t["content_type"]):
                    # 找一个不同类型的插入
                    for j, other in enumerate(tasks):
                        if other not in result and other["content_type"] != t["content_type"]:
                            result.append(other)
                            break
            result.append(t)
        # 去重保持顺序
        seen = set()
        final = []
        for t in result:
            key = (t.get("node_id"), t["content_type"])
            if key not in seen:
                seen.add(key)
                final.append(t)
        return final
