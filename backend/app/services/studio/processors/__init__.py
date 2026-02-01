# ============================================
# processors/__init__.py - 课程处理器插件系统
# ============================================

from .base import BaseProcessor, ProcessorRegistry, ProcessorInfo
from .loader import load_processor, get_processor, list_processors, reload_processors

__all__ = [
    'BaseProcessor',
    'ProcessorRegistry',
    'ProcessorInfo',
    'load_processor',
    'get_processor',
    'list_processors',
    'reload_processors',
]
