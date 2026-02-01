# -*- coding: utf-8 -*-
"""
SDL 编译器测试
"""

import sys
import json
sys.path.insert(0, r'F:\9\hercux-admin\backend')

from app.services.studio.sdl_compiler import SDLCompiler, SDLValidator, SDLAutoFixer


def test_compile_basic():
    """测试基本编译功能"""
    print("=" * 60)
    print("测试1: 基本编译功能")
    print("=" * 60)

    ai_input = {
        "scene": {
            "title": "海豚腿波浪传导技术",
            "description": "展示蝶泳海豚腿的波浪传导过程",
            "background_color": "#0c4a6e"
        },
        "elements": [
            {
                "id": "pool_bg",
                "name": "泳池背景",
                "type": "rectangle",
                "position": "center",
                "size": {"width": 760, "height": 300},
                "color": "#0369a1",
                "layer": "background"
            },
            {
                "id": "swimmer",
                "name": "游泳者",
                "type": "circle",
                "position": {"x": 150, "y": 250},
                "size": {"radius": 25},
                "color": "#fbbf24",
                "stroke": {"color": "#ffffff", "width": 3},
                "layer": "content",
                "animated": True
            }
        ],
        "phases": [
            {
                "name": "躯干发力",
                "description": "胸部下压启动波浪",
                "animation": {
                    "target": "swimmer",
                    "keyframes": [
                        {"position": {"x": 150, "y": 250}},
                        {"position": {"x": 300, "y": 230}}
                    ],
                    "duration": 1500
                }
            },
            {
                "name": "髋部传导",
                "description": "能量传递到髋部",
                "animation": {
                    "target": "swimmer",
                    "keyframes": [
                        {"position": {"x": 300, "y": 230}},
                        {"position": {"x": 450, "y": 260}}
                    ],
                    "duration": 1500
                }
            },
            {
                "name": "腿部完成",
                "description": "小腿鞭打完成动作",
                "animation": {
                    "target": "swimmer",
                    "keyframes": [
                        {"position": {"x": 450, "y": 260}},
                        {"position": {"x": 650, "y": 250}}
                    ],
                    "duration": 1500
                }
            }
        ]
    }

    compiler = SDLCompiler()
    sdl = compiler.compile(ai_input)

    print(f"生成的SDL:")
    print(f"  - 名称: {sdl['name']}")
    print(f"  - 元素数量: {len(sdl['elements'])}")
    print(f"  - 时间线数量: {len(sdl['timelines'])}")
    print(f"  - 交互数量: {len(sdl['interactions'])}")

    # 检查按钮
    buttons = [e for e in sdl['elements'] if e['id'].startswith('btn_') and '_text' not in e['id']]
    print(f"  - 按钮数量: {len(buttons)}")
    for btn in buttons:
        pos = btn['transform']['position']
        print(f"    - {btn['id']}: x={pos['x']}, y={pos['y']}, zIndex={btn['zIndex']}")

    # 检查必须的交互
    interaction_ids = [i['id'] for i in sdl['interactions']]
    print(f"  - 交互列表: {interaction_ids}")
    assert 'click_start' in interaction_ids, "缺少click_start交互"
    assert 'click_reset' in interaction_ids, "缺少click_reset交互"

    # 检查重置交互
    reset_inter = next(i for i in sdl['interactions'] if i['id'] == 'click_reset')
    action_types = [a['type'] for a in reset_inter['actions']]
    print(f"  - 重置动作: {action_types}")
    assert 'stopAllTimelines' in action_types, "重置交互缺少stopAllTimelines"
    assert 'setProperty' in action_types, "重置交��缺少setProperty"

    print("✓ 测试1通过!")
    return sdl


def test_validator():
    """测试验证器"""
    print("\n" + "=" * 60)
    print("测试2: 验证器")
    print("=" * 60)

    # 先编译一个正确的SDL
    compiler = SDLCompiler()
    ai_input = {
        "scene": {"title": "测试场景"},
        "elements": [
            {"id": "ball", "name": "球", "type": "circle", "position": {"x": 200, "y": 250},
             "size": {"radius": 30}, "color": "#6366f1", "animated": True}
        ],
        "phases": [
            {"name": "移动", "animation": {"target": "ball",
             "keyframes": [{"position": {"x": 200, "y": 250}}, {"position": {"x": 600, "y": 250}}],
             "duration": 2000}}
        ]
    }
    sdl = compiler.compile(ai_input)

    validator = SDLValidator()
    errors = validator.validate(sdl)

    print(f"验证结果: {len(errors)} 个错误")
    for err in errors:
        print(f"  - {err.type}: {err.message}")

    if len(errors) == 0:
        print("✓ 测试2通过! SDL验证无错误")
    else:
        print("✗ 测试2失败! 有验证错误")

    return sdl, errors


def test_fixer_button_overlap():
    """测试修复按钮重叠"""
    print("\n" + "=" * 60)
    print("测试3: 修复按钮重叠")
    print("=" * 60)

    # 创建一个按钮重叠的SDL
    broken_sdl = {
        "version": "1.0.0",
        "id": "test",
        "name": "测试",
        "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e293b"},
        "elements": [
            {"id": "demo", "name": "演示", "type": "shape", "transform": {"position": {"x": 400, "y": 250}},
             "zIndex": 10, "shape": {"shapeType": "circle", "radius": 30, "fill": {"color": "#6366f1"}}},
            # 重叠的按钮
            {"id": "btn_phase1", "name": "阶段1", "type": "shape",
             "transform": {"position": {"x": 400, "y": 460}}, "zIndex": 100, "interactive": True,
             "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"color": "#3b82f6"}}},
            {"id": "btn_phase1_text", "name": "阶段1文字", "type": "text",
             "transform": {"position": {"x": 400, "y": 460}}, "zIndex": 101, "interactive": False,
             "text": {"content": "阶段1", "fontSize": 14, "color": "#ffffff"}},
            {"id": "btn_phase2", "name": "阶段2", "type": "shape",
             "transform": {"position": {"x": 400, "y": 460}}, "zIndex": 100, "interactive": True,  # 同样位置!
             "shape": {"shapeType": "rectangle", "width": 100, "height": 40, "fill": {"color": "#22c55e"}}},
            {"id": "btn_phase2_text", "name": "阶段2文字", "type": "text",
             "transform": {"position": {"x": 400, "y": 460}}, "zIndex": 101, "interactive": False,
             "text": {"content": "阶段2", "fontSize": 14, "color": "#ffffff"}},
        ],
        "timelines": [
            {"id": "phase1_animation", "name": "阶段1动画", "duration": 2000, "loop": False, "autoPlay": False,
             "keyframes": [{"time": 0, "targetId": "demo", "property": "position", "value": {"x": 200, "y": 250}, "easing": "linear"},
                          {"time": 2000, "targetId": "demo", "property": "position", "value": {"x": 400, "y": 250}, "easing": "easeInOut"}]},
            {"id": "phase2_animation", "name": "阶段2动画", "duration": 2000, "loop": False, "autoPlay": False,
             "keyframes": [{"time": 0, "targetId": "demo", "property": "position", "value": {"x": 400, "y": 250}, "easing": "linear"},
                          {"time": 2000, "targetId": "demo", "property": "position", "value": {"x": 600, "y": 250}, "easing": "easeInOut"}]},
        ],
        "interactions": [
            {"id": "click_phase1", "name": "点击阶段1", "enabled": True,
             "trigger": {"type": "click", "targetId": "btn_phase1"}, "conditions": [],
             "actions": [{"type": "playTimeline", "params": {"timelineId": "phase1_animation"}}]},
            {"id": "click_phase2", "name": "点击阶段2", "enabled": True,
             "trigger": {"type": "click", "targetId": "btn_phase2"}, "conditions": [],
             "actions": [{"type": "playTimeline", "params": {"timelineId": "phase2_animation"}}]},
        ],
        "variables": []
    }

    validator = SDLValidator()
    fixer = SDLAutoFixer()

    # 验证修复前
    errors_before = validator.validate(broken_sdl)
    print(f"修复前错误数: {len(errors_before)}")
    for err in errors_before:
        print(f"  - {err.type}: {err.message}")

    # 修复
    fixed_sdl = fixer.fix_and_validate(broken_sdl, validator)

    # 验证修复后
    errors_after = validator.validate(fixed_sdl)
    print(f"修复后错误数: {len(errors_after)}")

    # 检查按钮位置
    buttons = [e for e in fixed_sdl['elements'] if e['id'].startswith('btn_') and '_text' not in e['id']]
    print(f"修复后按钮位置:")
    for btn in buttons:
        pos = btn['transform']['position']
        print(f"  - {btn['id']}: x={pos['x']:.1f}, y={pos['y']}")

    if len(errors_after) == 0:
        print("✓ 测试3通过! 按钮重叠已修复")
    else:
        print("✗ 测试3失败!")
        for err in errors_after:
            print(f"  - {err.type}: {err.message}")

    return fixed_sdl


def test_fixer_missing_buttons():
    """测试修复缺失按钮"""
    print("\n" + "=" * 60)
    print("测试4: 修复缺失的开始/重置按钮")
    print("=" * 60)

    # 创建一个缺少开始和重置按钮的SDL
    broken_sdl = {
        "version": "1.0.0",
        "id": "test",
        "name": "测试",
        "canvas": {"width": 800, "height": 500, "backgroundColor": "#1e293b"},
        "elements": [
            {"id": "demo", "name": "演示", "type": "shape", "transform": {"position": {"x": 200, "y": 250}},
             "zIndex": 10, "shape": {"shapeType": "circle", "radius": 30, "fill": {"color": "#6366f1"}}},
        ],
        "timelines": [],
        "interactions": [],
        "variables": []
    }

    validator = SDLValidator()
    fixer = SDLAutoFixer()

    # 修复
    fixed_sdl = fixer.fix_and_validate(broken_sdl, validator)

    # 验证
    errors = validator.validate(fixed_sdl)
    print(f"修复后错误数: {len(errors)}")

    # 检查按钮
    element_ids = [e['id'] for e in fixed_sdl['elements']]
    print(f"元素列表: {element_ids}")
    assert 'btn_start' in element_ids, "缺少btn_start"
    assert 'btn_reset' in element_ids, "缺少btn_reset"

    # 检查交互
    interaction_ids = [i['id'] for i in fixed_sdl['interactions']]
    print(f"交互列表: {interaction_ids}")
    assert 'click_start' in interaction_ids, "缺少click_start"
    assert 'click_reset' in interaction_ids, "缺少click_reset"

    if len(errors) == 0:
        print("✓ 测试4通过! 缺失按钮已添加")
    else:
        print("✗ 测试4失败!")

    return fixed_sdl


def test_reset_functionality():
    """测试重置功能"""
    print("\n" + "=" * 60)
    print("测试5: 重置功能完整性")
    print("=" * 60)

    compiler = SDLCompiler()
    ai_input = {
        "scene": {"title": "重置测试"},
        "elements": [
            {"id": "ball", "name": "球", "type": "circle", "position": {"x": 100, "y": 200},
             "size": {"radius": 30}, "color": "#6366f1", "animated": True}
        ],
        "phases": [
            {"name": "移动", "animation": {"target": "ball",
             "keyframes": [{"position": {"x": 100, "y": 200}}, {"position": {"x": 700, "y": 300}}],
             "duration": 3000}}
        ]
    }
    sdl = compiler.compile(ai_input)

    # 检查重置交互
    reset_inter = next(i for i in sdl['interactions'] if i['id'] == 'click_reset')
    print(f"重置交互动作:")
    for action in reset_inter['actions']:
        print(f"  - {action['type']}: {action.get('params', {})}")

    # 验证重置动作包含正确的初始位置
    set_position_actions = [a for a in reset_inter['actions']
                           if a['type'] == 'setProperty' and a['params'].get('property') == 'position']

    assert len(set_position_actions) > 0, "重置交互缺少位置恢复动作"

    for action in set_position_actions:
        target = action['params']['targetId']
        value = action['params']['value']
        print(f"  恢复 {target} 位置到: {value}")

        if target == 'ball':
            assert value['x'] == 100, f"初始X坐标错误: {value['x']}"
            assert value['y'] == 200, f"初始Y坐标错误: {value['y']}"

    print("✓ 测试5通过! 重置功能完整")
    return sdl


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("SDL 编译器测试套件")
    print("=" * 60)

    try:
        test_compile_basic()
        test_validator()
        test_fixer_button_overlap()
        test_fixer_missing_buttons()
        test_reset_functionality()

        print("\n" + "=" * 60)
        print("所有测试通过! ✓")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
