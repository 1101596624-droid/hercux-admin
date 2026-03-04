"""
Phase 13: Agent 强化学习与自适应任务生成 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.services.adaptive_agent_service import AdaptiveAgentService
from app.schemas.schemas import (
    AdaptiveTaskRequest,
    RewardSignalRequest,
    AdaptivePathRequest,
)

router = APIRouter()
service = AdaptiveAgentService()


@router.post("/adaptive-tasks")
async def adaptive_tasks(
    req: AdaptiveTaskRequest,
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """自适应任务生成（情感+BKT驱动）"""
    return await service.generate_adaptive_tasks(
        db, user_id,
        subject_id=req.subject_id,
        session_minutes=req.session_minutes,
    )


@router.post("/reward-signal")
async def reward_signal(
    req: RewardSignalRequest,
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """提交奖惩信号并更新策略权重"""
    return await service.compute_reward(
        db, user_id,
        strategy_type=req.strategy_type,
        action_taken=req.action_taken,
        state_before=req.student_state_before,
        state_after=req.student_state_after,
    )


@router.post("/adaptive-path")
async def adaptive_path(
    req: AdaptivePathRequest,
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """个性化学习路径（整合小课堂/做题家/模拟器/跨学科）"""
    return await service.generate_adaptive_path(
        db, user_id,
        subject_id=req.subject_id,
        session_minutes=req.session_minutes,
        include_cross_discipline=req.include_cross_discipline,
    )


@router.get("/strategy-weights")
async def strategy_weights(
    strategy_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前策略权重"""
    return await service.get_strategy_weights(db, strategy_type)


@router.get("/reward-history")
async def reward_history(
    user_id: int = Query(...),
    strategy_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取奖惩历史"""
    return await service.get_reward_history(
        db, user_id, strategy_type=strategy_type, limit=limit,
    )
