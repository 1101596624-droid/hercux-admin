"""
Multi-Task Service - Phase 8 多任务学习与多目标优化
统一编排 BKT/情感/复习/路径/推荐/评估，基于多目标加权优化生成任务计划
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
import math

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.models.models import (
    StudentMultiTaskPlan, StudentKnowledgeState,
    StudentEmotionState, StudentEvent, StudentMisconception,
    KnowledgeNode, ReviewSchedule, StudentAssessment,
)
from app.services.emotion_service import EmotionService


# 任务类型常量
TASK_LEARN = "learn"          # 学习新知识
TASK_REVIEW = "review"        # 间隔复习
TASK_PRACTICE = "practice"    # 巩固练习
TASK_REMEDIATE = "remediate"  # 误解纠正
TASK_CHALLENGE = "challenge"  # 挑战提升
TASK_RECOVER = "recover"      # 情感恢复

# 每种任务的默认时长（分钟）
TASK_DURATION = {
    TASK_LEARN: 8, TASK_REVIEW: 4, TASK_PRACTICE: 6,
    TASK_REMEDIATE: 7, TASK_CHALLENGE: 10, TASK_RECOVER: 3,
}


class MultiTaskService:
    """多任务学习与多目标优化服务"""

    @staticmethod
    async def generate_plan(
        db: AsyncSession,
        user_id: int,
        session_minutes: int = 30,
        subject_id: Optional[int] = None,
        objective_weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        多任务计划生成：收集全量信号 → 候选任务评分 → 多目标优化选择 → 时间分配
        """
        weights = objective_weights or {
            "mastery": 0.35, "retention": 0.25,
            "emotion": 0.2, "efficiency": 0.2,
        }

        # 1. 收集学生全量状态快照
        snapshot = await MultiTaskService._collect_snapshot(
            db, user_id, subject_id
        )

        # 2. 生成候选任务池
        candidates = MultiTaskService._generate_candidates(snapshot)

        # 3. 多目标评分
        scored = MultiTaskService._score_candidates(candidates, weights, snapshot)

        # 4. 贪心选择 + 时间分配
        selected = MultiTaskService._select_tasks(scored, session_minutes, snapshot)

        # 5. 活动穿插防疲劳
        selected = MultiTaskService._interleave(selected)

        # 6. 优化摘要
        summary = MultiTaskService._build_summary(selected, weights, snapshot)

        # 7. 标记旧计划过期
        old_plans = await db.execute(
            select(StudentMultiTaskPlan).where(and_(
                StudentMultiTaskPlan.user_id == user_id,
                StudentMultiTaskPlan.status == "active",
            ))
        )
        for p in old_plans.scalars().all():
            p.status = "expired"

        # 8. 持久化
        plan = StudentMultiTaskPlan(
            user_id=user_id,
            objective_weights=weights,
            student_snapshot=snapshot,
            tasks=[t for t in selected],
            optimization_summary=summary,
            total_tasks=len(selected),
            session_minutes=session_minutes,
        )
        db.add(plan)
        await db.flush()

        return {
            "plan_id": plan.id,
            "session_minutes": session_minutes,
            "objective_weights": weights,
            "tasks": selected,
            "optimization_summary": summary,
            "student_snapshot": snapshot,
        }

    @staticmethod
    async def _collect_snapshot(
        db: AsyncSession, user_id: int, subject_id: Optional[int],
    ) -> Dict[str, Any]:
        """收集学生全量信号快照"""
        # 知识状态
        ks_q = select(StudentKnowledgeState).where(
            StudentKnowledgeState.user_id == user_id
        )
        if subject_id:
            ks_q = ks_q.join(KnowledgeNode).where(
                KnowledgeNode.subject_id == subject_id
            )
        ks_result = await db.execute(ks_q)
        states = list(ks_result.scalars().all())

        weak_nodes = [s for s in states if s.mastery < 0.4]
        medium_nodes = [s for s in states if 0.4 <= s.mastery < 0.7]
        strong_nodes = [s for s in states if s.mastery >= 0.7]

        avg_mastery = sum(s.mastery for s in states) / len(states) if states else 0.0
        avg_stability = sum(s.stability for s in states) / len(states) if states else 0.5

        # 情感
        emotion = await EmotionService.get_current_emotion(db, user_id)
        emotion_type = emotion["emotion_type"] if emotion else "focus"
        emotion_intensity = emotion["intensity"] if emotion else 0.3

        # 到期复习
        due_result = await db.execute(
            select(ReviewSchedule).where(and_(
                ReviewSchedule.user_id == user_id,
                ReviewSchedule.next_review_at <= func.now(),
            ))
        )
        due_reviews = list(due_result.scalars().all())

        # 未解决误解
        misc_result = await db.execute(
            select(StudentMisconception).where(and_(
                StudentMisconception.user_id == user_id,
                StudentMisconception.resolved == 0,
            ))
        )
        misconceptions = list(misc_result.scalars().all())

        # 24h活跃度
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        ev_result = await db.execute(
            select(func.count()).select_from(StudentEvent).where(and_(
                StudentEvent.user_id == user_id,
                StudentEvent.created_at >= cutoff,
            ))
        )
        recent_events = ev_result.scalar() or 0

        return {
            "avg_mastery": round(avg_mastery, 4),
            "avg_stability": round(avg_stability, 4),
            "weak_count": len(weak_nodes),
            "medium_count": len(medium_nodes),
            "strong_count": len(strong_nodes),
            "total_nodes": len(states),
            "emotion_type": emotion_type,
            "emotion_intensity": round(emotion_intensity, 3),
            "due_review_count": len(due_reviews),
            "misconception_count": len(misconceptions),
            "recent_events_24h": recent_events,
            "_weak_nodes": [{"id": s.knowledge_node_id, "mastery": s.mastery, "stability": s.stability} for s in weak_nodes],
            "_medium_nodes": [{"id": s.knowledge_node_id, "mastery": s.mastery, "stability": s.stability} for s in medium_nodes],
            "_due_reviews": [{"id": r.knowledge_node_id, "stability": r.stability} for r in due_reviews],
            "_misconceptions": [{"id": m.knowledge_node_id, "text": m.misconception} for m in misconceptions],
        }

    @staticmethod
    def _generate_candidates(snapshot: Dict) -> List[Dict]:
        """基于学生状态生成候选任务池"""
        candidates = []

        # 薄弱节点 → 学习任务
        for node in snapshot.get("_weak_nodes", []):
            candidates.append({
                "type": TASK_LEARN,
                "knowledge_node_id": node["id"],
                "mastery": node["mastery"],
                "stability": node["stability"],
                "minutes": TASK_DURATION[TASK_LEARN],
                "reason": f"掌握度{node['mastery']:.0%}，需要学习巩固",
            })

        # 中等节点 → 练习任务
        for node in snapshot.get("_medium_nodes", []):
            candidates.append({
                "type": TASK_PRACTICE,
                "knowledge_node_id": node["id"],
                "mastery": node["mastery"],
                "stability": node["stability"],
                "minutes": TASK_DURATION[TASK_PRACTICE],
                "reason": f"掌握度{node['mastery']:.0%}，练习巩固",
            })

        # 到期复习 → 复习任务
        for rev in snapshot.get("_due_reviews", []):
            candidates.append({
                "type": TASK_REVIEW,
                "knowledge_node_id": rev["id"],
                "stability": rev.get("stability", 0.5),
                "mastery": 0.5,
                "minutes": TASK_DURATION[TASK_REVIEW],
                "reason": "记忆衰减，需要复习",
            })

        # 误解 → 纠正任务
        for misc in snapshot.get("_misconceptions", []):
            candidates.append({
                "type": TASK_REMEDIATE,
                "knowledge_node_id": misc["id"],
                "mastery": 0.3,
                "stability": 0.3,
                "minutes": TASK_DURATION[TASK_REMEDIATE],
                "reason": f"存在误解：{misc['text'][:30]}",
            })

        # 高掌握度 → 挑战任务（取前3个）
        if snapshot.get("strong_count", 0) > 0 and snapshot.get("avg_mastery", 0) > 0.6:
            candidates.append({
                "type": TASK_CHALLENGE,
                "knowledge_node_id": None,
                "mastery": snapshot["avg_mastery"],
                "stability": snapshot["avg_stability"],
                "minutes": TASK_DURATION[TASK_CHALLENGE],
                "reason": "整体掌握良好，挑战进阶内容",
            })

        # 情感恢复任务（挫败或焦虑时）
        emo = snapshot.get("emotion_type", "focus")
        intensity = snapshot.get("emotion_intensity", 0.3)
        if emo in ("frustration", "anxiety") and intensity > 0.4:
            candidates.append({
                "type": TASK_RECOVER,
                "knowledge_node_id": None,
                "mastery": 0.8,
                "stability": 0.8,
                "minutes": TASK_DURATION[TASK_RECOVER],
                "reason": f"检测到{emo}情绪，先做简单任务恢复状态",
            })

        return candidates

    @staticmethod
    def _score_candidates(
        candidates: List[Dict],
        weights: Dict[str, float],
        snapshot: Dict,
    ) -> List[Dict]:
        """多目标加权评分：每个候选任务在4个维度上打分"""
        emo_type = snapshot.get("emotion_type", "focus")
        emo_intensity = snapshot.get("emotion_intensity", 0.3)

        for c in candidates:
            t = c["type"]
            m = c.get("mastery", 0.5)
            s = c.get("stability", 0.5)

            # 维度1: 掌握度提升潜力（mastery越低，提升空间越大）
            if t == TASK_LEARN:
                score_mastery = 1.0 - m
            elif t == TASK_PRACTICE:
                score_mastery = max(0, 0.7 - m)
            elif t == TASK_REMEDIATE:
                score_mastery = 0.9  # 纠正误解对掌握度帮助大
            elif t == TASK_CHALLENGE:
                score_mastery = 0.3  # 已掌握，提升空间小
            elif t == TASK_REVIEW:
                score_mastery = 0.4
            else:  # recover
                score_mastery = 0.1

            # 维度2: 记忆保持（stability越低或到期复习，收益越大）
            if t == TASK_REVIEW:
                score_retention = 1.0 - s * 0.5
            elif t in (TASK_LEARN, TASK_PRACTICE):
                score_retention = 0.5 * (1.0 - s)
            elif t == TASK_REMEDIATE:
                score_retention = 0.6
            else:
                score_retention = 0.2

            # 维度3: 情感稳定（挫败/焦虑时，recover和简单任务得分高）
            if t == TASK_RECOVER:
                score_emotion = 1.0 if emo_type in ("frustration", "anxiety") else 0.1
            elif t == TASK_CHALLENGE:
                # 挫败时挑战得分低，兴奋时得分高
                if emo_type == "frustration":
                    score_emotion = 0.1
                elif emo_type == "excitement":
                    score_emotion = 0.9
                else:
                    score_emotion = 0.5
            elif t == TASK_LEARN and emo_type == "boredom":
                score_emotion = 0.8  # 无聊时学新东西
            else:
                score_emotion = 0.5

            # 维度4: 时间效率（分钟越少、收益越高 → 效率越高）
            minutes = c.get("minutes", 5)
            avg_score = (score_mastery + score_retention + score_emotion) / 3
            score_efficiency = avg_score / max(minutes, 1) * 5  # 归一化

            # 加权总分
            total = (
                weights.get("mastery", 0.35) * score_mastery
                + weights.get("retention", 0.25) * score_retention
                + weights.get("emotion", 0.2) * score_emotion
                + weights.get("efficiency", 0.2) * min(score_efficiency, 1.0)
            )

            c["scores"] = {
                "mastery": round(score_mastery, 3),
                "retention": round(score_retention, 3),
                "emotion": round(score_emotion, 3),
                "efficiency": round(min(score_efficiency, 1.0), 3),
            }
            c["total_score"] = round(total, 4)

        candidates.sort(key=lambda x: x["total_score"], reverse=True)
        return candidates

    @staticmethod
    def _select_tasks(
        scored: List[Dict], session_minutes: int, snapshot: Dict,
    ) -> List[Dict]:
        """贪心选择：按总分降序填充时间预算，去重同节点"""
        selected = []
        used_minutes = 0
        seen_nodes = set()

        # 情感修正：挫败/焦虑时缩减总量80%
        emo = snapshot.get("emotion_type", "focus")
        intensity = snapshot.get("emotion_intensity", 0.3)
        if emo in ("frustration", "anxiety") and intensity > 0.5:
            session_minutes = int(session_minutes * 0.8)

        for c in scored:
            if used_minutes >= session_minutes:
                break
            nid = c.get("knowledge_node_id")
            if nid and nid in seen_nodes:
                continue
            mins = c.get("minutes", 5)
            if used_minutes + mins > session_minutes + 2:  # 允许2分钟溢出
                continue

            task = {
                "order": len(selected) + 1,
                "type": c["type"],
                "knowledge_node_id": nid,
                "estimated_minutes": mins,
                "reason": c.get("reason", ""),
                "total_score": c["total_score"],
                "scores": c["scores"],
                "completed": False,
            }
            selected.append(task)
            used_minutes += mins
            if nid:
                seen_nodes.add(nid)

        return selected

    @staticmethod
    def _interleave(tasks: List[Dict]) -> List[Dict]:
        """活动穿插：避免连续3个以上相同类型"""
        if len(tasks) <= 2:
            return tasks
        result = [tasks[0]]
        for i in range(1, len(tasks)):
            if (len(result) >= 2
                and result[-1]["type"] == tasks[i]["type"]
                and result[-2]["type"] == tasks[i]["type"]):
                # 找下一个不同类型的交换
                for j in range(i + 1, len(tasks)):
                    if tasks[j]["type"] != tasks[i]["type"]:
                        tasks[i], tasks[j] = tasks[j], tasks[i]
                        break
            result.append(tasks[i])
        # 重新编号
        for idx, t in enumerate(result):
            t["order"] = idx + 1
        return result

    @staticmethod
    def _build_summary(
        tasks: List[Dict], weights: Dict, snapshot: Dict,
    ) -> Dict[str, Any]:
        """构建优化摘要"""
        type_counts = {}
        total_minutes = 0
        for t in tasks:
            tp = t["type"]
            type_counts[tp] = type_counts.get(tp, 0) + 1
            total_minutes += t.get("estimated_minutes", 0)

        avg_score = sum(t["total_score"] for t in tasks) / len(tasks) if tasks else 0

        return {
            "total_tasks": len(tasks),
            "total_minutes": total_minutes,
            "task_distribution": type_counts,
            "avg_optimization_score": round(avg_score, 4),
            "dominant_objective": max(weights, key=weights.get) if weights else "mastery",
            "emotion_adjusted": snapshot.get("emotion_type") in ("frustration", "anxiety"),
        }

    @staticmethod
    async def get_multi_objective_feedback(
        db: AsyncSession,
        user_id: int,
        plan_id: Optional[int] = None,
        subject_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        多目标反馈：基于当前状态 vs 计划目标，评估各维度达成情况并给出调整建议
        """
        # 获取最新计划
        if plan_id:
            plan_result = await db.execute(
                select(StudentMultiTaskPlan).where(
                    StudentMultiTaskPlan.id == plan_id
                )
            )
        else:
            plan_result = await db.execute(
                select(StudentMultiTaskPlan).where(
                    StudentMultiTaskPlan.user_id == user_id
                ).order_by(desc(StudentMultiTaskPlan.created_at)).limit(1)
            )
        plan = plan_result.scalar_one_or_none()

        # 收集当前状态
        current = await MultiTaskService._collect_snapshot(db, user_id, subject_id)

        # 对比分析
        feedback_items = []
        adjustments = []

        if plan and plan.student_snapshot:
            prev = plan.student_snapshot
            # 掌握度变化
            mastery_delta = current["avg_mastery"] - prev.get("avg_mastery", 0)
            if mastery_delta > 0.02:
                feedback_items.append(f"掌握度提升了{mastery_delta:.1%}，学习有效果！")
            elif mastery_delta < -0.02:
                feedback_items.append(f"掌握度下降了{abs(mastery_delta):.1%}，建议增加复习。")
                adjustments.append({"objective": "mastery", "action": "increase_review", "reason": "掌握度下降"})

            # 误解变化
            misc_delta = current["misconception_count"] - prev.get("misconception_count", 0)
            if misc_delta > 0:
                feedback_items.append(f"新增{misc_delta}个误解，建议优先纠正。")
                adjustments.append({"objective": "mastery", "action": "add_remediation", "reason": "新增误解"})
            elif misc_delta < 0:
                feedback_items.append(f"已纠正{abs(misc_delta)}个误解，继续保持！")

            # 情感变化
            prev_emo = prev.get("emotion_type", "focus")
            curr_emo = current["emotion_type"]
            if prev_emo in ("focus", "excitement") and curr_emo in ("frustration", "anxiety"):
                feedback_items.append("情绪状态有所下降，建议降低难度或休息。")
                adjustments.append({"objective": "emotion", "action": "reduce_difficulty", "reason": "情绪恶化"})
            elif prev_emo in ("frustration", "anxiety") and curr_emo in ("focus", "excitement"):
                feedback_items.append("情绪已恢复，可以恢复正常学习节奏。")

            # 复习积压
            if current["due_review_count"] > prev.get("due_review_count", 0) + 3:
                feedback_items.append(f"复习积压增加到{current['due_review_count']}个，建议优先处理。")
                adjustments.append({"objective": "retention", "action": "prioritize_review", "reason": "复习积压"})
        else:
            feedback_items.append("暂无历史计划对比，建议先生成一个多任务计划。")

        # 目标达成度评估
        objective_scores = {
            "mastery": min(current["avg_mastery"] / 0.8, 1.0),
            "retention": min(current["avg_stability"] / 0.7, 1.0),
            "emotion": 1.0 if current["emotion_type"] in ("focus", "excitement") else 0.5,
            "efficiency": min(current["recent_events_24h"] / 10, 1.0),
        }

        # 权重调整建议
        suggested_weights = MultiTaskService._suggest_weights(current, objective_scores)

        return {
            "current_snapshot": {k: v for k, v in current.items() if not k.startswith("_")},
            "objective_scores": objective_scores,
            "feedback": " ".join(feedback_items) if feedback_items else "学习状态良好，继续保持！",
            "adjustments": adjustments,
            "suggested_weights": suggested_weights,
            "plan_id": plan.id if plan else None,
        }

    @staticmethod
    def _suggest_weights(
        snapshot: Dict, scores: Dict,
    ) -> Dict[str, float]:
        """基于当前短板动态建议目标权重"""
        # 找最弱维度，增加其权重
        min_obj = min(scores, key=scores.get)
        weights = {"mastery": 0.35, "retention": 0.25, "emotion": 0.2, "efficiency": 0.2}
        # 短板维度 +0.1，其他等比缩减
        boost = 0.1
        weights[min_obj] = weights[min_obj] + boost
        remaining = 1.0 - weights[min_obj]
        others = {k: v for k, v in weights.items() if k != min_obj}
        total_others = sum(others.values())
        for k in others:
            weights[k] = round(others[k] / total_others * remaining, 3)
        weights[min_obj] = round(weights[min_obj], 3)
        return weights

    @staticmethod
    async def get_plan_history(
        db: AsyncSession, user_id: int, limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """获取多任务计划历史"""
        result = await db.execute(
            select(StudentMultiTaskPlan).where(
                StudentMultiTaskPlan.user_id == user_id
            ).order_by(desc(StudentMultiTaskPlan.created_at)).limit(limit)
        )
        plans = result.scalars().all()
        return [
            {
                "id": p.id,
                "status": p.status,
                "session_minutes": p.session_minutes,
                "total_tasks": p.total_tasks,
                "completed_tasks": p.completed_tasks,
                "objective_weights": p.objective_weights,
                "optimization_summary": p.optimization_summary,
                "created_at": p.created_at,
                "completed_at": p.completed_at,
            }
            for p in plans
        ]
