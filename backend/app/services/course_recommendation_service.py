"""
Course Recommendation Service - Phase 11
BKT驱动的课程推荐 + 课程关系图谱 + 进度聚合
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, update

from app.models.models import (
    Course, CourseNode, CourseRelation, StudentCourseProgress,
    UserCourse, LearningProgress, StudentKnowledgeState,
    KnowledgeNode, SubjectRelation, Subject,
)
from app.services.emotion_service import EmotionService


class CourseRecommendationService:
    """课程推荐与进度管理服务"""

    @staticmethod
    async def recommend_courses(
        db: AsyncSession,
        user_id: int,
        limit: int = 10,
        subject_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        BKT驱动的个性化课程推荐:
        1. 基于薄弱知识点 → 关联课程
        2. 基于课程关系图谱 → 后续课程
        3. 基于学科关系 → 跨学科课程
        4. 情感调整优先级
        """
        # 已学课程
        uc_result = await db.execute(
            select(UserCourse.course_id).where(
                UserCourse.user_id == user_id
            )
        )
        enrolled_ids = {r[0] for r in uc_result.all()}

        # BKT 知识状态
        ks_q = select(StudentKnowledgeState).where(
            StudentKnowledgeState.user_id == user_id
        )
        ks_result = await db.execute(ks_q)
        states = list(ks_result.scalars().all())

        # 节点→学科映射
        node_ids = [s.knowledge_node_id for s in states]
        kn_map = {}
        if node_ids:
            kn_result = await db.execute(
                select(KnowledgeNode).where(KnowledgeNode.id.in_(node_ids))
            )
            kn_map = {kn.id: kn for kn in kn_result.scalars().all()}

        weak_nodes = [s for s in states if s.mastery < 0.4]
        avg_mastery = sum(s.mastery for s in states) / len(states) if states else 0

        # 情感
        emotion = await EmotionService.get_current_emotion(db, user_id)
        emo_type = emotion["emotion_type"] if emotion else "focus"

        recommendations = []
        seen = set()

        # 策略1: 薄弱知识点关联课程
        weak_cn_ids = []
        for s in weak_nodes[:10]:
            kn = kn_map.get(s.knowledge_node_id)
            if kn and kn.course_node_id:
                weak_cn_ids.append(kn.course_node_id)

        if weak_cn_ids:
            cn_result = await db.execute(
                select(CourseNode.course_id).where(
                    CourseNode.id.in_(weak_cn_ids)
                ).distinct()
            )
            for r in cn_result.all():
                cid = r[0]
                if cid in enrolled_ids or cid in seen:
                    continue
                course = await CourseRecommendationService._get_course(db, cid)
                if not course:
                    continue
                recommendations.append({
                    "course_id": cid,
                    "course_name": course.name,
                    "difficulty": str(course.difficulty.value) if course.difficulty else "",
                    "reason": "包含你的薄弱知识点，建议复习巩固",
                    "strategy": "weakness",
                    "priority": 1,
                    "tags": course.tags or [],
                })
                seen.add(cid)

        # 策略2: 课程关系图谱（已完成课程的后续）
        if enrolled_ids:
            cr_result = await db.execute(
                select(CourseRelation).where(
                    CourseRelation.source_course_id.in_(enrolled_ids)
                ).order_by(desc(CourseRelation.weight))
            )
            for cr in cr_result.scalars().all():
                tid = cr.target_course_id
                if tid in enrolled_ids or tid in seen:
                    continue
                course = await CourseRecommendationService._get_course(db, tid)
                if not course:
                    continue

                priority_map = {"prerequisite": 2, "advanced": 3, "parallel": 4, "supplementary": 5}
                priority = priority_map.get(cr.relation_type, 5)

                if emo_type == "frustration" and cr.relation_type == "advanced":
                    priority += 2
                elif emo_type == "boredom" and cr.relation_type == "advanced":
                    priority -= 1

                recommendations.append({
                    "course_id": tid,
                    "course_name": course.name,
                    "difficulty": str(course.difficulty.value) if course.difficulty else "",
                    "reason": cr.description or f"基于课程关系推荐（{cr.relation_type}）",
                    "strategy": "relation",
                    "relation_type": cr.relation_type,
                    "priority": priority,
                    "tags": course.tags or [],
                })
                seen.add(tid)

        # 策略3: 未学的已发布课程（兜底）
        if len(recommendations) < limit:
            exclude = enrolled_ids | seen
            fallback_q = select(Course).where(
                Course.is_published == 1
            ).order_by(desc(Course.created_at)).limit(limit)
            fb_result = await db.execute(fallback_q)
            for course in fb_result.scalars().all():
                if course.id in exclude:
                    continue
                recommendations.append({
                    "course_id": course.id,
                    "course_name": course.name,
                    "difficulty": str(course.difficulty.value) if course.difficulty else "",
                    "reason": "探索新课程",
                    "strategy": "discover",
                    "priority": 6,
                    "tags": course.tags or [],
                })
                seen.add(course.id)
                if len(recommendations) >= limit:
                    break

        recommendations.sort(key=lambda x: x["priority"])

        return {
            "recommendations": recommendations[:limit],
            "context": {
                "enrolled_count": len(enrolled_ids),
                "avg_mastery": round(avg_mastery, 3),
                "weak_node_count": len(weak_nodes),
                "emotion": emo_type,
            },
        }

    @staticmethod
    async def _get_course(db, cid):
        r = await db.execute(select(Course).where(Course.id == cid))
        c = r.scalar_one_or_none()
        if c and c.is_published == 1:
            return c
        return None

    @staticmethod
    async def generate_learning_path(
        db: AsyncSession,
        user_id: int,
        course_id: Optional[int] = None,
        session_minutes: int = 30,
    ) -> Dict[str, Any]:
        """
        基于BKT+课程关系生成个性化学习路径:
        - 指定课程: 按节点mastery排序，薄弱优先
        - 未指定: 从推荐课程中选最优
        """
        if not course_id:
            rec = await CourseRecommendationService.recommend_courses(db, user_id, limit=1)
            if rec["recommendations"]:
                course_id = rec["recommendations"][0]["course_id"]
            else:
                return {"path": [], "reason": "暂无可推荐课程"}

        # 课程信息
        c_result = await db.execute(select(Course).where(Course.id == course_id))
        course = c_result.scalar_one_or_none()
        if not course:
            return {"path": [], "reason": "课程不存在"}

        # 课程节点
        cn_result = await db.execute(
            select(CourseNode).where(
                CourseNode.course_id == course_id
            ).order_by(CourseNode.sequence)
        )
        nodes = list(cn_result.scalars().all())

        # 节点进度
        node_ids = [n.id for n in nodes]
        prog_result = await db.execute(
            select(LearningProgress).where(and_(
                LearningProgress.user_id == user_id,
                LearningProgress.node_id.in_(node_ids),
            ))
        ) if node_ids else None
        prog_map = {}
        if prog_result:
            for p in prog_result.scalars().all():
                prog_map[p.node_id] = p

        # 知识节点mastery
        kn_result = await db.execute(
            select(KnowledgeNode).where(
                KnowledgeNode.course_node_id.in_(node_ids)
            )
        ) if node_ids else None
        kn_cn_map = {}
        kn_ids = []
        if kn_result:
            for kn in kn_result.scalars().all():
                kn_cn_map[kn.course_node_id] = kn
                kn_ids.append(kn.id)

        mastery_map = {}
        if kn_ids:
            ms_result = await db.execute(
                select(StudentKnowledgeState).where(and_(
                    StudentKnowledgeState.user_id == user_id,
                    StudentKnowledgeState.knowledge_node_id.in_(kn_ids),
                ))
            )
            for s in ms_result.scalars().all():
                mastery_map[s.knowledge_node_id] = s.mastery

        # 情感
        emotion = await EmotionService.get_current_emotion(db, user_id)
        emo_type = emotion["emotion_type"] if emotion else "focus"

        # 构建路径
        path_items = []
        used_minutes = 0

        # 按mastery升序排列（薄弱优先）
        scored_nodes = []
        for n in nodes:
            prog = prog_map.get(n.id)
            completion = prog.completion_percentage if prog else 0
            if completion >= 100:
                continue

            kn = kn_cn_map.get(n.id)
            mastery = mastery_map.get(kn.id, 0.0) if kn else 0.0
            scored_nodes.append((n, mastery, completion, kn))

        scored_nodes.sort(key=lambda x: x[1])

        for n, mastery, completion, kn in scored_nodes:
            if used_minutes >= session_minutes:
                break

            if mastery < 0.3:
                activity = "learn"
                minutes = 8
            elif mastery < 0.6:
                activity = "practice"
                minutes = 6
            else:
                activity = "review"
                minutes = 4

            if emo_type == "frustration":
                minutes = max(3, minutes - 2)

            if used_minutes + minutes > session_minutes + 2:
                continue

            path_items.append({
                "order": len(path_items) + 1,
                "course_node_id": n.id,
                "node_title": n.title,
                "node_type": str(n.type.value) if n.type else "",
                "activity_type": activity,
                "estimated_minutes": minutes,
                "current_mastery": round(mastery, 3),
                "completion_pct": round(completion, 1),
                "knowledge_node_id": kn.id if kn else None,
            })
            used_minutes += minutes

        return {
            "course_id": course_id,
            "course_name": course.name,
            "total_items": len(path_items),
            "total_minutes": used_minutes,
            "emotion": emo_type,
            "path": path_items,
        }

    @staticmethod
    async def sync_course_progress(
        db: AsyncSession,
        user_id: int,
        course_id: int,
    ) -> Dict[str, Any]:
        """同步课程级进度（从节点级聚合）"""
        # 课程节点
        cn_result = await db.execute(
            select(CourseNode.id).where(CourseNode.course_id == course_id)
        )
        node_ids = [r[0] for r in cn_result.all()]
        total_nodes = len(node_ids)

        if not total_nodes:
            return {"message": "课程无节点"}

        # 节点进度
        prog_result = await db.execute(
            select(LearningProgress).where(and_(
                LearningProgress.user_id == user_id,
                LearningProgress.node_id.in_(node_ids),
            ))
        )
        progs = list(prog_result.scalars().all())
        completed = sum(1 for p in progs if p.completion_percentage >= 100)
        total_time = sum(p.time_spent_seconds or 0 for p in progs)
        completion_pct = completed / total_nodes * 100 if total_nodes else 0

        # BKT mastery
        kn_result = await db.execute(
            select(KnowledgeNode).where(
                KnowledgeNode.course_node_id.in_(node_ids)
            )
        )
        kn_ids = [kn.id for kn in kn_result.scalars().all()]
        avg_mastery = 0.0
        if kn_ids:
            ms_result = await db.execute(
                select(func.avg(StudentKnowledgeState.mastery)).where(and_(
                    StudentKnowledgeState.user_id == user_id,
                    StudentKnowledgeState.knowledge_node_id.in_(kn_ids),
                ))
            )
            avg_mastery = ms_result.scalar() or 0.0

        status = "completed" if completion_pct >= 100 else "in_progress"

        # upsert
        existing = await db.execute(
            select(StudentCourseProgress).where(and_(
                StudentCourseProgress.user_id == user_id,
                StudentCourseProgress.course_id == course_id,
            ))
        )
        scp = existing.scalar_one_or_none()

        if scp:
            scp.total_nodes = total_nodes
            scp.completed_nodes = completed
            scp.completion_pct = round(completion_pct, 1)
            scp.avg_mastery = round(avg_mastery, 4)
            scp.total_time_seconds = total_time
            scp.status = status
            scp.last_activity_at = datetime.now(timezone.utc)
            scp.updated_at = datetime.now(timezone.utc)
        else:
            scp = StudentCourseProgress(
                user_id=user_id,
                course_id=course_id,
                total_nodes=total_nodes,
                completed_nodes=completed,
                completion_pct=round(completion_pct, 1),
                avg_mastery=round(avg_mastery, 4),
                total_time_seconds=total_time,
                status=status,
                last_activity_at=datetime.now(timezone.utc),
            )
            db.add(scp)

        await db.flush()

        return {
            "course_id": course_id,
            "total_nodes": total_nodes,
            "completed_nodes": completed,
            "completion_pct": round(completion_pct, 1),
            "avg_mastery": round(avg_mastery, 4),
            "total_time_seconds": total_time,
            "status": status,
        }

    @staticmethod
    async def get_course_progress(
        db: AsyncSession,
        user_id: int,
    ) -> List[Dict]:
        """获取学生所有课程进度"""
        result = await db.execute(
            select(StudentCourseProgress).where(
                StudentCourseProgress.user_id == user_id
            ).order_by(desc(StudentCourseProgress.last_activity_at))
        )
        progs = result.scalars().all()

        cids = [p.course_id for p in progs]
        c_result = await db.execute(
            select(Course).where(Course.id.in_(cids))
        ) if cids else None
        c_map = {c.id: c.name for c in c_result.scalars().all()} if c_result else {}

        return [
            {
                "course_id": p.course_id,
                "course_name": c_map.get(p.course_id, ""),
                "total_nodes": p.total_nodes,
                "completed_nodes": p.completed_nodes,
                "completion_pct": p.completion_pct,
                "avg_mastery": p.avg_mastery,
                "total_time_seconds": p.total_time_seconds,
                "status": p.status,
                "last_activity_at": p.last_activity_at,
            }
            for p in progs
        ]

    @staticmethod
    async def add_course_relation(
        db: AsyncSession, data: Dict[str, Any],
    ) -> CourseRelation:
        rel = CourseRelation(
            source_course_id=data["source_course_id"],
            target_course_id=data["target_course_id"],
            relation_type=data["relation_type"],
            weight=data.get("weight", 1.0),
            description=data.get("description"),
        )
        db.add(rel)
        await db.flush()
        return rel

    @staticmethod
    async def get_course_relations(
        db: AsyncSession, course_id: int,
    ) -> List[Dict]:
        result = await db.execute(
            select(CourseRelation).where(or_(
                CourseRelation.source_course_id == course_id,
                CourseRelation.target_course_id == course_id,
            ))
        )
        rels = result.scalars().all()

        cids = set()
        for r in rels:
            cids.add(r.source_course_id)
            cids.add(r.target_course_id)
        c_result = await db.execute(
            select(Course).where(Course.id.in_(cids))
        ) if cids else None
        c_map = {c.id: c.name for c in c_result.scalars().all()} if c_result else {}

        return [
            {
                "id": r.id,
                "source_course_id": r.source_course_id,
                "source_name": c_map.get(r.source_course_id, ""),
                "target_course_id": r.target_course_id,
                "target_name": c_map.get(r.target_course_id, ""),
                "relation_type": r.relation_type,
                "weight": r.weight,
                "description": r.description,
                "direction": "outgoing" if r.source_course_id == course_id else "incoming",
            }
            for r in rels
        ]
