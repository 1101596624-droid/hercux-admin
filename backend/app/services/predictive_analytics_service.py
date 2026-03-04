"""
Phase 15: 预测分析引擎
掌握度预测 + 遗忘风险预警 + 学习瓶颈检测 + 对比分析
"""
import math
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func, and_, Float
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    StudentKnowledgeState, KnowledgeNode, Subject,
    StudentEvent, StudentMisconception, ReviewSchedule,
)


class PredictiveAnalyticsService:

    # ---------- 1. 掌握度预测 ----------
    async def get_predictions(
        self, db: AsyncSession, user_id: int,
        subject_id: Optional[int] = None,
        target_mastery: float = 0.8,
    ) -> dict:
        nodes = await self._get_node_states(db, user_id, subject_id)
        predictions = []
        for n in nodes:
            if n["mastery"] >= target_mastery:
                continue
            slope = await self._calc_mastery_slope(
                db, user_id, n["node_id"], days=7
            )
            pred = self._predict_one(n, slope, target_mastery)
            predictions.append(pred)

        predictions.sort(key=lambda x: x.get("predicted_days") or 999)
        stalled = [p for p in predictions if p["risk"] == "stalled"]
        on_track = [p for p in predictions if p["risk"] is None]
        return {
            "target_mastery": target_mastery,
            "total_nodes": len(predictions),
            "on_track": len(on_track),
            "stalled": len(stalled),
            "predictions": predictions[:20],
        }

    # ---------- 2. 遗忘风险 ----------
    async def get_forgetting_risks(
        self, db: AsyncSession, user_id: int,
        subject_id: Optional[int] = None,
    ) -> dict:
        now = datetime.utcnow()
        q = (
            select(
                ReviewSchedule.knowledge_node_id,
                ReviewSchedule.fsrs_stability,
                ReviewSchedule.next_review_at,
                KnowledgeNode.name.label("node_name"),
            )
            .join(KnowledgeNode, KnowledgeNode.id == ReviewSchedule.knowledge_node_id)
            .where(ReviewSchedule.user_id == user_id)
        )
        if subject_id:
            q = q.where(KnowledgeNode.subject_id == subject_id)
        result = await db.execute(q)
        rows = result.all()

        risks = []
        for r in rows:
            if not r.next_review_at or not r.fsrs_stability:
                continue
            days_overdue = (now - r.next_review_at).total_seconds() / 86400
            if days_overdue <= 0:
                continue
            stab = max(r.fsrs_stability, 0.1)
            forget_prob = 1 - math.exp(-days_overdue / stab)
            level = "high" if forget_prob > 0.7 else "medium" if forget_prob > 0.4 else "low"
            risks.append({
                "node_id": r.knowledge_node_id,
                "node_name": r.node_name,
                "stability": round(r.fsrs_stability, 2),
                "days_overdue": round(days_overdue, 1),
                "forget_probability": round(forget_prob, 3),
                "risk_level": level,
            })

        risks.sort(key=lambda x: x["forget_probability"], reverse=True)
        return {
            "total": len(risks),
            "high_risk": len([r for r in risks if r["risk_level"] == "high"]),
            "risks": risks[:20],
        }

    # ---------- 3. 学习瓶颈 ----------
    async def get_bottlenecks(
        self, db: AsyncSession, user_id: int,
        subject_id: Optional[int] = None,
    ) -> dict:
        nodes = await self._get_node_states(db, user_id, subject_id)
        bottlenecks = []

        for n in nodes:
            issues = []
            # 规则1: 高练习量低掌握度
            if n["practice_count"] > 20 and n["mastery"] < 0.5:
                issues.append("inefficient_practice")
            # 规则2: 掌握度回退
            slope = await self._calc_mastery_slope(
                db, user_id, n["node_id"], days=7
            )
            if slope < -0.01 and n["mastery"] < 0.7:
                issues.append("regression")
            # 规则3: 未解决误解
            misc_count = await self._unresolved_misconceptions(
                db, user_id, n["node_id"]
            )
            if misc_count > 0 and n["mastery"] < 0.6:
                issues.append("misconception_block")
            # 规则4: 连续低正确率
            recent_acc = await self._recent_accuracy(
                db, user_id, n["node_id"], last_n=3
            )
            if recent_acc is not None and recent_acc < 0.4:
                issues.append("persistent_difficulty")

            if issues:
                bottlenecks.append({
                    "node_id": n["node_id"],
                    "node_name": n["node_name"],
                    "mastery": n["mastery"],
                    "practice_count": n["practice_count"],
                    "issues": issues,
                })

        return {"total": len(bottlenecks), "bottlenecks": bottlenecks}

    # ---------- 4. 对比分析 ----------
    async def get_comparative(
        self, db: AsyncSession, user_id: int,
        period: str = "weekly",
        subject_id: Optional[int] = None,
    ) -> dict:
        now = datetime.utcnow()
        if period == "weekly":
            cur_start = now - timedelta(days=7)
            prev_start = now - timedelta(days=14)
            prev_end = cur_start
        else:
            cur_start = now - timedelta(days=30)
            prev_start = now - timedelta(days=60)
            prev_end = cur_start

        current = await self._period_stats(
            db, user_id, cur_start, now, subject_id
        )
        previous = await self._period_stats(
            db, user_id, prev_start, prev_end, subject_id
        )

        changes = {}
        for key in ["events", "accuracy", "mastery_avg"]:
            cur_v = current.get(key, 0) or 0
            prev_v = previous.get(key, 0) or 0
            delta = round(cur_v - prev_v, 3)
            pct = f"{(delta / prev_v * 100):+.1f}%" if prev_v else "N/A"
            trend = "improving" if delta > 0 else "declining" if delta < 0 else "stable"
            changes[key] = {"delta": delta, "percent": pct, "trend": trend}

        return {
            "period": period,
            "current": current,
            "previous": previous,
            "changes": changes,
        }

    # ========== 内部方法 ==========

    async def _get_node_states(self, db, user_id, subject_id=None):
        q = (
            select(
                StudentKnowledgeState.knowledge_node_id,
                StudentKnowledgeState.mastery,
                StudentKnowledgeState.stability,
                StudentKnowledgeState.practice_count,
                KnowledgeNode.name.label("node_name"),
            )
            .join(KnowledgeNode, KnowledgeNode.id == StudentKnowledgeState.knowledge_node_id)
            .where(StudentKnowledgeState.user_id == user_id)
        )
        if subject_id:
            q = q.where(KnowledgeNode.subject_id == subject_id)
        result = await db.execute(q)
        return [
            {
                "node_id": r.knowledge_node_id,
                "node_name": r.node_name,
                "mastery": r.mastery or 0,
                "stability": r.stability or 0.5,
                "practice_count": r.practice_count or 0,
            }
            for r in result.all()
        ]

    async def _calc_mastery_slope(self, db, user_id, node_id, days=7):
        since = datetime.utcnow() - timedelta(days=days)
        q = (
            select(
                StudentEvent.is_correct,
                StudentEvent.created_at,
            )
            .where(and_(
                StudentEvent.user_id == user_id,
                StudentEvent.knowledge_node_id == node_id,
                StudentEvent.created_at >= since,
            ))
            .order_by(StudentEvent.created_at)
        )
        result = await db.execute(q)
        events = result.all()
        if len(events) < 2:
            return 0.0
        # 简单线性：首半段正确率 vs 后半段正确率
        mid = len(events) // 2
        first_acc = sum(1 for e in events[:mid] if e.is_correct) / mid
        second_acc = sum(1 for e in events[mid:] if e.is_correct) / (len(events) - mid)
        return round(second_acc - first_acc, 4)

    def _predict_one(self, node, slope, target):
        gap = target - node["mastery"]
        if slope <= 0.005:
            return {
                "node_id": node["node_id"],
                "node_name": node["node_name"],
                "current_mastery": round(node["mastery"], 3),
                "target_mastery": target,
                "slope": slope,
                "predicted_days": None,
                "confidence": "low",
                "risk": "stalled",
            }
        days = gap / max(slope, 0.01)
        # stability 修正
        if node["stability"] < 0.3:
            days *= 1.5
        conf = "high" if slope > 0.05 else "medium" if slope > 0.02 else "low"
        return {
            "node_id": node["node_id"],
            "node_name": node["node_name"],
            "current_mastery": round(node["mastery"], 3),
            "target_mastery": target,
            "slope": slope,
            "predicted_days": round(days, 1),
            "confidence": conf,
            "risk": None,
        }

    async def _unresolved_misconceptions(self, db, user_id, node_id):
        q = select(func.count()).select_from(StudentMisconception).where(and_(
            StudentMisconception.user_id == user_id,
            StudentMisconception.knowledge_node_id == node_id,
            StudentMisconception.resolved == 0,
        ))
        result = await db.execute(q)
        return result.scalar() or 0

    async def _recent_accuracy(self, db, user_id, node_id, last_n=3):
        q = (
            select(StudentEvent.is_correct)
            .where(and_(
                StudentEvent.user_id == user_id,
                StudentEvent.knowledge_node_id == node_id,
                StudentEvent.event_type == "answer",
            ))
            .order_by(StudentEvent.created_at.desc())
            .limit(last_n)
        )
        result = await db.execute(q)
        rows = result.all()
        if len(rows) < last_n:
            return None
        return sum(1 for r in rows if r.is_correct) / len(rows)

    async def _period_stats(self, db, user_id, start, end, subject_id=None):
        q = select(
            func.count().label("events"),
            func.avg(
                func.cast(StudentEvent.is_correct, Float)
            ).label("accuracy"),
        ).where(and_(
            StudentEvent.user_id == user_id,
            StudentEvent.created_at >= start,
            StudentEvent.created_at < end,
        ))
        if subject_id:
            q = q.join(
                KnowledgeNode,
                KnowledgeNode.id == StudentEvent.knowledge_node_id,
            ).where(KnowledgeNode.subject_id == subject_id)
        result = await db.execute(q)
        row = result.one()

        # 平均掌握度
        mq = select(
            func.avg(StudentKnowledgeState.mastery)
        ).where(StudentKnowledgeState.user_id == user_id)
        if subject_id:
            mq = mq.join(KnowledgeNode, KnowledgeNode.id == StudentKnowledgeState.knowledge_node_id)
            mq = mq.where(KnowledgeNode.subject_id == subject_id)
        mr = await db.execute(mq)
        avg_m = mr.scalar() or 0

        return {
            "events": row.events or 0,
            "accuracy": round(float(row.accuracy or 0), 3),
            "mastery_avg": round(float(avg_m), 3),
        }
