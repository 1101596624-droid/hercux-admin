"""
Simulator API endpoints
处理模拟器结果的提交和查询
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.models.models import SimulatorResult, CourseNode, User
from app.core.security import get_current_user

router = APIRouter()


class SimulatorResultCreate(BaseModel):
    """模拟器结果提交请求"""
    node_id: int
    session_id: str
    result_data: dict
    score: Optional[float] = None
    time_spent_seconds: Optional[int] = 0
    completed: Optional[bool] = False


class SimulatorResultResponse(BaseModel):
    """模拟器结果响应"""
    id: int
    node_id: int
    session_id: str
    result_data: dict
    score: Optional[float]
    time_spent_seconds: int
    completed: int

    class Config:
        from_attributes = True


@router.post("/results", response_model=SimulatorResultResponse)
async def submit_simulator_result(
    result: SimulatorResultCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    提交模拟器交互结果

    用于记录用户在模拟器中的操作和得分
    """
    # 验证节点存在
    node_result = await db.execute(
        select(CourseNode).where(CourseNode.id == result.node_id)
    )
    node = node_result.scalar_one_or_none()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {result.node_id} not found"
        )

    # 创建结果记录
    simulator_result = SimulatorResult(
        user_id=current_user.id,
        node_id=result.node_id,
        session_id=result.session_id,
        result_data=result.result_data,
        score=result.score,
        time_spent_seconds=result.time_spent_seconds or 0,
        completed=1 if result.completed else 0
    )

    db.add(simulator_result)
    await db.commit()
    await db.refresh(simulator_result)

    return simulator_result


@router.get("/results/{node_id}")
async def get_simulator_results(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户在特定节点的模拟器结果历史
    """
    result = await db.execute(
        select(SimulatorResult)
        .where(
            SimulatorResult.user_id == current_user.id,
            SimulatorResult.node_id == node_id
        )
        .order_by(SimulatorResult.created_at.desc())
    )
    results = result.scalars().all()

    return {
        "node_id": node_id,
        "total_attempts": len(results),
        "results": [
            {
                "id": r.id,
                "session_id": r.session_id,
                "score": r.score,
                "time_spent_seconds": r.time_spent_seconds,
                "completed": r.completed,
                "created_at": r.created_at
            }
            for r in results
        ]
    }


@router.get("/results/{node_id}/best")
async def get_best_simulator_result(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户在特定节点的最佳模拟器结果
    """
    result = await db.execute(
        select(SimulatorResult)
        .where(
            SimulatorResult.user_id == current_user.id,
            SimulatorResult.node_id == node_id,
            SimulatorResult.completed == 1
        )
        .order_by(SimulatorResult.score.desc())
        .limit(1)
    )
    best_result = result.scalar_one_or_none()

    if not best_result:
        return {
            "node_id": node_id,
            "has_completed": False,
            "best_result": None
        }

    return {
        "node_id": node_id,
        "has_completed": True,
        "best_result": {
            "id": best_result.id,
            "session_id": best_result.session_id,
            "score": best_result.score,
            "time_spent_seconds": best_result.time_spent_seconds,
            "created_at": best_result.created_at
        }
    }
