"""
Learning Report & Metacognitive API - Phase 5
GET  /report/session          生成单次学习报告
GET  /report/growth           生成成长报告(weekly/monthly)
GET  /report/history          获取报告历史
POST /metacognitive/prompt    获取元认知提示
POST /metacognitive/respond   记录学生回答
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import MetacognitivePromptRequest, MetacognitiveResponseRequest
from app.services.learning_report_service import LearningReportService, MetacognitiveService

router = APIRouter()


@router.get("/report/session")
async def get_session_report(
    minutes_back: int = Query(60, ge=10, le=480),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """生成单次学习会话报告"""
    report = await LearningReportService.generate_session_report(
        db, current_user.id, minutes_back
    )
    await db.commit()
    return report


@router.get("/report/growth")
async def get_growth_report(
    period: str = Query("weekly", pattern="^(weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """生成成长报告"""
    report = await LearningReportService.generate_growth_report(
        db, current_user.id, period
    )
    await db.commit()
    return report


@router.get("/report/history")
async def get_report_history(
    report_type: Optional[str] = Query(None, pattern="^(session|weekly|monthly)$"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取报告历史"""
    history = await LearningReportService.get_report_history(
        db, current_user.id, report_type, limit
    )
    return {"user_id": current_user.id, "reports": history}


@router.post("/metacognitive/prompt")
async def get_metacognitive_prompt(
    data: MetacognitivePromptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取元认知提示"""
    result = await MetacognitiveService.get_prompt(
        db, current_user.id, data.trigger, data.knowledge_node_id
    )
    await db.commit()
    return result


@router.post("/metacognitive/respond")
async def respond_to_prompt(
    data: MetacognitiveResponseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """记录学生对元认知提示的回答"""
    from fastapi import HTTPException
    result = await MetacognitiveService.record_response(
        db, data.log_id, current_user.id, data.response_text
    )
    if not result:
        raise HTTPException(status_code=404, detail="提示记录不存在")
    await db.commit()
    return result
