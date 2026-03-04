"""
Phase 15: 学习习惯追踪 API
习惯摘要 / 日历视图 / 个人最佳
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.services.habit_tracking_service import HabitTrackingService

router = APIRouter()
service = HabitTrackingService()


@router.get("/summary")
async def habit_summary(
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取习惯摘要"""
    return await service.get_summary(db, user_id)


@router.get("/calendar")
async def habit_calendar(
    user_id: int = Query(...),
    days: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取日历视图数据"""
    return await service.get_calendar(db, user_id, days=days)


@router.get("/personal-bests")
async def personal_bests(
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取个人最佳记录"""
    return await service.get_personal_bests(db, user_id)
