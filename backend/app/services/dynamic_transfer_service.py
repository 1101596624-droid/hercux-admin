"""
Phase 16: 动态迁移系数学习 + 时间模式分析
- 贝叶斯更新个性化跨学科迁移系数
- 时间模式分析（最佳学习时段、工作日/周末差异）
"""
import math
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract, case, Float as SAFloat
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.models import (
    StudentSubjectTransfer, SubjectRelation, Subject,
    StudentKnowledgeState, KnowledgeNode, StudentEvent,
    LearningHabit,
)


class DynamicTransferService:
    """动态迁移系数 + 时间模式引擎"""

    # ==================== 迁移系数 ====================

    @staticmethod
    async def get_my_coefficients(
        db: AsyncSession, user_id: int,
    ) -> dict:
        """获取个人化迁移系数（含全局回退）"""
        # 个人化系数
        result = await db.execute(
            select(StudentSubjectTransfer).where(
                StudentSubjectTransfer.user_id == user_id
            )
        )
        personal = list(result.scalars().all())

        # 全局系数
        global_result = await db.execute(select(SubjectRelation))
        global_rels = list(global_result.scalars().all())

        # 学科名称
        subj_result = await db.execute(select(Subject))
        subj_map = {s.id: s.name for s in subj_result.scalars().all()}

        # 构建个人化 map
        personal_map = {}
        for p in personal:
            key = (p.source_subject_id, p.target_subject_id)
            personal_map[key] = {
                "observed_transfer": round(p.observed_transfer, 4),
                "confidence": round(p.confidence, 4),
                "sample_count": p.sample_count,
            }

        coefficients = []
        for rel in global_rels:
            key = (rel.source_subject_id, rel.target_subject_id)
            p = personal_map.get(key)
            use_personal = p is not None and p["confidence"] > 0.3
            coefficients.append({
                "source_subject": subj_map.get(rel.source_subject_id, "?"),
                "target_subject": subj_map.get(rel.target_subject_id, "?"),
                "global_coefficient": round(rel.transfer_coefficient, 4),
                "personal_coefficient": p["observed_transfer"] if use_personal else None,
                "confidence": p["confidence"] if p else 0,
                "sample_count": p["sample_count"] if p else 0,
                "effective": round(p["observed_transfer"], 4) if use_personal else round(rel.transfer_coefficient, 4),
                "source": "personal" if use_personal else "global",
            })

        return {"user_id": user_id, "coefficients": coefficients}

    @staticmethod
    async def update_transfer(
        db: AsyncSession, user_id: int,
        source_subject_id: int, target_subject_id: int,
    ) -> dict:
        """基于最新学习数据，贝叶斯更新迁移系数"""
        # 获取全局先验
        rel_result = await db.execute(
            select(SubjectRelation).where(and_(
                SubjectRelation.source_subject_id == source_subject_id,
                SubjectRelation.target_subject_id == target_subject_id,
            ))
        )
        rel = rel_result.scalars().first()
        prior = rel.transfer_coefficient if rel else 0.3

        # 源学科掌握度
        src_result = await db.execute(
            select(func.avg(StudentKnowledgeState.mastery)).where(and_(
                StudentKnowledgeState.user_id == user_id,
                KnowledgeNode.subject_id == source_subject_id,
                StudentKnowledgeState.knowledge_node_id == KnowledgeNode.id,
            ))
        )
        src_avg = src_result.scalar() or 0

        # 目标学科掌握度
        tgt_result = await db.execute(
            select(func.avg(StudentKnowledgeState.mastery)).where(and_(
                StudentKnowledgeState.user_id == user_id,
                KnowledgeNode.subject_id == target_subject_id,
                StudentKnowledgeState.knowledge_node_id == KnowledgeNode.id,
            ))
        )
        tgt_avg = tgt_result.scalar() or 0

        # 观测迁移率
        observed = (tgt_avg / src_avg) if src_avg > 0.1 else 0.0
        observed = min(observed, 1.0)

        # 获取或创建个人记录
        existing = await db.execute(
            select(StudentSubjectTransfer).where(and_(
                StudentSubjectTransfer.user_id == user_id,
                StudentSubjectTransfer.source_subject_id == source_subject_id,
                StudentSubjectTransfer.target_subject_id == target_subject_id,
            ))
        )
        record = existing.scalars().first()

        if record:
            old_conf = record.confidence
            sample_weight = 1.0 / (record.sample_count + 1)
            posterior = (record.observed_transfer * old_conf + observed * sample_weight) / (old_conf + sample_weight)
            record.observed_transfer = posterior
            record.confidence = min(old_conf + sample_weight * 0.5, 1.0)
            record.sample_count += 1
            record.updated_at = datetime.utcnow()
        else:
            sample_weight = 1.0
            posterior = (prior * 0.1 + observed * sample_weight) / (0.1 + sample_weight)
            record = StudentSubjectTransfer(
                user_id=user_id,
                source_subject_id=source_subject_id,
                target_subject_id=target_subject_id,
                observed_transfer=posterior,
                confidence=min(0.1 + sample_weight * 0.5, 1.0),
                sample_count=1,
            )
            db.add(record)

        await db.commit()

        return {
            "source_subject_id": source_subject_id,
            "target_subject_id": target_subject_id,
            "prior": round(prior, 4),
            "observed": round(observed, 4),
            "posterior": round(posterior, 4),
            "confidence": round(record.confidence, 4),
            "sample_count": record.sample_count,
        }

    @staticmethod
    async def get_effective_coefficient(
        db: AsyncSession, user_id: int,
        source_subject_id: int, target_subject_id: int,
    ) -> float:
        """获取有效迁移系数（个人化优先，全局回退）"""
        result = await db.execute(
            select(StudentSubjectTransfer).where(and_(
                StudentSubjectTransfer.user_id == user_id,
                StudentSubjectTransfer.source_subject_id == source_subject_id,
                StudentSubjectTransfer.target_subject_id == target_subject_id,
            ))
        )
        personal = result.scalars().first()
        if personal and personal.confidence > 0.3:
            return personal.observed_transfer

        rel_result = await db.execute(
            select(SubjectRelation.transfer_coefficient).where(and_(
                SubjectRelation.source_subject_id == source_subject_id,
                SubjectRelation.target_subject_id == target_subject_id,
            ))
        )
        global_coeff = rel_result.scalar()
        return global_coeff if global_coeff is not None else 0.2

    # ==================== 时间模式 ====================

    @staticmethod
    async def get_temporal_patterns(
        db: AsyncSession, user_id: int, days: int = 30,
    ) -> dict:
        """分析学习时间模式"""
        since = datetime.utcnow() - timedelta(days=days)

        # 按小时统计事件数和正确率
        hour_stats = await db.execute(
            select(
                extract("hour", StudentEvent.created_at).label("hour"),
                func.count().label("cnt"),
                func.avg(case(
                    (StudentEvent.is_correct == 1, 1.0),
                    else_=0.0,
                )).label("accuracy"),
            ).where(and_(
                StudentEvent.user_id == user_id,
                StudentEvent.created_at >= since,
            )).group_by("hour").order_by("hour")
        )
        hourly = []
        best_hour = None
        best_acc = -1
        for row in hour_stats:
            h = int(row.hour)
            acc = round(float(row.accuracy or 0), 3)
            hourly.append({"hour": h, "events": row.cnt, "accuracy": acc})
            if acc > best_acc and row.cnt >= 3:
                best_acc = acc
                best_hour = h

        # 工作日 vs 周末
        dow_stats = await db.execute(
            select(
                extract("dow", StudentEvent.created_at).label("dow"),
                func.count().label("cnt"),
                func.avg(case(
                    (StudentEvent.is_correct == 1, 1.0),
                    else_=0.0,
                )).label("accuracy"),
            ).where(and_(
                StudentEvent.user_id == user_id,
                StudentEvent.created_at >= since,
            )).group_by("dow")
        )
        weekday_events = 0
        weekday_acc_sum = 0
        weekday_count = 0
        weekend_events = 0
        weekend_acc_sum = 0
        weekend_count = 0
        for row in dow_stats:
            d = int(row.dow)
            if d in (0, 6):  # 周日=0, 周六=6
                weekend_events += row.cnt
                weekend_acc_sum += float(row.accuracy or 0) * row.cnt
                weekend_count += row.cnt
            else:
                weekday_events += row.cnt
                weekday_acc_sum += float(row.accuracy or 0) * row.cnt
                weekday_count += row.cnt

        # 最优 session 时长（基于习惯数据）
        habit_result = await db.execute(
            select(LearningHabit.study_minutes, LearningHabit.accuracy).where(and_(
                LearningHabit.user_id == user_id,
                LearningHabit.date >= since,
                LearningHabit.study_minutes > 0,
            ))
        )
        habits = list(habit_result.all())
        optimal_minutes = 30  # 默认
        if habits:
            # 按时长分桶，找正确率最高的桶
            buckets = {}
            for h in habits:
                bucket = (h.study_minutes // 15) * 15  # 15分钟一桶
                if bucket not in buckets:
                    buckets[bucket] = []
                buckets[bucket].append(h.accuracy or 0)
            best_bucket = max(
                buckets.items(),
                key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
            )
            optimal_minutes = max(15, best_bucket[0])

        return {
            "period_days": days,
            "hourly_distribution": hourly,
            "best_hour": best_hour,
            "best_hour_accuracy": round(best_acc, 3) if best_acc >= 0 else None,
            "weekday_vs_weekend": {
                "weekday_events": weekday_events,
                "weekday_accuracy": round(weekday_acc_sum / weekday_count, 3) if weekday_count else None,
                "weekend_events": weekend_events,
                "weekend_accuracy": round(weekend_acc_sum / weekend_count, 3) if weekend_count else None,
            },
            "optimal_session_minutes": optimal_minutes,
            "insight": DynamicTransferService._temporal_insight(best_hour, optimal_minutes),
        }

    @staticmethod
    async def get_optimal_schedule(
        db: AsyncSession, user_id: int,
    ) -> dict:
        """获取最优学习时间建议"""
        patterns = await DynamicTransferService.get_temporal_patterns(db, user_id, days=30)
        best_hour = patterns["best_hour"]
        wk = patterns["weekday_vs_weekend"]

        schedule = {
            "recommended_time": f"{best_hour}:00" if best_hour is not None else "未知",
            "recommended_duration": patterns["optimal_session_minutes"],
            "weekday_tip": "工作日学习效率更高" if (wk["weekday_accuracy"] or 0) > (wk["weekend_accuracy"] or 0) else "周末学习效率更高",
            "patterns": patterns,
        }
        return schedule

    @staticmethod
    def _temporal_insight(best_hour: Optional[int], optimal_minutes: int) -> str:
        if best_hour is not None:
            period = "上午" if best_hour < 12 else "下午" if best_hour < 18 else "晚上"
            return f"你在{period}{best_hour}点学习效率最高，建议每次学习{optimal_minutes}分钟"
        return f"建议每次学习{optimal_minutes}分钟"
