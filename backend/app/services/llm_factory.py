"""
LLM 服务工厂
支持在 DeepSeek 和 Qwen 之间动态切换
"""

from typing import Union
from app.core.config import settings
from app.services.deepseek_service import DeepSeekService, get_deepseek_service
from app.services.qwen_service import QwenService, get_qwen_service


# 类型别名
LLMService = Union[DeepSeekService, QwenService]


def get_llm_service() -> LLMService:
    """
    获取 LLM 服务实例（根据配置动态选择）

    通过环境变量 LLM_PROVIDER 控制：
    - "deepseek": 使用 DeepSeek API
    - "qwen": 使用千问 API
    - 默认: DeepSeek

    Returns:
        LLM 服务实例（DeepSeekService 或 QwenService）
    """
    provider = getattr(settings, 'LLM_PROVIDER', 'deepseek').lower()

    if provider == 'qwen':
        return get_qwen_service()
    elif provider == 'deepseek':
        return get_deepseek_service()
    else:
        # 默认使用 DeepSeek
        return get_deepseek_service()


def get_llm_provider_name() -> str:
    """
    获取当前使用的 LLM 提供商名称

    Returns:
        提供商名称（"deepseek" 或 "qwen"）
    """
    provider = getattr(settings, 'LLM_PROVIDER', 'deepseek').lower()
    return provider if provider in ['deepseek', 'qwen'] else 'deepseek'


# 为了向后兼容，提供别名
def get_claude_service() -> LLMService:
    """
    向后兼容的接口（原 get_claude_service）
    现在返回配置的 LLM 服务
    """
    return get_llm_service()


# 导出 Message 类（从任一服务导入都可以，因为它们是相同的）
from app.services.deepseek_service import Message

__all__ = [
    'get_llm_service',
    'get_llm_provider_name',
    'get_claude_service',
    'Message',
    'LLMService'
]
