"""
Learning Report & Metacognitive Service - Phase 5
学习报告生成 + 元认知提示系统
"""

import random
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func, Integer, cast, case

from app.models.models import (
    StudentKnowledgeState, KnowledgeNode, StudentEvent,
    StudentEmotionState, ReviewSchedule, LearningReport,
    MetacognitiveLog, Subject, StudentLearningPath,
)


# 元认知提示库
METACOGNITIVE_PROMPTS = {
    "after_practice_set": [
        "刚才哪道题让你想得最久？你觉得是为什么？",
        "回顾一下，你觉得自己在哪个步骤最容易出错？",
        "如果要教别人这个知识点，你会怎么解释？",
    ],
    "after_hard_correct": [
        "这道题你是怎么想到解法的？",
        "你用了什么策略来解决这个问题？",
        "这个方法还能用在什么地方？",
    ],
    "after_error_recovery": [
        "之前答错的那道题，你现在知道错在哪里了吗？",
        "下次遇到类似的题目，你会注意什么？",
        "这个错误帮你发现了什么？",
    ],
    "session_start": [
        "今天想重点学习什么？",
        "上次学习后，你还记得哪些内容？",
        "给自己设个小目标：今天想掌握哪个知识点？",
    ],
    "session_end": [
        "今天学到的最重要的一个概念是什么？",
        "有什么地方还不太确定，想下次再看看的？",
        "用一句话总结今天的收获。",
    ],
}


class LearningReportService:

    @staticmethod
    async def generate_session_report(
        db: AsyncSession,
        user_id: int,
        minutes_back: int = 60,
    ) -> Dict[str, Any]:
        """生成单次学习会话报告"""
        now = datetime.now(timezone.utc)
        since = now - timedelta(minutes=minutes_back)

        # 获取时间窗口内的事件
        events_result = await db.execute(
            select(StudentEvent, KnowledgeNode.name.label("node_name"))
            .outerjoin(KnowledgeNode, StudentEvent.knowledge_node_id == KnowledgeNode.id)
            .where(
                and_(
                    StudentEvent.user_id == user_id,
                    StudentEvent.created_at >= since,
                )
            )
            .order_by(StudentEvent.created_at)
        )
        rows = events_result.all()

        if not rows:
            return {"message": "该时间段内无学习记录", "events_count": 0}

        # 统计
        answers = [r for r in rows if r.StudentEvent.event_type == "answer"]
        correct = sum(1 for r in answers if r.StudentEvent.is_correct == 1)
        total_answers = len(answers)
        accuracy = correct / total_answers if total_answers else 0

        hints = sum(1 for r in rows if r.StudentEvent.event_type == "hint")
        skips = sum(1 for r in rows if r.StudentEvent.event_type == "skip")

        # 涉及的知识节点
        node_ids = set()
        for r in rows:
            if r.StudentEvent.knowledge_node_id is not None:
                node_ids.add(r.StudentEvent.knowledge_node_id)

        # 获取知识状态变化
        states = []
        if node_ids:
            states_result = await db.execute(
                select(StudentKnowledgeState, KnowledgeNode.name.label("node_name"))
                .join(KnowledgeNode, StudentKnowledgeState.knowledge_node_id == KnowledgeNode.id)
                .where(
                    and_(
                        StudentKnowledgeState.user_id == user_id,
                        StudentKnowledgeState.knowledge_node_id.in_(node_ids),
                    )
                )
            )
            states = states_result.all()

        knowledge_updates = []
        for s in states:
            knowledge_updates.append({
                "node_name": s.node_name,
                "mastery": round(s.StudentKnowledgeState.mastery, 3),
                "practice_count": s.StudentKnowledgeState.practice_count,
                "streak": s.StudentKnowledgeState.streak,
            })
        weak_nodes = [
            s.node_name for s in sorted(states, key=lambda x: x.StudentKnowledgeState.mastery)
            if s.StudentKnowledgeState.mastery < 0.5
        ][:3]

        # 待复习数
        due_result = await db.execute(
            select(func.count()).where(
                and_(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.next_review_at <= now + timedelta(days=1),
                )
            )
        )
        upcoming_reviews = due_result.scalar() or 0

        # 最近情感
        emo_result = await db.execute(
            select(StudentEmotionState)
            .where(
                and_(
                    StudentEmotionState.user_id == user_id,
                    StudentEmotionState.created_at >= since,
                )
            )
            .order_by(desc(StudentEmotionState.created_at))
            .limit(1)
        )
        emo = emo_result.scalar_one_or_none()

        # 会话情感分布
        emotion_stats_result = await db.execute(
            select(
                StudentEmotionState.emotion_type,
                func.count().label("cnt"),
                func.avg(StudentEmotionState.intensity).label("avg_intensity"),
            )
            .where(
                and_(
                    StudentEmotionState.user_id == user_id,
                    StudentEmotionState.created_at >= since,
                )
            )
            .group_by(StudentEmotionState.emotion_type)
            .order_by(func.count().desc())
        )
        emotion_rows = emotion_stats_result.all()
        emotion_distribution = {
            r.emotion_type: int(r.cnt) for r in emotion_rows
        }
        dominant_emotion = (
            emotion_rows[0].emotion_type if emotion_rows else (emo.emotion_type if emo else "unknown")
        )
        avg_emotion_intensity = (
            round(float(emotion_rows[0].avg_intensity or 0.0), 3) if emotion_rows else 0.0
        )

        # 学习路径任务完成情况
        path_result = await db.execute(
            select(StudentLearningPath.path_items, StudentLearningPath.total_nodes, StudentLearningPath.completed_nodes)
            .where(
                and_(
                    StudentLearningPath.user_id == user_id,
                    StudentLearningPath.created_at >= since,
                )
            )
        )
        total_tasks = 0
        completed_tasks = 0
        for path_items, total_nodes, completed_nodes in path_result.all():
            items = path_items or []
            if items:
                total_tasks += len(items)
                completed_tasks += sum(1 for item in items if item.get("completed"))
            else:
                total_tasks += int(total_nodes or 0)
                completed_tasks += int(completed_nodes or 0)
        task_completion_rate = (completed_tasks / total_tasks) if total_tasks else 0.0

        # 鼓励语
        encouragement = LearningReportService._encouragement(accuracy, total_answers)
        personalized_recommendations = LearningReportService._build_personalized_recommendations(
            accuracy=accuracy,
            dominant_emotion=dominant_emotion,
            weak_nodes=weak_nodes,
            review_compliance=None,
            task_completion_rate=task_completion_rate,
            hints=hints,
            skips=skips,
        )

        summary = {
            "duration_minutes": minutes_back,
            "total_events": len(rows),
            "answers": total_answers,
            "correct": correct,
            "accuracy": round(accuracy, 3),
            "hints_used": hints,
            "skips": skips,
            "nodes_practiced": len(node_ids),
            "knowledge_updates": knowledge_updates,
            "upcoming_reviews_24h": upcoming_reviews,
            "emotion": emo.emotion_type if emo else "unknown",
            "emotion_summary": {
                "dominant_emotion": dominant_emotion,
                "distribution": emotion_distribution,
                "avg_intensity": avg_emotion_intensity,
            },
            "task_completion": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": round(task_completion_rate, 3),
            },
            "personalized_recommendations": personalized_recommendations,
            "encouragement": encouragement,
        }

        # 保存报告
        report = LearningReport(
            user_id=user_id,
            report_type="session",
            period_start=since,
            period_end=now,
            summary=summary,
        )
        db.add(report)
        await db.flush()

        summary["report_id"] = report.id
        return summary

    @staticmethod
    async def generate_growth_report(
        db: AsyncSession,
        user_id: int,
        period: str = "weekly",
    ) -> Dict[str, Any]:
        """生成成长报告（weekly/monthly）"""
        now = datetime.now(timezone.utc)
        if period == "monthly":
            since = now - timedelta(days=30)
        else:
            since = now - timedelta(days=7)

        # 事件统计
        events_result = await db.execute(
            select(
                func.count().label("total"),
                func.count(case((StudentEvent.is_correct == 1, 1))).label("correct"),
            )
            .where(
                and_(
                    StudentEvent.user_id == user_id,
                    StudentEvent.event_type == "answer",
                    StudentEvent.created_at >= since,
                )
            )
        )
        row = events_result.one()
        total_answers = row.total or 0
        total_correct = row.correct or 0

        # 知识覆盖
        all_states = await db.execute(
            select(StudentKnowledgeState)
            .where(StudentKnowledgeState.user_id == user_id)
        )
        states = all_states.scalars().all()

        mastered = sum(1 for s in states if s.mastery >= 0.8)
        learning = sum(1 for s in states if 0.3 <= s.mastery < 0.8)
        weak = sum(1 for s in states if s.mastery < 0.3)

        # 复习完成率
        review_total = await db.execute(
            select(func.count()).where(ReviewSchedule.user_id == user_id)
        )
        review_done = await db.execute(
            select(func.count()).where(
                and_(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.last_review_at >= since,
                )
            )
        )
        r_total = review_total.scalar() or 0
        r_done = review_done.scalar() or 0
        review_compliance = r_done / r_total if r_total else 0

        # 平均 mastery
        avg_mastery = sum(s.mastery for s in states) / len(states) if states else 0

        # 路径任务完成统计
        path_result = await db.execute(
            select(StudentLearningPath.path_items, StudentLearningPath.total_nodes, StudentLearningPath.completed_nodes)
            .where(
                and_(
                    StudentLearningPath.user_id == user_id,
                    StudentLearningPath.created_at >= since,
                )
            )
        )
        total_tasks = 0
        completed_tasks = 0
        for path_items, total_nodes, completed_nodes in path_result.all():
            items = path_items or []
            if items:
                total_tasks += len(items)
                completed_tasks += sum(1 for item in items if item.get("completed"))
            else:
                total_tasks += int(total_nodes or 0)
                completed_tasks += int(completed_nodes or 0)
        task_completion_rate = (completed_tasks / total_tasks) if total_tasks else 0.0

        # 情感趋势
        emotion_stats_result = await db.execute(
            select(
                StudentEmotionState.emotion_type,
                func.count().label("cnt"),
                func.avg(StudentEmotionState.intensity).label("avg_intensity"),
            )
            .where(
                and_(
                    StudentEmotionState.user_id == user_id,
                    StudentEmotionState.created_at >= since,
                )
            )
            .group_by(StudentEmotionState.emotion_type)
            .order_by(func.count().desc())
        )
        emotion_rows = emotion_stats_result.all()
        dominant_emotion = emotion_rows[0].emotion_type if emotion_rows else "unknown"
        emotion_distribution = {r.emotion_type: int(r.cnt) for r in emotion_rows}

        weak_nodes = []
        if states:
            weak_nodes = [
                str(s.knowledge_node_id) for s in sorted(states, key=lambda x: x.mastery) if s.mastery < 0.5
            ][:3]
        personalized_recommendations = LearningReportService._build_personalized_recommendations(
            accuracy=(total_correct / total_answers) if total_answers else 0.0,
            dominant_emotion=dominant_emotion,
            weak_nodes=weak_nodes,
            review_compliance=review_compliance,
            task_completion_rate=task_completion_rate,
        )

        summary = {
            "period": period,
            "period_start": since.isoformat(),
            "period_end": now.isoformat(),
            "total_answers": total_answers,
            "accuracy": round(total_correct / total_answers, 3) if total_answers else 0,
            "knowledge_coverage": {
                "total_nodes": len(states),
                "mastered": mastered,
                "learning": learning,
                "weak": weak,
            },
            "avg_mastery": round(avg_mastery, 3),
            "review_compliance": round(review_compliance, 3),
            "reviews_completed": r_done,
            "reviews_total": r_total,
            "emotion_summary": {
                "dominant_emotion": dominant_emotion,
                "distribution": emotion_distribution,
            },
            "task_completion": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": round(task_completion_rate, 3),
            },
            "personalized_recommendations": personalized_recommendations,
        }

        report = LearningReport(
            user_id=user_id,
            report_type=period,
            period_start=since,
            period_end=now,
            summary=summary,
        )
        db.add(report)
        await db.flush()

        summary["report_id"] = report.id
        return summary

    @staticmethod
    async def get_report_history(
        db: AsyncSession,
        user_id: int,
        report_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """获取报告历史"""
        query = select(LearningReport).where(LearningReport.user_id == user_id)
        if report_type:
            query = query.where(LearningReport.report_type == report_type)
        query = query.order_by(desc(LearningReport.created_at)).limit(limit)

        result = await db.execute(query)
        reports = result.scalars().all()
        return [
            {
                "id": r.id,
                "report_type": r.report_type,
                "period_start": r.period_start,
                "period_end": r.period_end,
                "summary": r.summary,
                "created_at": r.created_at,
            }
            for r in reports
        ]

    @staticmethod
    def _encouragement(accuracy: float, total: int) -> str:
        if total == 0:
            return "开始学习吧，每一步都是进步。"
        if accuracy >= 0.9:
            return "太棒了，正确率很高，继续保持！"
        if accuracy >= 0.7:
            return "做得不错，再巩固一下薄弱的地方就更好了。"
        if accuracy >= 0.5:
            return "有进步的空间，多练习几次会越来越熟练。"
        return "别灰心，每次错误都是学习的机会。"

    @staticmethod
    def _build_personalized_recommendations(
        accuracy: float,
        dominant_emotion: str,
        weak_nodes: Optional[List[str]] = None,
        review_compliance: Optional[float] = None,
        task_completion_rate: Optional[float] = None,
        hints: int = 0,
        skips: int = 0,
    ) -> List[str]:
        recs: List[str] = []
        weak_nodes = weak_nodes or []

        if dominant_emotion in {"frustration", "anxiety"}:
            recs.append("先做低难度复习与短时任务，优先恢复学习节奏。")
        elif dominant_emotion == "boredom":
            recs.append("可提高任务挑战度，穿插模拟器或综合题保持投入。")

        if accuracy < 0.6:
            recs.append("正确率偏低，建议先聚焦基础概念再做综合练习。")
        elif accuracy >= 0.85:
            recs.append("正确率较高，建议加入挑战任务提升上限。")

        if task_completion_rate is not None and task_completion_rate < 0.6:
            recs.append("任务完成率偏低，建议将单次路径时长控制在 15-25 分钟。")

        if review_compliance is not None and review_compliance < 0.5:
            recs.append("复习完成率偏低，建议开启每日固定复习时段。")

        if hints >= 5 or skips >= 3:
            recs.append("提示/跳过使用偏多，建议先做分步诊断练习再做整题。")

        if weak_nodes:
            recs.append(f"优先补强薄弱知识点：{', '.join(weak_nodes[:3])}。")

        if not recs:
            recs.append("当前学习状态稳定，保持节奏并按计划推进即可。")
        return recs


class MetacognitiveService:

    @staticmethod
    async def get_prompt(
        db: AsyncSession,
        user_id: int,
        trigger: str,
        knowledge_node_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """获取元认知提示"""
        candidates = METACOGNITIVE_PROMPTS.get(trigger, [])
        if not candidates:
            return {"prompt": None, "trigger": trigger}

        # 避免重复：查最近5条同trigger的提示
        recent_result = await db.execute(
            select(MetacognitiveLog.prompt_text)
            .where(
                and_(
                    MetacognitiveLog.user_id == user_id,
                    MetacognitiveLog.trigger == trigger,
                )
            )
            .order_by(desc(MetacognitiveLog.created_at))
            .limit(5)
        )
        recent_texts = {r[0] for r in recent_result.all()}

        available = [p for p in candidates if p not in recent_texts]
        if not available:
            available = candidates

        prompt_text = random.choice(available)

        # 记录
        log = MetacognitiveLog(
            user_id=user_id,
            trigger=trigger,
            prompt_text=prompt_text,
            knowledge_node_id=knowledge_node_id,
        )
        db.add(log)
        await db.flush()

        return {
            "log_id": log.id,
            "trigger": trigger,
            "prompt": prompt_text,
        }

    @staticmethod
    async def record_response(
        db: AsyncSession,
        log_id: int,
        user_id: int,
        response_text: str,
    ) -> Optional[Dict[str, Any]]:
        """记录学生对元认知提示的回答"""
        result = await db.execute(
            select(MetacognitiveLog).where(
                and_(
                    MetacognitiveLog.id == log_id,
                    MetacognitiveLog.user_id == user_id,
                )
            )
        )
        log = result.scalar_one_or_none()
        if not log:
            return None

        log.student_response = response_text
        await db.flush()

        return {
            "log_id": log.id,
            "trigger": log.trigger,
            "prompt": log.prompt_text,
            "response": response_text,
        }
