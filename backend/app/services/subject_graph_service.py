"""
Subject Graph Service - Phase 9 学科知识图谱与跨学科推荐
基于学科间关系图谱 + 学生知识状态，生成跨学科课程推荐
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc

from app.models.models import (
    SubjectRelation, Subject, KnowledgeNode,
    StudentKnowledgeState, CourseNode, Course,
    LearningProgress, CourseRecommendation,
)
from app.services.emotion_service import EmotionService


class SubjectGraphService:
    """学科知识图谱服务"""

    @staticmethod
    async def get_subject_graph(
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """获取完整学科知识图谱"""
        # 所有学科
        subj_result = await db.execute(select(Subject))
        subjects = subj_result.scalars().all()

        # 所有关系
        rel_result = await db.execute(
            select(SubjectRelation)
        )
        relations = rel_result.scalars().all()

        subj_map = {s.id: s.name for s in subjects}

        nodes = [
            {"id": s.id, "name": s.name, "description": s.description}
            for s in subjects
        ]
        edges = [
            {
                "id": r.id,
                "source": r.source_subject_id,
                "source_name": subj_map.get(r.source_subject_id, ""),
                "target": r.target_subject_id,
                "target_name": subj_map.get(r.target_subject_id, ""),
                "relation_type": r.relation_type,
                "weight": r.weight,
                "description": r.description,
                "shared_concepts": r.shared_concepts or [],
            }
            for r in relations
        ]

        return {"nodes": nodes, "edges": edges}

    @staticmethod
    async def get_cross_disciplinary_recommendations(
        db: AsyncSession,
        user_id: int,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        跨学科课程推荐：
        1. 找到学生正在学的学科（有知识状态的）
        2. 通过 subject_relations 找到关联学科
        3. 在关联学科中推荐课程（优先前置知识薄弱 + 扩展应用）
        4. 结合 course_recommendations 中的 cross_discipline 关联
        5. 情感调整推荐优先级
        """
        # 1. 学生当前学科 + 知识状态
        ks_result = await db.execute(
            select(StudentKnowledgeState).where(
                StudentKnowledgeState.user_id == user_id
            )
        )
        states = list(ks_result.scalars().all())
        if not states:
            return {"recommendations": [], "graph_context": {}, "reason": "暂无学习数据"}

        # 知识节点 → 学科映射
        node_ids = [s.knowledge_node_id for s in states]
        kn_result = await db.execute(
            select(KnowledgeNode).where(KnowledgeNode.id.in_(node_ids))
        )
        kn_map = {kn.id: kn for kn in kn_result.scalars().all()}

        # 学科掌握度汇总
        subject_mastery = {}
        for s in states:
            kn = kn_map.get(s.knowledge_node_id)
            if not kn:
                continue
            sid = kn.subject_id
            if sid not in subject_mastery:
                subject_mastery[sid] = {"total": 0, "sum": 0.0, "weak": 0}
            subject_mastery[sid]["total"] += 1
            subject_mastery[sid]["sum"] += s.mastery
            if s.mastery < 0.4:
                subject_mastery[sid]["weak"] += 1

        active_subject_ids = list(subject_mastery.keys())

        # 2. 查找关联学科
        rel_result = await db.execute(
            select(SubjectRelation).where(
                or_(
                    SubjectRelation.source_subject_id.in_(active_subject_ids),
                    SubjectRelation.target_subject_id.in_(active_subject_ids),
                )
            )
        )
        relations = list(rel_result.scalars().all())

        # 3. 情感状态
        emotion = await EmotionService.get_current_emotion(db, user_id)
        emo_type = emotion["emotion_type"] if emotion else "focus"

        # 4. 已学课程
        prog_result = await db.execute(
            select(LearningProgress.node_id).where(
                LearningProgress.user_id == user_id
            )
        )
        learned_cn_ids = {r[0] for r in prog_result.all() if r[0]}

        learned_course_result = await db.execute(
            select(CourseNode.course_id).where(
                CourseNode.id.in_(learned_cn_ids)
            )
        ) if learned_cn_ids else None
        learned_course_ids = {r[0] for r in learned_course_result.all()} if learned_course_result else set()

        # 5. 构建推荐
        recommendations = []
        seen_courses = set()

        # 学科名称映射
        all_subj_ids = set(active_subject_ids)
        for r in relations:
            all_subj_ids.add(r.source_subject_id)
            all_subj_ids.add(r.target_subject_id)
        subj_result = await db.execute(
            select(Subject).where(Subject.id.in_(all_subj_ids))
        )
        subj_map = {s.id: s for s in subj_result.scalars().all()}

        # 策略A: 基于学科关系推荐
        for rel in sorted(relations, key=lambda r: r.weight, reverse=True):
            # 找到关联的"另一个"学科
            if rel.source_subject_id in active_subject_ids:
                related_sid = rel.target_subject_id
                from_sid = rel.source_subject_id
            else:
                related_sid = rel.source_subject_id
                from_sid = rel.target_subject_id

            related_subj = subj_map.get(related_sid)
            from_subj = subj_map.get(from_sid)
            if not related_subj:
                continue

            # 在关联学科中找课程（删除无用查询）

            # 通过知识节点找关联学科的课程
            kn_course_result = await db.execute(
                select(KnowledgeNode).where(
                    KnowledgeNode.subject_id == related_sid
                )
            )
            related_kns = kn_course_result.scalars().all()
            related_cn_ids = [kn.course_node_id for kn in related_kns if kn.course_node_id]

            if related_cn_ids:
                cn_course_result = await db.execute(
                    select(CourseNode).where(CourseNode.id.in_(related_cn_ids))
                )
                for cn in cn_course_result.scalars().all():
                    cid = cn.course_id
                    if cid in seen_courses or cid in learned_course_ids:
                        continue

                    c_result = await db.execute(
                        select(Course).where(Course.id == cid)
                    )
                    course = c_result.scalar_one_or_none()
                    if not course or course.is_published != 1:
                        continue

                    # 优先级：prerequisite > extension > cross_discipline > complementary
                    priority_map = {"prerequisite": 1, "extension": 2, "cross_discipline": 3, "complementary": 4}
                    priority = priority_map.get(rel.relation_type, 5)

                    # 情感调整
                    if emo_type == "frustration" and rel.relation_type == "extension":
                        priority += 2  # 挫败时降低扩展推荐优先级
                    elif emo_type == "boredom" and rel.relation_type == "extension":
                        priority -= 1  # 无聊时提升扩展推荐

                    reason = SubjectGraphService._build_reason(
                        rel, from_subj, related_subj
                    )

                    recommendations.append({
                        "course_id": cid,
                        "course_name": course.name,
                        "from_subject": from_subj.name if from_subj else "",
                        "to_subject": related_subj.name,
                        "relation_type": rel.relation_type,
                        "weight": rel.weight,
                        "shared_concepts": rel.shared_concepts or [],
                        "reason": reason,
                        "priority": priority,
                    })
                    seen_courses.add(cid)

                    if len(recommendations) >= limit:
                        break

            if len(recommendations) >= limit:
                break

        # 策略B: 补充 course_recommendations 中的 cross_discipline
        if len(recommendations) < limit:
            cr_result = await db.execute(
                select(CourseRecommendation).where(
                    CourseRecommendation.relation_type == "cross_discipline"
                ).order_by(desc(CourseRecommendation.weight)).limit(limit)
            )
            for cr in cr_result.scalars().all():
                if cr.target_course_id in seen_courses or cr.target_course_id in learned_course_ids:
                    continue
                c_result = await db.execute(
                    select(Course).where(Course.id == cr.target_course_id)
                )
                course = c_result.scalar_one_or_none()
                if not course or course.status != "published":
                    continue

                recommendations.append({
                    "course_id": course.id,
                    "course_name": course.name,
                    "from_subject": "",
                    "to_subject": "",
                    "relation_type": "cross_discipline",
                    "weight": cr.weight,
                    "shared_concepts": [],
                    "reason": cr.reason or "跨学科关联课程",
                    "priority": 3,
                })
                seen_courses.add(course.id)
                if len(recommendations) >= limit:
                    break

        recommendations.sort(key=lambda x: (x["priority"], -x["weight"]))

        # 图谱上下文
        graph_context = {
            "active_subjects": [
                {
                    "id": sid,
                    "name": subj_map[sid].name if sid in subj_map else "",
                    "avg_mastery": round(v["sum"] / v["total"], 3) if v["total"] else 0,
                    "weak_nodes": v["weak"],
                }
                for sid, v in subject_mastery.items()
            ],
            "relation_count": len(relations),
            "emotion": emo_type,
        }

        return {
            "recommendations": recommendations[:limit],
            "graph_context": graph_context,
        }

    @staticmethod
    def _build_reason(rel, from_subj, to_subj) -> str:
        """构建推荐理由"""
        from_name = from_subj.name if from_subj else "当前学科"
        to_name = to_subj.name if to_subj else "关联学科"
        concepts = rel.shared_concepts or []
        concept_str = "、".join(concepts[:3]) if concepts else ""

        type_reasons = {
            "prerequisite": f"{from_name}是{to_name}的前置基础" + (f"，共享概念：{concept_str}" if concept_str else ""),
            "extension": f"{to_name}是{from_name}的扩展应用" + (f"，涉及：{concept_str}" if concept_str else ""),
            "cross_discipline": f"{from_name}与{to_name}存在跨学科关联" + (f"，交叉领域：{concept_str}" if concept_str else ""),
            "complementary": f"{to_name}与{from_name}互为补充" + (f"，相关概念：{concept_str}" if concept_str else ""),
        }
        return rel.description or type_reasons.get(rel.relation_type, "跨学科推荐")

    @staticmethod
    async def add_relation(
        db: AsyncSession,
        data: Dict[str, Any],
    ) -> SubjectRelation:
        """添加学科关系"""
        rel = SubjectRelation(
            source_subject_id=data["source_subject_id"],
            target_subject_id=data["target_subject_id"],
            relation_type=data["relation_type"],
            weight=data.get("weight", 1.0),
            description=data.get("description"),
            shared_concepts=data.get("shared_concepts", []),
        )
        db.add(rel)
        await db.flush()
        return rel

    @staticmethod
    async def get_subject_relations(
        db: AsyncSession,
        subject_id: int,
    ) -> List[Dict[str, Any]]:
        """获取指定学科的所有关系"""
        result = await db.execute(
            select(SubjectRelation).where(
                or_(
                    SubjectRelation.source_subject_id == subject_id,
                    SubjectRelation.target_subject_id == subject_id,
                )
            )
        )
        relations = result.scalars().all()

        # 学科名称
        subj_ids = set()
        for r in relations:
            subj_ids.add(r.source_subject_id)
            subj_ids.add(r.target_subject_id)
        subj_result = await db.execute(
            select(Subject).where(Subject.id.in_(subj_ids))
        ) if subj_ids else None
        subj_map = {s.id: s.name for s in subj_result.scalars().all()} if subj_result else {}

        return [
            {
                "id": r.id,
                "source_subject_id": r.source_subject_id,
                "source_name": subj_map.get(r.source_subject_id, ""),
                "target_subject_id": r.target_subject_id,
                "target_name": subj_map.get(r.target_subject_id, ""),
                "relation_type": r.relation_type,
                "weight": r.weight,
                "description": r.description,
                "shared_concepts": r.shared_concepts or [],
                "direction": "outgoing" if r.source_subject_id == subject_id else "incoming",
            }
            for r in relations
        ]
