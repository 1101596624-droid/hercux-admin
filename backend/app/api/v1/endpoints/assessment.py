"""
Assessment API - Phase 7 智能评估与自适应反馈
POST /learning-assessment    学习评估
POST /adaptive-feedback      自适应反馈
GET  /assessment-history     评估历史
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import LearningAssessmentRequest, AdaptiveFeedbackRequest
from app.services.assessment_service import AssessmentService

router = APIRouter()


@router.post("/learning-assessment")
async def learning_assessment(
    data: LearningAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """学习评估：返回掌握度、稳定性、情感状态和策略建议"""
    result = await AssessmentService.evaluate_student(
        db=db,
        user_id=current_user.id,
        knowledge_node_id=data.knowledge_node_id,
        assessment_type=data.assessment_type,
    )
    await db.commit()
    return result


@router.post("/adaptive-feedback")
async def adaptive_feedback(
    data: AdaptiveFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """自适应反馈：基于评估结果+趋势生成个性化建议"""
    result = await AssessmentService.get_adaptive_feedback(
        db=db,
        user_id=current_user.id,
        knowledge_node_id=data.knowledge_node_id,
    )
    await db.commit()
    return result


@router.get("/assessment-history")
async def get_assessment_history(
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取评估历史"""
    return await AssessmentService.get_assessment_history(
        db=db, user_id=current_user.id, limit=limit,
    )
