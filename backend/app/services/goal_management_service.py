"""
Phase 15: 目标管理系统
目标 CRUD + 自动进度同步 + 到期检查
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    StudentGoal, StudentKnowledgeState, KnowledgeNode,
    Subject, StudentEvent,
)


class GoalManagementService:

    # ---------- 创建目标 ----------
    async def create_goal(
        self, db: AsyncSession, user_id: int, data: dict,
    ) -> dict:
        goal = StudentGoal(
            user_id=user_id,
            goal_type=data["goal_type"],
            title=data["title"],
            description=data.get("description"),
            subject_id=data.get("subject_id"),
            node_id=data.get("node_id"),
            target_value=data["target_value"],
            current_value=0,
            deadline=data.get("deadline"),
            status="active",
        )
        # 初始化 current_value
        goal.current_value = await self._calc_current_value(
            db, user_id, goal
        )
        db.add(goal)
        await db.commit()
        await db.refresh(goal)
        return self._to_dict(goal)

    # ---------- 获取目标列表 ----------
    async def list_goals(
        self, db: AsyncSession, user_id: int,
        status: Optional[str] = None,
    ) -> list:
        q = select(StudentGoal).where(StudentGoal.user_id == user_id)
        if status:
            q = q.where(StudentGoal.status == status)
        q = q.order_by(StudentGoal.created_at.desc())
        result = await db.execute(q)
        return [self._to_dict(g) for g in result.scalars().all()]

    # ---------- 更新目标 ----------
    async def update_goal(
        self, db: AsyncSession, user_id: int,
        goal_id: int, data: dict,
    ) -> dict:
        q = select(StudentGoal).where(and_(
            StudentGoal.id == goal_id,
            StudentGoal.user_id == user_id,
        ))
        result = await db.execute(q)
        goal = result.scalar_one_or_none()
        if not goal:
            return {"error": "goal_not_found"}

        for key in ["title", "description", "target_value", "deadline", "status"]:
            if key in data and data[key] is not None:
                setattr(goal, key, data[key])

        if data.get("status") == "completed" and not goal.completed_at:
            goal.completed_at = datetime.utcnow()

        goal.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(goal)
        return self._to_dict(goal)

    # ---------- 删除目标 ----------
    async def delete_goal(
        self, db: AsyncSession, user_id: int, goal_id: int,
    ) -> dict:
        q = select(StudentGoal).where(and_(
            StudentGoal.id == goal_id,
            StudentGoal.user_id == user_id,
        ))
        result = await db.execute(q)
        goal = result.scalar_one_or_none()
        if not goal:
            return {"error": "goal_not_found"}
        await db.delete(goal)
        await db.commit()
        return {"deleted": goal_id}

    # ---------- 目标进度概览 ----------
    async def get_progress(
        self, db: AsyncSession, user_id: int,
    ) -> dict:
        q = select(StudentGoal).where(and_(
            StudentGoal.user_id == user_id,
            StudentGoal.status == "active",
        ))
        result = await db.execute(q)
        goals = result.scalars().all()

        now = datetime.utcnow()
        items = []
        for g in goals:
            # 刷新 current_value
            g.current_value = await self._calc_current_value(db, user_id, g)
            pct = round(g.current_value / g.target_value * 100, 1) if g.target_value else 0
            at_risk = False
            if g.deadline and g.deadline < now and pct < 100:
                g.status = "expired"
                at_risk = True
            elif g.deadline:
                total_days = (g.deadline - g.created_at).total_seconds() / 86400
                elapsed_days = (now - g.created_at).total_seconds() / 86400
                expected_pct = (elapsed_days / total_days * 100) if total_days > 0 else 0
                if pct < expected_pct * 0.7:
                    at_risk = True

            # 自动完成检测
            if pct >= 100 and g.status == "active":
                g.status = "completed"
                g.completed_at = now

            items.append({
                **self._to_dict(g),
                "progress_pct": min(pct, 100),
                "at_risk": at_risk,
            })

        await db.commit()
        return {
            "active_count": len([i for i in items if i["status"] == "active"]),
            "completed_count": len([i for i in items if i["status"] == "completed"]),
            "at_risk_count": len([i for i in items if i["at_risk"]]),
            "goals": items,
        }

    # ========== 内部方法 ==========

    async def _calc_current_value(self, db, user_id, goal):
        if goal.goal_type == "mastery":
            if goal.node_id:
                q = select(StudentKnowledgeState.mastery).where(and_(
                    StudentKnowledgeState.user_id == user_id,
                    StudentKnowledgeState.knowledge_node_id == goal.node_id,
                ))
                r = await db.execute(q)
                return r.scalar() or 0
            elif goal.subject_id:
                q = (
                    select(func.avg(StudentKnowledgeState.mastery))
                    .join(KnowledgeNode, KnowledgeNode.id == StudentKnowledgeState.knowledge_node_id)
                    .where(and_(
                        StudentKnowledgeState.user_id == user_id,
                        KnowledgeNode.subject_id == goal.subject_id,
                    ))
                )
                r = await db.execute(q)
                return r.scalar() or 0
        elif goal.goal_type == "completion":
            if goal.subject_id:
                total_q = select(func.count()).select_from(KnowledgeNode).where(
                    KnowledgeNode.subject_id == goal.subject_id
                )
                mastered_q = (
                    select(func.count())
                    .select_from(StudentKnowledgeState)
                    .join(KnowledgeNode, KnowledgeNode.id == StudentKnowledgeState.knowledge_node_id)
                    .where(and_(
                        StudentKnowledgeState.user_id == user_id,
                        KnowledgeNode.subject_id == goal.subject_id,
                        StudentKnowledgeState.mastery >= 0.6,
                    ))
                )
                tr = await db.execute(total_q)
                mr = await db.execute(mastered_q)
                return mr.scalar() or 0
        elif goal.goal_type == "streak":
            # 从 learning_habits 计算连续天数
            from app.models.models import LearningHabit
            from datetime import date, timedelta
            today = date.today()
            q = (
                select(LearningHabit.date)
                .where(and_(
                    LearningHabit.user_id == user_id,
                    LearningHabit.events_count > 0,
                ))
                .order_by(LearningHabit.date.desc())
                .limit(90)
            )
            r = await db.execute(q)
            dates = [row.date for row in r.all()]
            streak = 0
            check = today
            for d in dates:
                if hasattr(d, 'date'):
                    d = d.date() if callable(d.date) else d
                if d == check:
                    streak += 1
                    check -= timedelta(days=1)
                else:
                    break
            return streak
        return 0

    def _to_dict(self, goal):
        return {
            "id": goal.id,
            "user_id": goal.user_id,
            "goal_type": goal.goal_type,
            "title": goal.title,
            "description": goal.description,
            "subject_id": goal.subject_id,
            "node_id": goal.node_id,
            "target_value": goal.target_value,
            "current_value": goal.current_value,
            "deadline": goal.deadline.isoformat() if goal.deadline else None,
            "status": goal.status,
            "completed_at": goal.completed_at.isoformat() if goal.completed_at else None,
            "created_at": goal.created_at.isoformat() if goal.created_at else None,
        }
