"""
Phase 8: 多任务学习与多目标优化 API 端点
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.services.multi_task_service import MultiTaskService
from app.schemas.schemas import MultiTaskRequest, MultiObjectiveFeedbackRequest

router = APIRouter()


@router.post("/multi-task")
async def generate_multi_task_plan(
    request: MultiTaskRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """生成多任务学习计划（多目标优化）"""
    weights = None
    if request.objective_weights:
        weights = request.objective_weights.model_dump()

    result = await MultiTaskService.generate_plan(
        db=db,
        user_id=current_user.id,
        session_minutes=request.session_minutes,
        subject_id=request.subject_id,
        objective_weights=weights,
    )
    await db.commit()
    return result


@router.post("/multi-objective-feedback")
async def get_multi_objective_feedback(
    request: MultiObjectiveFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取多目标优化反馈与调整建议"""
    result = await MultiTaskService.get_multi_objective_feedback(
        db=db,
        user_id=current_user.id,
        plan_id=request.plan_id,
        subject_id=request.subject_id,
    )
    return result
