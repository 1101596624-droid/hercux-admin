from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.schemas.schemas import (
    TrainingPlanCreate,
    TrainingPlanResponse,
    AIGeneratePlanRequest,
    AIGeneratePlanResponse,
    AIAdjustPlanRequest
)
from app.services.ai_service import AIService
from app.models.models import TrainingPlan, User
from app.core.security import get_current_user

router = APIRouter()


@router.post("/generate-plan", response_model=AIGeneratePlanResponse)
async def generate_training_plan(
    request: AIGeneratePlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI training plan

    Takes user parameters and generates a structured 12-week plan
    """
    # Initialize AI service
    ai_service = AIService(db)

    # Generate plan
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

    # Save plan to database
    training_plan = TrainingPlan(
        user_id=current_user.id,
        title=plan_data.get("title", f"{request.goal} - {request.duration_weeks}周计划"),
        plan_data=plan_data,
        status="active"
    )
    db.add(training_plan)
    await db.commit()
    await db.refresh(training_plan)

    return AIGeneratePlanResponse(
        plan_data=plan_data
    )


@router.get("/plans/{plan_id}", response_model=TrainingPlanResponse)
async def get_training_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed training plan"""
    plan = await db.get(TrainingPlan, plan_id)

    if not plan:
        raise HTTPException(status_code=404, detail="Training plan not found")

    if plan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this plan")

    return TrainingPlanResponse(
        id=plan.id,
        title=plan.title,
        plan_data=plan.plan_data,
        status=plan.status,
        start_date=plan.start_date,
        end_date=plan.end_date,
        created_at=plan.created_at
    )


@router.post("/adjust-plan")
async def adjust_training_plan(
    request: AIAdjustPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    AI-powered plan adjustment

    Accepts natural language instructions like:
    - "Change Wednesday to recovery day"
    - "Replace squats with leg press"
    """
    # Get the plan
    plan = await db.get(TrainingPlan, request.plan_id)

    if not plan:
        raise HTTPException(status_code=404, detail="Training plan not found")

    if plan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this plan")

    # Initialize AI service
    ai_service = AIService(db)

    # Adjust plan using AI
    updated_plan_data = await ai_service.adjust_training_plan(
        plan_id=request.plan_id,
        current_plan=plan.plan_data,
        adjustment_request=request.adjustment_request
    )

    # Update plan in database
    plan.plan_data = updated_plan_data
    await db.commit()

    return {
        "message": "Plan adjusted successfully",
        "plan_id": request.plan_id,
        "updated_plan": updated_plan_data
    }


@router.get("/plans", response_model=List[TrainingPlanResponse])
async def get_user_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all user training plans"""
    stmt = select(TrainingPlan).where(TrainingPlan.user_id == current_user.id)
    result = await db.execute(stmt)
    plans = result.scalars().all()

    return [
        TrainingPlanResponse(
            id=plan.id,
            title=plan.title,
            plan_data=plan.plan_data,
            status=plan.status,
            start_date=plan.start_date,
            end_date=plan.end_date,
            created_at=plan.created_at
        )
        for plan in plans
    ]
