"""
Tavily Search API 集成服务
用于让 AI 获取最新的网络信息
"""

import httpx
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.core.config import settings


class SearchResult(BaseModel):
    """搜索结果"""
    title: str
    url: str
    content: str
    score: float = 0.0


class TavilySearchResponse(BaseModel):
    """Tavily 搜索响应"""
    query: str
    results: List[SearchResult]
    answer: Optional[str] = None  # Tavily 可以返回综合答案


class TavilyService:
    """Tavily Search API 服务类"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'TAVILY_API_KEY', None)
        self.base_url = "https://api.tavily.com"

        if not self.api_key:
            print("[WARN] TAVILY_API_KEY not configured, search will be disabled")

    async def search(
        self,
        query: str,
        search_depth: str = "basic",  # "basic" or "advanced"
        max_results: int = 5,
        include_answer: bool = True,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> TavilySearchResponse:
        """
        执行网络搜索

        Args:
            query: 搜索查询
            search_depth: 搜索深度 ("basic" 快速, "advanced" 深度)
            max_results: 最大结果数
            include_answer: 是否包含综合答案
            include_domains: 只搜索这些域名
            exclude_domains: 排除这些域名

        Returns:
            搜索结果
        """
        if not self.api_key:
            return TavilySearchResponse(
                query=query,
                results=[],
                answer="搜索功能未配置，请联系管理员"
            )

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": include_answer
        }

        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                results = [
                    SearchResult(
                        title=r.get("title", ""),
                        url=r.get("url", ""),
                        content=r.get("content", ""),
                        score=r.get("score", 0.0)
                    )
                    for r in data.get("results", [])
                ]

                return TavilySearchResponse(
                    query=query,
                    results=results,
                    answer=data.get("answer")
                )

        except httpx.HTTPError as e:
            print(f"[ERROR] Tavily search failed: {e}")
            return TavilySearchResponse(
                query=query,
                results=[],
                answer=f"搜索失败: {str(e)}"
            )

    async def search_for_context(
        self,
        topic: str,
        context_type: str = "general"
    ) -> str:
        """
        为 AI 上下文搜索最新信息

        Args:
            topic: 搜索主题
            context_type: 上下文类型 ("general", "academic", "news")

        Returns:
            格式化的搜索结果文本
        """
        # 根据类型调整搜索
        search_depth = "advanced" if context_type == "academic" else "basic"

        # 添加时间限定词以获取最新信息
        query = f"{topic} 最新 2026"

        result = await self.search(
            query=query,
            search_depth=search_depth,
            max_results=3,
            include_answer=True
        )

        if not result.results and not result.answer:
            return ""

        # 格式化为 AI 可用的上下文
        context_parts = []

        if result.answer:
            context_parts.append(f"【最新信息摘要】\n{result.answer}")

        if result.results:
            context_parts.append("\n【参考来源】")
            for i, r in enumerate(result.results[:3], 1):
                context_parts.append(f"{i}. {r.title}")
                context_parts.append(f"   {r.content[:200]}...")
                context_parts.append(f"   来源: {r.url}")

        return "\n".join(context_parts)


# 全局实例
_tavily_service: Optional[TavilyService] = None


def get_tavily_service() -> TavilyService:
    """获取 Tavily 服务实例（单例模式）"""
    global _tavily_service

    if _tavily_service is None:
        _tavily_service = TavilyService()

    return _tavily_service
