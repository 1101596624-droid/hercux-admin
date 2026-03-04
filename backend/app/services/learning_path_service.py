"""
Learning Path Service - Phase 2 自适应学习路径规划
基于学生知识状态(BKT mastery)、情感状态和前置依赖，动态生成个性化学习路径。
"""

import math
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, or_

from app.models.models import (
    KnowledgeNode, StudentKnowledgeState,
    StudentEmotionState, StudentLearningPath, Subject
)
from app.services.time_utils import as_utc, utcnow


class ActivityType:
    REVIEW = "review"          # 复习已学内容
    PRACTICE = "practice"      # 练习巩固薄弱点
    LEARN = "learn"            # 学习新知识
    CHALLENGE = "challenge"    # 进阶挑战


# 情感状态 → 难度调整系数
EMOTION_DIFFICULTY_MODIFIER = {
    "frustration": -0.2,   # 降低难度
    "anxiety": -0.1,       # 略降难度
    "boredom": 0.15,       # 提升难度
    "focus": 0.0,          # 保持不变
    "excitement": 0.1,     # 略升难度
}

# 活动类型 → 预估时间（分钟）
ACTIVITY_DURATION = {
    ActivityType.REVIEW: 3,
    ActivityType.PRACTICE: 5,
    ActivityType.LEARN: 8,
    ActivityType.CHALLENGE: 6,
}


class LearningPathService:

    @staticmethod
    async def generate_path(
        db: AsyncSession,
        user_id: int,
        subject_id: int,
        session_duration: int = 30,
    ) -> StudentLearningPath:
        """
        生成个性化学习路径。

        算法流程:
        1. 获取学科所有知识节点
        2. 获取学生当前知识状态 + 情感状态
        3. 根据情感调整难度偏好
        4. 按优先级排序节点: 薄弱→即将遗忘→新节点→进阶
        5. 按 session_duration 分配时间，穿插不同活动类型
        """
        now = utcnow()

        # 1. 获取学科所有知识节点
        nodes_result = await db.execute(
            select(KnowledgeNode)
            .where(KnowledgeNode.subject_id == subject_id)
            .order_by(KnowledgeNode.code)
        )
        all_nodes = {n.id: n for n in nodes_result.scalars().all()}

        if not all_nodes:
            # 无知识节点，返回空路径
            path = StudentLearningPath(
                user_id=user_id,
                subject_id=subject_id,
                session_duration=session_duration,
                status="active",
                path_items=[],
                total_nodes=0,
                completed_nodes=0,
            )
            db.add(path)
            await db.flush()
            return path

        # 2. 获取学生知识状态
        states_result = await db.execute(
            select(StudentKnowledgeState).where(
                and_(
                    StudentKnowledgeState.user_id == user_id,
                    StudentKnowledgeState.knowledge_node_id.in_(all_nodes.keys()),
                )
            )
        )
        state_map: Dict[int, StudentKnowledgeState] = {
            s.knowledge_node_id: s for s in states_result.scalars().all()
        }

        # 3. 获取当前情感状态
        emotion_result = await db.execute(
            select(StudentEmotionState)
            .where(StudentEmotionState.user_id == user_id)
            .order_by(desc(StudentEmotionState.created_at))
            .limit(1)
        )
        current_emotion = emotion_result.scalar_one_or_none()
        emotion_type = current_emotion.emotion_type if current_emotion else "focus"
        difficulty_mod = EMOTION_DIFFICULTY_MODIFIER.get(emotion_type, 0.0)

        # 4. 分类节点
        weak_nodes = []       # mastery < 0.4 → 练习巩固
        forgetting_nodes = [] # stability低 + 距上次练习久 → 复习
        new_nodes = []        # 无state记录 → 新学
        advancing_nodes = []  # mastery 0.4~0.8 → 提升
        challenge_nodes = []  # mastery > 0.8 → 挑战

        for node_id, node in all_nodes.items():
            state = state_map.get(node_id)

            if state is None:
                # 检查前置依赖是否满足
                if LearningPathService._prerequisites_met(
                    node, state_map, all_nodes
                ):
                    new_nodes.append((node_id, node, None))
                continue

            mastery = state.mastery

            # 遗忘风险计算
            forgetting_risk = 0.0
            if state.last_practice_at and state.stability:
                last_practice_at = as_utc(state.last_practice_at)
                elapsed_hours = (
                    (now - last_practice_at).total_seconds() / 3600.0
                    if last_practice_at
                    else 0.0
                )
                if elapsed_hours > 0.1:
                    retention = mastery * math.exp(-elapsed_hours / max(state.stability, 1.0))
                    forgetting_risk = mastery - retention

            if mastery < 0.4:
                weak_nodes.append((node_id, node, state, mastery))
            elif forgetting_risk > 0.1 and mastery >= 0.4:
                forgetting_nodes.append((node_id, node, state, forgetting_risk))
            elif mastery < 0.8:
                advancing_nodes.append((node_id, node, state, mastery))
            else:
                challenge_nodes.append((node_id, node, state, mastery))

        # 排序
        weak_nodes.sort(key=lambda x: x[3])              # mastery 升序
        forgetting_nodes.sort(key=lambda x: -x[3])       # 遗忘风险降序
        new_nodes.sort(key=lambda x: x[1].difficulty)     # 难度升序
        advancing_nodes.sort(key=lambda x: x[3])          # mastery 升序
        challenge_nodes.sort(key=lambda x: -x[3])         # mastery 降序

        # 5. 根据情感调整优先级
        if emotion_type == "frustration":
            # 挫败时：多复习已掌握内容，少新学
            priority_order = forgetting_nodes + advancing_nodes + weak_nodes + new_nodes
        elif emotion_type == "anxiety":
            # 焦虑时：优先低负担复习与薄弱巩固，减少挑战
            priority_order = forgetting_nodes + weak_nodes + advancing_nodes + new_nodes
        elif emotion_type == "boredom":
            # 无聊时：优先挑战和新内容
            priority_order = challenge_nodes + new_nodes + advancing_nodes + forgetting_nodes
        else:
            # 默认：薄弱→遗忘→新学→进阶→挑战
            priority_order = weak_nodes + forgetting_nodes + new_nodes + advancing_nodes + challenge_nodes

        # 6. 按时间预算分配活动
        path_items = []
        remaining_minutes = session_duration
        used_node_ids = set()

        for item in priority_order:
            if remaining_minutes <= 0:
                break

            node_id = item[0]
            node = item[1]
            state = item[2] if len(item) > 2 else None

            if node_id in used_node_ids:
                continue

            # 确定活动类型
            activity = LearningPathService._pick_activity(
                state, node, difficulty_mod
            )
            duration = ACTIVITY_DURATION[activity]

            if remaining_minutes < duration:
                break

            # 目标难度 = 节点难度 + 情感修正
            target_difficulty = max(0.1, min(1.0, node.difficulty + difficulty_mod))

            path_items.append({
                "knowledge_node_id": node_id,
                "node_code": node.code,
                "node_name": node.name,
                "activity_type": activity,
                "estimated_minutes": duration,
                "target_difficulty": round(target_difficulty, 2),
                "mastery_before": round(state.mastery, 3) if state else 0.0,
                "reason": LearningPathService._activity_reason(activity, state),
            })

            remaining_minutes -= duration
            used_node_ids.add(node_id)

        # 穿插不同活动类型，避免连续相同类型导致疲劳
        path_items = LearningPathService._interleave_activities(path_items)

        # 7. 将旧的 active 路径标记为 expired
        await db.execute(
            StudentLearningPath.__table__.update()
            .where(
                and_(
                    StudentLearningPath.user_id == user_id,
                    StudentLearningPath.subject_id == subject_id,
                    StudentLearningPath.status == "active",
                )
            )
            .values(status="expired", updated_at=now)
        )

        # 8. 创建新路径
        path = StudentLearningPath(
            user_id=user_id,
            subject_id=subject_id,
            status="active",
            session_duration=session_duration,
            path_items=path_items,
            emotion_snapshot=emotion_type,
            total_nodes=len(path_items),
            completed_nodes=0,
        )
        db.add(path)
        await db.flush()
        return path

    @staticmethod
    def _prerequisites_met(
        node: KnowledgeNode,
        state_map: Dict[int, StudentKnowledgeState],
        all_nodes: Dict[int, KnowledgeNode],
    ) -> bool:
        """检查前置依赖是否全部 mastery > 0.6"""
        prereqs = node.prerequisites or []
        if not prereqs:
            return True

        # prerequisites 存的是 knowledge_node_id 列表
        for prereq_id in prereqs:
            state = state_map.get(prereq_id)
            if not state or state.mastery < 0.6:
                return False
        return True

    @staticmethod
    def _pick_activity(
        state: Optional[StudentKnowledgeState],
        node: KnowledgeNode,
        difficulty_mod: float,
    ) -> str:
        """根据知识状态选择活动类型"""
        if state is None:
            return ActivityType.LEARN

        mastery = state.mastery
        if mastery < 0.4:
            return ActivityType.PRACTICE
        elif mastery >= 0.8 and difficulty_mod >= 0:
            return ActivityType.CHALLENGE
        elif state.last_practice_at:
            now = utcnow()
            last_practice_at = as_utc(state.last_practice_at)
            hours_since = (
                (now - last_practice_at).total_seconds() / 3600.0
                if last_practice_at
                else 0.0
            )
            if hours_since > 24 and state.stability and state.stability < 5.0:
                return ActivityType.REVIEW
        return ActivityType.PRACTICE

    @staticmethod
    def _activity_reason(
        activity: str,
        state: Optional[StudentKnowledgeState],
    ) -> str:
        """生成活动推荐理由"""
        if activity == ActivityType.LEARN:
            return "新知识点，满足前置条件"
        elif activity == ActivityType.PRACTICE:
            m = round(state.mastery, 2) if state else 0
            return f"掌握度{m}，需要巩固练习"
        elif activity == ActivityType.REVIEW:
            return "距上次练习较久，防止遗忘"
        elif activity == ActivityType.CHALLENGE:
            return "掌握度高，适合进阶挑战"
        return ""

    @staticmethod
    def _interleave_activities(items: List[Dict]) -> List[Dict]:
        """穿插不同活动类型，避免连续3个以上相同类型"""
        if len(items) <= 3:
            return items

        result = [items[0]]
        for i in range(1, len(items)):
            result.append(items[i])
            # 检查连续3个相同类型
            if len(result) >= 3:
                last3 = [r["activity_type"] for r in result[-3:]]
                if last3[0] == last3[1] == last3[2]:
                    # 从后面找一个不同类型的交换
                    for j in range(i + 1, len(items)):
                        if items[j]["activity_type"] != last3[0]:
                            items[i], items[j] = items[j], items[i]
                            result[-1] = items[i]
                            break
        return result

    @staticmethod
    async def get_active_path(
        db: AsyncSession,
        user_id: int,
        subject_id: Optional[int] = None,
    ) -> Optional[StudentLearningPath]:
        """获取当前活跃的学习路径"""
        query = select(StudentLearningPath).where(
            and_(
                StudentLearningPath.user_id == user_id,
                StudentLearningPath.status == "active",
            )
        )
        if subject_id:
            query = query.where(StudentLearningPath.subject_id == subject_id)

        query = query.order_by(desc(StudentLearningPath.created_at)).limit(1)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def complete_node(
        db: AsyncSession,
        path_id: int,
        knowledge_node_id: int,
        user_id: int,
    ) -> Optional[StudentLearningPath]:
        """标记路径中某个节点为已完成"""
        result = await db.execute(
            select(StudentLearningPath).where(
                and_(
                    StudentLearningPath.id == path_id,
                    StudentLearningPath.user_id == user_id,
                    StudentLearningPath.status == "active",
                )
            )
        )
        path = result.scalar_one_or_none()
        if not path:
            return None

        # 更新 path_items 中对应节点的完成状态
        items = path.path_items or []
        updated = False
        for item in items:
            if item.get("knowledge_node_id") == knowledge_node_id and not item.get("completed"):
                item["completed"] = True
                item["completed_at"] = utcnow().isoformat()
                updated = True
                break

        if updated:
            path.path_items = items
            path.completed_nodes = sum(1 for i in items if i.get("completed"))
            path.updated_at = utcnow()

            if path.completed_nodes >= path.total_nodes:
                path.status = "completed"
                path.completed_at = utcnow()

            await db.flush()

        return path

    @staticmethod
    async def get_next_activity(
        db: AsyncSession,
        user_id: int,
        subject_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """获取下一个推荐学习活动"""
        path = await LearningPathService.get_active_path(db, user_id, subject_id)
        if not path:
            return None

        items = path.path_items or []
        for item in items:
            if not item.get("completed"):
                adapted_item = await LearningPathService._adapt_activity_runtime(
                    db, user_id, item
                )
                return {
                    "path_id": path.id,
                    "subject_id": path.subject_id,
                    **adapted_item,
                }
        return None

    @staticmethod
    async def _adapt_activity_runtime(
        db: AsyncSession,
        user_id: int,
        item: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        运行时动态调整活动：
        - 负面情感（frustration/anxiety）自动降难度，挑战题转为练习/复习
        - boredom + 高掌握度时提升挑战性
        - 基于最新 BKT mastery 做细粒度修正
        """
        adapted = dict(item)

        # 1) 最新情感
        emotion_result = await db.execute(
            select(StudentEmotionState)
            .where(StudentEmotionState.user_id == user_id)
            .order_by(desc(StudentEmotionState.created_at))
            .limit(1)
        )
        emotion = emotion_result.scalar_one_or_none()
        emotion_type = emotion.emotion_type if emotion else "focus"
        emotion_intensity = float(emotion.intensity or 0.3) if emotion else 0.3

        # 2) 最新知识状态
        node_id = adapted.get("knowledge_node_id")
        mastery = adapted.get("mastery_before", 0.0)
        if node_id:
            state_result = await db.execute(
                select(StudentKnowledgeState).where(
                    and_(
                        StudentKnowledgeState.user_id == user_id,
                        StudentKnowledgeState.knowledge_node_id == node_id,
                    )
                )
            )
            state = state_result.scalar_one_or_none()
            if state:
                mastery = float(state.mastery or 0.0)
                adapted["mastery_before"] = round(mastery, 3)

        activity = adapted.get("activity_type", ActivityType.PRACTICE)
        difficulty = float(adapted.get("target_difficulty", 0.5))
        adjustments: List[str] = []

        # 3) 情感驱动修正
        if emotion_type in {"frustration", "anxiety"}:
            penalty = 0.2 if emotion_type == "frustration" else 0.12
            penalty += max(0.0, emotion_intensity - 0.7) * 0.2
            difficulty = max(0.1, difficulty - penalty)
            adjustments.append(f"{emotion_type} 降难度")

            if activity == ActivityType.CHALLENGE:
                activity = ActivityType.PRACTICE if mastery < 0.8 else ActivityType.REVIEW
                adjustments.append("挑战任务降级为低压任务")
        elif emotion_type == "boredom" and mastery >= 0.75:
            difficulty = min(1.0, difficulty + 0.15)
            if activity in {ActivityType.LEARN, ActivityType.PRACTICE}:
                activity = ActivityType.CHALLENGE
            adjustments.append("boredom 提升挑战")
        elif emotion_type in {"focus", "excitement"} and mastery >= 0.6:
            difficulty = min(1.0, difficulty + 0.05)
            adjustments.append("正向情感微升难度")

        # 4) BKT 兜底修正
        if mastery < 0.35 and activity == ActivityType.CHALLENGE:
            activity = ActivityType.PRACTICE
            difficulty = min(difficulty, 0.45)
            adjustments.append("低掌握度避免挑战")

        adapted["activity_type"] = activity
        adapted["target_difficulty"] = round(difficulty, 2)
        adapted["runtime_adjustments"] = adjustments
        adapted["emotion_runtime"] = {
            "type": emotion_type,
            "intensity": round(emotion_intensity, 2),
        }
        return adapted

    @staticmethod
    async def get_user_path_history(
        db: AsyncSession,
        user_id: int,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """获取用户学习路径历史"""
        result = await db.execute(
            select(StudentLearningPath)
            .where(StudentLearningPath.user_id == user_id)
            .order_by(desc(StudentLearningPath.created_at))
            .limit(limit)
        )
        paths = result.scalars().all()
        return [
            {
                "id": p.id,
                "subject_id": p.subject_id,
                "status": p.status,
                "session_duration": p.session_duration,
                "emotion_snapshot": p.emotion_snapshot,
                "total_nodes": p.total_nodes,
                "completed_nodes": p.completed_nodes,
                "path_items": p.path_items,
                "created_at": p.created_at,
                "completed_at": p.completed_at,
            }
            for p in paths
        ]
