# -*- coding: utf-8 -*-
"""
SDL 编译器
将AI生成的简化场景描述编译为完整的SDL格式
支持语义形状系统
"""

import uuid
import copy
from typing import Dict, List, Any, Optional, Tuple

from .semantic_shapes import SEMANTIC_SHAPES, get_semantic_shape, PARTICLE_EFFECTS, get_particle_effect


class SDLCompiler:
    """SDL场景编译器"""

    # 画布常量
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 500

    # 布局常量
    TITLE_Y = 40
    SUBTITLE_Y = 75
    CONTENT_AREA_TOP = 100
    CONTENT_AREA_BOTTOM = 400
    BUTTON_Y = 460

    # 按钮常量
    PHASE_BTN_WIDTH = 100
    CTRL_BTN_WIDTH = 90
    BTN_HEIGHT = 40
    BTN_GAP = 20
    BTN_SEPARATOR = 40

    # 阶段按钮颜色
    PHASE_COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ec4899']

    # 基础形状类型
    BASIC_SHAPES = {'circle', 'rectangle', 'rect', 'ellipse', 'polygon', 'line'}

    def compile(self, ai_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        编译AI输入为完整SDL

        Args:
            ai_input: AI生成的简化场景描述

        Returns:
            完整的SDL场景定义
        """
        scene = ai_input.get('scene', {})
        elements_input = ai_input.get('elements', [])
        phases = ai_input.get('phases', [])
        effects_input = ai_input.get('effects', [])
        variables_input = ai_input.get('variables', [])  # 变量定义
        formula_animations_input = ai_input.get('formula_animations', [])  # 公式动画
        computed_variables_input = ai_input.get('computed_variables', [])  # 计算变量
        dynamic_curves_input = ai_input.get('dynamic_curves', [])  # 动态曲线
        stage_indicators_input = ai_input.get('stage_indicators', [])  # 阶段指示器

        # 生成基础SDL结构
        sdl = self._create_base_sdl(scene)

        # 编译变量定义
        variables, var_bindings = self._compile_variables(variables_input)
        sdl['variables'] = variables

        # 编译计算变量
        if computed_variables_input:
            sdl['computedVariables'] = computed_variables_input

        # 编译公式动画
        if formula_animations_input:
            sdl['formulaAnimations'] = formula_animations_input

        # 编译动态曲线
        if dynamic_curves_input:
            sdl['dynamicCurves'] = dynamic_curves_input

        # 编译阶段指示器
        if stage_indicators_input:
            sdl['stageIndicators'] = stage_indicators_input

        # 编译元素（支持语义形状和交互控件）
        content_elements, animated_element_ids, semantic_parts_map = self._compile_elements(elements_input, var_bindings)
        sdl['elements'].extend(content_elements)

        # 编译粒子特效
        particle_systems = self._compile_effects(effects_input, content_elements)
        if particle_systems:
            sdl['particleSystems'] = particle_systems

        # 记录动画元素的初始状态
        initial_states = self._collect_initial_states(content_elements, animated_element_ids)

        # 生成阶段动画时间线（传入语义形状映射和元素列表）
        phase_timelines = self._compile_phase_timelines(phases, animated_element_ids, semantic_parts_map, content_elements)
        sdl['timelines'].extend(phase_timelines)

        # 生成完整动画时间线
        full_timeline = self._create_full_timeline(phase_timelines)
        sdl['timelines'].append(full_timeline)

        # 生成按钮和交互
        button_elements, button_interactions = self._generate_buttons(phases)
        sdl['elements'].extend(button_elements)
        sdl['interactions'].extend(button_interactions)

        # 生成变量交互（滑块拖动等）
        var_interactions = self._generate_variable_interactions(var_bindings)
        sdl['interactions'].extend(var_interactions)

        # 生成重置交互（需要初始状态）
        reset_interaction = self._create_reset_interaction(initial_states)
        sdl['interactions'].append(reset_interaction)

        # 添加标题元素
        title_elements = self._create_title_elements(scene)
        sdl['elements'].extend(title_elements)

        return sdl

    def _compile_variables(self, variables_input: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        编译变量定义

        Returns:
            (variables, var_bindings)
            var_bindings: 变量ID -> 绑定信息的映射
        """
        variables = []
        var_bindings = {}

        for var in variables_input:
            var_id = var.get('id', f"var_{uuid.uuid4().hex[:6]}")
            var_type = var.get('type', 'number')
            default_value = var.get('default', var.get('defaultValue', 0 if var_type == 'number' else ''))

            variable = {
                "id": var_id,
                "name": var.get('name', var_id),
                "type": var_type,
                "value": default_value,
                "defaultValue": default_value,  # 前端验证器需要这个字段
                "min": var.get('min', 0),
                "max": var.get('max', 100),
                "step": var.get('step', 1),
                "unit": var.get('unit', '')
            }
            variables.append(variable)

            # 记录绑定关系
            var_bindings[var_id] = {
                "variable": variable,
                "controls": var.get('controls', []),  # 控制哪些元素
                "formula": var.get('formula', None),  # 计算公式（因变量）
                "slider_id": var.get('slider_id', None),  # 关联的滑块
                "display_id": var.get('display_id', None)  # 关联的显示框
            }

        return variables, var_bindings

    def _generate_variable_interactions(self, var_bindings: Dict) -> List[Dict]:
        """生成变量相关的交互"""
        interactions = []

        for var_id, binding in var_bindings.items():
            slider_id = binding.get('slider_id')
            if slider_id:
                # 滑块拖动交互
                interactions.append({
                    "id": f"drag_{slider_id}",
                    "name": f"拖动{binding['variable'].get('name', var_id)}滑块",
                    "enabled": True,
                    "trigger": {"type": "drag", "targetId": f"{slider_id}_handle"},
                    "conditions": [],
                    "actions": [
                        {
                            "type": "updateVariable",
                            "params": {
                                "variableId": var_id,
                                "fromDrag": True,
                                "min": binding['variable'].get('min', 0),
                                "max": binding['variable'].get('max', 100)
                            }
                        }
                    ]
                })

                # 变量变化时更新绑定的元素
                for control in binding.get('controls', []):
                    target_id = control.get('targetId')
                    prop = control.get('property', 'position.x')
                    formula = control.get('formula', 'value')

                    interactions.append({
                        "id": f"bind_{var_id}_{target_id}_{prop.replace('.', '_')}",
                        "name": f"绑定{var_id}到{target_id}",
                        "enabled": True,
                        "trigger": {"type": "variableChange", "variableId": var_id},
                        "conditions": [],
                        "actions": [
                            {
                                "type": "setProperty",
                                "params": {
                                    "targetId": target_id,
                                    "property": prop,
                                    "formula": formula
                                }
                            }
                        ]
                    })

        return interactions

    def _compile_effects(self, effects_input: List[Dict], elements: List[Dict]) -> List[Dict]:
        """编译粒子特效"""
        particle_systems = []
        element_ids = {e['id'] for e in elements}

        for i, effect in enumerate(effects_input):
            effect_type = effect.get('type', '')
            effect_def = get_particle_effect(effect_type)

            if not effect_def:
                continue

            attach_to = effect.get('attachTo', '')
            # 检查附着目标是否存在（可能是语义形状的基础ID）
            target_exists = attach_to in element_ids
            if not target_exists:
                for eid in element_ids:
                    if eid.startswith(f"{attach_to}_"):
                        attach_to = eid  # 使用第一个匹配的部件
                        target_exists = True
                        break

            particle_system = {
                "id": f"effect_{effect_type}_{i}",
                "name": effect_def.get('description', effect_type),
                "enabled": True,
                "attachTo": attach_to if target_exists else None,
                "trigger": effect.get('trigger', 'manual'),
                "config": copy.deepcopy(effect_def.get('particleConfig', {}))
            }

            # 允许覆盖颜色
            if 'color' in effect:
                particle_system['config']['color'] = effect['color']

            particle_systems.append(particle_system)

        return particle_systems

    def _create_base_sdl(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """创建基础SDL结构"""
        return {
            "version": "1.0.0",
            "id": f"scene_{uuid.uuid4().hex[:8]}",
            "name": scene.get('title', '互动模拟'),
            "description": scene.get('description', ''),
            "canvas": {
                "width": self.CANVAS_WIDTH,
                "height": self.CANVAS_HEIGHT,
                "backgroundColor": scene.get('background_color', '#1e293b'),
                "renderer": "pixi",
                "antialias": True
            },
            "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
            "elements": [],
            "timelines": [],
            "interactions": [],
            "variables": []
        }

    def _compile_elements(self, elements_input: List[Dict], var_bindings: Dict = None) -> Tuple[List[Dict], set, Dict[str, List[str]]]:
        """
        编译元素列表，支持语义形状和交互控件

        Returns:
            (elements, animated_element_ids, semantic_parts_map)
            semantic_parts_map: 语义形状ID -> 部件ID列表的映射
        """
        elements = []
        animated_ids = set()
        semantic_parts_map = {}  # 记录语义形状的部件映射
        var_bindings = var_bindings or {}

        for elem_input in elements_input:
            elem_type = elem_input.get('type', 'circle').lower()
            elem_id = elem_input.get('id', '')

            # 检查是否是交互式控件
            if elem_type == 'slider':
                slider_elements = self._compile_slider_element(elem_input, var_bindings)
                elements.extend(slider_elements)
                part_ids = [e['id'] for e in slider_elements]
                semantic_parts_map[elem_id] = part_ids
            elif elem_type == 'value_display':
                display_elements = self._compile_value_display_element(elem_input, var_bindings)
                elements.extend(display_elements)
                part_ids = [e['id'] for e in display_elements]
                semantic_parts_map[elem_id] = part_ids
            # 检查是否是语义形状
            elif elem_type in SEMANTIC_SHAPES:
                # 语义形状：展开为多个基础形状
                expanded = self._compile_semantic_element(elem_input)
                elements.extend(expanded)
                # 记录部件ID映射
                part_ids = [e['id'] for e in expanded]
                semantic_parts_map[elem_id] = part_ids
                if elem_input.get('animated', False):
                    animated_ids.add(elem_id)
                    # 同时添加所有部件ID
                    for pid in part_ids:
                        animated_ids.add(pid)
            else:
                # 基础形状
                elem = self._compile_basic_element(elem_input)
                elements.append(elem)
                if elem_input.get('animated', False):
                    animated_ids.add(elem['id'])

        return elements, animated_ids, semantic_parts_map

    def _compile_slider_element(self, elem_input: Dict, var_bindings: Dict) -> List[Dict]:
        """编译滑块控件"""
        elements = []
        base_id = elem_input.get('id', f"slider_{uuid.uuid4().hex[:6]}")
        base_pos = elem_input.get('position', {})
        base_x = base_pos.get('x', 400) if isinstance(base_pos, dict) else 400
        base_y = base_pos.get('y', 400) if isinstance(base_pos, dict) else 400

        # 获取配置
        config = elem_input.get('config', {})
        width = config.get('width', 200)
        min_val = config.get('min', 0)
        max_val = config.get('max', 100)
        default_val = config.get('default', 50)
        label = elem_input.get('label', '')
        unit = config.get('unit', '')

        # 计算滑块初始位置
        ratio = (default_val - min_val) / (max_val - min_val) if max_val > min_val else 0.5
        handle_x = base_x - width/2 + ratio * width

        # 颜色
        primary_color = elem_input.get('color', '#3b82f6')
        track_color = elem_input.get('trackColor', '#374151')

        # 滑轨背景
        elements.append({
            "id": f"{base_id}_track",
            "name": f"{label}滑轨",
            "type": "shape",
            "transform": {
                "position": {"x": base_x, "y": base_y},
                "rotation": 0,
                "scale": {"x": 1, "y": 1},
                "anchor": {"x": 0.5, "y": 0.5}
            },
            "visible": True,
            "opacity": 1,
            "zIndex": 30,
            "interactive": False,
            "shape": {
                "shapeType": "rectangle",
                "width": width,
                "height": 8,
                "cornerRadius": 4,
                "fill": {"type": "solid", "color": track_color}
            }
        })

        # 滑轨填充
        fill_width = ratio * width
        elements.append({
            "id": f"{base_id}_fill",
            "name": f"{label}填充",
            "type": "shape",
            "transform": {
                "position": {"x": base_x - width/2 + fill_width/2, "y": base_y},
                "rotation": 0,
                "scale": {"x": 1, "y": 1},
                "anchor": {"x": 0.5, "y": 0.5}
            },
            "visible": True,
            "opacity": 1,
            "zIndex": 31,
            "interactive": False,
            "shape": {
                "shapeType": "rectangle",
                "width": fill_width,
                "height": 8,
                "cornerRadius": 4,
                "fill": {"type": "solid", "color": primary_color}
            }
        })

        # 滑块手柄（可拖动）
        elements.append({
            "id": f"{base_id}_handle",
            "name": f"{label}手柄",
            "type": "shape",
            "transform": {
                "position": {"x": handle_x, "y": base_y},
                "rotation": 0,
                "scale": {"x": 1, "y": 1},
                "anchor": {"x": 0.5, "y": 0.5}
            },
            "visible": True,
            "opacity": 1,
            "zIndex": 35,
            "interactive": True,
            "draggable": True,
            "dragConstraint": {
                "axis": "x",
                "min": base_x - width/2,
                "max": base_x + width/2
            },
            "shape": {
                "shapeType": "circle",
                "radius": 14,
                "fill": {"type": "solid", "color": "#ffffff"},
                "stroke": {"width": 3, "color": primary_color}
            }
        })

        # 标签文字
        if label:
            elements.append({
                "id": f"{base_id}_label",
                "name": f"{label}标签",
                "type": "text",
                "transform": {
                    "position": {"x": base_x - width/2, "y": base_y - 25},
                    "rotation": 0,
                    "scale": {"x": 1, "y": 1},
                    "anchor": {"x": 0, "y": 0.5}
                },
                "visible": True,
                "opacity": 1,
                "zIndex": 32,
                "interactive": False,
                "text": {
                    "content": label,
                    "fontFamily": "Arial",
                    "fontSize": 14,
                    "fontWeight": "bold",
                    "color": "#ffffff",
                    "align": "left"
                }
            })

        # 数值显示
        elements.append({
            "id": f"{base_id}_value",
            "name": f"{label}数值",
            "type": "text",
            "transform": {
                "position": {"x": base_x + width/2, "y": base_y - 25},
                "rotation": 0,
                "scale": {"x": 1, "y": 1},
                "anchor": {"x": 1, "y": 0.5}
            },
            "visible": True,
            "opacity": 1,
            "zIndex": 32,
            "interactive": False,
            "text": {
                "content": f"{default_val}{unit}",
                "fontFamily": "Arial",
                "fontSize": 14,
                "fontWeight": "normal",
                "color": primary_color,
                "align": "right"
            },
            "boundVariable": elem_input.get('variable')
        })

        return elements

    def _compile_value_display_element(self, elem_input: Dict, var_bindings: Dict) -> List[Dict]:
        """编译数值显示框"""
        elements = []
        base_id = elem_input.get('id', f"display_{uuid.uuid4().hex[:6]}")
        base_pos = elem_input.get('position', {})
        base_x = base_pos.get('x', 400) if isinstance(base_pos, dict) else 400
        base_y = base_pos.get('y', 200) if isinstance(base_pos, dict) else 200

        # 获取配置
        config = elem_input.get('config', {})
        label = elem_input.get('label', '变量')
        unit = config.get('unit', '')
        decimals = config.get('decimals', 2)
        value = config.get('value', 0)

        # 颜色
        primary_color = elem_input.get('color', '#3b82f6')
        bg_color = elem_input.get('bgColor', '#1f2937')

        # 背景框
        elements.append({
            "id": f"{base_id}_bg",
            "name": f"{label}背景",
            "type": "shape",
            "transform": {
                "position": {"x": base_x, "y": base_y},
                "rotation": 0,
                "scale": {"x": 1, "y": 1},
                "anchor": {"x": 0.5, "y": 0.5}
            },
            "visible": True,
            "opacity": 1,
            "zIndex": 25,
            "interactive": False,
            "shape": {
                "shapeType": "rectangle",
                "width": 120,
                "height": 60,
                "cornerRadius": 8,
                "fill": {"type": "solid", "color": bg_color},
                "stroke": {"width": 2, "color": primary_color}
            }
        })

        # 标签
        elements.append({
            "id": f"{base_id}_label",
            "name": f"{label}标签",
            "type": "text",
            "transform": {
                "position": {"x": base_x, "y": base_y - 15},
                "rotation": 0,
                "scale": {"x": 1, "y": 1},
                "anchor": {"x": 0.5, "y": 0.5}
            },
            "visible": True,
            "opacity": 1,
            "zIndex": 26,
            "interactive": False,
            "text": {
                "content": label,
                "fontFamily": "Arial",
                "fontSize": 12,
                "fontWeight": "normal",
                "color": "#9ca3af",
                "align": "center"
            }
        })

        # 数值
        value_str = f"{value:.{decimals}f}" if isinstance(value, float) else str(value)
        elements.append({
            "id": f"{base_id}_value",
            "name": f"{label}数值",
            "type": "text",
            "transform": {
                "position": {"x": base_x, "y": base_y + 10},
                "rotation": 0,
                "scale": {"x": 1, "y": 1},
                "anchor": {"x": 0.5, "y": 0.5}
            },
            "visible": True,
            "opacity": 1,
            "zIndex": 26,
            "interactive": False,
            "text": {
                "content": f"{value_str}{unit}",
                "fontFamily": "Arial",
                "fontSize": 20,
                "fontWeight": "bold",
                "color": primary_color,
                "align": "center"
            },
            "boundVariable": elem_input.get('variable'),
            "displayConfig": {
                "decimals": decimals,
                "unit": unit
            }
        })

        return elements

    def _compile_semantic_element(self, elem_input: Dict) -> List[Dict]:
        """编译语义形状为多个基础形状"""
        elem_type = elem_input.get('type', '').lower()
        shape_def = get_semantic_shape(elem_type)

        if not shape_def:
            # 未知语义形状，回退到基础形状
            return [self._compile_basic_element(elem_input)]

        elements = []
        base_id = elem_input.get('id', f"sem_{uuid.uuid4().hex[:6]}")
        base_pos = elem_input.get('position', {})
        if base_pos == 'center':
            base_x = self.CANVAS_WIDTH / 2
            base_y = (self.CONTENT_AREA_TOP + self.CONTENT_AREA_BOTTOM) / 2
        elif isinstance(base_pos, dict):
            base_x = base_pos.get('x', 400)
            base_y = base_pos.get('y', 250)
        else:
            base_x, base_y = 400, 250

        # 获取颜色
        user_color = elem_input.get('color', None)
        default_colors = shape_def.get('defaultColors', {})
        primary_color = user_color or default_colors.get('primary', '#6366f1')
        secondary_color = elem_input.get('secondaryColor', default_colors.get('secondary', '#818cf8'))

        layer = elem_input.get('layer', 'content')
        base_z = 1 if layer == 'background' else (10 if layer == 'content' else 50)

        # 展开每个部件
        for i, part in enumerate(shape_def.get('parts', [])):
            part_id = f"{base_id}_{part.get('id', i)}"
            offset = part.get('offset', {'x': 0, 'y': 0})
            # 确保 offset 是字典类型
            if not isinstance(offset, dict):
                offset = {'x': 0, 'y': 0}
            offset_x = offset.get('x', 0) if isinstance(offset.get('x'), (int, float)) else 0
            offset_y = offset.get('y', 0) if isinstance(offset.get('y'), (int, float)) else 0

            # 确定颜色
            color_key = part.get('colorKey', 'primary')
            part_color = primary_color if color_key == 'primary' else secondary_color

            # 创建基础形状输入
            part_input = {
                'id': part_id,
                'name': f"{elem_input.get('name', '元素')}_{part.get('id', i)}",
                'type': part.get('type', 'circle'),
                'position': {'x': base_x + offset_x, 'y': base_y + offset_y},
                'size': part.get('size', {}),
                'color': part_color,
                'rotation': part.get('rotation', 0),
                'layer': layer,
                'stroke': part.get('stroke', elem_input.get('stroke', {})),
                'noFill': part.get('noFill', False)
            }

            elem = self._compile_basic_element(part_input)
            elem['zIndex'] = base_z + i
            elements.append(elem)

        return elements

    def _compile_basic_element(self, elem_input: Dict) -> Dict:
        """编译基础形状元素"""
        elem_type = elem_input.get('type', 'circle').lower()
        layer = elem_input.get('layer', 'content')

        # 计算zIndex
        if layer == 'background':
            z_index = 1
        elif layer == 'content':
            z_index = 10
        else:
            z_index = 50

        # 计算位置
        position = elem_input.get('position', {})
        if position == 'center':
            pos = {'x': self.CANVAS_WIDTH / 2, 'y': (self.CONTENT_AREA_TOP + self.CONTENT_AREA_BOTTOM) / 2}
        elif isinstance(position, dict):
            pos = {'x': position.get('x', 400), 'y': position.get('y', 250)}
        else:
            pos = {'x': 400, 'y': 250}

        # 基础元素结构
        element = {
            "id": elem_input.get('id', f"elem_{uuid.uuid4().hex[:6]}"),
            "name": elem_input.get('name', '元素'),
            "type": "shape",
            "transform": {
                "position": pos,
                "rotation": elem_input.get('rotation', 0),
                "scale": {"x": 1, "y": 1},
                "anchor": {"x": 0.5, "y": 0.5}
            },
            "visible": True,
            "opacity": elem_input.get('opacity', 1),
            "zIndex": z_index,
            "interactive": elem_input.get('interactive', False)
        }

        # 根据类型设置shape
        size = elem_input.get('size', {})
        color = elem_input.get('color', '#6366f1')
        stroke = elem_input.get('stroke', {})
        no_fill = elem_input.get('noFill', False)

        if elem_type == 'circle':
            element['shape'] = {
                "shapeType": "circle",
                "radius": size.get('radius', 30)
            }
            if not no_fill:
                element['shape']['fill'] = {"type": "solid", "color": color}

        elif elem_type in ('rectangle', 'rect'):
            element['shape'] = {
                "shapeType": "rectangle",
                "width": size.get('width', 100),
                "height": size.get('height', 50),
                "cornerRadius": size.get('cornerRadius', 0)
            }
            if not no_fill:
                element['shape']['fill'] = {"type": "solid", "color": color}

        elif elem_type == 'ellipse':
            element['shape'] = {
                "shapeType": "ellipse",
                "radiusX": size.get('radiusX', size.get('width', 60) / 2),
                "radiusY": size.get('radiusY', size.get('height', 40) / 2)
            }
            if not no_fill:
                element['shape']['fill'] = {"type": "solid", "color": color}

        elif elem_type == 'polygon':
            points = size.get('points', elem_input.get('points', []))
            if not points:
                points = [{"x": 0, "y": -30}, {"x": 26, "y": 15}, {"x": -26, "y": 15}]
            element['shape'] = {
                "shapeType": "polygon",
                "points": points
            }
            if not no_fill:
                element['shape']['fill'] = {"type": "solid", "color": color}

        elif elem_type == 'line':
            points = size.get('points', elem_input.get('points', [{"x": 0, "y": 0}, {"x": 100, "y": 0}]))
            element['shape'] = {
                "shapeType": "line",
                "points": points,
                "stroke": {"color": color, "width": stroke.get('width', 2)}
            }

        else:
            # 默认使用矩形
            element['shape'] = {
                "shapeType": "rectangle",
                "width": size.get('width', 100),
                "height": size.get('height', 50),
                "cornerRadius": size.get('cornerRadius', 0)
            }
            if not no_fill:
                element['shape']['fill'] = {"type": "solid", "color": color}

        # 添加描边
        if stroke and elem_type != 'line':
            element['shape']['stroke'] = {
                "color": stroke.get('color', '#ffffff'),
                "width": stroke.get('width', 2)
            }

        return element

    def _collect_initial_states(self, elements: List[Dict], animated_ids: set) -> Dict[str, Dict]:
        """收集动画元素的初始状态"""
        initial_states = {}

        for elem in elements:
            elem_id = elem['id']
            # 检查是否是动画元素或其部件
            base_id = elem_id.rsplit('_', 1)[0] if '_' in elem_id else elem_id
            if elem_id in animated_ids or base_id in animated_ids:
                initial_states[elem_id] = {
                    'position': copy.deepcopy(elem['transform']['position']),
                    'opacity': elem.get('opacity', 1),
                    'rotation': elem['transform'].get('rotation', 0),
                    'scale': copy.deepcopy(elem['transform'].get('scale', {'x': 1, 'y': 1}))
                }

        return initial_states

    def _compile_phase_timelines(self, phases: List[Dict], animated_ids: set, semantic_parts_map: Dict[str, List[str]] = None, elements: List[Dict] = None) -> List[Dict]:
        """编译阶段动画时间线"""
        timelines = []
        semantic_parts_map = semantic_parts_map or {}
        elements = elements or []

        # 构建元素位置映射
        element_positions = {}
        for elem in elements:
            elem_id = elem.get('id', '')
            pos = elem.get('transform', {}).get('position', {})
            element_positions[elem_id] = {'x': pos.get('x', 0), 'y': pos.get('y', 0)}

        for i, phase in enumerate(phases):
            animation = phase.get('animation', {})
            target_id = animation.get('target')

            if not target_id:
                continue

            # 确定实际的目标ID列表和基准位置
            base_position = None
            if target_id in semantic_parts_map:
                target_ids = semantic_parts_map[target_id]
                # 计算语义形状的基准位置（第一个部件的位置减去偏移）
                if target_ids and target_ids[0] in element_positions:
                    first_part_pos = element_positions[target_ids[0]]
                    # 基准位置就是AI指定的位置
                    kf_list = animation.get('keyframes', [{}])
                    if kf_list and len(kf_list) > 0:
                        base_position = kf_list[0].get('position', first_part_pos)
                        # 确保 base_position 是字典类型
                        if not isinstance(base_position, dict):
                            base_position = first_part_pos
                    else:
                        base_position = first_part_pos
            elif target_id in animated_ids:
                target_ids = [target_id]
            else:
                target_ids = []
                for aid in animated_ids:
                    if aid.startswith(f"{target_id}_"):
                        target_ids.append(aid)
                if not target_ids:
                    continue

            keyframes_input = animation.get('keyframes', [])
            duration = animation.get('duration', 2000)

            # 转换关键帧 - 为每个目标ID生成关键帧
            keyframes = []
            time_step = duration / max(len(keyframes_input) - 1, 1) if len(keyframes_input) > 1 else 0

            for j, kf in enumerate(keyframes_input):
                time = int(j * time_step)

                # 为每个目标生成关键帧
                for tid in target_ids:
                    if 'position' in kf:
                        kf_pos = kf['position']
                        # 确保 kf_pos 是字典类型
                        if not isinstance(kf_pos, dict):
                            kf_pos = {'x': 400, 'y': 250}
                        kf_x = kf_pos.get('x', 400)
                        kf_y = kf_pos.get('y', 250)

                        # 计算部件的相对偏移
                        if base_position and isinstance(base_position, dict) and tid in element_positions:
                            part_pos = element_positions[tid]
                            base_x = base_position.get('x', 400)
                            base_y = base_position.get('y', 250)
                            # 计算部件相对于基准位置的偏移
                            offset_x = part_pos.get('x', 0) - base_x
                            offset_y = part_pos.get('y', 0) - base_y
                            # 应用偏移到目标位置
                            new_pos = {
                                'x': kf_x + offset_x,
                                'y': kf_y + offset_y
                            }
                        else:
                            new_pos = {'x': kf_x, 'y': kf_y}

                        keyframes.append({
                            "time": time,
                            "targetId": tid,
                            "property": "position",
                            "value": new_pos,
                            "easing": kf.get('easing', 'easeInOut')
                        })

                    if 'opacity' in kf:
                        keyframes.append({
                            "time": time,
                            "targetId": tid,
                            "property": "opacity",
                            "value": kf['opacity'],
                            "easing": kf.get('easing', 'easeInOut')
                        })

                    if 'rotation' in kf:
                        keyframes.append({
                            "time": time,
                            "targetId": tid,
                            "property": "rotation",
                            "value": kf['rotation'],
                            "easing": kf.get('easing', 'easeInOut')
                        })

                # 处理关节动画
                if 'joints' in kf:
                    for joint_name, joint_rotation in kf['joints'].items():
                        # 找到对应的部件ID
                        joint_part_id = f"{target_id}_{joint_name}"
                        if joint_part_id in element_positions or any(tid.endswith(f"_{joint_name}") for tid in target_ids):
                            # 找到实际的部件ID
                            actual_joint_id = joint_part_id if joint_part_id in element_positions else None
                            if not actual_joint_id:
                                for tid in target_ids:
                                    if tid.endswith(f"_{joint_name}"):
                                        actual_joint_id = tid
                                        break
                            if actual_joint_id:
                                keyframes.append({
                                    "time": time,
                                    "targetId": actual_joint_id,
                                    "property": "rotation",
                                    "value": joint_rotation,
                                    "easing": kf.get('easing', 'easeInOut')
                                })

            timeline = {
                "id": f"phase{i+1}_animation",
                "name": f"{phase.get('name', f'阶段{i+1}')}动画",
                "duration": duration,
                "loop": False,
                "autoPlay": False,
                "keyframes": keyframes
            }

            timelines.append(timeline)

        return timelines

    def _create_full_timeline(self, phase_timelines: List[Dict]) -> Dict:
        """将所有阶段动画合并为完整动画"""
        all_keyframes = []
        current_time = 0

        for tl in phase_timelines:
            for kf in tl.get('keyframes', []):
                new_kf = copy.deepcopy(kf)
                new_kf['time'] = current_time + kf['time']
                all_keyframes.append(new_kf)
            current_time += tl.get('duration', 2000)

        return {
            "id": "full_animation",
            "name": "完整动画",
            "duration": max(current_time, 2000),
            "loop": False,
            "autoPlay": False,
            "keyframes": all_keyframes
        }

    def _generate_buttons(self, phases: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """生成所有按钮元素和交互"""
        elements = []
        interactions = []

        n_phases = len(phases)

        # 计算布局
        phase_group_width = n_phases * self.PHASE_BTN_WIDTH + max(0, n_phases - 1) * self.BTN_GAP if n_phases > 0 else 0
        ctrl_group_width = 2 * self.CTRL_BTN_WIDTH + self.BTN_GAP
        total_width = phase_group_width + (self.BTN_SEPARATOR if n_phases > 0 else 0) + ctrl_group_width
        start_x = (self.CANVAS_WIDTH - total_width) / 2

        # 生成阶段按钮
        x = start_x + self.PHASE_BTN_WIDTH / 2
        for i, phase in enumerate(phases):
            btn_id = f"btn_phase{i+1}"
            timeline_id = f"phase{i+1}_animation"
            phase_name = phase.get('name', f'阶段{i+1}')
            color = self.PHASE_COLORS[i % len(self.PHASE_COLORS)]

            elements.append({
                "id": btn_id,
                "name": f"{phase_name}按钮",
                "type": "shape",
                "transform": {
                    "position": {"x": x, "y": self.BUTTON_Y},
                    "rotation": 0,
                    "scale": {"x": 1, "y": 1},
                    "anchor": {"x": 0.5, "y": 0.5}
                },
                "visible": True,
                "opacity": 1,
                "zIndex": 100,
                "interactive": True,
                "shape": {
                    "shapeType": "rectangle",
                    "width": self.PHASE_BTN_WIDTH,
                    "height": self.BTN_HEIGHT,
                    "fill": {"type": "solid", "color": color},
                    "cornerRadius": 20
                }
            })

            elements.append({
                "id": f"{btn_id}_text",
                "name": f"{phase_name}文字",
                "type": "text",
                "transform": {
                    "position": {"x": x, "y": self.BUTTON_Y},
                    "rotation": 0,
                    "scale": {"x": 1, "y": 1},
                    "anchor": {"x": 0.5, "y": 0.5}
                },
                "visible": True,
                "opacity": 1,
                "zIndex": 101,
                "interactive": False,
                "text": {
                    "content": phase_name,
                    "fontFamily": "Arial",
                    "fontSize": 14,
                    "fontWeight": "bold",
                    "color": "#ffffff",
                    "align": "center"
                }
            })

            interactions.append({
                "id": f"click_phase{i+1}",
                "name": f"点击{phase_name}",
                "enabled": True,
                "trigger": {"type": "click", "targetId": btn_id},
                "conditions": [],
                "actions": [{"type": "playTimeline", "params": {"timelineId": timeline_id}}]
            })

            x += self.PHASE_BTN_WIDTH + self.BTN_GAP

        # 计算控制按钮起始位置
        if n_phases > 0:
            x = start_x + phase_group_width + self.BTN_SEPARATOR + self.CTRL_BTN_WIDTH / 2
        else:
            x = (self.CANVAS_WIDTH - ctrl_group_width) / 2 + self.CTRL_BTN_WIDTH / 2

        # 开始按钮
        elements.append({
            "id": "btn_start",
            "name": "开始按钮",
            "type": "shape",
            "transform": {
                "position": {"x": x, "y": self.BUTTON_Y},
                "rotation": 0,
                "scale": {"x": 1, "y": 1},
                "anchor": {"x": 0.5, "y": 0.5}
            },
            "visible": True,
            "opacity": 1,
            "zIndex": 100,
            "interactive": True,
            "shape": {
                "shapeType": "rectangle",
                "width": self.CTRL_BTN_WIDTH,
                "height": self.BTN_HEIGHT,
                "fill": {"type": "solid", "color": "#22c55e"},
                "cornerRadius": 20
            }
        })
        elements.append({
            "id": "btn_start_text",
            "name": "开始文字",
            "type": "text",
            "transform": {
                "position": {"x": x, "y": self.BUTTON_Y},
                "rotation": 0,
                "scale": {"x": 1, "y": 1},
                "anchor": {"x": 0.5, "y": 0.5}
            },
            "visible": True,
            "opacity": 1,
            "zIndex": 101,
            "interactive": False,
            "text": {
                "content": "▶ 开始",
                "fontFamily": "Arial",
                "fontSize": 14,
                "fontWeight": "bold",
                "color": "#ffffff",
                "align": "center"
            }
        })
        interactions.append({
            "id": "click_start",
            "name": "点击开始",
            "enabled": True,
            "trigger": {"type": "click", "targetId": "btn_start"},
            "conditions": [],
            "actions": [{"type": "playTimeline", "params": {"timelineId": "full_animation"}}]
        })

        x += self.CTRL_BTN_WIDTH + self.BTN_GAP

        # 重置按钮
        elements.append({
            "id": "btn_reset",
            "name": "重置按钮",
            "type": "shape",
            "transform": {
                "position": {"x": x, "y": self.BUTTON_Y},
                "rotation": 0,
                "scale": {"x": 1, "y": 1},
                "anchor": {"x": 0.5, "y": 0.5}
            },
            "visible": True,
            "opacity": 1,
            "zIndex": 100,
            "interactive": True,
            "shape": {
                "shapeType": "rectangle",
                "width": self.CTRL_BTN_WIDTH,
                "height": self.BTN_HEIGHT,
                "fill": {"type": "solid", "color": "#ef4444"},
                "cornerRadius": 20
            }
        })
        elements.append({
            "id": "btn_reset_text",
            "name": "重置文字",
            "type": "text",
            "transform": {
                "position": {"x": x, "y": self.BUTTON_Y},
                "rotation": 0,
                "scale": {"x": 1, "y": 1},
                "anchor": {"x": 0.5, "y": 0.5}
            },
            "visible": True,
            "opacity": 1,
            "zIndex": 101,
            "interactive": False,
            "text": {
                "content": "↺ 重置",
                "fontFamily": "Arial",
                "fontSize": 14,
                "fontWeight": "bold",
                "color": "#ffffff",
                "align": "center"
            }
        })

        return elements, interactions

    def _create_reset_interaction(self, initial_states: Dict[str, Dict]) -> Dict:
        """创建重置交互"""
        actions = [{"type": "stopAllTimelines", "params": {}}]

        for elem_id, state in initial_states.items():
            for prop, value in state.items():
                actions.append({
                    "type": "setProperty",
                    "params": {
                        "targetId": elem_id,
                        "property": prop,
                        "value": copy.deepcopy(value)
                    }
                })

        return {
            "id": "click_reset",
            "name": "点击重置",
            "enabled": True,
            "trigger": {"type": "click", "targetId": "btn_reset"},
            "conditions": [],
            "actions": actions
        }

    def _create_title_elements(self, scene: Dict[str, Any]) -> List[Dict]:
        """创建标题元素"""
        elements = []

        title = scene.get('title', '')
        if title:
            elements.append({
                "id": "title_text",
                "name": "标题",
                "type": "text",
                "transform": {
                    "position": {"x": self.CANVAS_WIDTH / 2, "y": self.TITLE_Y},
                    "rotation": 0,
                    "scale": {"x": 1, "y": 1},
                    "anchor": {"x": 0.5, "y": 0.5}
                },
                "visible": True,
                "opacity": 1,
                "zIndex": 50,
                "interactive": False,
                "text": {
                    "content": title,
                    "fontFamily": "Arial",
                    "fontSize": 24,
                    "fontWeight": "bold",
                    "color": "#ffffff",
                    "align": "center"
                }
            })

        description = scene.get('description', '')
        if description:
            elements.append({
                "id": "subtitle_text",
                "name": "副标题",
                "type": "text",
                "transform": {
                    "position": {"x": self.CANVAS_WIDTH / 2, "y": self.SUBTITLE_Y},
                    "rotation": 0,
                    "scale": {"x": 1, "y": 1},
                    "anchor": {"x": 0.5, "y": 0.5}
                },
                "visible": True,
                "opacity": 1,
                "zIndex": 50,
                "interactive": False,
                "text": {
                    "content": description,
                    "fontFamily": "Arial",
                    "fontSize": 14,
                    "fontWeight": "normal",
                    "color": "#94a3b8",
                    "align": "center"
                }
            })

        return elements
