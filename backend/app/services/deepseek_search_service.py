"""
DeepSeek Search 服务 - 替代 Tavily，用 DeepSeek chat API 获取知识信息
"""

import httpx
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class DeepSeekSearchService:
    """用 DeepSeek chat API 提供搜索/知识查询能力"""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY not configured, search will be disabled")

    async def search_for_context(
        self,
        topic: str,
        context_type: str = "general"
    ) -> str:
        """
        用 DeepSeek 获取主题相关的知识信息

        Args:
            topic: 搜索主题
            context_type: 上下文类型 ("general", "academic", "educational", "news")

        Returns:
            格式化的知识信息文本
        """
        if not self.api_key:
            return ""

        type_prompts = {
            "academic": "请从学术角度",
            "educational": "请从教育教学角度",
            "news": "请从最新动态角度",
            "general": "请",
        }
        prefix = type_prompts.get(context_type, "请")

        prompt = (
            f"{prefix}简要介绍"{topic}"的核心知识点和关键信息。"
            f"要求：\n"
            f"1. 内容准确、简洁，300字以内\n"
            f"2. 突出重点概念和原理\n"
            f"3. 如有常见误区请指出\n"
            f"只输出知识内容，不要寒暄。"
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 1024,
                        "temperature": 0.3,
                    },
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()

                if content:
                    return f"【知识参考】\n{content}"
                return ""

        except Exception as e:
            logger.warning(f"DeepSeek search failed for '{topic}': {e}")
            return ""


_service: Optional[DeepSeekSearchService] = None


def get_search_service() -> DeepSeekSearchService:
    """获取搜索服务实例（单例）"""
    global _service
    if _service is None:
        _service = DeepSeekSearchService()
    return _service
