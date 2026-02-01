# -*- coding: utf-8 -*-
"""
SDL 自动修复器
自动修复SDL中的错误
"""

import uuid
import copy
from typing import Dict, List, Any, Optional

from .semantic_shapes import SEMANTIC_SHAPES


class SDLAutoFixer:
    """SDL自动修复器"""

    MAX_FIX_ATTEMPTS = 20  # 增加到20次，确保修复成功

    # 画布常量
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 500
    BUTTON_Y = 460

    # 按钮常量
    PHASE_BTN_WIDTH = 100
    CTRL_BTN_WIDTH = 90
    BTN_HEIGHT = 40
    BTN_GAP = 20
    BTN_SEPARATOR = 40

    def fix_and_validate(self, sdl: Dict[str, Any], validator) -> Dict[str, Any]:
        """
        修复并验证SDL，持续尝试直到成功

        Args:
            sdl: 待修复的SDL
            validator: SDLValidator实例

        Returns:
            修复后的SDL
        """
        prev_error_count = float('inf')

        for attempt in range(self.MAX_FIX_ATTEMPTS):
            errors = validator.validate(sdl)
            if not errors:
                return sdl  # 验证通过

            # 如果错误数量没有减少，说明修复陷入循环
            if len(errors) >= prev_error_count:
                # 尝试更激进的修复
                sdl = self._aggressive_fix(sdl, errors)

            prev_error_count = len(errors)
            sdl = self._apply_fixes(sdl, errors)

        # 最后一次验证
        final_errors = validator.validate(sdl)
        if final_errors:
            # 使用安全模板作为最后手段
            return self._get_safe_fallback_template(sdl)

        return sdl

    def _aggressive_fix(self, sdl: Dict[str, Any], errors: List) -> Dict[str, Any]:
        """激进修复 - 直接重建有问题的部分"""
        # 重建按钮
        sdl = self._rebuild_buttons(sdl)
        # 重建交互
        sdl = self._rebuild_interactions(sdl)
        # 重建时间线
        sdl = self._rebuild_timelines(sdl)
        return sdl

    def _rebuild_buttons(self, sdl: Dict[str, Any]) -> Dict[str, Any]:
        """重建所有按钮"""
        # 移除现有按钮
        sdl['elements'] = [e for e in sdl.get('elements', [])
                          if not (e.get('id', '').startswith('btn_'))]
        # 调用修复方法重新添加
        return self._fix_buttons(sdl)

    def _rebuild_interactions(self, sdl: Dict[str, Any]) -> Dict[str, Any]:
        """重建所有交互"""
        # 保留非按钮交互
        sdl['interactions'] = [i for i in sdl.get('interactions', [])
                              if not i.get('id', '').startswith('click_')]
        return self._fix_interactions(sdl)

    def _rebuild_timelines(self, sdl: Dict[str, Any]) -> Dict[str, Any]:
        """重建时间线"""
        if not any(t.get('id') == 'full_animation' for t in sdl.get('timelines', [])):
            return self._fix_timelines(sdl)
        return sdl

    def _apply_fixes(self, sdl: Dict[str, Any], errors: List) -> Dict[str, Any]:
        """按优先级应用修复"""
        # 按错误类型分组
        error_types = set(e.type for e in errors)

        # 优先修复结构性问题
        if 'missing_field' in error_types:
            sdl = self._fix_missing_fields(sdl, errors)

        if 'invalid_canvas' in error_types:
            sdl = self._fix_canvas(sdl)

        # 修复按钮问题
        if any(t in error_types for t in ['missing_required_button', 'invalid_button_y',
                                           'invalid_button_zindex', 'button_not_interactive',
                                           'button_overlap', 'missing_button_text']):
            sdl = self._fix_buttons(sdl)

        # 修复交互问题
        if any(t in error_types for t in ['missing_required_interaction', 'missing_interaction_field',
                                           'interaction_disabled', 'missing_trigger_type',
                                           'missing_trigger_target', 'empty_actions', 'reset_missing_stop']):
            sdl = self._fix_interactions(sdl)

        # 修复时间线问题
        if any(t in error_types for t in ['missing_full_animation', 'missing_timeline_field',
                                           'timeline_autoplay', 'missing_keyframe_field']):
            sdl = self._fix_timelines(sdl)

        # 修复引用问题
        if any(t in error_types for t in ['invalid_trigger_target', 'invalid_timeline_reference',
                                           'invalid_element_reference', 'invalid_keyframe_target']):
            sdl = self._fix_references(sdl)

        # 修复坐标问题
        if 'coordinate_out_of_range' in error_types:
            sdl = self._fix_coordinates(sdl)

        # 修复ID重复问题
        if any(t in error_types for t in ['duplicate_id', 'duplicate_interaction_id', 'duplicate_timeline_id']):
            sdl = self._fix_duplicate_ids(sdl)

        return sdl

    def _fix_missing_fields(self, sdl: Dict[str, Any], errors: List) -> Dict[str, Any]:
        """修复缺失的必填字段"""
        if 'version' not in sdl:
            sdl['version'] = '1.0.0'
        if 'id' not in sdl:
            sdl['id'] = f"scene_{uuid.uuid4().hex[:8]}"
        if 'name' not in sdl:
            sdl['name'] = '互动模拟'
        if 'canvas' not in sdl:
            sdl['canvas'] = {}
        if 'elements' not in sdl:
            sdl['elements'] = []
        if 'timelines' not in sdl:
            sdl['timelines'] = []
        if 'interactions' not in sdl:
            sdl['interactions'] = []
        if 'variables' not in sdl:
            sdl['variables'] = []
        else:
            # 修复变量缺少 defaultValue 字段
            for var in sdl.get('variables', []):
                if 'defaultValue' not in var:
                    var['defaultValue'] = var.get('value', 0)
                if 'value' not in var:
                    var['value'] = var.get('defaultValue', 0)
        if 'assets' not in sdl:
            sdl['assets'] = {"icons": [], "images": [], "sounds": [], "fonts": []}

        return sdl

    def _fix_canvas(self, sdl: Dict[str, Any]) -> Dict[str, Any]:
        """修复画布设置"""
        canvas = sdl.get('canvas', {})
        canvas['width'] = self.CANVAS_WIDTH
        canvas['height'] = self.CANVAS_HEIGHT
        if 'backgroundColor' not in canvas:
            canvas['backgroundColor'] = '#1e293b'
        if 'renderer' not in canvas:
            canvas['renderer'] = 'pixi'
        if 'antialias' not in canvas:
            canvas['antialias'] = True
        sdl['canvas'] = canvas
        return sdl

    def _fix_buttons(self, sdl: Dict[str, Any]) -> Dict[str, Any]:
        """修复按钮问题"""
        elements = sdl.get('elements', [])

        # 收集现有按钮
        buttons = {}
        button_texts = {}
        other_elements = []

        for elem in elements:
            elem_id = elem.get('id', '')
            if elem_id.startswith('btn_') and '_text' not in elem_id:
                buttons[elem_id] = elem
            elif elem_id.startswith('btn_') and '_text' in elem_id:
                button_texts[elem_id] = elem
            else:
                other_elements.append(elem)

        # 确保必须的按钮存在
        if 'btn_start' not in buttons:
            buttons['btn_start'] = self._create_button('btn_start', '开始', '#22c55e')
            button_texts['btn_start_text'] = self._create_button_text('btn_start_text', '▶ 开始')

        if 'btn_reset' not in buttons:
            buttons['btn_reset'] = self._create_button('btn_reset', '重置', '#ef4444')
            button_texts['btn_reset_text'] = self._create_button_text('btn_reset_text', '↺ 重置')

        # 重新计算按钮位置
        phase_buttons = {k: v for k, v in buttons.items() if k.startswith('btn_phase')}
        ctrl_buttons = {k: v for k, v in buttons.items() if k in ['btn_start', 'btn_reset']}

        n_phases = len(phase_buttons)
        phase_group_width = n_phases * self.PHASE_BTN_WIDTH + max(0, n_phases - 1) * self.BTN_GAP if n_phases > 0 else 0
        ctrl_group_width = 2 * self.CTRL_BTN_WIDTH + self.BTN_GAP
        total_width = phase_group_width + (self.BTN_SEPARATOR if n_phases > 0 else 0) + ctrl_group_width
        start_x = (self.CANVAS_WIDTH - total_width) / 2

        # 设置阶段按钮位置
        x = start_x + self.PHASE_BTN_WIDTH / 2
        for btn_id in sorted(phase_buttons.keys()):
            btn = phase_buttons[btn_id]
            self._set_button_properties(btn, x, self.PHASE_BTN_WIDTH)
            text_id = f"{btn_id}_text"
            if text_id in button_texts:
                self._set_button_text_properties(button_texts[text_id], x)
            x += self.PHASE_BTN_WIDTH + self.BTN_GAP

        # 设置控制按钮位置
        if n_phases > 0:
            x = start_x + phase_group_width + self.BTN_SEPARATOR + self.CTRL_BTN_WIDTH / 2
        else:
            x = (self.CANVAS_WIDTH - ctrl_group_width) / 2 + self.CTRL_BTN_WIDTH / 2

        # 开始按钮
        self._set_button_properties(ctrl_buttons['btn_start'], x, self.CTRL_BTN_WIDTH)
        self._set_button_text_properties(button_texts['btn_start_text'], x)
        x += self.CTRL_BTN_WIDTH + self.BTN_GAP

        # 重置按钮
        self._set_button_properties(ctrl_buttons['btn_reset'], x, self.CTRL_BTN_WIDTH)
        self._set_button_text_properties(button_texts['btn_reset_text'], x)

        # 重建元素列表
        sdl['elements'] = other_elements + list(buttons.values()) + list(button_texts.values())

        return sdl

    def _create_button(self, btn_id: str, name: str, color: str) -> Dict:
        """创建按钮元素"""
        return {
            "id": btn_id,
            "name": f"{name}按钮",
            "type": "shape",
            "transform": {
                "position": {"x": 400, "y": self.BUTTON_Y},
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
                "fill": {"type": "solid", "color": color},
                "cornerRadius": 20
            }
        }

    def _create_button_text(self, text_id: str, content: str) -> Dict:
        """创建按钮文字元素"""
        return {
            "id": text_id,
            "name": "按钮文字",
            "type": "text",
            "transform": {
                "position": {"x": 400, "y": self.BUTTON_Y},
                "rotation": 0,
                "scale": {"x": 1, "y": 1},
                "anchor": {"x": 0.5, "y": 0.5}
            },
            "visible": True,
            "opacity": 1,
            "zIndex": 101,
            "interactive": False,
            "text": {
                "content": content,
                "fontFamily": "Arial",
                "fontSize": 14,
                "fontWeight": "bold",
                "color": "#ffffff",
                "align": "center"
            }
        }

    def _set_button_properties(self, btn: Dict, x: float, width: float):
        """设置按钮属性"""
        if 'transform' not in btn:
            btn['transform'] = {}
        btn['transform']['position'] = {"x": x, "y": self.BUTTON_Y}
        btn['transform']['rotation'] = 0
        btn['transform']['scale'] = {"x": 1, "y": 1}
        btn['transform']['anchor'] = {"x": 0.5, "y": 0.5}
        btn['zIndex'] = 100
        btn['interactive'] = True
        btn['visible'] = True
        btn['opacity'] = 1
        if 'shape' in btn:
            btn['shape']['width'] = width
            btn['shape']['height'] = self.BTN_HEIGHT

    def _set_button_text_properties(self, text: Dict, x: float):
        """设置按钮文字属性"""
        if 'transform' not in text:
            text['transform'] = {}
        text['transform']['position'] = {"x": x, "y": self.BUTTON_Y}
        text['zIndex'] = 101
        text['interactive'] = False

    def _fix_interactions(self, sdl: Dict[str, Any]) -> Dict[str, Any]:
        """修复交互问题"""
        interactions = sdl.get('interactions', [])
        elements = sdl.get('elements', [])
        timelines = sdl.get('timelines', [])

        element_ids = {e.get('id', '') for e in elements}
        timeline_ids = {t.get('id', '') for t in timelines}
        interaction_ids = {i.get('id', '') for i in interactions}

        # 确保click_start存在
        if 'click_start' not in interaction_ids:
            interactions.append({
                "id": "click_start",
                "name": "点击开始",
                "enabled": True,
                "trigger": {"type": "click", "targetId": "btn_start"},
                "conditions": [],
                "actions": [{"type": "playTimeline", "params": {"timelineId": "full_animation"}}]
            })

        # 确保click_reset存在
        if 'click_reset' not in interaction_ids:
            # 收集动画元素的初始状态
            reset_actions = [{"type": "stopAllTimelines", "params": {}}]
            animated_elements = self._find_animated_elements(sdl)
            for elem_id, state in animated_elements.items():
                for prop, value in state.items():
                    reset_actions.append({
                        "type": "setProperty",
                        "params": {"targetId": elem_id, "property": prop, "value": copy.deepcopy(value)}
                    })

            interactions.append({
                "id": "click_reset",
                "name": "点击重置",
                "enabled": True,
                "trigger": {"type": "click", "targetId": "btn_reset"},
                "conditions": [],
                "actions": reset_actions
            })

        # 修复每个交互
        for inter in interactions:
            # 确保必填字段
            if 'id' not in inter:
                inter['id'] = f"inter_{uuid.uuid4().hex[:6]}"
            if 'name' not in inter:
                inter['name'] = inter['id']
            if 'enabled' not in inter:
                inter['enabled'] = True
            else:
                inter['enabled'] = True  # 强制启用
            if 'conditions' not in inter:
                inter['conditions'] = []
            if 'actions' not in inter:
                inter['actions'] = []

            # 确保trigger完整
            trigger = inter.get('trigger', {})
            if 'type' not in trigger:
                trigger['type'] = 'click'
            if 'targetId' not in trigger:
                # 尝试从id推断
                if inter['id'].startswith('click_'):
                    target = inter['id'].replace('click_', 'btn_')
                    if target in element_ids:
                        trigger['targetId'] = target
            inter['trigger'] = trigger

        # 确保重置交互包含stopAllTimelines
        for inter in interactions:
            if inter.get('id') == 'click_reset':
                actions = inter.get('actions', [])
                has_stop = any(a.get('type') == 'stopAllTimelines' for a in actions)
                if not has_stop:
                    actions.insert(0, {"type": "stopAllTimelines", "params": {}})
                inter['actions'] = actions

        sdl['interactions'] = interactions
        return sdl

    def _find_animated_elements(self, sdl: Dict[str, Any]) -> Dict[str, Dict]:
        """查找所有动画元素及其初始状态"""
        animated = {}
        elements = sdl.get('elements', [])
        timelines = sdl.get('timelines', [])

        # 从时间线中收集被动画的元素ID
        animated_ids = set()
        for tl in timelines:
            for kf in tl.get('keyframes', []):
                target_id = kf.get('targetId', '')
                if target_id:
                    animated_ids.add(target_id)

        # 收集这些元素的初始状态
        for elem in elements:
            elem_id = elem.get('id', '')
            if elem_id in animated_ids:
                animated[elem_id] = {
                    'position': copy.deepcopy(elem.get('transform', {}).get('position', {'x': 400, 'y': 250})),
                    'opacity': elem.get('opacity', 1),
                    'rotation': elem.get('transform', {}).get('rotation', 0),
                    'scale': copy.deepcopy(elem.get('transform', {}).get('scale', {'x': 1, 'y': 1}))
                }

        return animated

    def _fix_timelines(self, sdl: Dict[str, Any]) -> Dict[str, Any]:
        """修复时间线问题"""
        timelines = sdl.get('timelines', [])
        timeline_ids = {t.get('id', '') for t in timelines}

        # 确保full_animation存在
        if 'full_animation' not in timeline_ids:
            # 合并所有阶段动画
            phase_timelines = [t for t in timelines if t.get('id', '').startswith('phase')]
            all_keyframes = []
            current_time = 0

            for tl in sorted(phase_timelines, key=lambda t: t.get('id', '')):
                for kf in tl.get('keyframes', []):
                    new_kf = copy.deepcopy(kf)
                    new_kf['time'] = current_time + kf.get('time', 0)
                    all_keyframes.append(new_kf)
                current_time += tl.get('duration', 2000)

            # 如果没有阶段动画，创建一个默认动画
            if not all_keyframes:
                # 查找可动画的元素
                elements = sdl.get('elements', [])
                animated_elem = None
                for elem in elements:
                    if not elem.get('id', '').startswith('btn_') and not elem.get('id', '').endswith('_text'):
                        if elem.get('type') == 'shape':
                            animated_elem = elem
                            break

                if animated_elem:
                    elem_id = animated_elem.get('id')
                    start_pos = animated_elem.get('transform', {}).get('position', {'x': 200, 'y': 250})
                    start_x = start_pos.get('x', 200) if isinstance(start_pos, dict) else 200
                    start_y = start_pos.get('y', 250) if isinstance(start_pos, dict) else 250
                    all_keyframes = [
                        {"time": 0, "targetId": elem_id, "property": "position",
                         "value": {'x': start_x, 'y': start_y}, "easing": "linear"},
                        {"time": 2000, "targetId": elem_id, "property": "position",
                         "value": {"x": 600, "y": start_y}, "easing": "easeInOut"}
                    ]
                    current_time = 2000

            timelines.append({
                "id": "full_animation",
                "name": "完整动画",
                "duration": max(current_time, 2000),
                "loop": False,
                "autoPlay": False,
                "keyframes": all_keyframes
            })

        # 修复每个时间线
        for tl in timelines:
            if 'id' not in tl:
                tl['id'] = f"tl_{uuid.uuid4().hex[:6]}"
            if 'name' not in tl:
                tl['name'] = tl['id']
            if 'duration' not in tl:
                tl['duration'] = 2000
            if 'loop' not in tl:
                tl['loop'] = False
            tl['autoPlay'] = False  # 强制关闭自动播放
            if 'keyframes' not in tl:
                tl['keyframes'] = []

            # 修复关键帧
            for kf in tl.get('keyframes', []):
                if 'time' not in kf:
                    kf['time'] = 0
                if 'easing' not in kf:
                    kf['easing'] = 'linear'

        sdl['timelines'] = timelines
        return sdl

    def _fix_references(self, sdl: Dict[str, Any]) -> Dict[str, Any]:
        """修复无效引用"""
        element_ids = {e.get('id', '') for e in sdl.get('elements', [])}
        timeline_ids = {t.get('id', '') for t in sdl.get('timelines', [])}

        # 修复交互中的无效引用
        valid_interactions = []
        for inter in sdl.get('interactions', []):
            target_id = inter.get('trigger', {}).get('targetId', '')

            # 如果目标元素不存在，跳过这个交互（除非是必须的）
            if target_id not in element_ids:
                if inter.get('id') in ['click_start', 'click_reset']:
                    # 必须的交互，修复目标
                    if inter.get('id') == 'click_start':
                        inter['trigger']['targetId'] = 'btn_start'
                    else:
                        inter['trigger']['targetId'] = 'btn_reset'
                else:
                    continue  # 跳过无效交互

            # 修复actions中的无效引用
            valid_actions = []
            for action in inter.get('actions', []):
                action_type = action.get('type', '')
                params = action.get('params', {})

                if action_type == 'playTimeline':
                    tl_id = params.get('timelineId', '')
                    if tl_id in timeline_ids:
                        valid_actions.append(action)
                    elif inter.get('id') == 'click_start':
                        # 开始按钮必须播放full_animation
                        action['params']['timelineId'] = 'full_animation'
                        valid_actions.append(action)
                elif action_type == 'setProperty':
                    elem_id = params.get('targetId', '')
                    if elem_id in element_ids:
                        valid_actions.append(action)
                elif action_type == 'stopAllTimelines':
                    valid_actions.append(action)
                else:
                    valid_actions.append(action)

            inter['actions'] = valid_actions
            valid_interactions.append(inter)

        sdl['interactions'] = valid_interactions

        # 修复时间线中的无效引用
        for tl in sdl.get('timelines', []):
            valid_keyframes = []
            for kf in tl.get('keyframes', []):
                target_id = kf.get('targetId', '')
                if target_id in element_ids:
                    valid_keyframes.append(kf)
            tl['keyframes'] = valid_keyframes

        return sdl

    def _fix_coordinates(self, sdl: Dict[str, Any]) -> Dict[str, Any]:
        """修复坐标范围"""
        for elem in sdl.get('elements', []):
            pos = elem.get('transform', {}).get('position', {})
            if isinstance(pos, dict):
                if 'x' in pos:
                    pos['x'] = max(20, min(780, pos['x']))
                if 'y' in pos:
                    # 按钮保持在460
                    if elem.get('id', '').startswith('btn_'):
                        pos['y'] = self.BUTTON_Y
                    else:
                        pos['y'] = max(20, min(480, pos['y']))

        # 修复动画关键帧中的坐标
        for tl in sdl.get('timelines', []):
            for kf in tl.get('keyframes', []):
                if kf.get('property') == 'position':
                    val = kf.get('value', {})
                    if isinstance(val, dict):
                        if 'x' in val:
                            val['x'] = max(20, min(780, val['x']))
                        if 'y' in val:
                            val['y'] = max(20, min(400, val['y']))  # 动画区域不超过400

        return sdl

    def _fix_duplicate_ids(self, sdl: Dict[str, Any]) -> Dict[str, Any]:
        """修复重复ID"""
        # 修复元素ID
        seen_ids = set()
        for elem in sdl.get('elements', []):
            elem_id = elem.get('id', '')
            if elem_id in seen_ids:
                new_id = f"{elem_id}_{uuid.uuid4().hex[:4]}"
                elem['id'] = new_id
            seen_ids.add(elem.get('id', ''))

        # 修复交互ID
        seen_ids = set()
        for inter in sdl.get('interactions', []):
            inter_id = inter.get('id', '')
            if inter_id in seen_ids:
                new_id = f"{inter_id}_{uuid.uuid4().hex[:4]}"
                inter['id'] = new_id
            seen_ids.add(inter.get('id', ''))

        # 修复时间线ID
        seen_ids = set()
        for tl in sdl.get('timelines', []):
            tl_id = tl.get('id', '')
            if tl_id in seen_ids:
                new_id = f"{tl_id}_{uuid.uuid4().hex[:4]}"
                tl['id'] = new_id
            seen_ids.add(tl.get('id', ''))

        return sdl

    def _get_safe_fallback_template(self, original_sdl: Dict[str, Any]) -> Dict[str, Any]:
        """生成安全的回退模板 - 使用语义形状"""
        title = original_sdl.get('name', '互动模拟')
        desc = original_sdl.get('description', '点击按钮查看演示')
        bg_color = original_sdl.get('canvas', {}).get('backgroundColor', '#1e293b')

        # 根据标题选择合适的语义形状
        title_lower = title.lower()
        if any(kw in title_lower for kw in ['游泳', '泳', '划水']):
            shape_type = 'swimmer'
        elif any(kw in title_lower for kw in ['跑', '冲刺', '起跑']):
            shape_type = 'runner'
        elif any(kw in title_lower for kw in ['跳', '跳高', '跳远']):
            shape_type = 'jumper'
        else:
            shape_type = 'person'

        # 获取语义形状定义
        shape_def = SEMANTIC_SHAPES.get(shape_type, SEMANTIC_SHAPES.get('person'))
        default_colors = shape_def.get('defaultColors', {'primary': '#fbbf24', 'secondary': '#f59e0b'})

        # 生成语义形状的元素
        demo_elements = []
        base_x, base_y = 150, 250
        for i, part in enumerate(shape_def.get('parts', [])):
            offset = part.get('offset', {'x': 0, 'y': 0})
            # 确保 offset 是字典类型
            if not isinstance(offset, dict):
                offset = {'x': 0, 'y': 0}
            offset_x = offset.get('x', 0) if isinstance(offset.get('x'), (int, float)) else 0
            offset_y = offset.get('y', 0) if isinstance(offset.get('y'), (int, float)) else 0
            part_type = part.get('type', 'circle')
            size = part.get('size', {})
            color_key = part.get('colorKey', 'primary')
            color = default_colors.get(color_key, '#fbbf24')

            elem = {
                "id": f"demo_{part.get('id', i)}",
                "name": f"演示元素_{part.get('id', i)}",
                "type": "shape",
                "transform": {
                    "position": {"x": base_x + offset_x, "y": base_y + offset_y},
                    "rotation": part.get('rotation', 0),
                    "scale": {"x": 1, "y": 1},
                    "anchor": {"x": 0.5, "y": 0.5}
                },
                "visible": True,
                "opacity": 1,
                "zIndex": 10 + i,
                "interactive": False
            }

            # 设置形状
            if part_type == 'circle':
                elem['shape'] = {"shapeType": "circle", "radius": size.get('radius', 20), "fill": {"type": "solid", "color": color}}
            elif part_type == 'ellipse':
                elem['shape'] = {"shapeType": "ellipse", "radiusX": size.get('radiusX', 30), "radiusY": size.get('radiusY', 15), "fill": {"type": "solid", "color": color}}
            elif part_type == 'rectangle':
                elem['shape'] = {"shapeType": "rectangle", "width": size.get('width', 50), "height": size.get('height', 20), "fill": {"type": "solid", "color": color}}
            else:
                elem['shape'] = {"shapeType": "circle", "radius": 20, "fill": {"type": "solid", "color": color}}

            if part.get('stroke'):
                elem['shape']['stroke'] = part['stroke']

            demo_elements.append(elem)

        # 生成动画关键帧
        keyframes = []
        for elem in demo_elements:
            elem_id = elem['id']
            start_pos = elem['transform']['position'].copy()
            start_x = start_pos.get('x', 150) if isinstance(start_pos, dict) else 150
            start_y = start_pos.get('y', 250) if isinstance(start_pos, dict) else 250
            end_pos = {'x': start_x + 500, 'y': start_y}
            start_pos_safe = {'x': start_x, 'y': start_y}
            keyframes.append({"time": 0, "targetId": elem_id, "property": "position", "value": start_pos_safe, "easing": "linear"})
            keyframes.append({"time": 2000, "targetId": elem_id, "property": "position", "value": end_pos, "easing": "easeInOut"})

        # 生成重置动作
        reset_actions = [{"type": "stopAllTimelines", "params": {}}]
        for elem in demo_elements:
            reset_actions.append({
                "type": "setProperty",
                "params": {"targetId": elem['id'], "property": "position", "value": elem['transform']['position'].copy()}
            })

        return {
            "version": "1.0.0",
            "id": f"safe_{uuid.uuid4().hex[:8]}",
            "name": title,
            "description": desc,
            "canvas": {
                "width": 800,
                "height": 500,
                "backgroundColor": bg_color,
                "renderer": "pixi",
                "antialias": True
            },
            "assets": {"icons": [], "images": [], "sounds": [], "fonts": []},
            "elements": [
                # 标题
                {
                    "id": "title_text",
                    "name": "标题",
                    "type": "text",
                    "transform": {"position": {"x": 400, "y": 40}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}},
                    "visible": True,
                    "opacity": 1,
                    "zIndex": 50,
                    "interactive": False,
                    "text": {"content": title, "fontFamily": "Arial", "fontSize": 24, "fontWeight": "bold", "color": "#ffffff", "align": "center"}
                },
                # 副标题
                {
                    "id": "subtitle_text",
                    "name": "副标题",
                    "type": "text",
                    "transform": {"position": {"x": 400, "y": 75}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}},
                    "visible": True,
                    "opacity": 1,
                    "zIndex": 50,
                    "interactive": False,
                    "text": {"content": desc, "fontFamily": "Arial", "fontSize": 14, "fontWeight": "normal", "color": "#94a3b8", "align": "center"}
                },
                # 演示元素（语义形状）
                *demo_elements,
                # 开始按钮
                {
                    "id": "btn_start",
                    "name": "开始按钮",
                    "type": "shape",
                    "transform": {"position": {"x": 355, "y": 460}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}},
                    "visible": True,
                    "opacity": 1,
                    "zIndex": 100,
                    "interactive": True,
                    "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#22c55e"}, "cornerRadius": 20}
                },
                {
                    "id": "btn_start_text",
                    "name": "开始文字",
                    "type": "text",
                    "transform": {"position": {"x": 355, "y": 460}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}},
                    "visible": True,
                    "opacity": 1,
                    "zIndex": 101,
                    "interactive": False,
                    "text": {"content": "▶ 开始", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}
                },
                # 重置按钮
                {
                    "id": "btn_reset",
                    "name": "重置按钮",
                    "type": "shape",
                    "transform": {"position": {"x": 465, "y": 460}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}},
                    "visible": True,
                    "opacity": 1,
                    "zIndex": 100,
                    "interactive": True,
                    "shape": {"shapeType": "rectangle", "width": 90, "height": 40, "fill": {"type": "solid", "color": "#ef4444"}, "cornerRadius": 20}
                },
                {
                    "id": "btn_reset_text",
                    "name": "重置文字",
                    "type": "text",
                    "transform": {"position": {"x": 465, "y": 460}, "rotation": 0, "scale": {"x": 1, "y": 1}, "anchor": {"x": 0.5, "y": 0.5}},
                    "visible": True,
                    "opacity": 1,
                    "zIndex": 101,
                    "interactive": False,
                    "text": {"content": "↺ 重置", "fontFamily": "Arial", "fontSize": 14, "fontWeight": "bold", "color": "#ffffff", "align": "center"}
                }
            ],
            "timelines": [
                {
                    "id": "full_animation",
                    "name": "完整动画",
                    "duration": 2000,
                    "loop": False,
                    "autoPlay": False,
                    "keyframes": keyframes
                }
            ],
            "interactions": [
                {
                    "id": "click_start",
                    "name": "点击开始",
                    "enabled": True,
                    "trigger": {"type": "click", "targetId": "btn_start"},
                    "conditions": [],
                    "actions": [{"type": "playTimeline", "params": {"timelineId": "full_animation"}}]
                },
                {
                    "id": "click_reset",
                    "name": "点击重置",
                    "enabled": True,
                    "trigger": {"type": "click", "targetId": "btn_reset"},
                    "conditions": [],
                    "actions": reset_actions
                }
            ],
            "variables": []
        }
