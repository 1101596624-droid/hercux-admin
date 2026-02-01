"""
AI 导师对话 API - 简化版本
直接使用 DeepSeek API，不依赖数据库配置
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from app.services.deepseek_service import get_deepseek_service, Message

router = APIRouter(tags=["AI Tutor"])


class ChatRequest(BaseModel):
    """聊天请求"""
    node_id: int
    message: str
    conversation_history: List[Dict[str, str]] = []
    current_layer: str = "L1"


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str
    suggestions: Optional[List[str]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_tutor(request: ChatRequest):
    """
    与 AI 导师对话

    Args:
        request: 聊天请求

    Returns:
        AI 导师回复
    """
    try:
        # 暂时返回固定消息用于测试
        return ChatResponse(message=f"你好！我收到了你的消息：{request.message}。AI 导师功能正在调试中。")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")


@router.get("/welcome/{node_id}")
async def get_welcome_message(node_id: int):
    """获取欢迎消息"""
    return {"message": f"欢迎学习节点 {node_id}！我是你的 AI 学习助手，有任何问题都可以问我。"}


@router.get("/completion/{node_id}")
async def get_completion_message(node_id: int):
    """获取完成消息"""
    return {"message": f"恭喜完成节点 {node_id} 的学习！继续加油！"}
