"""
Cross-Disciplinary Service - Phase 10 跨学科推荐与知识推理
三大引擎：知识推荐 + 共享概念桥接 + 学习迁移预测
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import math

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc

from app.models.models import (
    ConceptBridge, SubjectRelation, Subject, KnowledgeNode,
    StudentKnowledgeState, CourseNode, Course,
    LearningProgress, StudentSubjectTransfer,
)
from app.services.emotion_service import EmotionService


class CrossDisciplinaryService:
    """跨学科推荐与知识推理服务"""

    # ── 引擎1: 知识推荐引擎 ──

    @staticmethod
    async def recommend_from_mastery(
        db: AsyncSession,
        user_id: int,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        基于学科A掌握度，推荐学科B内容
        逻辑：高掌握学科 → 通过 subject_relations → 推荐关联学科的薄弱/未学内容
        """
        # 学生全部知识状态
        ks_result = await db.execute(
            select(StudentKnowledgeState).where(
                StudentKnowledgeState.user_id == user_id
            )
        )
        states = list(ks_result.scalars().all())
        if not states:
            return {"recommendations": [], "reason": "暂无学习数据"}

        # 节点信息
        node_ids = [s.knowledge_node_id for s in states]
        kn_result = await db.execute(
            select(KnowledgeNode).where(KnowledgeNode.id.in_(node_ids))
        )
        kn_map = {kn.id: kn for kn in kn_result.scalars().all()}

        # 按学科汇总掌握度
        subj_stats = {}
        for s in states:
            kn = kn_map.get(s.knowledge_node_id)
            if not kn:
                continue
            sid = kn.subject_id
            if sid not in subj_stats:
                subj_stats[sid] = {"sum": 0, "count": 0, "nodes": []}
            subj_stats[sid]["sum"] += s.mastery
            subj_stats[sid]["count"] += 1
            subj_stats[sid]["nodes"].append(s)

        for sid in subj_stats:
            subj_stats[sid]["avg"] = subj_stats[sid]["sum"] / subj_stats[sid]["count"]

        # 找高掌握学科（avg > 0.5）的关联学科
        strong_sids = [sid for sid, v in subj_stats.items() if v["avg"] > 0.5]
        if not strong_sids:
            strong_sids = list(subj_stats.keys())

        rel_result = await db.execute(
            select(SubjectRelation).where(
                SubjectRelation.source_subject_id.in_(strong_sids)
            ).order_by(desc(SubjectRelation.weight))
        )
        relations = list(rel_result.scalars().all())

        # 学科名称
        all_sids = set(subj_stats.keys())
        for r in relations:
            all_sids.add(r.target_subject_id)
        subj_result = await db.execute(
            select(Subject).where(Subject.id.in_(all_sids))
        )
        subj_map = {s.id: s for s in subj_result.scalars().all()}

        # 情感
        emotion = await EmotionService.get_current_emotion(db, user_id)
        emo_type = emotion["emotion_type"] if emotion else "focus"

        # 构建推荐
        recommendations = []
        seen = set()

        for rel in relations:
            target_sid = rel.target_subject_id
            source_sid = rel.source_subject_id
            source_avg = subj_stats.get(source_sid, {}).get("avg", 0)
            target_subj = subj_map.get(target_sid)
            source_subj = subj_map.get(source_sid)
            if not target_subj:
                continue

            # Phase 16: 优先使用个性化迁移系数
            personal_result = await db.execute(
                select(StudentSubjectTransfer).where(and_(
                    StudentSubjectTransfer.user_id == user_id,
                    StudentSubjectTransfer.source_subject_id == source_sid,
                    StudentSubjectTransfer.target_subject_id == target_sid,
                ))
            )
            personal = personal_result.scalars().first()
            effective_coeff = personal.observed_transfer if (personal and personal.confidence > 0.3) else rel.transfer_coefficient

            # 目标学科的知识节点
            target_kn_result = await db.execute(
                select(KnowledgeNode).where(
                    KnowledgeNode.subject_id == target_sid
                )
            )
            target_kns = target_kn_result.scalars().all()

            # 学生在目标学科的状态
            target_state_map = {}
            if target_kns:
                t_ids = [kn.id for kn in target_kns]
                ts_result = await db.execute(
                    select(StudentKnowledgeState).where(and_(
                        StudentKnowledgeState.user_id == user_id,
                        StudentKnowledgeState.knowledge_node_id.in_(t_ids),
                    ))
                )
                for ts in ts_result.scalars().all():
                    target_state_map[ts.knowledge_node_id] = ts

            for kn in target_kns:
                if kn.id in seen:
                    continue
                state = target_state_map.get(kn.id)
                mastery = state.mastery if state else 0.0

                # 只推荐薄弱或未学的
                if mastery >= 0.7:
                    continue

                # 迁移预测分（Phase 16: 使用有效系数）
                predicted = source_avg * effective_coeff
                gap = max(0, 0.7 - mastery)

                # 优先级：gap越大越优先，迁移预测越高越优先
                score = gap * 0.6 + predicted * 0.2 + rel.weight * 0.2

                # 情感调整
                if emo_type == "frustration" and kn.difficulty > 0.6:
                    score *= 0.7
                elif emo_type == "boredom" and kn.difficulty < 0.4:
                    score *= 0.8

                recommendations.append({
                    "knowledge_node_id": kn.id,
                    "node_name": kn.name,
                    "node_code": kn.code,
                    "from_subject": source_subj.name if source_subj else "",
                    "to_subject": target_subj.name,
                    "relation_type": rel.relation_type,
                    "current_mastery": round(mastery, 3),
                    "predicted_transfer": round(predicted, 3),
                    "difficulty": kn.difficulty,
                    "score": round(score, 4),
                    "reason": CrossDisciplinaryService._mastery_reason(
                        source_subj, target_subj, rel, source_avg, mastery
                    ),
                })
                seen.add(kn.id)

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return {"recommendations": recommendations[:limit], "emotion": emo_type}

    @staticmethod
    def _mastery_reason(src, tgt, rel, src_avg, tgt_mastery):
        sn = src.name if src else "源学科"
        tn = tgt.name if tgt else "目标学科"
        if tgt_mastery == 0:
            return f"你在{sn}掌握度{src_avg:.0%}，可以开始学习{tn}的相关内容"
        return f"基于{sn}的{src_avg:.0%}掌握度，{tn}中此知识点({tgt_mastery:.0%})有提升空间"

    # ── 引擎2: 共享概念桥接引擎 ──

    @staticmethod
    async def recommend_by_concepts(
        db: AsyncSession,
        user_id: int,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        基于 concept_bridges 推荐：
        学生已掌握 source_node → 通过共享概念 → 推荐 target_node
        """
        # 学生已掌握的节点（mastery > 0.5）
        ks_result = await db.execute(
            select(StudentKnowledgeState).where(and_(
                StudentKnowledgeState.user_id == user_id,
                StudentKnowledgeState.mastery > 0.5,
            ))
        )
        mastered = {s.knowledge_node_id: s.mastery for s in ks_result.scalars().all()}
        if not mastered:
            return {"recommendations": [], "reason": "暂无已掌握的知识点"}

        # 查找概念桥接
        bridge_result = await db.execute(
            select(ConceptBridge).where(
                ConceptBridge.source_node_id.in_(list(mastered.keys()))
            ).order_by(desc(ConceptBridge.transfer_weight))
        )
        bridges = list(bridge_result.scalars().all())

        if not bridges:
            return {"recommendations": [], "reason": "暂无跨学科概念桥接"}

        # 目标节点信息
        target_ids = list({b.target_node_id for b in bridges})
        kn_result = await db.execute(
            select(KnowledgeNode).where(KnowledgeNode.id.in_(target_ids))
        )
        kn_map = {kn.id: kn for kn in kn_result.scalars().all()}

        # 目标节点的学生状态
        ts_result = await db.execute(
            select(StudentKnowledgeState).where(and_(
                StudentKnowledgeState.user_id == user_id,
                StudentKnowledgeState.knowledge_node_id.in_(target_ids),
            ))
        )
        target_states = {s.knowledge_node_id: s.mastery for s in ts_result.scalars().all()}

        # 源节点信息
        source_ids = list({b.source_node_id for b in bridges})
        src_kn_result = await db.execute(
            select(KnowledgeNode).where(KnowledgeNode.id.in_(source_ids))
        )
        src_kn_map = {kn.id: kn for kn in src_kn_result.scalars().all()}

        # 学科名称
        all_sids = set()
        for kn in list(kn_map.values()) + list(src_kn_map.values()):
            all_sids.add(kn.subject_id)
        subj_result = await db.execute(
            select(Subject).where(Subject.id.in_(all_sids))
        )
        subj_map = {s.id: s.name for s in subj_result.scalars().all()}

        recommendations = []
        seen = set()

        for b in bridges:
            tid = b.target_node_id
            if tid in seen:
                continue
            target_kn = kn_map.get(tid)
            source_kn = src_kn_map.get(b.source_node_id)
            if not target_kn:
                continue

            target_mastery = target_states.get(tid, 0.0)
            if target_mastery >= 0.7:
                continue

            source_mastery = mastered.get(b.source_node_id, 0.5)
            predicted = source_mastery * b.transfer_weight
            score = (0.7 - target_mastery) * 0.5 + predicted * 0.3 + b.transfer_weight * 0.2

            recommendations.append({
                "target_node_id": tid,
                "target_name": target_kn.name,
                "target_subject": subj_map.get(target_kn.subject_id, ""),
                "source_node_id": b.source_node_id,
                "source_name": source_kn.name if source_kn else "",
                "source_subject": subj_map.get(source_kn.subject_id, "") if source_kn else "",
                "concept": b.concept_name,
                "source_mastery": round(source_mastery, 3),
                "target_mastery": round(target_mastery, 3),
                "predicted_transfer": round(predicted, 3),
                "score": round(score, 4),
                "reason": f"你已掌握「{source_kn.name if source_kn else ''}」中的「{b.concept_name}」概念，可迁移到「{target_kn.name}」",
            })
            seen.add(tid)

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return {"recommendations": recommendations[:limit]}

    # ── 引擎3: 学习迁移预测 ──

    @staticmethod
    async def predict_transfer(
        db: AsyncSession,
        user_id: int,
        source_subject_id: int,
        target_subject_id: int,
    ) -> Dict[str, Any]:
        """
        预测学生从学科A到学科B的学习迁移效果
        公式: predicted_mastery = source_mastery * transfer_coefficient * concept_overlap
        """
        # 源学科掌握度
        src_states = await db.execute(
            select(StudentKnowledgeState).join(KnowledgeNode).where(and_(
                StudentKnowledgeState.user_id == user_id,
                KnowledgeNode.subject_id == source_subject_id,
            ))
        )
        src_list = list(src_states.scalars().all())
        src_avg = sum(s.mastery for s in src_list) / len(src_list) if src_list else 0

        # 目标学科当前掌握度
        tgt_states = await db.execute(
            select(StudentKnowledgeState).join(KnowledgeNode).where(and_(
                StudentKnowledgeState.user_id == user_id,
                KnowledgeNode.subject_id == target_subject_id,
            ))
        )
        tgt_list = list(tgt_states.scalars().all())
        tgt_avg = sum(s.mastery for s in tgt_list) / len(tgt_list) if tgt_list else 0

        # 学科关系
        rel_result = await db.execute(
            select(SubjectRelation).where(and_(
                SubjectRelation.source_subject_id == source_subject_id,
                SubjectRelation.target_subject_id == target_subject_id,
            ))
        )
        relations = list(rel_result.scalars().all())
        global_coeff = max((r.transfer_coefficient for r in relations), default=0.2)
        rel_weight = max((r.weight for r in relations), default=0.5)

        # Phase 16: 优先使用个性化迁移系数
        personal_result = await db.execute(
            select(StudentSubjectTransfer).where(and_(
                StudentSubjectTransfer.user_id == user_id,
                StudentSubjectTransfer.source_subject_id == source_subject_id,
                StudentSubjectTransfer.target_subject_id == target_subject_id,
            ))
        )
        personal = personal_result.scalars().first()
        transfer_coeff = personal.observed_transfer if (personal and personal.confidence > 0.3) else global_coeff

        # 概念桥接重叠度
        src_node_result = await db.execute(
            select(KnowledgeNode.id).where(KnowledgeNode.subject_id == source_subject_id)
        )
        src_node_ids = [r[0] for r in src_node_result.all()]

        tgt_node_result = await db.execute(
            select(KnowledgeNode.id).where(KnowledgeNode.subject_id == target_subject_id)
        )
        tgt_node_ids = [r[0] for r in tgt_node_result.all()]

        bridge_count = 0
        if src_node_ids and tgt_node_ids:
            bc_result = await db.execute(
                select(func.count()).select_from(ConceptBridge).where(and_(
                    ConceptBridge.source_node_id.in_(src_node_ids),
                    ConceptBridge.target_node_id.in_(tgt_node_ids),
                ))
            )
            bridge_count = bc_result.scalar() or 0

        max_bridges = max(len(src_node_ids), 1)
        concept_overlap = min(bridge_count / max_bridges, 1.0)

        # 迁移预测
        predicted_mastery = src_avg * transfer_coeff * (0.5 + 0.5 * concept_overlap)
        predicted_mastery = min(predicted_mastery, 0.8)  # 上限0.8，不能完全替代学习

        # 学科名称
        subj_result = await db.execute(
            select(Subject).where(Subject.id.in_([source_subject_id, target_subject_id]))
        )
        subj_map = {s.id: s.name for s in subj_result.scalars().all()}

        # 建议
        if predicted_mastery > 0.4:
            suggestion = "迁移效果良好，建议直接从中等难度内容开始"
        elif predicted_mastery > 0.2:
            suggestion = "有一定迁移基础，建议从基础内容开始并结合已有知识"
        else:
            suggestion = "迁移效果有限，建议从零基础内容系统学习"

        return {
            "source_subject": subj_map.get(source_subject_id, ""),
            "target_subject": subj_map.get(target_subject_id, ""),
            "source_mastery": round(src_avg, 3),
            "target_current_mastery": round(tgt_avg, 3),
            "transfer_coefficient": round(transfer_coeff, 3),
            "concept_overlap": round(concept_overlap, 3),
            "concept_bridge_count": bridge_count,
            "predicted_mastery": round(predicted_mastery, 3),
            "relation_weight": round(rel_weight, 3),
            "suggestion": suggestion,
        }

    # ── 跨学科学习路径 ──

    @staticmethod
    async def generate_cross_path(
        db: AsyncSession,
        user_id: int,
        target_subject_id: int,
        session_minutes: int = 30,
    ) -> Dict[str, Any]:
        """
        生成跨学科学习路径：
        1. 找到与目标学科有关系的源学科
        2. 利用迁移预测确定起点难度
        3. 混合概念桥接节点 + 目标学科薄弱节点
        """
        # 目标学科节点
        tgt_kn_result = await db.execute(
            select(KnowledgeNode).where(
                KnowledgeNode.subject_id == target_subject_id
            ).order_by(KnowledgeNode.difficulty)
        )
        tgt_kns = list(tgt_kn_result.scalars().all())
        if not tgt_kns:
            return {"path": [], "reason": "目标学科暂无知识节点"}

        # 学生在目标学科的状态
        tgt_ids = [kn.id for kn in tgt_kns]
        ts_result = await db.execute(
            select(StudentKnowledgeState).where(and_(
                StudentKnowledgeState.user_id == user_id,
                StudentKnowledgeState.knowledge_node_id.in_(tgt_ids),
            ))
        )
        state_map = {s.knowledge_node_id: s for s in ts_result.scalars().all()}

        # 概念桥接节点（优先）
        bridge_result = await db.execute(
            select(ConceptBridge).where(
                ConceptBridge.target_node_id.in_(tgt_ids)
            ).order_by(desc(ConceptBridge.transfer_weight))
        )
        bridge_targets = {b.target_node_id: b for b in bridge_result.scalars().all()}

        # 情感
        emotion = await EmotionService.get_current_emotion(db, user_id)
        emo_type = emotion["emotion_type"] if emotion else "focus"
        difficulty_mod = 0.0
        if emo_type == "frustration":
            difficulty_mod = -0.15
        elif emo_type == "boredom":
            difficulty_mod = 0.1

        # 构建路径
        path_items = []
        used_minutes = 0

        # 学科名称
        subj_result = await db.execute(
            select(Subject).where(Subject.id == target_subject_id)
        )
        target_subj = subj_result.scalar_one_or_none()

        for kn in tgt_kns:
            if used_minutes >= session_minutes:
                break
            state = state_map.get(kn.id)
            mastery = state.mastery if state else 0.0
            if mastery >= 0.8:
                continue

            # 活动类型
            if mastery < 0.3:
                activity = "learn"
                minutes = 8
            elif mastery < 0.6:
                activity = "practice"
                minutes = 6
            else:
                activity = "review"
                minutes = 4

            if used_minutes + minutes > session_minutes + 2:
                continue

            bridge = bridge_targets.get(kn.id)
            is_bridged = bridge is not None

            path_items.append({
                "order": len(path_items) + 1,
                "knowledge_node_id": kn.id,
                "node_name": kn.name,
                "activity_type": activity,
                "estimated_minutes": minutes,
                "current_mastery": round(mastery, 3),
                "difficulty": round(kn.difficulty + difficulty_mod, 2),
                "is_concept_bridged": is_bridged,
                "bridge_concept": bridge.concept_name if bridge else None,
                "completed": False,
            })
            used_minutes += minutes

        return {
            "target_subject": target_subj.name if target_subj else "",
            "total_items": len(path_items),
            "total_minutes": used_minutes,
            "emotion": emo_type,
            "path": path_items,
        }

    # ── 概念桥接管理 ──

    @staticmethod
    async def add_concept_bridge(
        db: AsyncSession, data: Dict[str, Any],
    ) -> ConceptBridge:
        bridge = ConceptBridge(
            source_node_id=data["source_node_id"],
            target_node_id=data["target_node_id"],
            concept_name=data["concept_name"],
            transfer_weight=data.get("transfer_weight", 0.5),
            description=data.get("description"),
        )
        db.add(bridge)
        await db.flush()
        return bridge

    @staticmethod
    async def get_concept_bridges(
        db: AsyncSession, node_id: int,
    ) -> List[Dict]:
        result = await db.execute(
            select(ConceptBridge).where(or_(
                ConceptBridge.source_node_id == node_id,
                ConceptBridge.target_node_id == node_id,
            ))
        )
        bridges = result.scalars().all()

        node_ids = set()
        for b in bridges:
            node_ids.add(b.source_node_id)
            node_ids.add(b.target_node_id)
        kn_result = await db.execute(
            select(KnowledgeNode).where(KnowledgeNode.id.in_(node_ids))
        ) if node_ids else None
        kn_map = {kn.id: kn.name for kn in kn_result.scalars().all()} if kn_result else {}

        return [
            {
                "id": b.id,
                "source_node_id": b.source_node_id,
                "source_name": kn_map.get(b.source_node_id, ""),
                "target_node_id": b.target_node_id,
                "target_name": kn_map.get(b.target_node_id, ""),
                "concept_name": b.concept_name,
                "transfer_weight": b.transfer_weight,
                "direction": "outgoing" if b.source_node_id == node_id else "incoming",
            }
            for b in bridges
        ]
