"""
Phase 15: 预测分析 API
掌握度预测 / 遗忘风险 / 学习瓶颈 / 对比分析
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.services.predictive_analytics_service import PredictiveAnalyticsService
from app.schemas.schemas import PredictiveRequest, ComparativeRequest

router = APIRouter()
service = PredictiveAnalyticsService()


@router.get("/predictions")
async def predictions(
    user_id: int = Query(...),
    subject_id: Optional[int] = Query(None),
    target_mastery: float = Query(0.8, ge=0.1, le=1.0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取掌握度预测"""
    return await service.get_predictions(
        db, user_id,
        subject_id=subject_id,
        target_mastery=target_mastery,
    )


@router.get("/forgetting-risks")
async def forgetting_risks(
    user_id: int = Query(...),
    subject_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取遗忘风险列表"""
    return await service.get_forgetting_risks(
        db, user_id, subject_id=subject_id,
    )


@router.get("/bottlenecks")
async def bottlenecks(
    user_id: int = Query(...),
    subject_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取学习瓶颈列表"""
    return await service.get_bottlenecks(
        db, user_id, subject_id=subject_id,
    )


@router.get("/comparative")
async def comparative(
    user_id: int = Query(...),
    period: str = Query("weekly", regex="^(weekly|monthly)$"),
    subject_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取周期对比分析"""
    return await service.get_comparative(
        db, user_id, period=period, subject_id=subject_id,
    )
