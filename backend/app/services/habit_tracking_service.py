"""
Phase 15: 学习习惯追踪
每日快照 + 连续天数 + 一致性评分 + 个人最佳
"""
from datetime import datetime, timedelta, date
from typing import Optional
from sqlalchemy import select, func, and_, desc, Float
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    LearningHabit, StudentEvent, StudentEmotionState, KnowledgeNode,
)


class HabitTrackingService:

    # ---------- 习惯摘要 ----------
    async def get_summary(
        self, db: AsyncSession, user_id: int,
    ) -> dict:
        today = date.today()
        # 获取近90天习惯数据
        since = today - timedelta(days=90)
        rows = await self._get_habit_rows(db, user_id, since)

        current_streak = self._calc_streak(rows, today)
        longest_streak = self._calc_longest_streak(rows)
        days_30 = [r for r in rows if r["date"] >= today - timedelta(days=30)]
        consistency = len(days_30) / 30.0 if days_30 else 0

        avg_events = (
            sum(r["events_count"] for r in days_30) / len(days_30)
            if days_30 else 0
        )
        avg_minutes = (
            sum(r["study_minutes"] for r in days_30) / len(days_30)
            if days_30 else 0
        )

        # 习惯洞察
        if consistency > 0.8:
            insight = "学习习惯优秀，保持节奏"
        elif consistency > 0.5:
            insight = "建议固定每天学习时间，培养规律性"
        else:
            insight = "学习频率偏低，试试每天10分钟的小目标"

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "consistency_score": round(consistency, 3),
            "avg_daily_events": round(avg_events, 1),
            "avg_daily_minutes": round(avg_minutes, 1),
            "active_days_30": len(days_30),
            "insight": insight,
        }

    # ---------- 日历视图 ----------
    async def get_calendar(
        self, db: AsyncSession, user_id: int, days: int = 30,
    ) -> dict:
        today = date.today()
        since = today - timedelta(days=days)
        rows = await self._get_habit_rows(db, user_id, since)

        # 确保每天都有记录（无数据的天填0）
        calendar = []
        for i in range(days):
            d = since + timedelta(days=i + 1)
            matched = next((r for r in rows if r["date"] == d), None)
            if matched:
                calendar.append(matched)
            else:
                calendar.append({
                    "date": d, "events_count": 0,
                    "study_minutes": 0, "accuracy": None, "active": False,
                })

        return {"days": days, "calendar": calendar}

    # ---------- 个人最佳 ----------
    async def get_personal_bests(
        self, db: AsyncSession, user_id: int,
    ) -> dict:
        # 最高单日练习量
        q_max_events = (
            select(
                LearningHabit.date,
                LearningHabit.events_count,
            )
            .where(LearningHabit.user_id == user_id)
            .order_by(LearningHabit.events_count.desc())
            .limit(1)
        )
        r1 = await db.execute(q_max_events)
        max_events_row = r1.first()

        # 最高单日学习时长
        q_max_min = (
            select(
                LearningHabit.date,
                LearningHabit.study_minutes,
            )
            .where(LearningHabit.user_id == user_id)
            .order_by(LearningHabit.study_minutes.desc())
            .limit(1)
        )
        r2 = await db.execute(q_max_min)
        max_min_row = r2.first()

        # 最长连续天数
        rows = await self._get_habit_rows(
            db, user_id, date.today() - timedelta(days=365)
        )
        longest = self._calc_longest_streak(rows)

        return {
            "max_daily_events": {
                "value": max_events_row.events_count if max_events_row else 0,
                "date": str(max_events_row.date) if max_events_row else None,
            },
            "max_daily_minutes": {
                "value": max_min_row.study_minutes if max_min_row else 0,
                "date": str(max_min_row.date) if max_min_row else None,
            },
            "longest_streak": longest,
        }

    # ---------- 快照同步（由事件触发调用） ----------
    async def sync_today(
        self, db: AsyncSession, user_id: int,
    ) -> None:
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = today_start + timedelta(days=1)

        # 统计今日事件
        eq = select(
            func.count().label("cnt"),
            func.avg(func.cast(StudentEvent.is_correct, Float)).label("acc"),
        ).where(and_(
            StudentEvent.user_id == user_id,
            StudentEvent.created_at >= today_start,
            StudentEvent.created_at < today_end,
        ))
        er = await db.execute(eq)
        erow = er.one()

        # 统计涉及学科数（通过 join KnowledgeNode）
        sq = (
            select(func.count(func.distinct(KnowledgeNode.subject_id)))
            .select_from(StudentEvent)
            .join(KnowledgeNode, KnowledgeNode.id == StudentEvent.knowledge_node_id)
            .where(and_(
                StudentEvent.user_id == user_id,
                StudentEvent.created_at >= today_start,
                StudentEvent.created_at < today_end,
            ))
        )
        sr = await db.execute(sq)
        subj_count = sr.scalar() or 0

        # 主导情感
        emq = (
            select(StudentEmotionState.emotion_type)
            .where(and_(
                StudentEmotionState.user_id == user_id,
                StudentEmotionState.created_at >= today_start,
            ))
            .order_by(StudentEmotionState.created_at.desc())
            .limit(1)
        )
        emr = await db.execute(emq)
        emo_row = emr.first()
        dominant = emo_row.emotion_type if emo_row else None

        # upsert
        existing_q = select(LearningHabit).where(and_(
            LearningHabit.user_id == user_id,
            LearningHabit.date == today,
        ))
        existing_r = await db.execute(existing_q)
        habit = existing_r.scalar_one_or_none()

        if habit:
            habit.events_count = erow.cnt or 0
            habit.accuracy = round(float(erow.acc or 0), 3)
            habit.subjects_touched = subj_count
            habit.dominant_emotion = dominant
        else:
            habit = LearningHabit(
                user_id=user_id,
                date=today,
                events_count=erow.cnt or 0,
                accuracy=round(float(erow.acc or 0), 3),
                subjects_touched=subj_count,
                dominant_emotion=dominant,
            )
            db.add(habit)

        await db.commit()

    # ========== 内部方法 ==========

    async def _get_habit_rows(self, db, user_id, since):
        q = (
            select(LearningHabit)
            .where(and_(
                LearningHabit.user_id == user_id,
                LearningHabit.date >= since,
            ))
            .order_by(LearningHabit.date)
        )
        result = await db.execute(q)
        rows = []
        for h in result.scalars().all():
            d = h.date
            if hasattr(d, 'date') and callable(d.date):
                d = d.date()
            rows.append({
                "date": d,
                "events_count": h.events_count or 0,
                "study_minutes": h.study_minutes or 0,
                "accuracy": round(h.accuracy, 3) if h.accuracy else None,
                "dominant_emotion": h.dominant_emotion,
                "active": (h.events_count or 0) > 0,
            })
        return rows

    def _calc_streak(self, rows, today):
        active_dates = sorted(
            [r["date"] for r in rows if r["events_count"] > 0], reverse=True
        )
        streak = 0
        check = today
        for d in active_dates:
            if d == check:
                streak += 1
                check -= timedelta(days=1)
            elif d < check:
                break
        return streak

    def _calc_longest_streak(self, rows):
        active_dates = sorted([r["date"] for r in rows if r["events_count"] > 0])
        if not active_dates:
            return 0
        longest = 1
        current = 1
        for i in range(1, len(active_dates)):
            if active_dates[i] - active_dates[i - 1] == timedelta(days=1):
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        return longest
