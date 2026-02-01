from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.schemas import (
    AIGuideChatRequest,
    AIGuideChatResponse,
    AIGeneratePlanRequest,
    AIGeneratePlanResponse
)
from app.services.ai_service import AIService
from app.models.models import CourseNode, User
from app.core.security import get_current_user

router = APIRouter()


@router.post("/guide-chat", response_model=AIGuideChatResponse)
async def ai_guide_chat(
    request: AIGuideChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    AI Guide conversation endpoint

    The "Right Sidebar AI Tutor" uses this endpoint.
    Provides Socratic questioning based on:
    - Current node context
    - User's question/response
    - Simulator state (if applicable)
    """
    # Convert node_id to int if it's a string
    try:
        node_id = int(request.node_id) if isinstance(request.node_id, str) else request.node_id
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid node_id format")

    # Get node information
    node = await db.get(CourseNode, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Initialize AI service
    ai_service = AIService(db)

    # Get AI response
    response_text = await ai_service.guide_chat(
        user_id=current_user.id,
        node_id=node_id,
        user_message=request.user_message,
        node_context=request.context
    )

    # Generate suggestions based on node type
    suggestions = []
    if node.type.value == "simulator":
        suggestions = [
            "这个参数如果改变会发生什么？",
            "为什么会出现这个结果？",
            "能解释一下背后的原理吗？"
        ]
    elif node.type.value == "video":
        suggestions = [
            "能再解释一下这个概念吗？",
            "这个在实际中如何应用？",
            "有什么常见的误区？"
        ]
    elif node.type.value == "quiz":
        suggestions = [
            "为什么这个答案是正确的？",
            "其他选项错在哪里？",
            "有什么记忆技巧吗？"
        ]

    return AIGuideChatResponse(
        response=response_text,
        suggestions=suggestions
    )


@router.post("/generate-plan", response_model=AIGeneratePlanResponse)
async def generate_plan(
    request: AIGeneratePlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate structured training plan using AI

    This is the core of Module 5 (AI Training Planner)
    """
    # Initialize AI service
    ai_service = AIService(db)

    # Generate training plan
    plan_data = await ai_service.generate_training_plan(
        user_id=current_user.id,
        role=request.role,
        goal=request.goal,
        weeks=request.duration_weeks,
        sessions_per_week=request.sessions_per_week,
        experience_level=request.experience_level,
        available_equipment=request.available_equipment,
        constraints=request.constraints
    )

    return AIGeneratePlanResponse(
        plan_data=plan_data
    )
