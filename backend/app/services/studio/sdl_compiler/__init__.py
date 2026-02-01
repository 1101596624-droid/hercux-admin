# -*- coding: utf-8 -*-
"""
SDL 编译器模块
将AI生成的简化场景描述编译为完整的SDL格式
支持语义形状系统和粒子特效
"""

from .compiler import SDLCompiler
from .validator import SDLValidator
from .fixer import SDLAutoFixer
from .semantic_shapes import (
    SEMANTIC_SHAPES, get_semantic_shape, list_semantic_shapes,
    PARTICLE_EFFECTS, get_particle_effect, list_particle_effects
)

__all__ = [
    'SDLCompiler', 'SDLValidator', 'SDLAutoFixer',
    'SEMANTIC_SHAPES', 'get_semantic_shape', 'list_semantic_shapes',
    'PARTICLE_EFFECTS', 'get_particle_effect', 'list_particle_effects'
]
