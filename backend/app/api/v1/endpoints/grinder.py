"""
Grinder API - 做题家模块后端代理
代理前端请求到 Claude API
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import httpx
import json
import ssl
import certifi

from app.models.models import User
from app.core.security import get_current_user
from app.core.config import settings

router = APIRouter()


# 创建使用 certifi 证书的 SSL 上下文
def get_ssl_context():
    """获取配置了 certifi CA 证书的 SSL 上下文"""
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return ssl_context


# Claude API 配置 - 从 settings 读取
# 处理 BASE_URL 可能已包含 /api 或 /v1 的情况
_base = settings.ANTHROPIC_BASE_URL.rstrip('/')
if _base.endswith('/api'):
    CLAUDE_API_URL = f"{_base}/v1/messages"
elif _base.endswith('/v1'):
    CLAUDE_API_URL = f"{_base}/messages"
else:
    CLAUDE_API_URL = f"{_base}/v1/messages"

# 支持两种配置名称
CLAUDE_API_KEY = getattr(settings, 'ANTHROPIC_AUTH_TOKEN', None) or settings.ANTHROPIC_API_KEY


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    max_tokens: int
    messages: List[Message]
    system: Optional[str] = None
    stream: Optional[bool] = False


class ContentBlock(BaseModel):
    type: str
    text: str


class ChatResponse(BaseModel):
    id: str
    type: str
    role: str
    content: List[ContentBlock]
    model: str
    stop_reason: str
    usage: dict


@router.post("/chat")
async def grinder_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    代理 Claude API 请求
    用于做题家模块的 AI 题目生成和对话
    """
    if not CLAUDE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Claude API key not configured"
        )

    headers = {
        "Content-Type": "application/json",
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
    }

    payload = {
        "model": request.model,
        "max_tokens": request.max_tokens,
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
    }

    if request.system:
        payload["system"] = request.system

    try:
        async with httpx.AsyncClient(timeout=120.0, verify=get_ssl_context()) as client:
            response = await client.post(
                CLAUDE_API_URL,
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Claude API error: {response.text}"
                )

            return response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Claude API request timed out"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to call Claude API: {str(e)}"
        )


@router.post("/chat/stream")
async def grinder_chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    代理 Claude API 流式请求
    用于实时显示 AI 生成内容
    """
    if not CLAUDE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Claude API key not configured"
        )

    headers = {
        "Content-Type": "application/json",
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
    }

    payload = {
        "model": request.model,
        "max_tokens": request.max_tokens,
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
        "stream": True,
    }

    if request.system:
        payload["system"] = request.system

    async def generate():
        try:
            async with httpx.AsyncClient(timeout=180.0, verify=get_ssl_context()) as client:
                async with client.stream(
                    "POST",
                    CLAUDE_API_URL,
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        yield f"data: {json.dumps({'error': error_text.decode()})}\n\n"
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                yield "data: [DONE]\n\n"
                                break
                            try:
                                parsed = json.loads(data)
                                # 提取文本内容
                                if parsed.get("type") == "content_block_delta":
                                    delta = parsed.get("delta", {})
                                    if delta.get("type") == "text_delta":
                                        text = delta.get("text", "")
                                        if text:
                                            # 发送两种格式以兼容前端
                                            yield f"data: {json.dumps({'text': text, 'delta': {'text': text}})}\n\n"
                                elif parsed.get("type") == "message_stop":
                                    yield "data: [DONE]\n\n"
                            except json.JSONDecodeError:
                                pass
        except httpx.TimeoutException:
            yield f"data: {json.dumps({'error': 'Request timed out'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
