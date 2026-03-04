"""
Knowledge Tracking API - 学生端
学生知识追踪接口（需要登录）
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import StudentEventCreate
from app.services.bkt_service import BKTService

router = APIRouter()


@router.post("/events")
async def record_event(
    data: StudentEventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """记录学习事件（触发 BKT 更新）"""
    event = await BKTService.record_event(
        db=db,
        user_id=current_user.id,
        knowledge_node_id=data.knowledge_node_id,
        event_type=data.event_type,
        is_correct=data.is_correct,
        response_time_ms=data.response_time_ms,
        event_data=data.event_data,
    )
    await db.commit()
    return {"id": event.id, "message": "事件已记录"}


@router.get("/my-state")
async def get_my_state(
    subject_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取自己的知识状态"""
    states = await BKTService.get_user_knowledge_summary(
        db, current_user.id, subject_id
    )
    return {"user_id": current_user.id, "states": states}


@router.get("/weak-nodes")
async def get_weak_nodes(
    threshold: float = Query(0.4, ge=0, le=1),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取自己的薄弱知识点"""
    nodes = await BKTService.get_weak_nodes(
        db, current_user.id, threshold, limit
    )
    return {"user_id": current_user.id, "weak_nodes": nodes}
