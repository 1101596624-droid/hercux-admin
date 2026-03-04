"""
Phase 12: 学习反馈系统 + 智能报告系统 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.services.smart_feedback_service import SmartFeedbackService
from app.schemas.schemas import (
    ProgressFeedbackRequest,
    EmotionFeedbackRequest,
    SmartReportRequest,
)

router = APIRouter()
service = SmartFeedbackService()


@router.post("/progress-feedback")
async def progress_feedback(
    req: ProgressFeedbackRequest,
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """生成学习进度反馈"""
    return await service.generate_progress_feedback(
        db, user_id,
        subject_id=req.subject_id,
        include_suggestions=req.include_suggestions,
    )


@router.post("/emotion-feedback")
async def emotion_feedback(
    req: EmotionFeedbackRequest,
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """生成情感反馈（含难度调整和任务建议）"""
    return await service.generate_emotion_feedback(
        db, user_id, subject_id=req.subject_id,
    )


@router.post("/smart-report")
async def smart_report(
    req: SmartReportRequest,
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """生成智能学习报告"""
    return await service.generate_smart_report(
        db, user_id,
        period=req.period,
        subject_id=req.subject_id,
    )


@router.get("/feedback-history")
async def feedback_history(
    user_id: int = Query(...),
    feedback_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取反馈历史"""
    return await service.get_feedback_history(
        db, user_id,
        feedback_type=feedback_type,
        limit=limit,
    )


@router.get("/dashboard")
async def dashboard(
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取学习仪表盘数据"""
    return await service.get_dashboard(db, user_id)
