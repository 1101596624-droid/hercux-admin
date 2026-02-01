"""
物理学科 SDL 场景模板
"""

from .physics_part1 import FORCE_COMPOSITION_TEMPLATE, PROJECTILE_MOTION_TEMPLATE
from .physics_part2 import CIRCUIT_TEMPLATE, PENDULUM_TEMPLATE

# 导出所有物理模板
PHYSICS_TEMPLATES = {
    "physics_force_composition": FORCE_COMPOSITION_TEMPLATE,
    "physics_projectile_motion": PROJECTILE_MOTION_TEMPLATE,
    "physics_circuit": CIRCUIT_TEMPLATE,
    "physics_pendulum": PENDULUM_TEMPLATE,
}
