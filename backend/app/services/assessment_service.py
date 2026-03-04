"""
Assessment Service - Phase 7 智能评估与自适应反馈
基于 BKT 掌握度 + 记忆稳定性 + 情感状态 实时评估，生成个性化反馈
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.models.models import (
    StudentAssessment, StudentKnowledgeState,
    StudentEmotionState, StudentEvent, StudentMisconception,
    KnowledgeNode, ReviewSchedule,
)
from app.services.emotion_service import EmotionService


class AssessmentService:

    @staticmethod
    async def evaluate_student(
        db: AsyncSession,
        user_id: int,
        knowledge_node_id: Optional[int] = None,
        assessment_type: str = "auto",
    ) -> Dict[str, Any]:
        """
        智能评估：综合 BKT + 稳定性 + 情感
        """
        # 1. 收集知识状态
        if knowledge_node_id:
            ks_result = await db.execute(
                select(StudentKnowledgeState).where(
                    and_(
                        StudentKnowledgeState.user_id == user_id,
                        StudentKnowledgeState.knowledge_node_id
                            == knowledge_node_id,
                    )
                )
            )
            states = [ks_result.scalar_one_or_none()]
            states = [s for s in states if s]
        else:
            ks_result = await db.execute(
                select(StudentKnowledgeState).where(
                    StudentKnowledgeState.user_id == user_id
                )
            )
            states = list(ks_result.scalars().all())

        # 计算综合掌握度和稳定性
        if states:
            avg_mastery = sum(s.mastery for s in states) / len(states)
            avg_stability = sum(s.stability for s in states) / len(states)
        else:
            avg_mastery = 0.0
            avg_stability = 0.5

        # 2. 情感状态分析
        emotion = await EmotionService.get_current_emotion(db, user_id)
        emotion_type = emotion["emotion_type"] if emotion else "focus"
        emotion_intensity = emotion["intensity"] if emotion else 0.3

        frustration = 0.0
        anxiety = 0.0
        focus = 0.5
        if emotion_type == "frustration":
            frustration = emotion_intensity
        elif emotion_type == "anxiety":
            anxiety = emotion_intensity
        elif emotion_type == "focus":
            focus = emotion_intensity
        elif emotion_type == "boredom":
            focus = max(0.0, 0.5 - emotion_intensity * 0.5)

        # 3. 未解决误解数量
        misc_result = await db.execute(
            select(func.count()).select_from(StudentMisconception).where(
                and_(
                    StudentMisconception.user_id == user_id,
                    StudentMisconception.resolved == 0,
                )
            )
        )
        unresolved_misconceptions = misc_result.scalar() or 0

        # 4. 到期复习数量
        due_result = await db.execute(
            select(func.count()).select_from(ReviewSchedule).where(
                and_(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.next_review_at <= func.now(),
                )
            )
        )
        due_reviews = due_result.scalar() or 0

        # 5. 最近练习频率
        cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)
        event_result = await db.execute(
            select(func.count()).select_from(StudentEvent).where(
                and_(
                    StudentEvent.user_id == user_id,
                    StudentEvent.created_at >= cutoff_24h,
                )
            )
        )
        recent_events = event_result.scalar() or 0

        # 6. 生成反馈
        feedback, strategies = AssessmentService._generate_feedback(
            mastery=avg_mastery,
            stability=avg_stability,
            frustration=frustration,
            anxiety=anxiety,
            focus=focus,
            unresolved_misconceptions=unresolved_misconceptions,
            due_reviews=due_reviews,
            recent_events=recent_events,
        )

        # 7. 持久化评估记录
        assessment = StudentAssessment(
            user_id=user_id,
            knowledge_node_id=knowledge_node_id,
            mastery=round(avg_mastery, 4),
            stability=round(avg_stability, 4),
            frustration_level=round(frustration, 3),
            anxiety_level=round(anxiety, 3),
            focus_level=round(focus, 3),
            assessment_type=assessment_type,
            feedback=feedback,
            strategy_suggestions=strategies,
        )
        db.add(assessment)
        await db.flush()

        return {
            "assessment_id": assessment.id,
            "mastery": round(avg_mastery, 4),
            "stability": round(avg_stability, 4),
            "frustration_level": round(frustration, 3),
            "anxiety_level": round(anxiety, 3),
            "focus_level": round(focus, 3),
            "emotion": emotion_type,
            "unresolved_misconceptions": unresolved_misconceptions,
            "due_reviews": due_reviews,
            "recent_events_24h": recent_events,
            "feedback": feedback,
            "strategies": strategies,
        }

    @staticmethod
    def _generate_feedback(
        mastery: float,
        stability: float,
        frustration: float,
        anxiety: float,
        focus: float,
        unresolved_misconceptions: int,
        due_reviews: int,
        recent_events: int,
    ) -> tuple:
        """基于评估维度生成反馈文本和策略建议"""
        feedback_parts = []
        strategies = []

        # === 掌握度反馈 ===
        if mastery < 0.3:
            feedback_parts.append("你目前处于学习初期，基础还需要加强。")
            strategies.append({
                "type": "mastery_low",
                "action": "review_basics",
                "message": "建议从基础概念开始，多看小课堂讲解，不要急于做难题。",
                "priority": 1,
            })
        elif mastery < 0.6:
            feedback_parts.append("你已经有了一定基础，但还需要更多练习来巩固。")
            strategies.append({
                "type": "mastery_medium",
                "action": "practice_more",
                "message": "建议多做做题家练习，重点攻克薄弱知识点。",
                "priority": 2,
            })
        elif mastery < 0.85:
            feedback_parts.append("掌握得不错！继续保持，向精通迈进。")
            strategies.append({
                "type": "mastery_good",
                "action": "challenge",
                "message": "可以尝试更高难度的题目，挑战自己的极限。",
                "priority": 3,
            })
        else:
            feedback_parts.append("你已经很好地掌握了这些知识！")
            strategies.append({
                "type": "mastery_high",
                "action": "extend",
                "message": "建议探索相关的进阶内容或跨学科知识。",
                "priority": 4,
            })

        # === 稳定性反馈 ===
        if stability < 0.4:
            feedback_parts.append("记忆稳定性偏低，容易遗忘。")
            strategies.append({
                "type": "stability_low",
                "action": "spaced_review",
                "message": "建议按照复习计划定期复习，利用间隔重复巩固记忆。",
                "priority": 1,
            })

        # === 情感反馈 ===
        if frustration > 0.5:
            feedback_parts.append("我注意到你可能有些受挫，这很正常。")
            strategies.append({
                "type": "emotion_frustration",
                "action": "reduce_difficulty",
                "message": "先做一些你擅长的题目找回信心，然后再逐步提高难度。休息一下也是好的。",
                "priority": 1,
            })
        elif anxiety > 0.5:
            feedback_parts.append("别紧张，学习是一个循序渐进的过程。")
            strategies.append({
                "type": "emotion_anxiety",
                "action": "slow_pace",
                "message": "放慢节奏，一次只专注一个知识点。深呼吸，你做得比你想象的好。",
                "priority": 1,
            })
        elif focus < 0.3:
            feedback_parts.append("注意力似乎有些分散。")
            strategies.append({
                "type": "emotion_distracted",
                "action": "engage",
                "message": "试试切换到模拟器互动学习，或者做一些有趣的挑战题。",
                "priority": 2,
            })

        # === 误解反馈 ===
        if unresolved_misconceptions > 0:
            feedback_parts.append(f"你有 {unresolved_misconceptions} 个知识误区需要纠正。")
            strategies.append({
                "type": "misconception",
                "action": "targeted_practice",
                "message": "建议通过诊断式Tutor对话来理清这些误区。",
                "priority": 1,
            })

        # === 复习提醒 ===
        if due_reviews > 0:
            feedback_parts.append(f"有 {due_reviews} 个知识点到了复习时间。")
            strategies.append({
                "type": "review_due",
                "action": "review_now",
                "message": "趁记忆还在，现在复习效果最好。",
                "priority": 2,
            })

        # === 学习频率 ===
        if recent_events == 0:
            strategies.append({
                "type": "inactive",
                "action": "start_session",
                "message": "今天还没有学习记录，开始一个短时学习吧，哪怕10分钟也有帮助。",
                "priority": 3,
            })

        feedback = " ".join(feedback_parts) if feedback_parts else "继续保持良好的学习状态！"
        strategies.sort(key=lambda s: s["priority"])
        return feedback, strategies

    @staticmethod
    async def get_adaptive_feedback(
        db: AsyncSession,
        user_id: int,
        knowledge_node_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        获取自适应反馈：基于最新评估 + 学习趋势
        """
        # 先执行评估
        assessment = await AssessmentService.evaluate_student(
            db, user_id, knowledge_node_id, assessment_type="feedback"
        )

        # 获取历史评估趋势（最近5次）
        hist_result = await db.execute(
            select(StudentAssessment).where(
                StudentAssessment.user_id == user_id
            ).order_by(desc(StudentAssessment.created_at)).limit(6)
        )
        history = list(hist_result.scalars().all())

        # 计算趋势
        trend = "stable"
        if len(history) >= 3:
            recent_mastery = [h.mastery for h in history[:3] if h.mastery is not None]
            older_mastery = [h.mastery for h in history[3:] if h.mastery is not None]
            if recent_mastery and older_mastery:
                recent_avg = sum(recent_mastery) / len(recent_mastery)
                older_avg = sum(older_mastery) / len(older_mastery)
                if recent_avg > older_avg + 0.05:
                    trend = "improving"
                elif recent_avg < older_avg - 0.05:
                    trend = "declining"

        # 趋势反馈
        trend_feedback = ""
        if trend == "improving":
            trend_feedback = "你的学习曲线在上升，继续保持这个势头！"
        elif trend == "declining":
            trend_feedback = "最近的掌握度有所下降，建议回顾之前的内容。"

        return {
            "assessment": assessment,
            "trend": trend,
            "trend_feedback": trend_feedback,
            "history_count": len(history),
        }

    @staticmethod
    async def get_assessment_history(
        db: AsyncSession,
        user_id: int,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """获取评估历史"""
        result = await db.execute(
            select(StudentAssessment).where(
                StudentAssessment.user_id == user_id
            ).order_by(desc(StudentAssessment.created_at)).limit(limit)
        )
        records = result.scalars().all()
        return [
            {
                "id": r.id,
                "mastery": r.mastery,
                "stability": r.stability,
                "frustration_level": r.frustration_level,
                "anxiety_level": r.anxiety_level,
                "focus_level": r.focus_level,
                "assessment_type": r.assessment_type,
                "feedback": r.feedback,
                "strategies": r.strategy_suggestions,
                "created_at": r.created_at,
            }
            for r in records
        ]
