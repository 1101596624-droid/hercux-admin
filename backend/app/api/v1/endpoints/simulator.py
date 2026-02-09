"""
Simulator API endpoints
处理模拟器结果的提交和查询，以及AI代码生成
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from pydantic import BaseModel

from app.db.session import get_db
from app.models.models import SimulatorResult, CourseNode, User
from app.core.security import get_current_user, require_admin

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


class VariableSpec(BaseModel):
    """变量规格"""
    name: str
    min: Optional[float] = 0
    max: Optional[float] = 100
    default: Optional[float] = 50


class GenerateCodeRequest(BaseModel):
    """模拟器代码生成请求"""
    prompt: str
    variables: Optional[List[VariableSpec]] = None


class GenerateCodeResponse(BaseModel):
    """模拟器代码生成响应"""
    custom_code: str
    variables: List[dict]
    name: str
    description: str


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


@router.post("/generate-code", response_model=GenerateCodeResponse)
async def generate_simulator_code(
    request: GenerateCodeRequest,
    current_user: User = Depends(require_admin),
):
    """
    使用AI生成模拟器代码（Admin only）- 经验增强版

    调用 HERCU Agent 服务进行经验晶化增强的代码生成
    """
    import httpx

    # 构建变量列表
    variables_list = None
    if request.variables:
        variables_list = [
            {"name": v.name, "min": v.min, "max": v.max, "default": v.default}
            for v in request.variables
        ]

    # 调用 HERCU Agent API
    agent_url = "http://127.0.0.1:8100/enhance/simulator"
    payload = {
        "topic": request.prompt,
        "subject": "通用",
        "variables": variables_list,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(agent_url, json=payload)
            response.raise_for_status()
            result = response.json()

        # 提取生成的代码
        code = result["code"]
        quality_score = result["quality_score"]

        # 从代码中提取变量（如果未提供）
        if not variables_list:
            from app.services.studio.custom_code_generator import extract_variables_from_code
            used_vars = extract_variables_from_code(code)
            variables_list = [
                {"name": v, "label": v, "min": 0, "max": 100, "default": 50, "step": 1}
                for v in used_vars
            ]

        return GenerateCodeResponse(
            custom_code=code,
            variables=variables_list or [],
            name=request.prompt[:50],
            description=f"{request.prompt} (质量分: {quality_score:.2f})",
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"HERCU Agent 返回错误: {e.response.text}"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="代码生成超时，请稍后重试"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"代码生成失败: {str(e)}"
        )
