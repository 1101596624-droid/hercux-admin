"""
Studio Generation Package
整合课程生成器的核心模块
"""

# 导出主要组件
from .providers import create_provider, AnthropicProvider
from .processors import get_processor, ProcessorRegistry, BaseProcessor
from .json_utils import safe_parse_json

# Alias for backward compatibility
get_provider = create_provider

__all__ = [
    "get_provider",
    "create_provider",
    "AnthropicProvider",
    "get_processor",
    "ProcessorRegistry",
    "BaseProcessor",
    "safe_parse_json",
]
