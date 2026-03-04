"""
Phase 12: 学习反馈系统 + 智能报告系统
整合 BKT、情感、课程进度、评估、复习等全维度数据
Phase 15: 集成预测分析、目标管理、学习习惯
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    StudentKnowledgeState, KnowledgeNode, Subject,
    StudentEmotionState, StudentEvent, StudentMisconception,
    ReviewSchedule, StudentCourseProgress, StudentAssessment,
    StudentFeedback, StudentLearningPath, StudentGoal, LearningHabit,
)


class SmartFeedbackService:

    # ---------- 1. 学习进度反馈 ----------
    async def generate_progress_feedback(
        self, db: AsyncSession, user_id: int,
        subject_id: Optional[int] = None,
        include_suggestions: bool = True,
    ) -> dict:
        # 收集各学科掌握度
        subject_progress = await self._collect_subject_progress(
            db, user_id, subject_id
        )
        # 学习路径完成情况
        path_stats = await self._collect_path_stats(db, user_id, subject_id)
        # 复习到期统计
        review_stats = await self._collect_review_stats(db, user_id)
        # 当前情感
        emotion = await self._get_current_emotion(db, user_id)

        progress_summary = {
            "subjects": subject_progress,
            "path_completion": path_stats,
            "review_due": review_stats["due_count"],
            "review_overdue": review_stats["overdue_count"],
        }

        suggestions = []
        if include_suggestions:
            suggestions = self._generate_progress_suggestions(
                subject_progress, path_stats, review_stats, emotion
            )

        encouragement = self._generate_encouragement(
            subject_progress, emotion
        )

        # 持久化
        fb = StudentFeedback(
            user_id=user_id,
            feedback_type="progress",
            subject_id=subject_id,
            progress_summary=progress_summary,
            emotion_summary={"current": emotion},
            suggestions=suggestions,
            encouragement=encouragement,
        )
        db.add(fb)
        await db.commit()
        await db.refresh(fb)

        return {
            "feedback_id": fb.id,
            "type": "progress",
            "progress": progress_summary,
            "suggestions": suggestions,
            "encouragement": encouragement,
            "emotion": emotion,
        }

    # ---------- 2. 情感反馈 ----------
    async def generate_emotion_feedback(
        self, db: AsyncSession, user_id: int,
        subject_id: Optional[int] = None,
    ) -> dict:
        emotion = await self._get_current_emotion(db, user_id)
        emotion_history = await self._get_emotion_trend(db, user_id)
        subject_progress = await self._collect_subject_progress(
            db, user_id, subject_id
        )

        difficulty_adj = self._compute_difficulty_adjustment(
            emotion, subject_progress
        )
        task_adj = self._compute_task_adjustment(emotion)
        encouragement = self._emotion_encouragement(emotion, emotion_history)

        emotion_summary = {
            "current": emotion,
            "trend": emotion_history,
            "dominant": emotion_history.get("dominant", emotion.get("type", "focus")),
        }

        fb = StudentFeedback(
            user_id=user_id,
            feedback_type="emotion",
            subject_id=subject_id,
            emotion_summary=emotion_summary,
            difficulty_adjustment=difficulty_adj,
            suggestions=task_adj,
            encouragement=encouragement,
        )
        db.add(fb)
        await db.commit()
        await db.refresh(fb)

        return {
            "feedback_id": fb.id,
            "type": "emotion",
            "emotion": emotion_summary,
            "difficulty_adjustment": difficulty_adj,
            "task_adjustment": task_adj,
            "encouragement": encouragement,
        }

    # ---------- 3. 智能报告 ----------
    async def generate_smart_report(
        self, db: AsyncSession, user_id: int,
        period: str = "weekly",
        subject_id: Optional[int] = None,
    ) -> dict:
        now = datetime.utcnow()
        delta = {"daily": 1, "weekly": 7, "monthly": 30}.get(period, 7)
        since = now - timedelta(days=delta)

        # 各维度数据
        subject_progress = await self._collect_subject_progress(
            db, user_id, subject_id
        )
        event_stats = await self._collect_event_stats(
            db, user_id, since
        )
        emotion_history = await self._get_emotion_trend(db, user_id, since)
        review_stats = await self._collect_review_stats(db, user_id)
        misconception_stats = await self._collect_misconception_stats(
            db, user_id
        )
        assessment_trend = await self._collect_assessment_trend(
            db, user_id, since
        )

        progress_summary = {
            "period": period,
            "since": since.isoformat(),
            "subjects": subject_progress,
            "events": event_stats,
            "review": review_stats,
            "misconceptions": misconception_stats,
            "assessment_trend": assessment_trend,
            "learning_velocity": self._compute_learning_velocity(
                event_stats, subject_progress, delta
            ),
        }

        emotion_summary = {
            "trend": emotion_history,
            "dominant": emotion_history.get("dominant", "focus"),
            "stability_score": self._compute_emotion_stability(emotion_history),
        }

        suggestions = self._generate_report_suggestions(
            subject_progress, event_stats, emotion_history,
            review_stats, misconception_stats, assessment_trend,
        )

        encouragement = self._report_encouragement(
            event_stats, subject_progress
        )

        # Phase 15: 集成预测、目标、习惯数据
        goals_summary = await self._collect_goals_summary(db, user_id)
        habits_summary = await self._collect_habits_summary(db, user_id)

        fb = StudentFeedback(
            user_id=user_id,
            feedback_type="smart_report",
            subject_id=subject_id,
            progress_summary=progress_summary,
            emotion_summary=emotion_summary,
            suggestions=suggestions,
            encouragement=encouragement,
        )
        db.add(fb)
        await db.commit()
        await db.refresh(fb)

        return {
            "report_id": fb.id,
            "type": "smart_report",
            "period": period,
            "progress": progress_summary,
            "emotion": emotion_summary,
            "goals": goals_summary,
            "habits": habits_summary,
            "suggestions": suggestions,
            "encouragement": encouragement,
        }

    # ---------- 4. 反馈历史 ----------
    async def get_feedback_history(
        self, db: AsyncSession, user_id: int,
        feedback_type: Optional[str] = None,
        limit: int = 20,
    ) -> list:
        q = select(StudentFeedback).where(
            StudentFeedback.user_id == user_id
        )
        if feedback_type:
            q = q.where(StudentFeedback.feedback_type == feedback_type)
        q = q.order_by(desc(StudentFeedback.created_at)).limit(limit)
        rows = (await db.execute(q)).scalars().all()
        return [
            {
                "id": r.id,
                "type": r.feedback_type,
                "subject_id": r.subject_id,
                "progress_summary": r.progress_summary,
                "emotion_summary": r.emotion_summary,
                "suggestions": r.suggestions,
                "encouragement": r.encouragement,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]

    # ---------- 5. 学习仪表盘 ----------
    async def get_dashboard(
        self, db: AsyncSession, user_id: int,
    ) -> dict:
        subject_progress = await self._collect_subject_progress(
            db, user_id, None
        )
        emotion = await self._get_current_emotion(db, user_id)
        review_stats = await self._collect_review_stats(db, user_id)
        path_stats = await self._collect_path_stats(db, user_id, None)

        # 今日学习事件数
        today = datetime.utcnow().replace(hour=0, minute=0, second=0)
        today_q = select(func.count()).select_from(StudentEvent).where(
            and_(
                StudentEvent.user_id == user_id,
                StudentEvent.created_at >= today,
            )
        )
        today_events = (await db.execute(today_q)).scalar() or 0

        return {
            "subjects": subject_progress,
            "emotion": emotion,
            "review_due": review_stats["due_count"],
            "review_overdue": review_stats["overdue_count"],
            "active_paths": path_stats.get("active_count", 0),
            "today_events": today_events,
            "goals": await self._collect_goals_summary(db, user_id),
            "habits": await self._collect_habits_summary(db, user_id),
        }

    # ==================== 内部数据收集方法 ====================

    async def _collect_subject_progress(
        self, db: AsyncSession, user_id: int,
        subject_id: Optional[int],
    ) -> list:
        q = (
            select(
                Subject.id, Subject.name,
                func.count(StudentKnowledgeState.id).label("node_count"),
                func.avg(StudentKnowledgeState.mastery).label("avg_mastery"),
                func.sum(StudentKnowledgeState.practice_count).label("total_practice"),
            )
            .join(KnowledgeNode, KnowledgeNode.subject_id == Subject.id)
            .join(
                StudentKnowledgeState,
                and_(
                    StudentKnowledgeState.knowledge_node_id == KnowledgeNode.id,
                    StudentKnowledgeState.user_id == user_id,
                ),
            )
            .group_by(Subject.id, Subject.name)
        )
        if subject_id:
            q = q.where(Subject.id == subject_id)

        rows = (await db.execute(q)).all()
        result = []
        for r in rows:
            mastery = float(r.avg_mastery or 0)
            level = (
                "mastered" if mastery >= 0.8
                else "learning" if mastery >= 0.4
                else "weak"
            )
            result.append({
                "subject_id": r.id,
                "subject_name": r.name,
                "node_count": r.node_count,
                "avg_mastery": round(mastery, 3),
                "total_practice": r.total_practice or 0,
                "level": level,
            })
        return result

    async def _collect_path_stats(
        self, db: AsyncSession, user_id: int,
        subject_id: Optional[int],
    ) -> dict:
        q = select(StudentLearningPath).where(
            StudentLearningPath.user_id == user_id
        )
        if subject_id:
            q = q.where(StudentLearningPath.subject_id == subject_id)
        rows = (await db.execute(q)).scalars().all()

        active = [p for p in rows if p.status == "active"]
        completed = [p for p in rows if p.status == "completed"]
        total_nodes = sum(p.total_nodes or 0 for p in active)
        done_nodes = sum(p.completed_nodes or 0 for p in active)

        return {
            "active_count": len(active),
            "completed_count": len(completed),
            "total_nodes": total_nodes,
            "completed_nodes": done_nodes,
            "completion_pct": round(done_nodes / total_nodes * 100, 1) if total_nodes else 0,
        }

    async def _collect_review_stats(
        self, db: AsyncSession, user_id: int,
    ) -> dict:
        now = datetime.utcnow()
        due_q = select(func.count()).select_from(ReviewSchedule).where(
            and_(
                ReviewSchedule.user_id == user_id,
                ReviewSchedule.next_review_at <= now,
            )
        )
        due = (await db.execute(due_q)).scalar() or 0

        overdue_q = select(func.count()).select_from(ReviewSchedule).where(
            and_(
                ReviewSchedule.user_id == user_id,
                ReviewSchedule.next_review_at <= now - timedelta(days=1),
            )
        )
        overdue = (await db.execute(overdue_q)).scalar() or 0

        return {"due_count": due, "overdue_count": overdue}

    async def _get_current_emotion(
        self, db: AsyncSession, user_id: int,
    ) -> dict:
        q = (
            select(StudentEmotionState)
            .where(StudentEmotionState.user_id == user_id)
            .order_by(desc(StudentEmotionState.created_at))
            .limit(1)
        )
        row = (await db.execute(q)).scalar_one_or_none()
        if not row:
            return {"type": "focus", "intensity": 0.5, "confidence": 0.3}
        return {
            "type": row.emotion_type,
            "intensity": row.intensity,
            "confidence": row.confidence,
        }

    async def _get_emotion_trend(
        self, db: AsyncSession, user_id: int,
        since: Optional[datetime] = None,
    ) -> dict:
        if not since:
            since = datetime.utcnow() - timedelta(days=7)
        q = (
            select(
                StudentEmotionState.emotion_type,
                func.count().label("cnt"),
                func.avg(StudentEmotionState.intensity).label("avg_intensity"),
            )
            .where(and_(
                StudentEmotionState.user_id == user_id,
                StudentEmotionState.created_at >= since,
            ))
            .group_by(StudentEmotionState.emotion_type)
            .order_by(desc("cnt"))
        )
        rows = (await db.execute(q)).all()
        dist = {r.emotion_type: r.cnt for r in rows}
        intensity_map = {
            r.emotion_type: round(float(r.avg_intensity or 0.5), 3)
            for r in rows
        }
        dominant = rows[0].emotion_type if rows else "focus"
        return {
            "distribution": dist,
            "intensity": intensity_map,
            "dominant": dominant,
        }

    async def _collect_event_stats(
        self, db: AsyncSession, user_id: int, since: datetime,
    ) -> dict:
        q = select(
            func.count().label("total"),
            func.sum(StudentEvent.is_correct).label("correct"),
        ).where(and_(
            StudentEvent.user_id == user_id,
            StudentEvent.created_at >= since,
        ))
        row = (await db.execute(q)).one()
        total = row.total or 0
        correct = int(row.correct or 0)
        return {
            "total_events": total,
            "correct": correct,
            "accuracy": round(correct / total, 3) if total else 0,
        }

    async def _collect_misconception_stats(
        self, db: AsyncSession, user_id: int,
    ) -> dict:
        total_q = select(func.count()).select_from(
            StudentMisconception
        ).where(StudentMisconception.user_id == user_id)
        total = (await db.execute(total_q)).scalar() or 0

        unresolved_q = select(func.count()).select_from(
            StudentMisconception
        ).where(and_(
            StudentMisconception.user_id == user_id,
            StudentMisconception.resolved == 0,
        ))
        unresolved = (await db.execute(unresolved_q)).scalar() or 0

        return {"total": total, "unresolved": unresolved}

    async def _collect_assessment_trend(
        self, db: AsyncSession, user_id: int, since: datetime,
    ) -> dict:
        q = (
            select(StudentAssessment)
            .where(and_(
                StudentAssessment.user_id == user_id,
                StudentAssessment.created_at >= since,
            ))
            .order_by(StudentAssessment.created_at)
        )
        rows = (await db.execute(q)).scalars().all()
        if len(rows) < 2:
            return {"trend": "insufficient_data", "count": len(rows)}

        first_half = rows[: len(rows) // 2]
        second_half = rows[len(rows) // 2:]
        avg_first = sum(r.mastery or 0 for r in first_half) / len(first_half)
        avg_second = sum(r.mastery or 0 for r in second_half) / len(second_half)

        diff = avg_second - avg_first
        if diff > 0.05:
            trend = "improving"
        elif diff < -0.05:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "count": len(rows),
            "avg_mastery_early": round(avg_first, 3),
            "avg_mastery_recent": round(avg_second, 3),
        }

    # ==================== 建议生成逻辑 ====================

    def _generate_progress_suggestions(
        self, subjects, path_stats, review_stats, emotion,
    ) -> list:
        suggestions = []

        # 薄弱学科优先
        weak = [s for s in subjects if s["level"] == "weak"]
        if weak:
            names = "、".join(s["subject_name"] for s in weak[:3])
            suggestions.append({
                "type": "weak_subject",
                "priority": 1,
                "message": f"{names} 掌握度较低，建议优先巩固基础知识点",
            })

        # 复习到期
        if review_stats["overdue_count"] > 0:
            suggestions.append({
                "type": "review_overdue",
                "priority": 2,
                "message": f"有 {review_stats['overdue_count']} 个知识点复习已逾期，及时复习可防止遗忘",
            })
        elif review_stats["due_count"] > 0:
            suggestions.append({
                "type": "review_due",
                "priority": 3,
                "message": f"有 {review_stats['due_count']} 个知识点待复习",
            })

        # 路径完成度
        if path_stats.get("active_count", 0) > 0 and path_stats["completion_pct"] < 50:
            suggestions.append({
                "type": "path_progress",
                "priority": 4,
                "message": f"当前学习路径完成 {path_stats['completion_pct']}%，继续加油",
            })

        # 情感调整
        emo = emotion.get("type", "focus")
        if emo == "frustration":
            suggestions.append({
                "type": "emotion_care",
                "priority": 1,
                "message": "检测到你可能有些受挫，建议先做一些已掌握的题目找回信心",
            })
        elif emo == "anxiety":
            suggestions.append({
                "type": "emotion_care",
                "priority": 2,
                "message": "别着急，学习是一个循序渐进的过程，试试放慢节奏",
            })

        suggestions.sort(key=lambda x: x["priority"])
        return suggestions

    def _generate_encouragement(self, subjects, emotion) -> str:
        if not subjects:
            return "开始你的学习之旅吧！每一步都是进步。"

        avg = sum(s["avg_mastery"] for s in subjects) / len(subjects)
        emo = emotion.get("type", "focus")

        if avg >= 0.8:
            return "你的整体掌握度非常出色，继续保持这个势头！"
        if avg >= 0.6:
            if emo == "frustration":
                return "你已经掌握了大部分内容，遇到困难很正常，坚持下去就会突破。"
            return "学习进展不错，再努力一把就能达到精通水平。"
        if avg >= 0.4:
            return "基础正在稳步建立，每天进步一点点，积累起来就是大进步。"
        return "万事开头难，你已经迈出了第一步，这就是最大的进步！"

    def _compute_difficulty_adjustment(
        self, emotion: dict, subjects: list,
    ) -> dict:
        emo = emotion.get("type", "focus")
        intensity = emotion.get("intensity", 0.5)

        base_factor = 1.0
        if emo == "frustration":
            base_factor = max(0.5, 1.0 - intensity * 0.5)
        elif emo == "anxiety":
            base_factor = max(0.6, 1.0 - intensity * 0.4)
        elif emo == "boredom":
            base_factor = min(1.5, 1.0 + intensity * 0.5)
        elif emo == "excitement":
            base_factor = min(1.3, 1.0 + intensity * 0.3)

        return {
            "factor": round(base_factor, 2),
            "reason": {
                "frustration": "降低难度以恢复信心",
                "anxiety": "适当降低难度减轻压力",
                "boredom": "提升难度增加挑战性",
                "excitement": "适当提升难度保持兴趣",
                "focus": "保持当前难度",
            }.get(emo, "保持当前难度"),
        }

    def _compute_task_adjustment(self, emotion: dict) -> list:
        emo = emotion.get("type", "focus")
        adjustments = {
            "frustration": [
                {"action": "reduce_new_content", "message": "减少新知识点，增加复习已掌握内容"},
                {"action": "add_easy_practice", "message": "穿插简单练习题提升成就感"},
                {"action": "shorten_session", "message": "缩短学习时长，避免疲劳累积"},
            ],
            "anxiety": [
                {"action": "slow_pace", "message": "放慢学习节奏，每个知识点多花些时间"},
                {"action": "add_review", "message": "增加复习环节巩固已学内容"},
            ],
            "boredom": [
                {"action": "increase_challenge", "message": "增加挑战性题目"},
                {"action": "cross_discipline", "message": "尝试跨学科内容激发兴趣"},
            ],
            "excitement": [
                {"action": "maintain_momentum", "message": "保持当前学习节奏"},
                {"action": "add_challenge", "message": "趁热打铁挑战更高难度"},
            ],
            "focus": [
                {"action": "balanced", "message": "当前状态良好，保持均衡学习"},
            ],
        }
        return adjustments.get(emo, adjustments["focus"])

    def _emotion_encouragement(
        self, emotion: dict, trend: dict,
    ) -> str:
        emo = emotion.get("type", "focus")
        dominant = trend.get("dominant", "focus")

        messages = {
            "frustration": "遇到困难是学习的一部分，每次克服困难都会让你更强大。试试换个角度思考？",
            "anxiety": "深呼吸，你比自己想象的更有能力。一步一步来，不用急。",
            "boredom": "看起来你已经很熟练了！试试更有挑战性的内容，或者探索新的学科领域。",
            "excitement": "太棒了！你现在状态很好，趁着这股劲头多学一些吧！",
            "focus": "你现在很专注，这是最好的学习状态，继续保持！",
        }
        return messages.get(emo, messages["focus"])

    def _generate_report_suggestions(
        self, subjects, events, emotion_trend,
        review_stats, misconceptions, assessment_trend,
    ) -> list:
        suggestions = []

        # 基于评估趋势
        trend = assessment_trend.get("trend", "stable")
        if trend == "declining":
            suggestions.append({
                "type": "trend_alert",
                "priority": 1,
                "message": "近期掌握度有下降趋势，建议增加复习频率并关注薄弱环节",
            })
        elif trend == "improving":
            suggestions.append({
                "type": "trend_positive",
                "priority": 5,
                "message": "掌握度持续提升，学习方法很有效，继续保持",
            })

        # 基于正确率
        acc = events.get("accuracy", 0)
        if acc < 0.5 and events.get("total_events", 0) > 10:
            suggestions.append({
                "type": "accuracy_low",
                "priority": 1,
                "message": "正确率偏低，建议回顾基础知识点后再做练习",
            })

        # 基于未解决误解
        if misconceptions.get("unresolved", 0) > 3:
            suggestions.append({
                "type": "misconception",
                "priority": 2,
                "message": f"有 {misconceptions['unresolved']} 个未解决的知识误区，建议通过诊断式Tutor逐一攻克",
            })

        # 基于情感趋势（含强度分析）
        dominant = emotion_trend.get("dominant", "focus")
        if dominant in ("frustration", "anxiety"):
            intensity_info = emotion_trend.get("intensity", {})
            avg_neg = intensity_info.get(dominant, 0.5)
            if avg_neg > 0.7:
                suggestions.append({
                    "type": "emotion_trend",
                    "priority": 1,
                    "message": f"近期{dominant}情绪频繁且强度较高({avg_neg:.0%})，强烈建议降低学习强度，穿插轻松内容",
                })
            else:
                suggestions.append({
                    "type": "emotion_trend",
                    "priority": 2,
                    "message": "近期负面情绪较多，建议适当降低学习强度，穿插轻松内容",
                })

        # 基于情感稳定性
        stability = self._compute_emotion_stability(emotion_trend)
        if stability < 0.4:
            suggestions.append({
                "type": "emotion_unstable",
                "priority": 2,
                "message": f"情感波动较大（稳定性 {stability:.0%}），建议保持规律学习节奏，避免高强度突击",
            })

        # 基于学习效率
        total_events = events.get("total_events", 0)
        if total_events > 20 and acc >= 0.7:
            weak_count = sum(1 for s in subjects if s.get("level") == "weak")
            if weak_count == 0:
                suggestions.append({
                    "type": "efficiency_high",
                    "priority": 5,
                    "message": "学习效率很高，正确率和掌握度都表现优秀，可以尝试更有挑战性的内容",
                })

        # 基于复习
        if review_stats.get("overdue_count", 0) > 5:
            suggestions.append({
                "type": "review_backlog",
                "priority": 2,
                "message": f"有 {review_stats['overdue_count']} 个逾期复习，建议优先清理复习积压",
            })

        suggestions.sort(key=lambda x: x["priority"])
        return suggestions

    def _report_encouragement(self, events, subjects) -> str:
        total = events.get("total_events", 0)
        acc = events.get("accuracy", 0)

        if total == 0:
            return "这段时间还没有学习记录，开始学习吧！"
        if acc >= 0.8:
            return f"这段时间完成了 {total} 次练习，正确率 {acc*100:.0f}%，表现非常出色！"
        if acc >= 0.6:
            return f"完成了 {total} 次练习，正确率 {acc*100:.0f}%，继续努力会更好。"
        return f"完成了 {total} 次练习，虽然正确率还需提升，但坚持学习本身就值得肯定！"

    def _compute_learning_velocity(
        self, events: dict, subjects: list, period_days: int,
    ) -> dict:
        """计算学习速度指标"""
        total = events.get("total_events", 0)
        daily_events = round(total / max(period_days, 1), 1)
        avg_mastery = (
            sum(s["avg_mastery"] for s in subjects) / len(subjects)
            if subjects else 0
        )
        # 学习效率 = 正确率 × 日均练习量 / 10（归一化到0~1）
        acc = events.get("accuracy", 0)
        efficiency = round(min(1.0, acc * daily_events / 10), 3)

        if daily_events >= 5 and acc >= 0.7:
            pace = "high"
        elif daily_events >= 2:
            pace = "moderate"
        elif daily_events > 0:
            pace = "low"
        else:
            pace = "inactive"

        return {
            "daily_events": daily_events,
            "avg_mastery": round(avg_mastery, 3),
            "efficiency": efficiency,
            "pace": pace,
        }

    def _compute_emotion_stability(self, emotion_trend: dict) -> float:
        """计算情感稳定性评分 (0~1, 1=非常稳定)"""
        dist = emotion_trend.get("distribution", {})
        if not dist:
            return 0.5
        total = sum(dist.values())
        if total == 0:
            return 0.5
        # 正面情感占比
        positive = dist.get("focus", 0) + dist.get("excitement", 0)
        negative = dist.get("frustration", 0) + dist.get("anxiety", 0)
        # 稳定性 = 正面占比 - 负面占比的波动惩罚
        pos_ratio = positive / total
        neg_ratio = negative / total
        # 情感类型越集中越稳定（用最大占比衡量）
        max_ratio = max(dist.values()) / total
        stability = pos_ratio * 0.5 + max_ratio * 0.3 + (1 - neg_ratio) * 0.2
        return round(min(1.0, max(0.0, stability)), 3)

    # ==================== Phase 15: 目标 & 习惯集成 ====================

    async def _collect_goals_summary(self, db, user_id):
        q = select(StudentGoal).where(and_(
            StudentGoal.user_id == user_id,
            StudentGoal.status == "active",
        ))
        result = await db.execute(q)
        goals = result.scalars().all()
        at_risk = 0
        now = datetime.utcnow()
        for g in goals:
            if g.deadline and g.deadline < now:
                at_risk += 1
            elif g.deadline and g.target_value:
                total_d = (g.deadline - g.created_at).total_seconds() / 86400
                elapsed = (now - g.created_at).total_seconds() / 86400
                pct = (g.current_value / g.target_value) if g.target_value else 0
                expected = elapsed / total_d if total_d > 0 else 0
                if pct < expected * 0.7:
                    at_risk += 1
        completed_q = select(func.count()).select_from(StudentGoal).where(and_(
            StudentGoal.user_id == user_id,
            StudentGoal.status == "completed",
        ))
        completed = (await db.execute(completed_q)).scalar() or 0
        return {
            "active_count": len(goals),
            "completed_count": completed,
            "at_risk_count": at_risk,
        }

    async def _collect_habits_summary(self, db, user_id):
        from datetime import date
        today = date.today()
        since = today - timedelta(days=30)
        q = select(LearningHabit).where(and_(
            LearningHabit.user_id == user_id,
            LearningHabit.date >= since,
        )).order_by(LearningHabit.date)
        result = await db.execute(q)
        rows = result.scalars().all()
        active_days = [r for r in rows if (r.events_count or 0) > 0]
        consistency = len(active_days) / 30.0

        # 连续天数
        streak = 0
        check = today
        dates = sorted(
            [r.date if not hasattr(r.date, 'date') else r.date for r in active_days],
            reverse=True,
        )
        for d in dates:
            if hasattr(d, 'date') and callable(d.date):
                d = d.date()
            if d == check:
                streak += 1
                check -= timedelta(days=1)
            else:
                break

        return {
            "current_streak": streak,
            "consistency_score": round(consistency, 3),
            "active_days_30": len(active_days),
            "trend": "improving" if consistency > 0.6 else "needs_attention" if consistency < 0.3 else "moderate",
        }
