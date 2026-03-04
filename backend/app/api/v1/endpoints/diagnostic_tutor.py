"""
Diagnostic Tutor API - Phase 3 诊断式AI Tutor
情感感知 + BKT状态 + 多轮苏格拉底式对话
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import StartConversationRequest, SendMessageRequest
from app.services.diagnostic_tutor_service import DiagnosticTutorService

router = APIRouter()


@router.post("/start")
async def start_conversation(
    data: StartConversationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """开始诊断式对话"""
    result = await DiagnosticTutorService.start_conversation(
        db=db,
        user_id=current_user.id,
        knowledge_node_id=data.knowledge_node_id,
        mode=data.mode,
        initial_message=data.initial_message,
    )
    await db.commit()
    return result


@router.post("/message")
async def send_message(
    data: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """在对话中发送消息"""
    try:
        result = await DiagnosticTutorService.send_message(
            db=db,
            user_id=current_user.id,
            session_id=data.session_id,
            message=data.message,
        )
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/conversation/{session_id}")
async def get_conversation(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取对话详情"""
    result = await DiagnosticTutorService.get_conversation(
        db=db, user_id=current_user.id, session_id=session_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="对话不存在")
    return result


@router.get("/history")
async def get_conversation_history(
    knowledge_node_id: Optional[int] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取对话历史列表"""
    return await DiagnosticTutorService.get_conversation_history(
        db=db,
        user_id=current_user.id,
        knowledge_node_id=knowledge_node_id,
        limit=limit,
    )
