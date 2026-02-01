# -*- coding: utf-8 -*-
"""
SDL 验证器
验证SDL格式的完整性和正确性
"""

from typing import Dict, List, Any, Tuple


class ValidationError:
    """验证错误"""

    def __init__(self, error_type: str, message: str, path: str = "", data: Any = None):
        self.type = error_type
        self.message = message
        self.path = path
        self.data = data

    def __repr__(self):
        return f"ValidationError({self.type}: {self.message})"


class SDLValidator:
    """SDL验证器"""

    # 画布常量
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 500
    BUTTON_Y = 460

    # 必须存在的按钮
    REQUIRED_BUTTONS = ['btn_start', 'btn_reset']

    # 必须存在的交互
    REQUIRED_INTERACTIONS = ['click_start', 'click_reset']

    def validate(self, sdl: Dict[str, Any]) -> List[ValidationError]:
        """
        验证SDL

        Returns:
            错误列表，空列表表示验证通过
        """
        errors = []

        # 1. 基础结构验证
        errors.extend(self._validate_base_structure(sdl))

        # 2. 元素验证
        errors.extend(self._validate_elements(sdl))

        # 3. 按钮验证
        errors.extend(self._validate_buttons(sdl))

        # 4. 交互验证
        errors.extend(self._validate_interactions(sdl))

        # 5. 时间线验证
        errors.extend(self._validate_timelines(sdl))

        # 6. 引用完整性验证
        errors.extend(self._validate_references(sdl))

        return errors

    def _validate_base_structure(self, sdl: Dict[str, Any]) -> List[ValidationError]:
        """验证基础结构"""
        errors = []

        required_fields = ['version', 'id', 'name', 'canvas', 'elements', 'timelines', 'interactions']
        for field in required_fields:
            if field not in sdl:
                errors.append(ValidationError(
                    'missing_field',
                    f"缺少必填字段: {field}",
                    path=field
                ))

        # 验证canvas
        canvas = sdl.get('canvas', {})
        if canvas.get('width') != self.CANVAS_WIDTH:
            errors.append(ValidationError(
                'invalid_canvas',
                f"画布宽度必须为{self.CANVAS_WIDTH}",
                path='canvas.width',
                data={'expected': self.CANVAS_WIDTH, 'actual': canvas.get('width')}
            ))
        if canvas.get('height') != self.CANVAS_HEIGHT:
            errors.append(ValidationError(
                'invalid_canvas',
                f"画布高度必须为{self.CANVAS_HEIGHT}",
                path='canvas.height',
                data={'expected': self.CANVAS_HEIGHT, 'actual': canvas.get('height')}
            ))

        return errors

    def _validate_elements(self, sdl: Dict[str, Any]) -> List[ValidationError]:
        """验证元素"""
        errors = []
        elements = sdl.get('elements', [])
        seen_ids = set()

        for i, elem in enumerate(elements):
            elem_id = elem.get('id', '')
            path = f"elements[{i}]"

            # ID唯一性
            if elem_id in seen_ids:
                errors.append(ValidationError(
                    'duplicate_id',
                    f"元素ID重复: {elem_id}",
                    path=path,
                    data={'id': elem_id}
                ))
            seen_ids.add(elem_id)

            # 必填字段
            required = ['id', 'name', 'type', 'transform', 'zIndex']
            for field in required:
                if field not in elem:
                    errors.append(ValidationError(
                        'missing_element_field',
                        f"元素缺少必填字段: {field}",
                        path=f"{path}.{field}",
                        data={'element_id': elem_id}
                    ))

            # 坐标范围 - 必须在画布内
            pos = elem.get('transform', {}).get('position', {})
            x, y = pos.get('x', 0), pos.get('y', 0)
            if not (0 <= x <= self.CANVAS_WIDTH):
                errors.append(ValidationError(
                    'coordinate_out_of_range',
                    f"元素X坐标超出范围: {x}",
                    path=f"{path}.transform.position.x",
                    data={'element_id': elem_id, 'x': x}
                ))
            if not (0 <= y <= self.CANVAS_HEIGHT):
                errors.append(ValidationError(
                    'coordinate_out_of_range',
                    f"元素Y坐标超出范围: {y}",
                    path=f"{path}.transform.position.y",
                    data={'element_id': elem_id, 'y': y}
                ))

        return errors

    def _validate_buttons(self, sdl: Dict[str, Any]) -> List[ValidationError]:
        """验证按钮"""
        errors = []
        elements = sdl.get('elements', [])

        # 收集所有按钮
        buttons = {}
        for elem in elements:
            elem_id = elem.get('id', '')
            if elem_id.startswith('btn_') and '_text' not in elem_id:
                buttons[elem_id] = elem

        # 检查必须的按钮
        for btn_id in self.REQUIRED_BUTTONS:
            if btn_id not in buttons:
                errors.append(ValidationError(
                    'missing_required_button',
                    f"缺少必须的按钮: {btn_id}",
                    path='elements',
                    data={'button_id': btn_id}
                ))

        # 验证按钮属性
        for btn_id, btn in buttons.items():
            # Y坐标
            y = btn.get('transform', {}).get('position', {}).get('y', 0)
            if y != self.BUTTON_Y:
                errors.append(ValidationError(
                    'invalid_button_y',
                    f"按钮Y坐标必须为{self.BUTTON_Y}: {btn_id}",
                    path=f"elements.{btn_id}.transform.position.y",
                    data={'button_id': btn_id, 'expected': self.BUTTON_Y, 'actual': y}
                ))

            # zIndex
            z_index = btn.get('zIndex', 0)
            if z_index < 100:
                errors.append(ValidationError(
                    'invalid_button_zindex',
                    f"按钮zIndex必须>=100: {btn_id}",
                    path=f"elements.{btn_id}.zIndex",
                    data={'button_id': btn_id, 'expected': '>=100', 'actual': z_index}
                ))

            # interactive
            if not btn.get('interactive', False):
                errors.append(ValidationError(
                    'button_not_interactive',
                    f"按钮必须设置interactive=true: {btn_id}",
                    path=f"elements.{btn_id}.interactive",
                    data={'button_id': btn_id}
                ))

        # 检查按钮重叠
        button_positions = [(btn_id, btn.get('transform', {}).get('position', {}).get('x', 0),
                            btn.get('shape', {}).get('width', 100))
                           for btn_id, btn in buttons.items()]
        button_positions.sort(key=lambda x: x[1])

        for i in range(len(button_positions) - 1):
            btn1_id, x1, w1 = button_positions[i]
            btn2_id, x2, w2 = button_positions[i + 1]
            min_distance = (w1 + w2) / 2 + 10  # 至少10px间距

            if x2 - x1 < min_distance:
                errors.append(ValidationError(
                    'button_overlap',
                    f"按钮重叠: {btn1_id} 和 {btn2_id}",
                    path='elements',
                    data={'button1': btn1_id, 'button2': btn2_id, 'distance': x2 - x1, 'min_required': min_distance}
                ))

        # 检查按钮文字
        for btn_id in buttons:
            text_id = f"{btn_id}_text"
            text_elem = next((e for e in elements if e.get('id') == text_id), None)
            if not text_elem:
                errors.append(ValidationError(
                    'missing_button_text',
                    f"按钮缺少对应的文字元素: {text_id}",
                    path='elements',
                    data={'button_id': btn_id, 'text_id': text_id}
                ))
            elif text_elem.get('interactive', True):
                errors.append(ValidationError(
                    'button_text_interactive',
                    f"按钮文字不应该是interactive: {text_id}",
                    path=f"elements.{text_id}.interactive",
                    data={'text_id': text_id}
                ))

        return errors

    def _validate_interactions(self, sdl: Dict[str, Any]) -> List[ValidationError]:
        """验证交互"""
        errors = []
        interactions = sdl.get('interactions', [])
        seen_ids = set()

        # 检查必须的交互
        interaction_ids = {i.get('id', '') for i in interactions}
        for inter_id in self.REQUIRED_INTERACTIONS:
            if inter_id not in interaction_ids:
                errors.append(ValidationError(
                    'missing_required_interaction',
                    f"缺少必须的交互: {inter_id}",
                    path='interactions',
                    data={'interaction_id': inter_id}
                ))

        for i, inter in enumerate(interactions):
            inter_id = inter.get('id', '')
            path = f"interactions[{i}]"

            # ID唯一性
            if inter_id in seen_ids:
                errors.append(ValidationError(
                    'duplicate_interaction_id',
                    f"交互ID重复: {inter_id}",
                    path=path,
                    data={'id': inter_id}
                ))
            seen_ids.add(inter_id)

            # 必填字段
            required = ['id', 'name', 'enabled', 'trigger', 'conditions', 'actions']
            for field in required:
                if field not in inter:
                    errors.append(ValidationError(
                        'missing_interaction_field',
                        f"交互缺少必填字段: {field}",
                        path=f"{path}.{field}",
                        data={'interaction_id': inter_id}
                    ))

            # enabled必须为true
            if not inter.get('enabled', False):
                errors.append(ValidationError(
                    'interaction_disabled',
                    f"交互未启用: {inter_id}",
                    path=f"{path}.enabled",
                    data={'interaction_id': inter_id}
                ))

            # trigger验证
            trigger = inter.get('trigger', {})
            if 'type' not in trigger:
                errors.append(ValidationError(
                    'missing_trigger_type',
                    f"交互缺少trigger.type: {inter_id}",
                    path=f"{path}.trigger.type",
                    data={'interaction_id': inter_id}
                ))
            if 'targetId' not in trigger:
                errors.append(ValidationError(
                    'missing_trigger_target',
                    f"交互缺少trigger.targetId: {inter_id}",
                    path=f"{path}.trigger.targetId",
                    data={'interaction_id': inter_id}
                ))

            # actions验证
            actions = inter.get('actions', [])
            if not actions:
                errors.append(ValidationError(
                    'empty_actions',
                    f"交互没有actions: {inter_id}",
                    path=f"{path}.actions",
                    data={'interaction_id': inter_id}
                ))

        # 验证重置交互必须包含stopAllTimelines
        reset_inter = next((i for i in interactions if i.get('id') == 'click_reset'), None)
        if reset_inter:
            actions = reset_inter.get('actions', [])
            has_stop = any(a.get('type') == 'stopAllTimelines' for a in actions)
            if not has_stop:
                errors.append(ValidationError(
                    'reset_missing_stop',
                    "重置交互必须包含stopAllTimelines动作",
                    path='interactions.click_reset.actions',
                    data={}
                ))

        return errors

    def _validate_timelines(self, sdl: Dict[str, Any]) -> List[ValidationError]:
        """验证时间线"""
        errors = []
        timelines = sdl.get('timelines', [])
        seen_ids = set()

        # 检查full_animation是否存在
        timeline_ids = {t.get('id', '') for t in timelines}
        if 'full_animation' not in timeline_ids:
            errors.append(ValidationError(
                'missing_full_animation',
                "缺少full_animation时间线",
                path='timelines',
                data={}
            ))

        for i, tl in enumerate(timelines):
            tl_id = tl.get('id', '')
            path = f"timelines[{i}]"

            # ID唯一性
            if tl_id in seen_ids:
                errors.append(ValidationError(
                    'duplicate_timeline_id',
                    f"时间线ID重复: {tl_id}",
                    path=path,
                    data={'id': tl_id}
                ))
            seen_ids.add(tl_id)

            # 必填字段
            required = ['id', 'name', 'duration', 'loop', 'autoPlay', 'keyframes']
            for field in required:
                if field not in tl:
                    errors.append(ValidationError(
                        'missing_timeline_field',
                        f"时间线缺少必填字段: {field}",
                        path=f"{path}.{field}",
                        data={'timeline_id': tl_id}
                    ))

            # autoPlay必须为false
            if tl.get('autoPlay', True):
                errors.append(ValidationError(
                    'timeline_autoplay',
                    f"时间线autoPlay必须为false: {tl_id}",
                    path=f"{path}.autoPlay",
                    data={'timeline_id': tl_id}
                ))

            # 验证关键帧
            keyframes = tl.get('keyframes', [])
            for j, kf in enumerate(keyframes):
                kf_path = f"{path}.keyframes[{j}]"
                kf_required = ['time', 'targetId', 'property', 'value', 'easing']
                for field in kf_required:
                    if field not in kf:
                        errors.append(ValidationError(
                            'missing_keyframe_field',
                            f"关键帧缺少必填字段: {field}",
                            path=f"{kf_path}.{field}",
                            data={'timeline_id': tl_id, 'keyframe_index': j}
                        ))

        return errors

    def _validate_references(self, sdl: Dict[str, Any]) -> List[ValidationError]:
        """验证引用完整性"""
        errors = []

        # 收集所有元素ID
        element_ids = {e.get('id', '') for e in sdl.get('elements', [])}

        # 收集所有时间线ID
        timeline_ids = {t.get('id', '') for t in sdl.get('timelines', [])}

        # 验证交互中的引用
        for i, inter in enumerate(sdl.get('interactions', [])):
            inter_id = inter.get('id', '')

            # 验证trigger.targetId
            target_id = inter.get('trigger', {}).get('targetId', '')
            if target_id and target_id not in element_ids:
                errors.append(ValidationError(
                    'invalid_trigger_target',
                    f"交互引用了不存在的元素: {target_id}",
                    path=f"interactions[{i}].trigger.targetId",
                    data={'interaction_id': inter_id, 'target_id': target_id}
                ))

            # 验证actions中的引用
            for j, action in enumerate(inter.get('actions', [])):
                action_type = action.get('type', '')
                params = action.get('params', {})

                if action_type == 'playTimeline':
                    tl_id = params.get('timelineId', '')
                    if tl_id and tl_id not in timeline_ids:
                        errors.append(ValidationError(
                            'invalid_timeline_reference',
                            f"交互引用了不存在的时间线: {tl_id}",
                            path=f"interactions[{i}].actions[{j}].params.timelineId",
                            data={'interaction_id': inter_id, 'timeline_id': tl_id}
                        ))

                elif action_type == 'setProperty':
                    elem_id = params.get('targetId', '')
                    if elem_id and elem_id not in element_ids:
                        errors.append(ValidationError(
                            'invalid_element_reference',
                            f"交互引用了不存在的元素: {elem_id}",
                            path=f"interactions[{i}].actions[{j}].params.targetId",
                            data={'interaction_id': inter_id, 'element_id': elem_id}
                        ))

        # 验证时间线中的引用
        for i, tl in enumerate(sdl.get('timelines', [])):
            tl_id = tl.get('id', '')
            for j, kf in enumerate(tl.get('keyframes', [])):
                target_id = kf.get('targetId', '')
                if target_id and target_id not in element_ids:
                    errors.append(ValidationError(
                        'invalid_keyframe_target',
                        f"关键帧引用了不存在的元素: {target_id}",
                        path=f"timelines[{i}].keyframes[{j}].targetId",
                        data={'timeline_id': tl_id, 'target_id': target_id}
                    ))

        return errors
