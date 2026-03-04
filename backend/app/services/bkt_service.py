"""
BKT (Bayesian Knowledge Tracing) Service
增强版贝叶斯知识追踪：含遗忘曲线、响应时间修正、难度加权
"""

import math
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_


from app.models.models import (
    KnowledgeNode, StudentKnowledgeState,
    StudentEvent, StudentMisconception
)
from app.services.emotion_service import EmotionService
from app.services.time_utils import as_utc, utcnow


class BKTParams:
    """BKT 模型参数"""
    P_INIT = 0.1       # 初始掌握概率
    P_TRANSIT = 0.15    # 学习转移概率
    P_SLIP = 0.1        # 失误概率（会但答错）
    P_GUESS = 0.25      # 猜测概率（不会但答对）


class BKTService:

    @staticmethod
    async def update_mastery(
        db: AsyncSession,
        user_id: int,
        knowledge_node_id: int,
        is_correct: bool,
        response_time_ms: Optional[int] = None,
        difficulty: float = 0.5
    ) -> StudentKnowledgeState:
        """
        增强版 BKT 更新：遗忘衰减 + 贝叶斯后验 + 学习转移 + 难度加权 + 响应时间修正
        """
        # 1. 获取/创建 state
        result = await db.execute(
            select(StudentKnowledgeState).where(
                and_(
                    StudentKnowledgeState.user_id == user_id,
                    StudentKnowledgeState.knowledge_node_id == knowledge_node_id
                )
            )
        )
        state = result.scalar_one_or_none()

        now = utcnow()

        if not state:
            state = StudentKnowledgeState(
                user_id=user_id,
                knowledge_node_id=knowledge_node_id,
                mastery=BKTParams.P_INIT,
                stability=1.0,
                practice_count=0,
                correct_count=0,
                streak=0,
                last_practice_at=now,
            )
            db.add(state)
            await db.flush()

        mastery = state.mastery
        stab = state.stability

        # 2. 遗忘衰减
        last_practice_at = as_utc(state.last_practice_at)
        if last_practice_at:
            elapsed = (now - last_practice_at).total_seconds()
            elapsed_hours = elapsed / 3600.0
            if elapsed_hours > 0.1:  # 6 分钟以上才衰减
                retention = mastery * math.exp(-elapsed_hours / max(stab, 1.0))
                mastery = retention

        # 3. 贝叶斯后验更新
        p_slip = BKTParams.P_SLIP
        p_guess = BKTParams.P_GUESS

        if is_correct:
            denom = mastery * (1 - p_slip) + (1 - mastery) * p_guess
            if denom > 0:
                posterior = mastery * (1 - p_slip) / denom
            else:
                posterior = mastery
        else:
            denom = mastery * p_slip + (1 - mastery) * (1 - p_guess)
            if denom > 0:
                posterior = mastery * p_slip / denom
            else:
                posterior = mastery

        # 4. 学习转移
        posterior = posterior + (1 - posterior) * BKTParams.P_TRANSIT

        # 5. 难度加权
        if is_correct:
            posterior += difficulty * 0.05

        # 6. 响应时间修正
        if response_time_ms is not None:
            if response_time_ms < 2000:
                posterior *= 0.85   # 太快 → 可能猜测
            elif response_time_ms > 60000:
                posterior *= 0.92   # 太慢 → 不熟练

        # 7. 稳定性更新
        if last_practice_at:
            elapsed_hours = (now - last_practice_at).total_seconds() / 3600.0
        else:
            elapsed_hours = 0

        if is_correct:
            stab *= (1.2 + 0.1 * min(math.log(1 + elapsed_hours / 24.0), 2.0))
        else:
            stab *= 0.8

        # Clamp values
        posterior = max(0.01, min(0.99, posterior))
        stab = max(0.1, min(100.0, stab))

        # 8. 更新 state
        state.mastery = posterior
        state.stability = stab
        state.last_practice_at = now
        state.practice_count += 1
        if is_correct:
            state.correct_count += 1
            state.streak += 1
        else:
            state.streak = 0
        state.updated_at = now

        await db.flush()
        return state

    @staticmethod
    async def record_event(
        db: AsyncSession,
        user_id: int,
        knowledge_node_id: int,
        event_type: str,
        is_correct: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        event_data: Optional[Dict[str, Any]] = None,
    ) -> StudentEvent:
        """记录学习事件，answer 类型触发 BKT 更新"""
        event = StudentEvent(
            user_id=user_id,
            knowledge_node_id=knowledge_node_id,
            event_type=event_type,
            is_correct=is_correct,
            response_time_ms=response_time_ms,
            event_data=event_data or {},
        )
        db.add(event)
        await db.flush()

        # answer 事件触发 BKT 更新
        if event_type == "answer" and is_correct is not None:
            # 获取节点难度
            node_result = await db.execute(
                select(KnowledgeNode).where(KnowledgeNode.id == knowledge_node_id)
            )
            node = node_result.scalar_one_or_none()
            difficulty = node.difficulty if node else 0.5

            await BKTService.update_mastery(
                db, user_id, knowledge_node_id,
                is_correct=bool(is_correct),
                response_time_ms=response_time_ms,
                difficulty=difficulty,
            )

            # 错误答题 + 有 misconception → 记录
            if is_correct == 0 and event_data and event_data.get("misconception"):
                await BKTService._record_misconception(
                    db, user_id, knowledge_node_id,
                    event_data["misconception"]
                )

            # Phase 2: 情感推断
            try:
                await EmotionService.record_emotion(
                    db, user_id, knowledge_node_id,
                    trigger_event_id=event.id,
                )
            except Exception:
                pass  # 情感推断失败不影响主流程

        return event

    @staticmethod
    async def _record_misconception(
        db: AsyncSession,
        user_id: int,
        knowledge_node_id: int,
        misconception_text: str,
    ):
        """插入或更新错误概念"""
        result = await db.execute(
            select(StudentMisconception).where(
                and_(
                    StudentMisconception.user_id == user_id,
                    StudentMisconception.knowledge_node_id == knowledge_node_id,
                    StudentMisconception.misconception == misconception_text,
                )
            )
        )
        existing = result.scalar_one_or_none()
        now = utcnow()

        if existing:
            existing.frequency += 1
            existing.last_seen_at = now
            existing.resolved = 0
        else:
            db.add(StudentMisconception(
                user_id=user_id,
                knowledge_node_id=knowledge_node_id,
                misconception=misconception_text,
                frequency=1,
                last_seen_at=now,
            ))
        await db.flush()

    @staticmethod
    async def get_user_knowledge_summary(
        db: AsyncSession,
        user_id: int,
        subject_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取用户知识状态汇总"""
        query = (
            select(
                StudentKnowledgeState,
                KnowledgeNode.name.label("node_name"),
                KnowledgeNode.code.label("node_code"),
            )
            .join(KnowledgeNode, StudentKnowledgeState.knowledge_node_id == KnowledgeNode.id)
            .where(StudentKnowledgeState.user_id == user_id)
        )
        if subject_id:
            query = query.where(KnowledgeNode.subject_id == subject_id)

        query = query.order_by(KnowledgeNode.code)
        result = await db.execute(query)
        rows = result.all()

        return [
            {
                "id": row.StudentKnowledgeState.id,
                "user_id": user_id,
                "knowledge_node_id": row.StudentKnowledgeState.knowledge_node_id,
                "mastery": row.StudentKnowledgeState.mastery,
                "stability": row.StudentKnowledgeState.stability,
                "last_practice_at": row.StudentKnowledgeState.last_practice_at,
                "practice_count": row.StudentKnowledgeState.practice_count,
                "correct_count": row.StudentKnowledgeState.correct_count,
                "streak": row.StudentKnowledgeState.streak,
                "node_name": row.node_name,
                "node_code": row.node_code,
                "created_at": row.StudentKnowledgeState.created_at,
                "updated_at": row.StudentKnowledgeState.updated_at,
            }
            for row in rows
        ]

    @staticmethod
    async def get_weak_nodes(
        db: AsyncSession,
        user_id: int,
        threshold: float = 0.4,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """获取薄弱知识点（mastery < threshold）"""
        result = await db.execute(
            select(
                StudentKnowledgeState,
                KnowledgeNode.name.label("node_name"),
                KnowledgeNode.code.label("node_code"),
            )
            .join(KnowledgeNode, StudentKnowledgeState.knowledge_node_id == KnowledgeNode.id)
            .where(
                and_(
                    StudentKnowledgeState.user_id == user_id,
                    StudentKnowledgeState.mastery < threshold,
                )
            )
            .order_by(StudentKnowledgeState.mastery.asc())
            .limit(limit)
        )
        rows = result.all()

        return [
            {
                "knowledge_node_id": row.StudentKnowledgeState.knowledge_node_id,
                "mastery": row.StudentKnowledgeState.mastery,
                "stability": row.StudentKnowledgeState.stability,
                "practice_count": row.StudentKnowledgeState.practice_count,
                "streak": row.StudentKnowledgeState.streak,
                "node_name": row.node_name,
                "node_code": row.node_code,
            }
            for row in rows
        ]
