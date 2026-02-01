"""
Public Analytics API
Handles token usage reporting and other public analytics endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.models.models import TokenUsage, User
from app.core.security import get_current_user_optional

router = APIRouter()


class TokenUsageCreate(BaseModel):
    """Token usage report request"""
    feature: str  # ai_training_plan, ai_tutor, etc.
    model: str  # claude-sonnet-4-20250514
    input_tokens: int
    output_tokens: int
    total_tokens: int
    plan_id: Optional[str] = None
    metadata: Optional[dict] = None
    timestamp: Optional[str] = None


class TokenUsageResponse(BaseModel):
    """Token usage report response"""
    success: bool
    id: Optional[int] = None
    message: str


@router.post("/analytics/token-usage", response_model=TokenUsageResponse)
async def report_token_usage(
    data: TokenUsageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Report AI token usage for analytics tracking.

    This endpoint accepts token usage data from the frontend and stores it
    in the database for analytics purposes. Authentication is optional -
    if a user is logged in, their user_id will be associated with the record
    and their cumulative token usage will be updated.
    """
    try:
        # Create token usage record
        token_usage = TokenUsage(
            user_id=current_user.id if current_user else None,
            feature=data.feature,
            model=data.model,
            input_tokens=data.input_tokens,
            output_tokens=data.output_tokens,
            total_tokens=data.total_tokens,
            plan_id=data.plan_id,
            extra_data=data.metadata
        )

        db.add(token_usage)

        # Update user's cumulative token usage if logged in
        if current_user:
            await db.execute(
                update(User)
                .where(User.id == current_user.id)
                .values(
                    total_tokens_used=User.total_tokens_used + data.total_tokens,
                    total_input_tokens=User.total_input_tokens + data.input_tokens,
                    total_output_tokens=User.total_output_tokens + data.output_tokens
                )
            )

        await db.commit()
        await db.refresh(token_usage)

        return TokenUsageResponse(
            success=True,
            id=token_usage.id,
            message="Token usage recorded successfully"
        )
    except Exception as e:
        await db.rollback()
        # Log error but don't fail the request - this is analytics, not critical
        print(f"Failed to record token usage: {e}")
        return TokenUsageResponse(
            success=False,
            message=f"Failed to record: {str(e)}"
        )
