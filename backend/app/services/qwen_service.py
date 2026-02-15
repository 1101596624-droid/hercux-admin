"""
Qwen (千问) API 集成服务
兼容 OpenAI API 格式
"""

import json
import ssl
import certifi
from typing import List, Dict, Optional, AsyncGenerator
import httpx
from pydantic import BaseModel
from app.core.config import settings


def get_ssl_context():
    """获取配置了 certifi CA 证书的 SSL 上下文"""
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return ssl_context


class Message(BaseModel):
    role: str  # 'user', 'assistant', 'system'
    content: str


class QwenService:
    """Qwen API 服务类（OpenAI 兼容格式）"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'QWEN_API_KEY', settings.ANTHROPIC_API_KEY)
        self.base_url = base_url or getattr(settings, 'QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.model = getattr(settings, 'QWEN_MODEL', 'qwen-plus')

        if not self.api_key:
            raise ValueError("QWEN_API_KEY environment variable is required")

    async def chat_completion(
        self,
        messages: List[Message],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict:
        """
        调用 Qwen Chat API (OpenAI 兼容格式)

        Args:
            messages: 对话历史
            system_prompt: 系统提示词
            temperature: 温度参数 (0-2)
            max_tokens: 最大生成 token 数

        Returns:
            API 响应
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # OpenAI 格式：system 消息放在 messages 数组开头
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})

        api_messages.extend([{"role": msg.role, "content": msg.content} for msg in messages])

        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(timeout=120.0, verify=get_ssl_context()) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )

            response.raise_for_status()
            result = response.json()

            # 转换为 Claude 兼容格式
            return {
                "content": [{"text": result["choices"][0]["message"]["content"]}],
                "model": result["model"],
                "usage": result.get("usage", {})
            }

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ):
        """
        流式生成响应

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数

        Yields:
            生成的文本块
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=300.0, verify=get_ssl_context()) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line or not line.strip():
                        continue

                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            # OpenAI 流式响应格式
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

    async def generate_raw_response(
        self,
        messages: List[Dict] = None,
        prompt: str = None,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        生成原始响应（兼容 ClaudeService 接口）

        Args:
            messages: 消息列表（优先使用）
            prompt: 提示词（如果没有messages）
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            原始响应文本
        """
        msg_list = []

        # 添加系统提示词
        if system_prompt:
            msg_list.append(Message(role="system", content=system_prompt))

        # 处理消息列表或单个提示词
        if messages:
            for msg in messages:
                msg_list.append(Message(role=msg.get("role", "user"), content=msg.get("content", "")))
        elif prompt:
            msg_list.append(Message(role="user", content=prompt))
        else:
            raise ValueError("Either messages or prompt must be provided")

        response = await self.chat_completion(msg_list, temperature=temperature, max_tokens=max_tokens)

        return response["content"][0]["text"]

    async def generate_with_json_mode(
        self,
        messages: List[Dict],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        生成 JSON 格式响应（兼容 ClaudeService 接口）
        """
        return await self.generate_raw_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

    async def generate_tutor_response(
        self,
        user_message: str,
        context: Dict,
        conversation_history: List[Message]
    ) -> str:
        """
        生成 AI 导师回复（兼容接口）

        Args:
            user_message: 用户消息
            context: 上下文信息
            conversation_history: 对话历史

        Returns:
            AI 导师回复
        """
        # 构建系统提示词
        system_prompt = self._build_system_prompt(context)

        # 构建消息列表
        messages = [Message(role="system", content=system_prompt)]
        messages.extend(conversation_history[-20:])
        messages.append(Message(role="user", content=user_message))

        # 调用 API
        response = await self.chat_completion(messages, temperature=0.7)

        return response["content"][0]["text"]

    def _build_system_prompt(self, context: Dict) -> str:
        """构建系统提示词"""
        node = context.get("node", {})
        ai_tutor_config = context.get("ai_tutor_config", {})

        persona = ai_tutor_config.get(
            "tutor_persona",
            "专业但友好的导师，善于用生活化的比喻解释复杂概念"
        )

        node_title = node.get("title", "")
        learning_objectives = node.get("learning_objectives", [])

        prompt = f"""你是一位{persona}。

当前教学场景：
- 课程节点：{node_title}
- 学习目标：{', '.join(learning_objectives)}

你的职责：
1. 根据学生的问题和当前学习进度，提供个性化的引导和解答
2. 使用生活化的比喻和例子帮助学生理解抽象概念
3. 鼓励学生主动思考，而不是直接给出答案
4. 识别学生的误区并温和地纠正

对话风格：
- 友好、耐心、鼓励性
- 使用简洁的语言，避免过于学术化
- 根据学生的理解程度调整解释的深度
"""
        return prompt


# 全局实例
_qwen_service: Optional[QwenService] = None


def get_qwen_service() -> QwenService:
    """获取 Qwen 服务实例（单例模式）"""
    global _qwen_service

    if _qwen_service is None:
        _qwen_service = QwenService()

    return _qwen_service
