"""
Learning Path API - 学生端自适应学习路径
POST /knowledge/learning-path  生成个性化学习路径
GET  /knowledge/learning-path  获取当前活跃路径
GET  /knowledge/next-activity   获取下一个推荐活动
POST /knowledge/learning-path/{path_id}/complete  标记节点完成
GET  /knowledge/learning-path/history  获取路径历史
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import LearningPathRequest, CompleteNodeRequest
from app.services.learning_path_service import LearningPathService

router = APIRouter()


@router.post("/learning-path")
async def generate_learning_path(
    data: LearningPathRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """生成个性化学习路径"""
    path = await LearningPathService.generate_path(
        db=db,
        user_id=current_user.id,
        subject_id=data.subject_id,
        session_duration=data.session_duration,
    )
    await db.commit()
    return {
        "id": path.id,
        "subject_id": path.subject_id,
        "status": path.status,
        "session_duration": path.session_duration,
        "emotion_snapshot": path.emotion_snapshot,
        "total_nodes": path.total_nodes,
        "completed_nodes": path.completed_nodes,
        "path_items": path.path_items,
        "created_at": path.created_at,
    }


@router.get("/learning-path")
async def get_active_path(
    subject_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前活跃的学习路径"""
    path = await LearningPathService.get_active_path(
        db, current_user.id, subject_id
    )
    if not path:
        return {"path": None, "message": "无活跃学习路径"}
    return {
        "id": path.id,
        "subject_id": path.subject_id,
        "status": path.status,
        "session_duration": path.session_duration,
        "emotion_snapshot": path.emotion_snapshot,
        "total_nodes": path.total_nodes,
        "completed_nodes": path.completed_nodes,
        "path_items": path.path_items,
        "created_at": path.created_at,
    }


@router.get("/next-activity")
async def get_next_activity(
    subject_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取下一个推荐学习活动"""
    activity = await LearningPathService.get_next_activity(
        db, current_user.id, subject_id
    )
    if not activity:
        return {"activity": None, "message": "无待完成活动，请生成新路径"}
    return activity


@router.post("/learning-path/{path_id}/complete")
async def complete_path_node(
    path_id: int,
    data: CompleteNodeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """标记学习路径中某个节点为已完成"""
    path = await LearningPathService.complete_node(
        db=db,
        path_id=path_id,
        knowledge_node_id=data.knowledge_node_id,
        user_id=current_user.id,
    )
    if not path:
        raise HTTPException(status_code=404, detail="路径不存在或已过期")
    await db.commit()
    return {
        "id": path.id,
        "status": path.status,
        "completed_nodes": path.completed_nodes,
        "total_nodes": path.total_nodes,
    }


@router.get("/learning-path/history")
async def get_path_history(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取学习路径历史"""
    history = await LearningPathService.get_user_path_history(
        db, current_user.id, limit
    )
    return {"user_id": current_user.id, "paths": history}
