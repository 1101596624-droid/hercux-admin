"""
Spaced Repetition Service - Phase 4 间隔复习系统
基于 FSRS (Free Spaced Repetition Scheduler) 改进算法，
结合 BKT stability 和学生情感状态，实现最优复习调度。
"""

import math
import random
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.models.models import (
    ReviewSchedule, StudentKnowledgeState,
    KnowledgeNode, StudentEmotionState,
)
from app.services.time_utils import as_utc, utcnow


# FSRS v4 核心参数
FSRS_W = [0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01,
          1.49, 0.14, 0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61]

# 复习内容类型及预估时间
REVIEW_TYPES = {
    "flashcard":        {"minutes": 1, "label": "概念卡片"},
    "mini_quiz":        {"minutes": 3, "label": "迷你测验"},
    "simulator_replay": {"minutes": 5, "label": "模拟器回顾"},
    "explain_to_ai":    {"minutes": 4, "label": "向AI解释"},
}

# 情感 → 复习量调整
EMOTION_REVIEW_MODIFIER = {
    "frustration": 0.5,   # 减半复习量
    "anxiety": 0.7,
    "boredom": 1.3,       # 增加复习量
    "focus": 1.0,
    "excitement": 1.2,
}


class FSRSEngine:
    """FSRS v4 核心计算引擎"""

    def __init__(self, target_retention: float = 0.9):
        self.target_retention = target_retention

    def retrievability(self, stability: float, elapsed_days: float) -> float:
        """记忆保持率 R = (1 + t/9S)^(-1)"""
        if stability <= 0:
            return 0.0
        return pow(1 + elapsed_days / (9 * stability), -1)

    def optimal_interval(self, stability: float) -> float:
        """达到目标保持率的最优间隔（天）"""
        if stability <= 0:
            return 1.0
        return max(1.0, 9 * stability * (1 / self.target_retention - 1))

    def update(
        self,
        stability: float,
        difficulty: float,
        rating: int,
        elapsed_days: float,
    ) -> Dict[str, float]:
        """
        FSRS 更新。rating: 1=Again, 2=Hard, 3=Good, 4=Easy
        返回 {stability, difficulty, interval_days}
        """
        w = FSRS_W
        r = self.retrievability(stability, elapsed_days)

        # 更新稳定性
        if rating == 1:  # Again — 遗忘
            new_stab = w[11] * pow(difficulty, -w[12]) * \
                (pow(stability + 1, w[13]) - 1) * \
                math.exp((1 - r) * w[14])
            new_stab = max(0.1, new_stab)
        else:
            hard_penalty = w[15] if rating == 2 else 1.0
            easy_bonus = w[16] if rating == 4 else 1.0
            new_stab = stability * (
                1 + math.exp(w[8])
                * (11 - difficulty)
                * pow(stability, -w[9])
                * (math.exp((1 - r) * w[10]) - 1)
                * hard_penalty
                * easy_bonus
            )
            new_stab = max(0.1, new_stab)

        # 更新难度
        new_diff = difficulty - w[6] * (rating - 3)
        new_diff = max(1.0, min(10.0, new_diff))

        interval = self.optimal_interval(new_stab)

        return {
            "stability": round(new_stab, 4),
            "difficulty": round(new_diff, 4),
            "interval_days": round(interval, 2),
        }

    def init_params(self, rating: int) -> Dict[str, float]:
        """首次复习的初始参数"""
        w = FSRS_W
        stability = w[rating - 1]  # w[0]~w[3] 对应 rating 1~4
        difficulty = w[4] - math.exp(w[5] * (rating - 1)) + 1
        difficulty = max(1.0, min(10.0, difficulty))
        interval = self.optimal_interval(stability)
        return {
            "stability": round(stability, 4),
            "difficulty": round(difficulty, 4),
            "interval_days": round(interval, 2),
        }


_engine = FSRSEngine()


class SpacedRepetitionService:

    @staticmethod
    async def get_due_reviews(
        db: AsyncSession,
        user_id: int,
        max_count: int = 20,
        max_minutes: int = 30,
        subject_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """获取到期的复习项"""
        now = utcnow()

        query = (
            select(ReviewSchedule, KnowledgeNode)
            .join(KnowledgeNode, ReviewSchedule.knowledge_node_id == KnowledgeNode.id)
            .where(
                and_(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.next_review_at <= now,
                )
            )
        )
        if subject_id:
            query = query.where(KnowledgeNode.subject_id == subject_id)

        query = query.order_by(ReviewSchedule.next_review_at.asc()).limit(max_count * 2)
        result = await db.execute(query)
        rows = result.all()

        # 获取情感状态调整复习量
        emo_result = await db.execute(
            select(StudentEmotionState)
            .where(StudentEmotionState.user_id == user_id)
            .order_by(desc(StudentEmotionState.created_at))
            .limit(1)
        )
        emo = emo_result.scalar_one_or_none()
        emotion_type = emo.emotion_type if emo else "focus"
        modifier = EMOTION_REVIEW_MODIFIER.get(emotion_type, 1.0)
        adjusted_max = max(3, int(max_count * modifier))

        items = []
        total_minutes = 0
        for row in rows:
            if len(items) >= adjusted_max or total_minutes >= max_minutes:
                break

            sched = row.ReviewSchedule
            node = row.KnowledgeNode

            # 选择复习类型
            review_type = SpacedRepetitionService._pick_review_type(
                sched, node
            )
            duration = REVIEW_TYPES[review_type]["minutes"]

            if total_minutes + duration > max_minutes:
                break

            last_review_at = as_utc(sched.last_review_at)
            elapsed = (now - last_review_at).total_seconds() / 86400.0 if last_review_at else 1.0
            r = _engine.retrievability(sched.fsrs_stability, elapsed)
            next_review_at = as_utc(sched.next_review_at) or now

            items.append({
                "review_schedule_id": sched.id,
                "knowledge_node_id": node.id,
                "node_code": node.code,
                "node_name": node.name,
                "review_type": review_type,
                "review_type_label": REVIEW_TYPES[review_type]["label"],
                "estimated_minutes": duration,
                "retrievability": round(r, 3),
                "review_count": sched.review_count,
                "overdue_hours": round((now - next_review_at).total_seconds() / 3600, 1),
            })
            total_minutes += duration

        return {
            "user_id": user_id,
            "emotion_snapshot": emotion_type,
            "due_count": len(rows),
            "selected_count": len(items),
            "total_minutes": total_minutes,
            "items": items,
        }

    @staticmethod
    async def record_review(
        db: AsyncSession,
        user_id: int,
        knowledge_node_id: int,
        rating: int,
        review_type: str = "mini_quiz",
    ) -> Dict[str, Any]:
        """记录复习结果并更新 FSRS 调度"""
        now = utcnow()

        # 获取或创建 schedule
        result = await db.execute(
            select(ReviewSchedule).where(
                and_(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.knowledge_node_id == knowledge_node_id,
                )
            )
        )
        sched = result.scalar_one_or_none()

        if sched is None:
            # 首次复习 — 初始化 FSRS 参数
            params = _engine.init_params(rating)
            next_at = now + timedelta(days=params["interval_days"])
            sched = ReviewSchedule(
                user_id=user_id,
                knowledge_node_id=knowledge_node_id,
                fsrs_stability=params["stability"],
                fsrs_difficulty=params["difficulty"],
                interval_days=params["interval_days"],
                next_review_at=next_at,
                last_review_at=now,
                last_review_type=review_type,
                last_rating=rating,
                review_count=1,
            )
            db.add(sched)
        else:
            # 后续复习 — FSRS 更新
            last_review_at = as_utc(sched.last_review_at)
            elapsed = (now - last_review_at).total_seconds() / 86400.0 if last_review_at else 1.0
            params = _engine.update(
                stability=sched.fsrs_stability,
                difficulty=sched.fsrs_difficulty,
                rating=rating,
                elapsed_days=elapsed,
            )
            sched.fsrs_stability = params["stability"]
            sched.fsrs_difficulty = params["difficulty"]
            sched.interval_days = params["interval_days"]
            sched.next_review_at = now + timedelta(days=params["interval_days"])
            sched.last_review_at = now
            sched.last_review_type = review_type
            sched.last_rating = rating
            sched.review_count += 1

        await db.flush()

        # 同步更新 BKT stability（保持一致性）
        state_result = await db.execute(
            select(StudentKnowledgeState).where(
                and_(
                    StudentKnowledgeState.user_id == user_id,
                    StudentKnowledgeState.knowledge_node_id == knowledge_node_id,
                )
            )
        )
        state = state_result.scalar_one_or_none()
        if state:
            state.stability = max(state.stability, sched.fsrs_stability)
            state.last_practice_at = now

        return {
            "review_schedule_id": sched.id,
            "knowledge_node_id": knowledge_node_id,
            "rating": rating,
            "new_stability": sched.fsrs_stability,
            "new_difficulty": sched.fsrs_difficulty,
            "interval_days": sched.interval_days,
            "next_review_at": sched.next_review_at.isoformat(),
            "review_count": sched.review_count,
        }

    @staticmethod
    async def ensure_schedules(
        db: AsyncSession,
        user_id: int,
        subject_id: Optional[int] = None,
    ) -> int:
        """
        为已有 knowledge_state 但无 review_schedule 的节点创建初始调度。
        返回新创建的调度数量。
        """
        now = utcnow()

        # 找出有 state 但无 schedule 的节点
        query = (
            select(StudentKnowledgeState, KnowledgeNode)
            .join(KnowledgeNode, StudentKnowledgeState.knowledge_node_id == KnowledgeNode.id)
            .where(StudentKnowledgeState.user_id == user_id)
        )
        if subject_id:
            query = query.where(KnowledgeNode.subject_id == subject_id)

        states_result = await db.execute(query)
        states = states_result.all()

        existing_result = await db.execute(
            select(ReviewSchedule.knowledge_node_id)
            .where(ReviewSchedule.user_id == user_id)
        )
        existing_ids = {r[0] for r in existing_result.all()}

        created = 0
        for row in states:
            state = row.StudentKnowledgeState
            node = row.KnowledgeNode
            if state.knowledge_node_id in existing_ids:
                continue

            # 用 BKT stability 推算初始 FSRS 间隔
            stab = max(state.stability, 0.5)
            interval = _engine.optimal_interval(stab)
            last_at = as_utc(state.last_practice_at) or now
            next_at = last_at + timedelta(days=interval)

            sched = ReviewSchedule(
                user_id=user_id,
                knowledge_node_id=state.knowledge_node_id,
                fsrs_stability=stab,
                fsrs_difficulty=5.0,
                interval_days=interval,
                next_review_at=next_at,
                last_review_at=last_at,
                review_count=0,
            )
            db.add(sched)
            created += 1

        if created:
            await db.flush()
        return created

    @staticmethod
    async def get_review_stats(
        db: AsyncSession,
        user_id: int,
    ) -> Dict[str, Any]:
        """获取复习统计概览"""
        now = utcnow()

        # 总调度数
        total_result = await db.execute(
            select(func.count()).where(ReviewSchedule.user_id == user_id)
        )
        total = total_result.scalar() or 0

        # 到期数
        due_result = await db.execute(
            select(func.count()).where(
                and_(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.next_review_at <= now,
                )
            )
        )
        due = due_result.scalar() or 0

        # 今日已复习数
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        reviewed_result = await db.execute(
            select(func.count()).where(
                and_(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.last_review_at >= today_start,
                    ReviewSchedule.review_count > 0,
                )
            )
        )
        reviewed_today = reviewed_result.scalar() or 0

        # 平均保持率
        all_scheds = await db.execute(
            select(ReviewSchedule).where(
                and_(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.review_count > 0,
                )
            )
        )
        scheds = all_scheds.scalars().all()
        if scheds:
            retentions = []
            for s in scheds:
                last_review_at = as_utc(s.last_review_at)
                elapsed = (now - last_review_at).total_seconds() / 86400.0 if last_review_at else 0
                retentions.append(_engine.retrievability(s.fsrs_stability, elapsed))
            avg_retention = sum(retentions) / len(retentions)
        else:
            avg_retention = 0.0

        return {
            "total_scheduled": total,
            "due_now": due,
            "reviewed_today": reviewed_today,
            "avg_retention": round(avg_retention, 3),
        }

    @staticmethod
    def _pick_review_type(
        sched: ReviewSchedule,
        node: KnowledgeNode,
    ) -> str:
        """选择复习内容类型，避免连续相同"""
        types = list(REVIEW_TYPES.keys())
        weights = [1.0] * len(types)

        # 避免连续相同类型
        if sched.last_review_type:
            for i, t in enumerate(types):
                if t == sched.last_review_type:
                    weights[i] *= 0.2

        # 高复习次数 → 偏向快速类型
        if sched.review_count > 5:
            for i, t in enumerate(types):
                if t == "flashcard":
                    weights[i] *= 2.0

        # 加权随机
        total = sum(weights)
        r = random.random() * total
        cumulative = 0.0
        for i, w in enumerate(weights):
            cumulative += w
            if r <= cumulative:
                return types[i]
        return types[0]
