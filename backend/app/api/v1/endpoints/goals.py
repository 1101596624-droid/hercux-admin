"""
Phase 15: 目标管理 API
目标 CRUD + 进度概览
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.services.goal_management_service import GoalManagementService
from app.schemas.schemas import GoalCreateRequest, GoalUpdateRequest

router = APIRouter()
service = GoalManagementService()


@router.post("/")
async def create_goal(
    req: GoalCreateRequest,
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建学习目标"""
    return await service.create_goal(db, user_id, req.model_dump())


@router.get("/")
async def list_goals(
    user_id: int = Query(...),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取目标列表"""
    return await service.list_goals(db, user_id, status=status)


@router.put("/{goal_id}")
async def update_goal(
    goal_id: int,
    req: GoalUpdateRequest,
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新目标"""
    return await service.update_goal(
        db, user_id, goal_id, req.model_dump(exclude_none=True),
    )


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: int,
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除目标"""
    return await service.delete_goal(db, user_id, goal_id)


@router.get("/progress")
async def goal_progress(
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取所有活跃目标的进度概览"""
    return await service.get_progress(db, user_id)
