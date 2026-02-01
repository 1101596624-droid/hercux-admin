# ============================================
# processors/loader.py - 处理器加载器（简化版）
# ============================================

import importlib
from pathlib import Path
from typing import Optional, List, Dict, Any

from .base import BaseProcessor, ProcessorRegistry

# 处理器目录
PROCESSORS_DIR = Path(__file__).parent


def _load_builtin_processors():
    """加载内置处理器"""
    builtin_modules = [
        "intelligent",  # 智能教学规划处理器
        "rcs",          # RCS 三层讲解处理器
    ]

    for module_name in builtin_modules:
        module_path = PROCESSORS_DIR / f"{module_name}.py"
        if module_path.exists():
            try:
                importlib.import_module(f".{module_name}", package="app.services.studio.processors")
            except Exception as e:
                print(f"[WARNING] 加载内置处理器 '{module_name}' 失败: {e}")


def load_processor(processor_id: str) -> Optional[BaseProcessor]:
    """加载指定的处理器"""
    if not ProcessorRegistry.exists(processor_id):
        _load_builtin_processors()
    return ProcessorRegistry.get(processor_id)


def get_processor(processor_id: str = None) -> BaseProcessor:
    """获取处理器实例"""
    if not ProcessorRegistry._processors:
        _load_builtin_processors()

    if processor_id is None:
        return ProcessorRegistry.get_default()

    processor = ProcessorRegistry.get(processor_id)
    if processor is not None:
        return processor

    available = [p["id"] for p in ProcessorRegistry.list_all()]
    raise ValueError(
        f"处理器 '{processor_id}' 不存在。可用的处理器: {', '.join(available)}"
    )


def list_processors() -> List[Dict[str, Any]]:
    """列出所有可用的处理器"""
    if not ProcessorRegistry._processors:
        _load_builtin_processors()
    return ProcessorRegistry.list_all()


def reload_processors():
    """重新加载所有处理器"""
    ProcessorRegistry.reload()
    _load_builtin_processors()


# 模块加载时自动加载内置处理器
_load_builtin_processors()
