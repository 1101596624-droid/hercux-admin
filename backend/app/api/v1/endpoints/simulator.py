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
from app.core.config import settings

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


class GenerateCodeTaskCreateResponse(BaseModel):
    """异步生成任务创建响应"""
    task_id: str
    status: str
    queue_depth: int
    retry_of: Optional[str] = None


class GenerateCodeTaskStatusResponse(BaseModel):
    """异步生成任务状态响应"""
    task_id: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    current_stage: Optional[str] = None
    stage_message: Optional[str] = None
    stage_updated_at: Optional[str] = None
    stage_history: Optional[List[dict]] = None
    queue_wait_seconds: Optional[float] = None
    running_seconds: Optional[float] = None
    total_elapsed_seconds: Optional[float] = None
    cancel_requested_at: Optional[str] = None
    result: Optional[GenerateCodeResponse] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


def _build_variables_list(variables: Optional[List[VariableSpec]]) -> Optional[List[dict]]:
    if not variables:
        return None
    return [
        {"name": v.name, "min": v.min, "max": v.max, "default": v.default}
        for v in variables
    ]


def _build_generate_response(
    prompt: str,
    agent_result: dict,
    variables_list: Optional[List[dict]],
) -> GenerateCodeResponse:
    code = (agent_result.get("code") or "").strip()
    if not code:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="HERCU Agent 返回空代码",
        )

    quality_score = float(agent_result.get("quality_score") or 0.0)

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
        name=prompt[:50],
        description=f"{prompt} (质量分: {quality_score:.2f})",
    )


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
    variables_list = _build_variables_list(request.variables)

    # 调用 HERCU Agent API
    agent_url = f"{settings.AGENT_BASE_URL}/enhance/simulator"
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

        return _build_generate_response(
            prompt=request.prompt,
            agent_result=result,
            variables_list=variables_list,
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


@router.post("/generate-code/tasks", response_model=GenerateCodeTaskCreateResponse)
async def create_simulator_code_task(
    request: GenerateCodeRequest,
    current_user: User = Depends(require_admin),
):
    """
    创建模拟器代码异步生成任务（Admin only）
    """
    import httpx

    variables_list = _build_variables_list(request.variables)
    agent_url = f"{settings.AGENT_BASE_URL}/enhance/simulator/tasks"
    payload = {
        "topic": request.prompt,
        "subject": "通用",
        "variables": variables_list,
    }

    try:
        timeout = httpx.Timeout(connect=10.0, read=20.0, write=20.0, pool=20.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(agent_url, json=payload)
            response.raise_for_status()
            result = response.json()

        return GenerateCodeTaskCreateResponse(
            task_id=result["task_id"],
            status=result.get("status", "queued"),
            queue_depth=int(result.get("queue_depth", 0)),
            retry_of=result.get("retry_of"),
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"HERCU Agent 返回错误: {e.response.text}"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="任务创建超时，请稍后重试"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务创建失败: {str(e)}"
        )


@router.get("/generate-code/tasks/{task_id}", response_model=GenerateCodeTaskStatusResponse)
async def get_simulator_code_task_status(
    task_id: str,
    current_user: User = Depends(require_admin),
):
    """
    查询模拟器代码异步生成任务状态（Admin only）
    """
    import httpx

    agent_url = f"{settings.AGENT_BASE_URL}/enhance/simulator/tasks/{task_id}"

    try:
        timeout = httpx.Timeout(connect=10.0, read=20.0, write=20.0, pool=20.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(agent_url)
            response.raise_for_status()
            task_data = response.json()

        prompt = (task_data.get("request") or {}).get("topic") or "模拟器生成"
        task_vars = (task_data.get("request") or {}).get("variables")
        variables_list = task_vars if isinstance(task_vars, list) else None

        result_payload = None
        raw_result = task_data.get("result")
        if isinstance(raw_result, dict) and raw_result.get("code"):
            result_payload = _build_generate_response(
                prompt=prompt,
                agent_result=raw_result,
                variables_list=variables_list,
            )

        return GenerateCodeTaskStatusResponse(
            task_id=task_data["task_id"],
            status=task_data.get("status", "queued"),
            created_at=task_data.get("created_at", ""),
            started_at=task_data.get("started_at"),
            finished_at=task_data.get("finished_at"),
            current_stage=task_data.get("current_stage"),
            stage_message=task_data.get("stage_message"),
            stage_updated_at=task_data.get("stage_updated_at"),
            stage_history=task_data.get("stage_history"),
            queue_wait_seconds=task_data.get("queue_wait_seconds"),
            running_seconds=task_data.get("running_seconds"),
            total_elapsed_seconds=task_data.get("total_elapsed_seconds"),
            cancel_requested_at=task_data.get("cancel_requested_at"),
            result=result_payload,
            error_code=task_data.get("error_code"),
            error_message=task_data.get("error_message"),
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"HERCU Agent 返回错误: {e.response.text}"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="任务状态查询超时，请稍后重试"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务状态查询失败: {str(e)}"
        )


@router.post("/generate-code/tasks/{task_id}/cancel", response_model=GenerateCodeTaskStatusResponse)
async def cancel_simulator_code_task(
    task_id: str,
    current_user: User = Depends(require_admin),
):
    """
    取消模拟器代码异步生成任务（Admin only）
    """
    import httpx

    agent_url = f"{settings.AGENT_BASE_URL}/enhance/simulator/tasks/{task_id}/cancel"

    try:
        timeout = httpx.Timeout(connect=10.0, read=20.0, write=20.0, pool=20.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(agent_url)
            response.raise_for_status()
            task_data = response.json()

        prompt = (task_data.get("request") or {}).get("topic") or "模拟器生成"
        task_vars = (task_data.get("request") or {}).get("variables")
        variables_list = task_vars if isinstance(task_vars, list) else None

        result_payload = None
        raw_result = task_data.get("result")
        if isinstance(raw_result, dict) and raw_result.get("code"):
            result_payload = _build_generate_response(
                prompt=prompt,
                agent_result=raw_result,
                variables_list=variables_list,
            )

        return GenerateCodeTaskStatusResponse(
            task_id=task_data["task_id"],
            status=task_data.get("status", "queued"),
            created_at=task_data.get("created_at", ""),
            started_at=task_data.get("started_at"),
            finished_at=task_data.get("finished_at"),
            current_stage=task_data.get("current_stage"),
            stage_message=task_data.get("stage_message"),
            stage_updated_at=task_data.get("stage_updated_at"),
            stage_history=task_data.get("stage_history"),
            queue_wait_seconds=task_data.get("queue_wait_seconds"),
            running_seconds=task_data.get("running_seconds"),
            total_elapsed_seconds=task_data.get("total_elapsed_seconds"),
            cancel_requested_at=task_data.get("cancel_requested_at"),
            result=result_payload,
            error_code=task_data.get("error_code"),
            error_message=task_data.get("error_message"),
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"HERCU Agent 返回错误: {e.response.text}"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="任务取消请求超时，请稍后重试"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务取消失败: {str(e)}"
        )


@router.post("/generate-code/tasks/{task_id}/retry", response_model=GenerateCodeTaskCreateResponse)
async def retry_simulator_code_task(
    task_id: str,
    current_user: User = Depends(require_admin),
):
    """
    重试已结束的模拟器代码异步任务（Admin only）
    """
    import httpx

    agent_url = f"{settings.AGENT_BASE_URL}/enhance/simulator/tasks/{task_id}/retry"

    try:
        timeout = httpx.Timeout(connect=10.0, read=20.0, write=20.0, pool=20.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(agent_url)
            response.raise_for_status()
            result = response.json()

        return GenerateCodeTaskCreateResponse(
            task_id=result["task_id"],
            status=result.get("status", "queued"),
            queue_depth=int(result.get("queue_depth", 0)),
            retry_of=result.get("retry_of"),
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"HERCU Agent 返回错误: {e.response.text}"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="任务重试请求超时，请稍后重试"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务重试失败: {str(e)}"
        )
