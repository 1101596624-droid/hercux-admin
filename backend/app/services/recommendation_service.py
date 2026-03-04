"""
Recommendation Service - Phase 6 多模态推荐系统
基于学习路径、薄弱点、情感状态推荐：小课堂内容、做题家题目、课程
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, or_, insert

from app.models.models import (
    Course, CourseNode, KnowledgeNode, StudentKnowledgeState,
    StudentEmotionState, StudentEvent, StudentMisconception,
    ReviewSchedule, CourseRecommendation, LearningProgress,
    RecommendedLesson, RecommendedGrinder,
    StudentGoal, LearningHabit,
)
from app.services.emotion_service import EmotionService


class RecommendationService:

    @staticmethod
    async def get_recommended_content(
        db: AsyncSession,
        user_id: int,
        limit: int = 10,
        persist: bool = True,
    ) -> Dict[str, Any]:
        """
        获取个性化推荐内容
        返回三类推荐：小课堂(lectures)、做题家题目(grinder)、课程(courses)
        """
        # 1. 收集学生状态数据
        ctx = await RecommendationService._gather_student_context(db, user_id)

        # 2. 生成三类推荐
        lectures = await RecommendationService._recommend_lectures(db, user_id, ctx, limit=4)
        grinder = await RecommendationService._recommend_grinder(db, user_id, ctx, limit=4)
        courses = await RecommendationService._recommend_courses(db, user_id, ctx, limit=4)

        # 3. 可选持久化推荐记录到数据库（高并发场景可由调用方降频）
        if persist:
            await RecommendationService._persist_recommendations(db, user_id, ctx, lectures, grinder)

        return {
            "lectures": lectures,
            "grinder": grinder,
            "courses": courses,
            "student_context": {
                "emotion": ctx["emotion_type"],
                "weak_node_count": len(ctx["weak_nodes"]),
                "avg_mastery": ctx["avg_mastery"],
            },
        }

    @staticmethod
    async def _gather_student_context(
        db: AsyncSession, user_id: int
    ) -> Dict[str, Any]:
        """收集学生状态：薄弱点、情感、掌握度、复习到期等"""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=3)

        # 平均掌握度（聚合查询，避免全量加载）
        avg_result = await db.execute(
            select(func.avg(StudentKnowledgeState.mastery)).where(
                StudentKnowledgeState.user_id == user_id
            )
        )
        avg_mastery = float(avg_result.scalar() or 0.0)

        # 薄弱知识点 (mastery < 0.5)
        weak_result = await db.execute(
            select(StudentKnowledgeState)
            .where(
                and_(
                    StudentKnowledgeState.user_id == user_id,
                    StudentKnowledgeState.mastery < 0.5,
                )
            )
            .order_by(StudentKnowledgeState.mastery.asc())
            .limit(50)
        )
        weak_nodes = list(weak_result.scalars().all())

        # 遗忘中的知识点 (mastery 0.5~0.7 且超过3天未练习)
        forgetting_result = await db.execute(
            select(StudentKnowledgeState)
            .where(
                and_(
                    StudentKnowledgeState.user_id == user_id,
                    StudentKnowledgeState.mastery >= 0.5,
                    StudentKnowledgeState.mastery < 0.7,
                    StudentKnowledgeState.last_practice_at.isnot(None),
                    StudentKnowledgeState.last_practice_at < cutoff,
                )
            )
            .order_by(StudentKnowledgeState.last_practice_at.asc())
            .limit(50)
        )
        forgetting_nodes = list(forgetting_result.scalars().all())

        # 巩固区间节点 (0.4~0.7) 用于做题家推荐
        consolidation_result = await db.execute(
            select(StudentKnowledgeState)
            .where(
                and_(
                    StudentKnowledgeState.user_id == user_id,
                    StudentKnowledgeState.mastery >= 0.4,
                    StudentKnowledgeState.mastery < 0.7,
                )
            )
            .order_by(StudentKnowledgeState.mastery.asc(), StudentKnowledgeState.stability.asc())
            .limit(50)
        )
        consolidation_nodes = list(consolidation_result.scalars().all())

        # 情感状态
        emotion = await EmotionService.get_current_emotion(db, user_id)
        emotion_type = emotion["emotion_type"] if emotion else "focus"
        emotion_intensity = emotion["intensity"] if emotion else 0.3

        # 到期复习
        due_result = await db.execute(
            select(ReviewSchedule)
            .where(
                and_(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.next_review_at <= func.now(),
                )
            )
            .order_by(ReviewSchedule.next_review_at.asc())
            .limit(10)
        )
        due_reviews = list(due_result.scalars().all())

        # 已知误解
        misc_result = await db.execute(
            select(StudentMisconception)
            .where(
                and_(
                    StudentMisconception.user_id == user_id,
                    StudentMisconception.resolved == 0,
                )
            )
            .order_by(
                desc(StudentMisconception.last_seen_at),
                desc(StudentMisconception.frequency),
            )
            .limit(10)
        )
        misconceptions = list(misc_result.scalars().all())

        # Phase 16: 活跃目标
        goal_result = await db.execute(
            select(StudentGoal).where(and_(
                StudentGoal.user_id == user_id,
                StudentGoal.status == "active",
            ))
        )
        active_goals = list(goal_result.scalars().all())

        # Phase 16: 习惯一致性
        habit_result = await db.execute(
            select(LearningHabit).where(
                LearningHabit.user_id == user_id,
            ).order_by(LearningHabit.date.desc()).limit(14)
        )
        recent_habits = list(habit_result.scalars().all())
        consistency_score = len(recent_habits) / 14.0 if recent_habits else 0.0

        return {
            "weak_nodes": weak_nodes,
            "forgetting_nodes": forgetting_nodes,
            "consolidation_nodes": consolidation_nodes,
            "avg_mastery": round(avg_mastery, 3),
            "emotion_type": emotion_type,
            "emotion_intensity": emotion_intensity,
            "due_reviews": due_reviews,
            "misconceptions": misconceptions,
            "active_goals": active_goals,
            "consistency_score": consistency_score,
        }

    @staticmethod
    async def _recommend_lectures(
        db: AsyncSession, user_id: int, ctx: Dict[str, Any], limit: int = 4
    ) -> List[Dict[str, Any]]:
        """
        推荐小课堂内容
        策略：
        - 薄弱知识点 → 对应课程节点的讲解内容
        - 遗忘中的知识点 → 复习型讲解
        - 情感调整：挫败时推简单内容，无聊时推进阶内容
        """
        recommendations = []
        target_nodes = []

        # 优先级1: 薄弱知识点对应的课程内容
        for state in ctx["weak_nodes"][:limit]:
            target_nodes.append((state.knowledge_node_id, "weak", state.mastery))

        # 优先级2: 遗忘中的知识点
        remaining = limit - len(target_nodes)
        if remaining > 0:
            for state in ctx["forgetting_nodes"][:remaining]:
                target_nodes.append((state.knowledge_node_id, "forgetting", state.mastery))

        if not target_nodes:
            return recommendations

        # 查询知识节点 → 课程节点映射
        node_ids = [t[0] for t in target_nodes]
        kn_result = await db.execute(
            select(KnowledgeNode).where(KnowledgeNode.id.in_(node_ids))
        )
        kn_map = {kn.id: kn for kn in kn_result.scalars().all()}

        for node_id, reason_type, mastery in target_nodes:
            kn = kn_map.get(node_id)
            if not kn:
                continue

            # 情感调整难度偏好
            if ctx["emotion_type"] == "frustration":
                reason = f"巩固基础：{kn.name}（当前掌握度 {mastery:.0%}，先从简单内容开始）"
            elif ctx["emotion_type"] == "boredom":
                reason = f"进阶挑战：{kn.name}（尝试更深入的理解）"
            else:
                reason = f"{'薄弱补强' if reason_type == 'weak' else '防遗忘复习'}：{kn.name}（掌握度 {mastery:.0%}）"

            rec = {
                "knowledge_node_id": kn.id,
                "knowledge_node_name": kn.name,
                "course_node_id": kn.course_node_id,
                "type": "lecture",
                "reason": reason,
                "priority": 1 if reason_type == "weak" else 2,
                "mastery": round(mastery, 3),
            }
            recommendations.append(rec)

        recommendations.sort(key=lambda r: r["priority"])
        return recommendations[:limit]

    @staticmethod
    async def _recommend_grinder(
        db: AsyncSession, user_id: int, ctx: Dict[str, Any], limit: int = 4
    ) -> List[Dict[str, Any]]:
        """
        推荐做题家题目
        策略：
        - 有误解的知识点 → 针对性练习
        - 到期复习 → 复习型练习
        - 掌握度 0.4~0.7 → 巩固练习
        - 情感调整：挫败时降低难度，兴奋时提高难度
        """
        recommendations = []

        # 情感驱动难度调整（基于情感强度动态计算）
        intensity = ctx["emotion_intensity"]
        difficulty_bias = 0.0
        if ctx["emotion_type"] == "frustration":
            difficulty_bias = -0.1 - intensity * 0.3  # -0.1 ~ -0.4
        elif ctx["emotion_type"] == "anxiety":
            difficulty_bias = -0.05 - intensity * 0.2  # -0.05 ~ -0.25
        elif ctx["emotion_type"] == "boredom":
            difficulty_bias = 0.1 + intensity * 0.3  # 0.1 ~ 0.4
        elif ctx["emotion_type"] == "excitement":
            difficulty_bias = 0.05 + intensity * 0.2  # 0.05 ~ 0.25

        # 批量收集所有需要查询的 knowledge_node_id，避免 N+1
        all_node_ids = set()
        for misc in ctx["misconceptions"][:2]:
            all_node_ids.add(misc.knowledge_node_id)
        for rev in ctx["due_reviews"][:limit]:
            all_node_ids.add(rev.knowledge_node_id)
        consolidation = list(ctx.get("consolidation_nodes", []))
        consolidation.sort(key=lambda s: s.mastery)
        for state in consolidation[:limit]:
            all_node_ids.add(state.knowledge_node_id)

        # 单次批量查询所有 KnowledgeNode
        kn_map = {}
        if all_node_ids:
            kn_result = await db.execute(
                select(KnowledgeNode).where(KnowledgeNode.id.in_(all_node_ids))
            )
            kn_map = {kn.id: kn for kn in kn_result.scalars().all()}

        # 优先级1: 有误解的知识点 → 针对性练习
        for misc in ctx["misconceptions"][:2]:
            kn = kn_map.get(misc.knowledge_node_id)
            if kn:
                target_diff = max(0.1, min(1.0, kn.difficulty + difficulty_bias))
                recommendations.append({
                    "knowledge_node_id": kn.id,
                    "knowledge_node_name": kn.name,
                    "type": "grinder",
                    "reason": f"纠正误解：{misc.misconception[:50]}",
                    "priority": 1,
                    "suggested_difficulty": round(target_diff, 2),
                    "misconception_id": misc.id,
                })

        # 优先级2: 到期复习 → 复习型练习
        remaining = limit - len(recommendations)
        for rev in ctx["due_reviews"][:remaining]:
            kn = kn_map.get(rev.knowledge_node_id)
            if kn:
                recommendations.append({
                    "knowledge_node_id": kn.id,
                    "knowledge_node_name": kn.name,
                    "type": "grinder",
                    "reason": f"复习到期：间隔 {rev.interval_days:.0f} 天",
                    "priority": 2,
                    "suggested_difficulty": round(max(0.1, min(1.0, kn.difficulty + difficulty_bias)), 2),
                })

        # 优先级3: 掌握度 0.4~0.7 的知识点 → 巩固练习（稳定性加权：stability低的优先）
        remaining = limit - len(recommendations)
        if remaining > 0:
            # 按 mastery 升序 + stability 升序排序（不稳定的优先巩固）
            consolidation.sort(key=lambda s: (s.mastery, getattr(s, 'stability', 0.5) or 0.5))
            for state in consolidation[:remaining]:
                kn = kn_map.get(state.knowledge_node_id)
                if kn:
                    stability = getattr(state, 'stability', 0.5) or 0.5
                    # 稳定性低的知识点额外降低难度，避免挫败
                    stability_adj = -0.1 if stability < 0.3 else 0.0
                    recommendations.append({
                        "knowledge_node_id": kn.id,
                        "knowledge_node_name": kn.name,
                        "type": "grinder",
                        "reason": f"巩固练习：掌握度 {state.mastery:.0%}" + (f"（记忆不稳定）" if stability < 0.3 else ""),
                        "priority": 3,
                        "suggested_difficulty": round(max(0.1, min(1.0, state.mastery + difficulty_bias + stability_adj)), 2),
                    })

        # Phase 16: 目标对齐加权 + 习惯驱动难度调整
        goal_node_ids = set()
        goal_subject_ids = set()
        for g in ctx.get("active_goals", []):
            if g.node_id:
                goal_node_ids.add(g.node_id)
            if g.subject_id:
                goal_subject_ids.add(g.subject_id)

        consistency = ctx.get("consistency_score", 0.5)
        habit_diff_adj = 0.1 if consistency > 0.8 else (-0.15 if consistency < 0.3 else 0.0)

        for rec in recommendations:
            nid = rec.get("knowledge_node_id")
            # 目标对齐：关联节点优先级提升
            if nid in goal_node_ids:
                rec["priority"] = max(1, rec["priority"] - 1)
                rec["reason"] += "（目标关联）"
            # 习惯驱动难度微调
            if "suggested_difficulty" in rec:
                rec["suggested_difficulty"] = round(
                    max(0.1, min(1.0, rec["suggested_difficulty"] + habit_diff_adj)), 2
                )

        recommendations.sort(key=lambda r: r["priority"])
        return recommendations[:limit]

    @staticmethod
    async def _recommend_courses(
        db: AsyncSession, user_id: int, ctx: Dict[str, Any], limit: int = 4
    ) -> List[Dict[str, Any]]:
        """
        推荐课程
        策略：
        - course_recommendations 表中的关联课程
        - 学生薄弱知识点所属学科的未学课程
        - 已完成课程的进阶课程
        """
        recommendations = []

        # 获取学生已学课程ID
        progress_result = await db.execute(
            select(LearningProgress.node_id).where(
                LearningProgress.user_id == user_id
            ).distinct()
        )
        learned_node_ids = {r[0] for r in progress_result.all()}

        # 获取已学课程
        if learned_node_ids:
            cn_result = await db.execute(
                select(CourseNode.course_id).where(
                    CourseNode.id.in_(learned_node_ids)
                ).distinct()
            )
            learned_course_ids = {r[0] for r in cn_result.all()}
        else:
            learned_course_ids = set()

        # 策略1: course_recommendations 表关联推荐
        if learned_course_ids:
            rec_result = await db.execute(
                select(CourseRecommendation, Course).join(
                    Course, Course.id == CourseRecommendation.target_course_id
                ).where(
                    and_(
                        CourseRecommendation.source_course_id.in_(learned_course_ids),
                        ~CourseRecommendation.target_course_id.in_(learned_course_ids),
                        Course.is_published == 1,
                    )
                ).order_by(desc(CourseRecommendation.weight)).limit(limit)
            )
            for rec, course in rec_result.all():
                relation_labels = {
                    "prerequisite": "前置基础",
                    "complementary": "互补课程",
                    "advanced": "进阶课程",
                    "cross_discipline": "跨学科关联",
                }
                label = relation_labels.get(rec.relation_type, rec.relation_type)
                recommendations.append({
                    "course_id": course.id,
                    "course_name": course.name,
                    "type": "course",
                    "relation": rec.relation_type,
                    "reason": rec.reason or f"{label}推荐",
                    "priority": 1,
                    "weight": rec.weight,
                    "difficulty": course.difficulty.value if course.difficulty else "intermediate",
                    "tags": course.tags or [],
                })

        # 策略2: 薄弱知识点所属学科的未学课程
        remaining = limit - len(recommendations)
        if remaining > 0 and ctx["weak_nodes"]:
            weak_node_ids = [s.knowledge_node_id for s in ctx["weak_nodes"][:5]]
            kn_result = await db.execute(
                select(KnowledgeNode.course_node_id).where(
                    and_(
                        KnowledgeNode.id.in_(weak_node_ids),
                        KnowledgeNode.course_node_id.isnot(None),
                    )
                )
            )
            weak_course_node_ids = [r[0] for r in kn_result.all()]

            if weak_course_node_ids:
                cn_result = await db.execute(
                    select(CourseNode.course_id).where(
                        CourseNode.id.in_(weak_course_node_ids)
                    ).distinct()
                )
                weak_course_ids = {r[0] for r in cn_result.all()}
                new_course_ids = weak_course_ids - learned_course_ids
                if new_course_ids:
                    course_result = await db.execute(
                        select(Course).where(
                            and_(
                                Course.id.in_(new_course_ids),
                                Course.is_published == 1,
                            )
                        ).limit(remaining)
                    )
                    for course in course_result.scalars().all():
                        recommendations.append({
                            "course_id": course.id,
                            "course_name": course.name,
                            "type": "course",
                            "relation": "weak_area",
                            "reason": "薄弱领域补强",
                            "priority": 2,
                            "difficulty": course.difficulty.value if course.difficulty else "intermediate",
                            "tags": course.tags or [],
                        })

        # 策略3: 未学过的已发布课程（兜底）
        remaining = limit - len(recommendations)
        if remaining > 0:
            existing_ids = learned_course_ids | {r["course_id"] for r in recommendations if "course_id" in r}
            fallback_query = select(Course).where(Course.is_published == 1)
            if existing_ids:
                fallback_query = fallback_query.where(~Course.id.in_(existing_ids))
            fallback_query = fallback_query.order_by(desc(Course.created_at)).limit(remaining)

            fallback_result = await db.execute(fallback_query)
            for course in fallback_result.scalars().all():
                recommendations.append({
                    "course_id": course.id,
                    "course_name": course.name,
                    "type": "course",
                    "relation": "discover",
                    "reason": "探索新课程",
                    "priority": 3,
                    "difficulty": course.difficulty.value if course.difficulty else "intermediate",
                    "tags": course.tags or [],
                })

        recommendations.sort(key=lambda r: r["priority"])
        return recommendations[:limit]

    @staticmethod
    async def _persist_recommendations(
        db: AsyncSession,
        user_id: int,
        ctx: Dict[str, Any],
        lectures: List[Dict],
        grinder: List[Dict],
    ):
        """将推荐结果持久化到数据库"""
        lesson_rows = [
            {
                "user_id": user_id,
                "knowledge_node_id": lec["knowledge_node_id"],
                "course_node_id": lec.get("course_node_id"),
                "reason": lec["reason"],
                "priority": lec["priority"],
                "mastery_at_recommend": lec.get("mastery"),
                "emotion_at_recommend": ctx["emotion_type"],
            }
            for lec in lectures
        ]
        if lesson_rows:
            await db.execute(insert(RecommendedLesson), lesson_rows)

        grinder_rows = [
            {
                "user_id": user_id,
                "knowledge_node_id": gr["knowledge_node_id"],
                "reason": gr["reason"],
                "priority": gr["priority"],
                "suggested_difficulty": gr.get("suggested_difficulty", 0.5),
                "mastery_at_recommend": gr.get("mastery"),
                "emotion_at_recommend": ctx["emotion_type"],
                "misconception_id": gr.get("misconception_id"),
            }
            for gr in grinder
        ]
        if grinder_rows:
            await db.execute(insert(RecommendedGrinder), grinder_rows)
