# ============================================
# generation/__init__.py - 生成层导出
# ============================================

from .output_processor import process_output, process_output_v2, IDGenerator

__all__ = [
    "process_output",
    "process_output_v2",
    "IDGenerator",
]
