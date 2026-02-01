"""
AI 导师 - 临时模拟版本
用于测试前端功能，返回模拟的 AI 响应
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional
import random

router = APIRouter(tags=["AI Tutor Mock"])


class ChatRequest(BaseModel):
    node_id: int
    message: str
    conversation_history: List[Dict[str, str]] = []
    current_layer: str = "L1"


class ChatResponse(BaseModel):
    message: str
    suggestions: Optional[List[str]] = None


# 预设的响应模板
RESPONSES = [
    "这是一个很好的问题！让我来帮你理解这个概念。",
    "我理解你的困惑。让我们一步一步来分析。",
    "很高兴看到你在思考这个问题。",
    "这个知识点确实需要仔细理解。",
    "你提出了一个关键的问题。",
]

SUGGESTIONS = [
    "能再详细解释一下吗？",
    "这个在实际中如何应用？",
    "有什么常见的误区？",
    "能举个例子吗？",
]


@router.post("/chat", response_model=ChatResponse)
async def chat_with_tutor(request: ChatRequest):
    """
    与 AI 导师对话（模拟版本）
    """
    # 根据用户消息生成响应
    response_text = random.choice(RESPONSES)
    response_text += f"\n\n关于你的问题「{request.message}」，"

    if "什么" in request.message or "是什么" in request.message:
        response_text += "这是一个定义性的问题。让我为你解释一下核心概念。"
    elif "为什么" in request.message or "怎么" in request.message:
        response_text += "这涉及到原理和机制。让我们深入探讨一下。"
    elif "如何" in request.message or "怎样" in request.message:
        response_text += "这是一个应用性的问题。让我给你一些实用的建议。"
    else:
        response_text += "让我根据当前的学习内容来回答你。"

    response_text += f"\n\n当前你正在学习节点 {request.node_id} 的 {request.current_layer} 层内容。"
    response_text += "\n\n💡 提示：真实的 AI 导师功能正在开发中，目前显示的是模拟响应。"

    return ChatResponse(
        message=response_text,
        suggestions=random.sample(SUGGESTIONS, 3)
    )


@router.get("/welcome/{node_id}")
async def get_welcome_message(node_id: int):
    """获取欢迎消息"""
    return {
        "message": f"👋 欢迎学习节点 {node_id}！我是你的 AI 学习助手。\n\n在学习过程中，你可以随时向我提问。我会根据你的学习进度和问题，提供个性化的指导和解答。\n\n现在，让我们开始学习吧！"
    }


@router.get("/completion/{node_id}")
async def get_completion_message(node_id: int):
    """获取完成消息"""
    return {
        "message": f"🎉 恭喜你完成节点 {node_id} 的学习！\n\n你已经掌握了这部分的核心知识。如果还有任何疑问，随时可以回来复习或向我提问。\n\n继续加油，向下一个节点前进吧！"
    }
