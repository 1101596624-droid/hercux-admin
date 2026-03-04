"""
Grinder API - 做题家模块后端代理
支持监督式题目生成，确保内容质量和时效性
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional
from sqlalchemy.orm import Session
import httpx
import json
import ssl
import certifi
import logging

from app.models.models import User
from app.core.security import get_current_user
from app.core.config import settings
from app.services.grinder.service import get_grinder_service
from app.db.session import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

# 输入限制 (用户输入在前端限制，后端代理需要支持更长的内部调用如 SVG 监督者检查)
from app.core.constants import MAX_MESSAGE_LENGTH_INTERNAL as MAX_MESSAGE_LENGTH


def sanitize_text(text: str) -> str:
    """过滤特殊字符，防止 API 报错"""
    if not text:
        return text
    return (
        text
        # 移除控制字符 (ASCII 0-31, 127)，保留换行(\n)和制表符(\t)
        .replace('\r', '\n')
        .translate(str.maketrans('', '', ''.join(chr(i) for i in range(32) if i not in (9, 10)) + chr(127)))
        # 移除零宽字符
        .replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
        .replace('\ufeff', '').replace('\u2060', '').replace('\u00ad', '')
    )


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

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """验证并清理消息内容"""
        v = sanitize_text(v)
        if len(v) > MAX_MESSAGE_LENGTH:
            raise ValueError(f'消息过长，最多 {MAX_MESSAGE_LENGTH} 字符，请精简后重新输入')
        return v


class ChatRequest(BaseModel):
    model: str
    max_tokens: int
    messages: List[Message]
    system: Optional[str] = None
    stream: Optional[bool] = False

    @field_validator('system')
    @classmethod
    def validate_system(cls, v: Optional[str]) -> Optional[str]:
        """清理系统提示"""
        if v:
            return sanitize_text(v)
        return v


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

    # 重试机制，最多重试 3 次
    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
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
        except HTTPException:
            raise
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                logger.warning(f"Claude API call failed (attempt {attempt + 1}/{max_retries}): {last_error}")
                import asyncio
                await asyncio.sleep(1)  # 等待 1 秒后重试
                continue
            raise HTTPException(
                status_code=500,
                detail=f"Failed to call Claude API after {max_retries} attempts: {last_error}"
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


# ============ 监督式题目生成 API ============

class ExamGenerateRequest(BaseModel):
    """考试生成请求"""
    topic: str
    question_count: int = 5
    focus_categories: Optional[List[str]] = None


@router.post("/generate-exam")
async def generate_exam_supervised(
    request: ExamGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    监督式生成考试题目 + 学习集成

    特点：
    1. 自动搜索最新信息确保内容时效性
    2. AI 监督者审核题目质量
    3. 验证答案正确性
    4. 自动修复 JSON 格式问题
    5. 使用QuizScorer对审核通过的题目评分 (NEW)
    6. 85+分的题目自动保存为学习模板 (NEW)
    """
    try:
        logger.info(f"Generating supervised exam for topic: {request.topic}")

        # 使用数据库会话创建service
        grinder_service = get_grinder_service(db)

        result = await grinder_service.generate_exam(
            topic=request.topic,
            question_count=request.question_count,
            focus_categories=request.focus_categories
        )

        # 提取质量评分结果
        review = result.get('review', {})
        quality_results = review.get('quality_results', {})

        return {
            "success": True,
            "exam": result.get('exam'),
            "review": {
                "approved": review.get('approved', False),
                "score": review.get('score', 0),
                "issues": review.get('issues', []),
                "suggestions": review.get('suggestions', [])
            },
            "quality_evaluation": {
                "total_evaluated": quality_results.get('total_evaluated', 0),
                "high_quality_count": quality_results.get('high_quality_count', 0),
                "saved_as_template": quality_results.get('saved_as_template', 0),
                "quality_scores": quality_results.get('quality_scores', []),
                "saved_questions": quality_results.get('saved_questions', [])
            },
            "metadata": {
                "latest_info_used": result.get('latest_info_used', False),
                "generation_attempts": result.get('attempts', 1),
                "warning": result.get('warning')
            }
        }

    except ValueError as e:
        logger.error(f"Exam generation failed: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"题目生成失败: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in exam generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"服务器错误: {str(e)}"
        )
