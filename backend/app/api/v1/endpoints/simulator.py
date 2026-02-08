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
    使用AI生成模拟器代码（Admin only）

    接收用户描述，调用AI生成PixiJS模拟器代码
    """
    from app.services.claude_service import get_claude_service, Message
    from app.services.studio.custom_code_generator import (
        CUSTOM_CODE_SYSTEM_PROMPT,
        get_custom_code_prompt,
        validate_custom_code,
        extract_variables_from_code,
    )

    try:
        claude = get_claude_service()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI 服务不可用: {str(e)}"
        )

    # Build variables list for the prompt
    variables_list = None
    if request.variables:
        variables_list = [
            {"name": v.name, "min": v.min, "max": v.max, "default": v.default}
            for v in request.variables
        ]

    user_prompt = get_custom_code_prompt(
        topic=request.prompt,
        description=request.prompt,
        variables=variables_list,
    )

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            response = await claude.chat_completion(
                messages=[Message(role="user", content=user_prompt)],
                system_prompt=CUSTOM_CODE_SYSTEM_PROMPT,
                temperature=0.7,
                max_tokens=4000,
            )

            # Extract text from Claude response
            content_blocks = response.get("content", [])
            code = ""
            for block in content_blocks:
                if isinstance(block, dict) and block.get("type") == "text":
                    code = block.get("text", "").strip()
                    break

            if not code:
                if attempt < max_retries:
                    continue
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="AI 未返回有效代码"
                )

            # Remove markdown code block markers if present
            if code.startswith("```"):
                lines = code.split("\n")
                code = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

            # Validate
            is_valid, error_msg = validate_custom_code(code)
            if not is_valid:
                if attempt < max_retries:
                    user_prompt += f"\n\n上次生成的代码有问题：{error_msg}，请修正。"
                    continue
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"生成的代码验证失败: {error_msg}"
                )

            # Extract variables used in code
            used_vars = extract_variables_from_code(code)
            variables_output = [
                {"name": v, "label": v, "min": 0, "max": 100, "default": 50, "step": 1}
                for v in used_vars
            ]

            # If user provided variable specs, merge them
            if request.variables:
                var_map = {v.name: v for v in request.variables}
                for vo in variables_output:
                    if vo["name"] in var_map:
                        spec = var_map[vo["name"]]
                        vo["min"] = spec.min
                        vo["max"] = spec.max
                        vo["default"] = spec.default

            return GenerateCodeResponse(
                custom_code=code,
                variables=variables_output,
                name=request.prompt[:50],
                description=request.prompt,
            )

        except HTTPException:
            raise
        except Exception as e:
            if attempt < max_retries:
                continue
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"代码生成失败: {str(e)}"
            )
