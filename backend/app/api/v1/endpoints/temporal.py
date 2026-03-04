"""Phase 16: 时间模式分析 API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.services.dynamic_transfer_service import DynamicTransferService

router = APIRouter()


@router.get("/patterns")
async def get_temporal_patterns(
    days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取时间模式分析"""
    return await DynamicTransferService.get_temporal_patterns(
        db, current_user.id, days
    )


@router.get("/optimal-schedule")
async def get_optimal_schedule(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取最优学习时间建议"""
    return await DynamicTransferService.get_optimal_schedule(db, current_user.id)
