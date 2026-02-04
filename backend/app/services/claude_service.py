"""
Anthropic Claude API 集成服务
用于 AI 导师对话功能
"""

import json
import ssl
import certifi
from typing import List, Dict, Optional, AsyncGenerator
import httpx
from pydantic import BaseModel
from app.core.config import settings


# 创建使用 certifi 证书的 SSL 上下文
def get_ssl_context():
    """获取配置了 certifi CA 证书的 SSL 上下文"""
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return ssl_context


class Message(BaseModel):
    role: str  # 'user', 'assistant'
    content: str


class ClaudeService:
    """Anthropic Claude API 服务类"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.base_url = base_url or settings.ANTHROPIC_BASE_URL
        self.model = settings.ANTHROPIC_MODEL  # 从配置读取模型名称
        self.anthropic_version = "2023-06-01"

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

    async def chat_completion(
        self,
        messages: List[Message],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict:
        """
        调用 Claude Chat API

        Args:
            messages: 对话历史（不包含 system）
            system_prompt: 系统提示词
            temperature: 温度参数 (0-1)
            max_tokens: 最大生成 token 数

        Returns:
            API 响应
        """
        headers = {
            "x-api-key": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "anthropic-version": self.anthropic_version,
            "content-type": "application/json"
        }

        # Claude API 格式：system 单独传递，messages 只包含 user/assistant
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages]
        }

        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=120.0, verify=get_ssl_context()) as client:
            response = await client.post(
                f"{self.base_url}/v1/messages",
                headers=headers,
                json=payload
            )

            response.raise_for_status()
            return response.json()

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AsyncGenerator[str, None]:
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
            "x-api-key": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "anthropic-version": self.anthropic_version,
            "content-type": "application/json"
        }

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=300.0, verify=get_ssl_context()) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/messages",
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line:
                        continue

                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            # Claude 流式响应格式
                            if data.get("type") == "content_block_delta":
                                delta = data.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    text = delta.get("text", "")
                                    if text:
                                        yield text
                        except json.JSONDecodeError:
                            continue

    async def generate_tutor_response(
        self,
        user_message: str,
        context: Dict,
        conversation_history: List[Message]
    ) -> str:
        """
        生成 AI 导师回复

        Args:
            user_message: 用户消息
            context: 上下文信息 (当前节点、内容、进度等)
            conversation_history: 对话历史

        Returns:
            AI 导师回复
        """
        # 构建系统提示词
        system_prompt = self._build_system_prompt(context)

        # 构建消息列表（只包含 user/assistant，不包含 system）
        messages = []

        # 添加对话历史 (最多保留最近 10 轮)
        for msg in conversation_history[-20:]:
            if msg.role in ["user", "assistant"]:
                messages.append(msg)

        # 添加当前用户消息
        messages.append(Message(role="user", content=user_message))

        # 调用 API
        response = await self.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )

        # 提取回复内容
        assistant_message = response["content"][0]["text"]

        return assistant_message

    def _build_system_prompt(self, context: Dict) -> str:
        """
        构建系统提示词

        Args:
            context: 上下文信息

        Returns:
            系统提示词
        """
        node = context.get("node", {})
        ai_tutor_config = context.get("ai_tutor_config", {})
        current_layer = context.get("current_layer", "L1")
        progress = context.get("progress", {})

        # 基础角色设定
        persona = ai_tutor_config.get(
            "tutor_persona",
            "专业但友好的导师，善于用生活化的比喻解释复杂概念"
        )

        # 当前节点信息
        node_title = node.get("title", "")
        learning_objectives = node.get("learning_objectives", [])

        # 常见误区
        misconceptions = ai_tutor_config.get("common_misconceptions", [])

        # 提示语
        hints = ai_tutor_config.get("hints", [])

        # 构建提示词
        prompt = f"""你是一位{persona}。

当前教学场景：
- 课程节点：{node_title}
- 学习目标：{', '.join(learning_objectives)}
- 当前层级：{current_layer} ({'直觉理解' if current_layer == 'L1' else '原理机制' if current_layer == 'L2' else '本质规律'})

你的职责：
1. 根据学生的问题和当前学习进度，提供个性化的引导和解答
2. 使用生活化的比喻和例子帮助学生理解抽象概念
3. 鼓励学生主动思考，而不是直接给出答案
4. 识别学生的误区并温和地纠正

常见误区（需要注意）：
{chr(10).join(f'- {m}' for m in misconceptions) if misconceptions else '无'}

可用提示语（适时使用）：
{chr(10).join(f'- {h}' for h in hints) if hints else '无'}

对话风格：
- 友好、耐心、鼓励性
- 使用简洁的语言，避免过于学术化
- 适当使用表情符号增加亲和力（但不要过度）
- 根据学生的理解程度调整解释的深度

重要原则：
- 不要直接给出测验答案，而是引导学生思考
- 如果学生理解有困难，尝试换一个角度或比喻
- 及时肯定学生的正确理解和进步
"""

        return prompt

    async def generate_hint(
        self,
        question: str,
        user_answer: str,
        correct_answer: str,
        context: Dict
    ) -> str:
        """
        为错误答案生成提示

        Args:
            question: 问题
            user_answer: 用户答案
            correct_answer: 正确答案
            context: 上下文

        Returns:
            提示信息
        """
        system_prompt = f"""你是一位耐心的导师。学生回答错了一道题，你需要给出提示，但不要直接告诉答案。

问题：{question}
学生答案：{user_answer}
正确答案：{correct_answer}

请生成一个简短的提示（1-2句话），帮助学生重新思考，但不要直接揭示答案。"""

        messages = [
            Message(role="user", content="请给我一个提示")
        ]

        response = await self.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=200
        )

        return response["content"][0]["text"]


    async def generate_raw_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000, system_prompt: str = "") -> str:
        """
        生成原始响应（用于结构化输出如JSON）

        Args:
            prompt: 提示词
            temperature: 温度参数
            max_tokens: 最大token数
            system_prompt: 系统提示词

        Returns:
            原始响应文本
        """
        messages = [
            Message(role="user", content=prompt)
        ]

        response = await self.chat_completion(messages, system_prompt=system_prompt, temperature=temperature, max_tokens=max_tokens)

        return response["content"][0]["text"]


# 全局实例
_claude_service: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    """获取 Claude 服务实例（单例模式）"""
    global _claude_service

    if _claude_service is None:
        _claude_service = ClaudeService()

    return _claude_service
