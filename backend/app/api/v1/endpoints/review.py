"""
Spaced Repetition API - 学生端间隔复习
GET  /review/due          获取到期复习项
POST /review/record       记录复习结果
POST /review/init         为已学知识点初始化复习调度
GET  /review/stats        获取复习统计
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import RecordReviewRequest
from app.services.spaced_repetition_service import SpacedRepetitionService

router = APIRouter()


@router.get("/due")
async def get_due_reviews(
    max_count: int = Query(20, ge=1, le=50),
    max_minutes: int = Query(30, ge=5, le=120),
    subject_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取到期的复习项"""
    result = await SpacedRepetitionService.get_due_reviews(
        db=db,
        user_id=current_user.id,
        max_count=max_count,
        max_minutes=max_minutes,
        subject_id=subject_id,
    )
    return result


@router.post("/record")
async def record_review(
    data: RecordReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """记录复习结果并更新 FSRS 调度"""
    result = await SpacedRepetitionService.record_review(
        db=db,
        user_id=current_user.id,
        knowledge_node_id=data.knowledge_node_id,
        rating=data.rating,
        review_type=data.review_type,
    )
    await db.commit()
    return result


@router.post("/init")
async def init_review_schedules(
    subject_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """为已学知识点初始化复习调度"""
    created = await SpacedRepetitionService.ensure_schedules(
        db=db,
        user_id=current_user.id,
        subject_id=subject_id,
    )
    await db.commit()
    return {"created": created, "message": f"已创建 {created} 个复习调度"}


@router.get("/stats")
async def get_review_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取复习统计概览"""
    stats = await SpacedRepetitionService.get_review_stats(
        db=db,
        user_id=current_user.id,
    )
    return stats
