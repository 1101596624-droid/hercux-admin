"""
Emotion Service - Phase 2 情感感知系统
基于学生行为数据推断情感状态（挫败、焦虑、无聊、专注、兴奋）
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.models.models import (
    StudentEvent, StudentKnowledgeState,
    StudentEmotionState, KnowledgeNode
)


class EmotionType:
    FRUSTRATION = "frustration"
    ANXIETY = "anxiety"
    BOREDOM = "boredom"
    FOCUS = "focus"
    EXCITEMENT = "excitement"


class EmotionService:

    @staticmethod
    async def infer_emotion(
        db: AsyncSession,
        user_id: int,
        recent_events: List[StudentEvent],
        knowledge_state: Optional[StudentKnowledgeState] = None,
    ) -> Dict[str, Any]:
        """
        基于最近行为事件推断情感状态
        返回: {"emotion_type": str, "intensity": float, "confidence": float, "trigger_type": str}
        """
        if not recent_events:
            return {"emotion_type": EmotionType.FOCUS, "intensity": 0.3, "confidence": 0.2, "trigger_type": "no_data"}

        # 提取行为特征
        answers = [e for e in recent_events if e.event_type == "answer"]
        recent_n = answers[-5:] if len(answers) >= 5 else answers

        if not recent_n:
            return {"emotion_type": EmotionType.FOCUS, "intensity": 0.3, "confidence": 0.3, "trigger_type": "no_answers"}

        correct_count = sum(1 for e in recent_n if e.is_correct == 1)
        wrong_count = len(recent_n) - correct_count
        accuracy = correct_count / len(recent_n) if recent_n else 0

        # 连续错误计数
        consecutive_wrong = 0
        for e in reversed(answers):
            if e.is_correct == 0:
                consecutive_wrong += 1
            else:
                break

        # 连续正确计数
        consecutive_correct = 0
        for e in reversed(answers):
            if e.is_correct == 1:
                consecutive_correct += 1
            else:
                break

        # 平均响应时间
        response_times = [e.response_time_ms for e in recent_n if e.response_time_ms]
        avg_rt = sum(response_times) / len(response_times) if response_times else 5000
        latest_rt = response_times[-1] if response_times else 5000

        # hint/skip 频率
        hints = sum(1 for e in recent_events if e.event_type == "hint")
        skips = sum(1 for e in recent_events if e.event_type == "skip")

        # mastery 信息
        mastery = knowledge_state.mastery if knowledge_state else 0.5
        streak = knowledge_state.streak if knowledge_state else 0

        # === 情感推断规则 ===

        # 1. 挫败感: 连续3+错误 且 mastery下降
        if consecutive_wrong >= 3 and mastery < 0.4:
            intensity = min(0.3 + consecutive_wrong * 0.15, 1.0)
            return {
                "emotion_type": EmotionType.FRUSTRATION,
                "intensity": intensity,
                "confidence": 0.8,
                "trigger_type": "streak_fail",
            }

        # 2. 焦虑: 响应时间突增>2倍 且 答错
        if latest_rt > avg_rt * 2 and recent_n[-1].is_correct == 0:
            intensity = min(0.4 + (latest_rt / avg_rt - 2) * 0.1, 0.9)
            return {
                "emotion_type": EmotionType.ANXIETY,
                "intensity": intensity,
                "confidence": 0.6,
                "trigger_type": "slow_wrong",
            }

        # 3. 无聊: 响应时间<2s 且 连续正确 且 mastery>0.8
        if avg_rt < 2000 and consecutive_correct >= 3 and mastery > 0.8:
            return {
                "emotion_type": EmotionType.BOREDOM,
                "intensity": 0.5 + consecutive_correct * 0.05,
                "confidence": 0.7,
                "trigger_type": "fast_correct",
            }

        # 4. 兴奋: streak>5 且 mastery快速上升
        if streak > 5 and accuracy > 0.8:
            return {
                "emotion_type": EmotionType.EXCITEMENT,
                "intensity": min(0.5 + streak * 0.05, 1.0),
                "confidence": 0.7,
                "trigger_type": "high_streak",
            }

        # 5. 默认: 专注
        focus_intensity = 0.3 + accuracy * 0.4
        return {
            "emotion_type": EmotionType.FOCUS,
            "intensity": focus_intensity,
            "confidence": 0.5,
            "trigger_type": "normal_pace",
        }

    @staticmethod
    async def record_emotion(
        db: AsyncSession,
        user_id: int,
        knowledge_node_id: int,
        trigger_event_id: Optional[int] = None,
    ) -> Optional[StudentEmotionState]:
        """
        分析最近事件并记录情感状态
        """
        # 获取最近20条事件
        result = await db.execute(
            select(StudentEvent)
            .where(
                and_(
                    StudentEvent.user_id == user_id,
                    StudentEvent.knowledge_node_id == knowledge_node_id,
                )
            )
            .order_by(desc(StudentEvent.created_at))
            .limit(20)
        )
        recent_events = list(result.scalars().all())
        recent_events.reverse()  # 按时间正序

        # 获取知识状态
        state_result = await db.execute(
            select(StudentKnowledgeState).where(
                and_(
                    StudentKnowledgeState.user_id == user_id,
                    StudentKnowledgeState.knowledge_node_id == knowledge_node_id,
                )
            )
        )
        knowledge_state = state_result.scalar_one_or_none()

        # 推断情感
        emotion_data = await EmotionService.infer_emotion(
            db, user_id, recent_events, knowledge_state
        )

        # 写入数据库
        emotion_record = StudentEmotionState(
            user_id=user_id,
            emotion_type=emotion_data["emotion_type"],
            intensity=emotion_data["intensity"],
            confidence=emotion_data["confidence"],
            trigger_event_id=trigger_event_id,
            trigger_type=emotion_data["trigger_type"],
            context={
                "knowledge_node_id": knowledge_node_id,
                "recent_event_count": len(recent_events),
            },
        )
        db.add(emotion_record)
        await db.flush()
        return emotion_record

    @staticmethod
    async def get_user_emotion_history(
        db: AsyncSession,
        user_id: int,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """获取用户情感历史"""
        result = await db.execute(
            select(StudentEmotionState)
            .where(StudentEmotionState.user_id == user_id)
            .order_by(desc(StudentEmotionState.created_at))
            .limit(limit)
        )
        records = result.scalars().all()
        return [
            {
                "id": r.id,
                "emotion_type": r.emotion_type,
                "intensity": r.intensity,
                "confidence": r.confidence,
                "trigger_type": r.trigger_type,
                "context": r.context,
                "created_at": r.created_at,
            }
            for r in records
        ]

    @staticmethod
    async def get_current_emotion(
        db: AsyncSession,
        user_id: int,
    ) -> Optional[Dict[str, Any]]:
        """获取用户当前情感状态（最新一条）"""
        result = await db.execute(
            select(StudentEmotionState)
            .where(StudentEmotionState.user_id == user_id)
            .order_by(desc(StudentEmotionState.created_at))
            .limit(1)
        )
        r = result.scalar_one_or_none()
        if not r:
            return None
        return {
            "id": r.id,
            "emotion_type": r.emotion_type,
            "intensity": r.intensity,
            "confidence": r.confidence,
            "trigger_type": r.trigger_type,
            "context": r.context,
            "created_at": r.created_at,
        }
