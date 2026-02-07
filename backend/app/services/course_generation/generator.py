"""
生成者 AI - 负责根据监督者的指令生成单个章节
支持分步生成和 JSON 修复
"""

import json
import logging
import re
from typing import AsyncGenerator, Dict, Any, Optional, List

from app.services.claude_service import ClaudeService
from .models import (
    GenerationState, ChapterResult, ChapterStep, SimulatorSpec,
    ChapterOutline, CodeSyntaxError, SyntaxErrorType, CodeQualityScore
)

logger = logging.getLogger(__name__)

# 模拟器代码可用的API白名单
VALID_CREATE_APIS = [
    'createCircle', 'createRect', 'createText', 'createLine',
    'createCurve', 'createPolygon'
]
VALID_OPERATION_APIS = [
    'setPosition', 'setScale', 'setRotation', 'setAlpha',
    'setColor', 'setText', 'setVisible', 'remove', 'clear'
]
VALID_VAR_APIS = ['getVar', 'setVar']
VALID_CTX_PROPERTIES = ['width', 'height', 'time', 'deltaTime', 'math']

ALL_VALID_APIS = VALID_CREATE_APIS + VALID_OPERATION_APIS + VALID_VAR_APIS + VALID_CTX_PROPERTIES

# 禁止使用的API（常见错误写法）
FORBIDDEN_APIS = [
    'rect', 'circle', 'line', 'text', 'polygon', 'curve',  # 简写形式
    'drawRect', 'drawCircle', 'drawLine', 'drawText',      # draw前缀
    'fillRect', 'fillCircle', 'strokeRect',                # canvas原生API
    'arc', 'moveTo', 'lineTo', 'beginPath', 'closePath',   # canvas路径API
    'fillText', 'strokeText', 'fill', 'stroke',            # canvas绑定API
    'createPath', 'path',                                   # 不存在的path API
    'updateText', 'updateCircle', 'updateRect', 'updateLine',  # 不存在的update API
    'update', 'create',                                     # 单独的update/create
]


class JSONRepairTool:
    """
    JSON 修复工具 V2 - 全面检查并修复所有问题

    设计原则：
    1. 不依赖 in_string 状态追踪（容易出错）
    2. 使用正则分段处理每个字符串字段
    3. 一次性全面修复所有问题
    """

    @staticmethod
    def repair(json_str: str) -> str:
        """全面检查并修复 JSON 字符串"""
        original = json_str

        # 1. 基础清理
        json_str = json_str.strip().lstrip('\ufeff')

        # 2. 全局替换中文标点（在任何位置）
        json_str = JSONRepairTool._replace_chinese_punctuation(json_str)

        # 3. 分段修复每个字符串值
        json_str = JSONRepairTool._fix_string_values(json_str)

        # 4. 修复结构问题
        json_str = JSONRepairTool._fix_structural_issues(json_str)

        if json_str != original:
            logger.info("JSON repair applied")

        return json_str

    @staticmethod
    def _replace_chinese_punctuation(s: str) -> str:
        """替换中文标点为英文标点"""
        replacements = {
            '，': ',',
            '：': ':',
            '；': ';',
            '【': '[',
            '】': ']',
            '｛': '{',
            '｝': '}',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '。': '.',
        }
        for cn, en in replacements.items():
            s = s.replace(cn, en)
        return s

    @staticmethod
    def _fix_string_values(s: str) -> str:
        """
        分段修复每个字符串值
        使用正则找到 "key": "value" 模式，对 value 部分进行修复
        """
        # 找到所有 "key": " 的位置，然后找到对应的结束引号
        result = []
        i = 0

        while i < len(s):
            # 查找 ": " 或 ":" 后跟引号的模式（字符串值的开始）
            if i < len(s) - 1 and s[i] == ':':
                # 跳过冒号后的空白
                j = i + 1
                while j < len(s) and s[j] in ' \t\n\r':
                    j += 1

                if j < len(s) and s[j] == '"':
                    # 找到字符串值的开始
                    result.append(s[i:j+1])  # 包括 : 和空白和开始引号
                    i = j + 1

                    # 找到字符串值的结束
                    value_chars = []
                    while i < len(s):
                        char = s[i]

                        if char == '\\' and i + 1 < len(s):
                            # 转义序列
                            next_char = s[i + 1]
                            if next_char in '"\\nrtbfu/':
                                value_chars.append(char)
                                value_chars.append(next_char)
                                i += 2
                                continue
                            elif next_char == '\n':
                                # \后直接跟换行，转为 \\n
                                value_chars.append('\\')
                                value_chars.append('n')
                                i += 2
                                continue
                            else:
                                # 无效转义，保留反斜杠
                                value_chars.append('\\')
                                value_chars.append('\\')
                                i += 1
                                continue

                        if char == '"':
                            # 检查是否是字符串结束
                            # 结束标志：后面是 , } ] 或空白+这些
                            remaining = s[i+1:].lstrip()
                            if not remaining or remaining[0] in ',}]\n':
                                # 字符串结束
                                result.append(''.join(value_chars))
                                result.append('"')
                                i += 1
                                break
                            else:
                                # 字符串内部的引号，需要转义
                                value_chars.append('\\"')
                                i += 1
                                continue

                        if char == '\n':
                            value_chars.append('\\n')
                            i += 1
                            continue

                        if char == '\r':
                            i += 1
                            continue

                        if char == '\t':
                            value_chars.append('\\t')
                            i += 1
                            continue

                        # 控制字符
                        if ord(char) < 32:
                            i += 1
                            continue

                        value_chars.append(char)
                        i += 1

                    continue

            result.append(s[i])
            i += 1

        return ''.join(result)

    @staticmethod
    def _fix_structural_issues(s: str) -> str:
        """修复 JSON 结构问题"""
        # 1. 移除尾随逗号
        s = re.sub(r',(\s*[\]}])', r'\1', s)

        # 2. 修复未闭合的括号
        open_braces = 0
        open_brackets = 0
        in_string = False
        escape_next = False

        for char in s:
            if escape_next:
                escape_next = False
                continue
            if char == '\\':
                escape_next = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if not in_string:
                if char == '{':
                    open_braces += 1
                elif char == '}':
                    open_braces -= 1
                elif char == '[':
                    open_brackets += 1
                elif char == ']':
                    open_brackets -= 1

        if open_braces > 0:
            s = s.rstrip()
            # 如果末尾是逗号，先移除
            if s.endswith(','):
                s = s[:-1]
            s = s + '}' * open_braces

        if open_brackets > 0:
            s = s.rstrip()
            if s.endswith(','):
                s = s[:-1]
            s = s + ']' * open_brackets

        # 3. 修复未闭合的字符串
        quote_count = 0
        escape_next = False
        for char in s:
            if escape_next:
                escape_next = False
                continue
            if char == '\\':
                escape_next = True
                continue
            if char == '"':
                quote_count += 1

        if quote_count % 2 == 1:
            s = s.rstrip()
            if not s.endswith('"'):
                s = s + '"'
            # 还需要闭合可能的括号
            s = s + '}' * max(0, open_braces) + ']' * max(0, open_brackets)

        return s


class ChapterGenerator:
    """
    章节生成器


    职责：
    1. 根据监督者的指令生成单个章节
    2. 支持分步生成（先结构后代码）
    3. 内置 JSON 修复逻辑
    """

    def __init__(self):
        self.claude_service = ClaudeService()
        self.json_repair = JSONRepairTool()

    async def generate_chapter(
        self,
        prompt: str,
        system_prompt: str
    ) -> ChapterResult:
        """生成单个章节"""

        response = await self.claude_service.generate_raw_response(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=8000
        )

        return self._parse_chapter(response)

    async def generate_chapter_stream(
        self,
        prompt: str,
        system_prompt: str
    ) -> AsyncGenerator[str, None]:
        """流式生成单个章节"""

        async for chunk in self.claude_service.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=8000
        ):
            yield chunk

    async def generate_simulator_code(
        self,
        simulator_name: str,
        simulator_description: str,
        variables: List[Dict],
        chapter_context: str,
        system_prompt: str,
        additional_prompt: str = ""
    ) -> str:
        """
        单独生成模拟器代码（分步生成的第二步）

        Args:
            simulator_name: 模拟器名称
            simulator_description: 模拟器描述
            variables: 变量列表
            chapter_context: 章节上下文
            system_prompt: 系统提示词
            additional_prompt: 额外提示词（用于动态调整，如错误修复指导）

        Returns:
            生成的 JavaScript 代码
        """
        variables_desc = "\n".join([
            f"  - {v.get('name')}: {v.get('label')} (范围: {v.get('min')}-{v.get('max')}, 默认: {v.get('default')})"
            for v in variables
        ])

        prompt = f"""请为以下模拟器生成完整的 JavaScript 代码。

【模拟器信息】
名称：{simulator_name}
描述：{simulator_description}

【变量定义】
{variables_desc}

【章节上下文】
{chapter_context}

【必须遵循的代码结构 - 严格按此模板】
```javascript
// {simulator_name}
let elements = {{}};

function setup(ctx) {{
  const {{ width, height }} = ctx;
  // 在这里初始化所有视觉元素
  // 必须包含：标题、图例、背景、主要图形元素
}}

function update(ctx) {{
  const {{ width, height, math, time }} = ctx;
  // 读取变量
  const var1 = ctx.getVar('变量名');
  // 更新显示
  // 必须响应所有变量变化
}}
```

【禁止事项 - 违反将导致代码无法运行】
- 禁止使用 ctx.rect、ctx.circle、ctx.line、ctx.text（必须用 ctx.createRect、ctx.createCircle 等）
- 禁止省略 setup 或 update 函数
- 禁止使用深色：#000000、#1a1a1a、#2c3e50、#333333（背景是深色，会看不见）

【代码要求】
1. 必须有 function setup(ctx) 和 function update(ctx) 两个函数
2. 使用 ctx.getVar('变量名') 读取滑块变量值
3. 代码 80-150 行，结构清晰
4. 必须有：标题、图例、变量数值显示、主要动画元素
5. 使用 ctx.math.lerp 实现平滑过渡

【内容完整性要求】
- 每个变量都必须有对应的视觉反馈
- 核心动画逻辑必须完整（不能只画静态图）
- 标题、图例、数值显示缺一不可

【画布尺寸与边界约束 - 非常重要】
- 画布尺寸：1000 x 650 像素
- 所有元素必须完全在画布内，不能超出边界
- 动画轨迹必须限制在画布范围内，使用 ctx.math.clamp 约束坐标
- 文字元素必须留足边距，确保完整显示：
  * 左侧文字 x >= 100（留出滑块控制区域）
  * 右侧文字 x <= 950
  * 顶部文字 y >= 50
  * 底部文字 y <= 620
- 主要内容区域建议：x: 100-950, y: 60-600
- 左上角区域(0-80, 0-50)预留给系统UI，不要放置元素

【颜色规范 - 严格遵守，只能使用以下颜色】
画布背景是深色(#0f172a)，必须使用以下亮色：

推荐颜色（直接复制使用）：
- 标题文字：'#ffffff'
- 普通文字：'#e2e8f0'
- 数值显示：'#60a5fa'
- 主色调：'#6366f1'（靛蓝）
- 次色调：'#8b5cf6'（紫色）
- 强调色：'#a855f7'（亮紫）
- 成功/正确：'#22c55e'（绿色）
- 警告/注意：'#f59e0b'（橙色）
- 错误/危险：'#ef4444'（红色）
- 辅助线条：'#94a3b8'（浅灰）

绝对禁止的颜色（会导致不可见）：
#000000, #111111, #1a1a1a, #1e293b, #0f172a, #1f2937
#222222, #2c3e50, #333333, #334155, #374151, #444444
#555555, #666666（任何深色或中灰色都禁止）

【可用的绘图 API - 返回元素ID字符串】
- ctx.createCircle(x, y, radius, color) → id
- ctx.createRect(x, y, width, height, color, cornerRadius?) → id
- ctx.createText(text, x, y, {{fontSize?, fontWeight?, color?, align?}}) → id
- ctx.createLine([{{x,y}}, ...], color, lineWidth?) → id
- ctx.createCurve([{{x,y}}, ...], color, lineWidth?, smooth?) → id  // 平滑曲线
- ctx.createPolygon([{{x,y}}, ...], fillColor, strokeColor?) → id

【元素操作 API - 使用元素ID】
- ctx.setPosition(id, x, y)
- ctx.setScale(id, sx, sy)
- ctx.setRotation(id, angleDegrees)
- ctx.setAlpha(id, alpha)  // 0-1
- ctx.setColor(id, color)
- ctx.setText(id, newText)
- ctx.setVisible(id, visible)
- ctx.remove(id)
- ctx.clear()

【变量和工具】
- ctx.getVar('name') → number  // 读取滑块变量
- ctx.setVar('name', value)    // 设置变量
- ctx.width = 1000, ctx.height = 650
- ctx.time  // 累计时间(秒)
- ctx.deltaTime  // 帧间隔(秒)
- ctx.math.sin/cos/tan/abs/sqrt/pow/min/max/random/PI
- ctx.math.lerp(a, b, t)  // 线性插值
- ctx.math.clamp(value, min, max)
- ctx.math.wave(t, frequency?, amplitude?)

【重要】
- 只输出纯 JavaScript 代码
- 不要有 ```javascript 标记
- 不要有任何解释文字
- 代码必须完整可运行
- 不要使用 createArc（不存在此方法）"""

        # 添加动态调整的提示词（如果有）
        if additional_prompt:
            prompt += f"\n\n{additional_prompt}"

        # 方案C：增加 max_tokens 避免截断
        response = await self.claude_service.generate_raw_response(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=8000
        )

        # 方案D：更强的代码清理
        code = self._clean_simulator_code(response)

        # 方案B：代码结构检查与修复
        code = self._ensure_code_structure(code, variables)

        # 方案A：代码语法验证 + 方案3：自动补全截断代码
        is_valid, error = self._validate_js_syntax(code)
        if not is_valid:
            logger.warning(f"Generated code has syntax error: {error}")

            # 方案3：尝试自动补全未闭合的括号
            if "Unclosed brackets" in str(error):
                logger.info("Attempting to auto-fix unclosed brackets...")
                code = self._auto_fix_unclosed_brackets(code)
                is_valid, error = self._validate_js_syntax(code)

                if is_valid:
                    logger.info(f"Auto-fix successful! Code now has {len(code.splitlines())} lines")
                else:
                    logger.error(f"Auto-fix failed, still has error: {error}")
                    logger.error(f"Code preview: {code[:500]}...")
                    return self._get_fallback_code(simulator_name, variables)
            else:
                logger.error(f"Code preview: {code[:500]}...")
                return self._get_fallback_code(simulator_name, variables)

        # 方案E：API白名单验证 - 检查是否使用了无效的API
        api_valid, api_error, invalid_apis = self._validate_api_usage(code)
        if not api_valid:
            logger.warning(f"Generated code uses invalid API: {api_error}")
            logger.error(f"Invalid APIs found: {invalid_apis}")
            # 返回错误信息，让上层触发重试
            raise ValueError(f"invalid_api:{','.join(invalid_apis)}")

        # 方案F：颜色对比度验证 - 检查是否使用了深色（与背景融合）
        color_valid, color_errors, dark_colors = self._validate_color_contrast(code)
        if not color_valid:
            logger.warning(f"Generated code uses low contrast colors: {dark_colors}")
            for err in color_errors:
                logger.warning(f"  Line {err.line_number}: {err.message}")
            # 返回错误信息，让上层触发重试
            raise ValueError(f"low_contrast:{','.join(dark_colors)}")

        return code

    async def generate_simulator_code_progressive(
        self,
        simulator_name: str,
        simulator_description: str,
        variables: List[Dict],
        chapter_context: str,
        system_prompt: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        生产者-监督者架构生成模拟器代码（async generator）

        Yields:
            {"type": "progress", "round": N, "max_rounds": 3, "stage": str, "message": str}
            {"type": "result", "code": str, "score": int, "source": "generated"|"fallback"}
        """
        variables_desc = "\n".join([
            f"  - {v.get('name')}: {v.get('label')} (范围: {v.get('min')}-{v.get('max')}, 默认: {v.get('default')})"
            for v in variables
        ])
        variable_names = [v.get('name') for v in variables]

        max_rounds = 3
        best_code = None
        best_score = 0
        history = []

        for round_num in range(1, max_rounds + 1):
            logger.info(f"[Simulator Gen] Round {round_num}/{max_rounds} for '{simulator_name}'")

            # ========== 生产者生成代码 ==========
            if round_num == 1:
                yield {"type": "progress", "round": round_num, "max_rounds": max_rounds,
                       "stage": "generating", "message": f"正在生成模拟器代码 (第{round_num}轮)..."}
                code = await self._producer_generate(
                    simulator_name=simulator_name,
                    simulator_description=simulator_description,
                    variables_desc=variables_desc,
                    variable_names=variable_names,
                    system_prompt=system_prompt,
                    history=None
                )
            else:
                decision = await self._producer_decide_action(
                    history=history,
                    system_prompt=system_prompt
                )

                if decision == 'regenerate':
                    logger.info(f"[Producer] Decision: regenerate from scratch")
                    yield {"type": "progress", "round": round_num, "max_rounds": max_rounds,
                           "stage": "generating", "message": f"重新生成模拟器代码 (第{round_num}轮)..."}
                    code = await self._producer_generate(
                        simulator_name=simulator_name,
                        simulator_description=simulator_description,
                        variables_desc=variables_desc,
                        variable_names=variable_names,
                        system_prompt=system_prompt,
                        history=history
                    )
                else:
                    logger.info(f"[Producer] Decision: fix existing code")
                    yield {"type": "progress", "round": round_num, "max_rounds": max_rounds,
                           "stage": "fixing", "message": f"修复模拟器代码 (第{round_num}轮)..."}
                    code = await self._producer_fix_code(
                        code=best_code,
                        issues=history[-1]['issues'] if history else [],
                        simulator_name=simulator_name,
                        variable_names=variable_names,
                        system_prompt=system_prompt
                    )

            if not code:
                logger.warning(f"[Round {round_num}] Producer returned empty code")
                continue

            # ========== 监督者审核打分 ==========
            yield {"type": "progress", "round": round_num, "max_rounds": max_rounds,
                   "stage": "reviewing", "message": f"审核模拟器代码 (第{round_num}轮)..."}
            score, issues = self._supervisor_review(code, variable_names)
            logger.info(f"[Supervisor] Score: {score}/100, Issues: {len(issues)}")

            history.append({
                'round': round_num,
                'score': score,
                'issues': issues,
                'code_lines': len([l for l in code.split('\n') if l.strip()])
            })

            if score > best_score:
                best_score = score
                best_code = code

            if score >= 70:
                logger.info(f"[Simulator Gen] Passed with score {score}/100")
                yield {"type": "result", "code": self._auto_fix_colors(code), "score": score, "source": "generated"}
                return

            logger.warning(f"[Round {round_num}] Score {score}/100 < 70, issues: {issues}")

        # 所有轮次结束
        if best_code and best_score >= 40:
            logger.warning(f"[Simulator Gen] Using best code with score {best_score}/100")
            yield {"type": "result", "code": self._auto_fix_colors(best_code), "score": best_score, "source": "generated"}
        else:
            logger.error(f"[Simulator Gen] All rounds failed, using fallback")
            yield {"type": "result", "code": self._get_fallback_code(simulator_name, variables), "score": 0, "source": "fallback"}

    async def _producer_generate(
        self,
        simulator_name: str,
        simulator_description: str,
        variables_desc: str,
        variable_names: List[str],
        system_prompt: str,
        history: Optional[List[Dict]] = None
    ) -> Optional[str]:
        """生产者：生成完整模拟器代码"""

        # 构建历史问题提示
        history_hint = ""
        if history:
            history_hint = "\n【之前的问题 - 必须避免】\n"
            for h in history:
                history_hint += f"- 第{h['round']}轮 ({h['score']}分): {', '.join(h['issues'][:3])}\n"

        prompt = f"""生成模拟器代码。只输出代码，不要解释。

【模拟器】{simulator_name}
【描述】{simulator_description}
【画布尺寸】1000 x 650 像素（通过 ctx.width / ctx.height 获取，所有坐标用比例计算）
【变量】
{variables_desc}
{history_hint}
【代码结构 - 必须严格遵守】
// {simulator_name}
let elements = {{}};

function setup(ctx) {{
  const {{ width, height }} = ctx;
  // 1. 创建标题
  elements.title = ctx.createText('{simulator_name}', width/2, 40, {{fontSize: 24, fontWeight: 'bold', color: '#ffffff', align: 'center'}});
  // 2. 创建变量显示标签（每个变量一个）
  // 3. 创建主要图形元素（至少5个 ctx.create 调用）
}}

function update(ctx) {{
  const {{ width, height, math, time }} = ctx;
  // 1. 读取所有变量
{chr(10).join([f"  const {name} = ctx.getVar('{name}');" for name in variable_names])}
  // 2. 用 ctx.setText 更新每个变量的显示值
  // 3. 用变量值计算新位置/大小，用 ctx.setPosition/setScale/setColor 更新图形
}}

【API白名单 - 只能用这些，注意参数格式】
创建:
  ctx.createText(text, x, y, {{fontSize, fontWeight, color, align}}) → id
  ctx.createRect(x, y, width, height, color, cornerRadius?) → id
  ctx.createCircle(x, y, radius, color) → id
  ctx.createLine(x1, y1, x2, y2, {{color, width}}) → id  ← 4个坐标+选项对象
  ctx.createCurve(pointsArray, color, lineWidth) → id
  ctx.createPolygon(pointsArray, fillColor, strokeColor?) → id
操作:
  ctx.setText(id, text)
  ctx.setPosition(id, x, y) 或 ctx.setPosition(lineId, x1, y1, x2, y2)
  ctx.setColor(id, color)
  ctx.setScale(id, sx, sy)
  ctx.setRotation(id, angleDeg)
  ctx.setAlpha(id, alpha)
  ctx.setVisible(id, true/false)
  ctx.remove(id)
  ctx.clear()
读取: ctx.getVar('name'), ctx.time, ctx.deltaTime
数学: ctx.math.sin/cos/tan/abs/floor/ceil/round/sqrt/pow/min/max/random/PI
      ctx.math.lerp(a, b, t), ctx.math.clamp(val, min, max)
      ctx.math.smoothstep(edge0, edge1, x), ctx.math.wave(t, freq?, amp?)

【颜色白名单 - 只能用这些】
'#ffffff', '#e2e8f0', '#60a5fa', '#6366f1', '#8b5cf6', '#a855f7', '#94a3b8', '#22c55e', '#f59e0b', '#ef4444'

【完整示例 - 弹簧振子模拟器】
// 弹簧振子
let elements = {{}};

function setup(ctx) {{
  const {{ width, height }} = ctx;
  elements.title = ctx.createText('弹簧振子', width/2, 30, {{fontSize: 22, fontWeight: 'bold', color: '#ffffff', align: 'center'}});
  elements.massLabel = ctx.createText('质量: 1.0 kg', width/2, height - 40, {{fontSize: 14, color: '#94a3b8', align: 'center'}});
  elements.kLabel = ctx.createText('弹性系数: 50', width/2, height - 20, {{fontSize: 14, color: '#94a3b8', align: 'center'}});
  elements.wall = ctx.createRect(100, height/2, 10, 120, '#94a3b8');
  elements.spring = ctx.createLine(105, height/2, 400, height/2, {{color: '#60a5fa', width: 3}});
  elements.ball = ctx.createCircle(400, height/2, 30, '#6366f1');
  elements.trail = ctx.createCircle(400, height/2, 5, '#8b5cf6');
}}

function update(ctx) {{
  const {{ width, height, math, time }} = ctx;
  const mass = ctx.getVar('mass');
  const k = ctx.getVar('k');
  const omega = math.sqrt(k / math.max(mass, 0.1));
  const x = 150 * math.sin(time * omega);
  const ballX = width/2 + x;
  ctx.setPosition(elements.ball, ballX, height/2);
  ctx.setPosition(elements.spring, 105, height/2, ballX - 30, height/2);
  ctx.setPosition(elements.trail, ballX, height/2);
  ctx.setAlpha(elements.trail, 0.3);
  ctx.setScale(elements.ball, 0.8 + mass/5, 0.8 + mass/5);
  ctx.setText(elements.massLabel, `质量: ${{mass.toFixed(1)}} kg`);
  ctx.setText(elements.kLabel, `弹性系数: ${{math.round(k)}}`);
}}

【要求】
- 代码 60-100 行
- 必须有 function setup(ctx) 和 function update(ctx)
- 必须读取所有变量并有视觉反馈
- 所有坐标使用 width/height 比例计算，不要硬编码绝对坐标
- 必须以 // 或 let 开头
- 不要 ``` 标记"""

        try:
            response = await self.claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=6000
            )
            return self._clean_simulator_code(response)
        except Exception as e:
            logger.error(f"[Producer] Generate error: {e}")
            return None

    async def _producer_decide_action(
        self,
        history: List[Dict],
        system_prompt: str
    ) -> str:
        """生产者：根据历史问题决定重做还是修改"""
        if not history:
            return 'regenerate'

        last = history[-1]

        # 结构性问题 → 必须重做
        structural_keywords = [
            'function setup', 'function update',  # 缺少核心函数
            '代码严重不足', '代码太短',              # 代码量不够
            '元素太少',                             # 视觉元素不足
            '缺少动画',                             # 无动画逻辑
        ]
        for issue in last['issues']:
            if any(kw in issue for kw in structural_keywords):
                return 'regenerate'

        # 分数太低 → 重做
        if last['score'] < 50:
            return 'regenerate'

        # 连续两轮 fix 但分数没有提升 → 重做
        if len(history) >= 2:
            prev = history[-2]
            if last['score'] <= prev['score']:
                return 'regenerate'

        # 表面问题（颜色、缺少变量读取、缺少setText）→ 修改
        return 'fix'

    async def _producer_fix_code(
        self,
        code: str,
        issues: List[str],
        simulator_name: str,
        variable_names: List[str],
        system_prompt: str
    ) -> Optional[str]:
        """生产者：修复现有代码"""
        if not code:
            return None

        prompt = f"""修复以下代码的问题。只输出修复后的完整代码。

【原代码】
{code}

【需要修复的问题】
{chr(10).join([f"- {issue}" for issue in issues])}

【模拟器】{simulator_name}
【变量】{', '.join(variable_names)}

【修复要求】
1. 保持 function setup(ctx) 和 function update(ctx) 结构
2. 只用白名单API:
   创建: ctx.createText(text,x,y,opts), ctx.createRect(x,y,w,h,color), ctx.createCircle(x,y,r,color), ctx.createLine(x1,y1,x2,y2,{{color,width}}), ctx.createCurve(pts,color,w), ctx.createPolygon(pts,fill,stroke?)
   操作: ctx.setText(id,text), ctx.setPosition(id,x,y) 或 ctx.setPosition(lineId,x1,y1,x2,y2), ctx.setColor(id,color), ctx.setScale(id,sx,sy), ctx.setRotation(id,deg), ctx.setAlpha(id,alpha), ctx.setVisible(id,bool), ctx.remove(id)
   读取: ctx.getVar('name'), ctx.time, ctx.deltaTime
   数学: ctx.math.sin/cos/abs/floor/ceil/round/sqrt/pow/min/max/PI/lerp/clamp/smoothstep/wave
3. 只用亮色: '#ffffff', '#e2e8f0', '#60a5fa', '#6366f1', '#8b5cf6', '#a855f7', '#94a3b8', '#22c55e', '#f59e0b', '#ef4444'
4. 读取所有变量: {', '.join([f"ctx.getVar('{n}')" for n in variable_names])}
5. 变量读取后必须用于视觉更新（setText/setPosition/setScale等）

【严格要求】
- 直接输出完整代码
- 不要 ``` 标记
- 不要解释
- 必须以 // 或 let 开头"""

        try:
            response = await self.claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=6000
            )
            return self._clean_simulator_code(response)
        except Exception as e:
            logger.error(f"[Producer] Fix error: {e}")
            return None

    def _supervisor_review(self, code: str, variable_names: List[str]) -> tuple:
        """
        监督者：审核代码并打分

        评分标准（满分100）：
        - 可运行性: 30分（函数结构、API正确）
        - 内容完整: 30分（变量读取、视觉反馈）
        - 表达深度: 20分（代码行数、元素丰富度）
        - 渲染质量: 20分（颜色正确、动画逻辑）

        Returns:
            (score, issues)
        """
        score = 100
        issues = []

        # === 可运行性 (30分) ===
        has_setup = 'function setup' in code
        has_update = 'function update' in code
        if not has_setup:
            score -= 20
            issues.append("缺少 function setup(ctx)")
        if not has_update:
            score -= 10
            issues.append("缺少 function update(ctx)")

        api_valid, _, invalid_apis = self._validate_api_usage(code)
        if not api_valid:
            score -= 15
            issues.append(f"无效API: {', '.join(invalid_apis[:3])}")

        # 检查 API 参数格式是否正确
        import re
        # createLine 应该用 (x1, y1, x2, y2, ...) 或 ([{x,y},...], ...)
        # createCircle 应该用 (x, y, radius, color) 不是 (x, y, radius, {color:...})
        # createRect 应该用 (x, y, w, h, color) 不是 (x, y, w, h, {color:...})
        param_issues = []

        # 检查是否使用了全局 Math 而非 ctx.math / math
        global_math_calls = re.findall(r'(?<!\w)Math\.(floor|ceil|round|sin|cos|tan|abs|sqrt|pow|min|max|random|PI)\b', code)
        if global_math_calls:
            unique_calls = list(set(global_math_calls))[:3]
            param_issues.append(f"使用了全局Math而非math: Math.{', Math.'.join(unique_calls)}")

        if param_issues:
            score -= 10
            issues.extend(param_issues)

        # --- 参数数量验证 ---
        # createCircle: (x, y, radius, color) = 3-4 args
        for match in re.finditer(r'ctx\.createCircle\(([^)]+)\)', code):
            arg_count = self._count_top_level_args(match.group(1))
            if arg_count < 3 or arg_count > 4:
                score -= 10
                issues.append(f"createCircle参数数量错误: {arg_count}个(需3-4)")
                break

        # createRect: (x, y, w, h, color, cornerRadius?) = 5-6 args
        for match in re.finditer(r'ctx\.createRect\(([^)]+)\)', code):
            arg_count = self._count_top_level_args(match.group(1))
            if arg_count < 5 or arg_count > 6:
                score -= 10
                issues.append(f"createRect参数数量错误: {arg_count}个(需5-6)")
                break

        # createLine 非数组形式: (x1, y1, x2, y2, opts) = 5+ args
        for match in re.finditer(r'ctx\.createLine\(([^)]+)\)', code):
            args_str = match.group(1).strip()
            if not args_str.startswith('['):
                arg_count = self._count_top_level_args(args_str)
                if arg_count < 4:
                    score -= 10
                    issues.append(f"createLine参数不足: {arg_count}个(需4+)")
                    break

        # === 内容完整 (30分) ===
        missing_vars = []
        for var_name in variable_names:
            if f"ctx.getVar('{var_name}')" not in code and f'ctx.getVar("{var_name}")' not in code:
                missing_vars.append(var_name)
        if missing_vars:
            penalty = min(20, len(missing_vars) * 7)
            score -= penalty
            issues.append(f"未读取变量: {', '.join(missing_vars)}")

        # 检查是否有 setText 更新显示
        if 'ctx.setText' not in code:
            score -= 10
            issues.append("缺少数值显示更新(ctx.setText)")

        # === 表达深度 (20分) ===
        code_lines = len([l for l in code.split('\n') if l.strip()])
        if code_lines < 20:
            # 代码太短，不可能是完整模拟器，直接判0分
            return 0, [f"代码严重不足: {code_lines}行(需20+)"]
        elif code_lines < 30:
            score -= 20
            issues.append(f"代码太短: {code_lines}行(需30+)")
        elif code_lines < 50:
            score -= 10
            issues.append(f"代码偏短: {code_lines}行(建议50+)")

        # 检查元素丰富度
        create_count = code.count('ctx.create')
        if create_count < 5:
            score -= 10
            issues.append(f"元素太少: {create_count}个(建议5+)")

        # === 渲染质量 (20分) ===
        color_valid, _, dark_colors = self._validate_color_contrast(code)
        if not color_valid:
            score -= 10
            issues.append(f"深色: {', '.join(dark_colors[:3])}")

        # 检查动画逻辑
        has_animation = ('ctx.setPosition' in code or 'ctx.setScale' in code or
                        'ctx.setRotation' in code)
        has_math = ('math.sin' in code or 'math.cos' in code or
                   'math.lerp' in code)
        if not has_animation:
            score -= 10
            issues.append("缺少动画(setPosition/setScale)")
        if not has_math:
            score -= 5
            issues.append("缺少数学运算(sin/cos/lerp)")

        # === 变量-视觉映射检查 ===
        update_section = code.split('function update')[1] if 'function update' in code else ''
        visual_apis = ['setPosition', 'setScale', 'setRotation', 'setAlpha', 'setColor', 'setText']
        vars_used_in_visuals = 0
        for var_name in variable_names:
            if f"ctx.getVar('{var_name}')" in code or f'ctx.getVar("{var_name}")' in code:
                var_pattern = re.compile(rf'\b{re.escape(var_name)}\b')
                for api in visual_apis:
                    api_calls = re.findall(rf'ctx\.{api}\([^)]*\)', update_section)
                    for call in api_calls:
                        if var_pattern.search(call):
                            vars_used_in_visuals += 1
                            break
                    else:
                        continue
                    break

        if variable_names and vars_used_in_visuals == 0:
            score -= 15
            issues.append("变量读取后未用于视觉更新(setPosition/setText等)")
        elif len(variable_names) >= 2 and vars_used_in_visuals < len(variable_names) / 2:
            score -= 8
            issues.append(f"仅{vars_used_in_visuals}/{len(variable_names)}个变量用于视觉更新")

        # === setup/update 职责检查 ===
        setup_section = ''
        if 'function setup' in code and 'function update' in code:
            setup_start = code.index('function setup')
            update_start = code.index('function update')
            setup_section = code[setup_start:update_start]
        setup_creates = len(re.findall(r'ctx\.create\w+', setup_section))
        update_creates = len(re.findall(r'ctx\.create\w+', update_section))
        if update_creates > setup_creates and update_creates > 2:
            score -= 10
            issues.append(f"update中创建了{update_creates}个元素(应在setup中创建)")

        return max(0, score), issues

    def _count_top_level_args(self, args_str: str) -> int:
        """计算函数调用的顶层参数数量（忽略嵌套括号内的逗号）"""
        depth = 0
        count = 1
        for ch in args_str:
            if ch in '({[':
                depth += 1
            elif ch in ')}]':
                depth -= 1
            elif ch == ',' and depth == 0:
                count += 1
        return count

    async def _generate_and_validate_step(
        self,
        prompt: str,
        system_prompt: str,
        step_name: str,
        require_functions: bool = True,
        require_colors: bool = False,
        min_lines: int = 20,
        max_retries: int = 2
    ) -> Optional[str]:
        """
        生成并验证单个步骤的代码

        Args:
            min_lines: 最小代码行数要求

        Returns:
            验证通过的代码，或 None（失败）
        """
        for attempt in range(max_retries):
            try:
                response = await self.claude_service.generate_raw_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=6000
                )

                code = self._clean_simulator_code(response)

                # 验证代码行数
                code_lines = len([l for l in code.split('\n') if l.strip()])
                if code_lines < min_lines:
                    logger.warning(f"[{step_name}] Attempt {attempt+1}: Code too short ({code_lines} lines, need {min_lines}+)")
                    continue

                # 验证函数结构
                if require_functions:
                    has_setup = 'function setup' in code
                    has_update = 'function update' in code
                    if not has_setup or not has_update:
                        logger.warning(f"[{step_name}] Attempt {attempt+1}: Missing functions (setup={has_setup}, update={has_update})")
                        continue

                # 验证API
                api_valid, api_error, invalid_apis = self._validate_api_usage(code)
                if not api_valid:
                    logger.warning(f"[{step_name}] Attempt {attempt+1}: Invalid API: {invalid_apis}")
                    continue

                # 验证颜色（第2步开始检查）
                if require_colors:
                    color_valid, _, dark_colors = self._validate_color_contrast(code)
                    if not color_valid:
                        logger.warning(f"[{step_name}] Attempt {attempt+1}: Dark colors found: {dark_colors}")
                        # 尝试自动修复颜色
                        code = self._auto_fix_colors(code)
                        # 再次验证
                        color_valid, _, dark_colors = self._validate_color_contrast(code)
                        if not color_valid:
                            logger.warning(f"[{step_name}] Auto-fix failed, still has dark colors: {dark_colors}")
                            continue

                logger.info(f"[{step_name}] Attempt {attempt+1}: Validation passed")
                return code

            except Exception as e:
                logger.error(f"[{step_name}] Attempt {attempt+1}: Exception: {e}")
                continue

        return None

    def _auto_fix_colors(self, code: str) -> str:
        """
        自动替换深色为亮色
        """
        replacements = {
            '#334155': '#6366f1',
            '#1e293b': '#8b5cf6',
            '#0f172a': '#a855f7',
            '#2c3e50': '#60a5fa',
            '#333333': '#94a3b8',
            '#333': '#94a3b8',
            '#1a1a1a': '#6366f1',
            '#222222': '#8b5cf6',
            '#222': '#8b5cf6',
            '#000000': '#ffffff',
            '#000': '#ffffff',
            '#111111': '#e2e8f0',
            '#111': '#e2e8f0',
            '#1f2937': '#6366f1',
            '#374151': '#94a3b8',
            '#444444': '#94a3b8',
            '#444': '#94a3b8',
            '#555555': '#94a3b8',
            '#555': '#94a3b8',
            '#666666': '#94a3b8',
            '#666': '#94a3b8',
        }

        for dark, light in replacements.items():
            code = code.replace(dark, light)
            code = code.replace(dark.upper(), light)

        return code

    def validate_code_quality(self, code: str, variables: List[Dict], threshold: int = 70) -> tuple:
        """
        验证代码质量评分
        返回 (passed: bool, score: CodeQualityScore, report: str)
        """
        from .models import SimulatorSpec, SimulatorQualityStandards

        # 创建临时 SimulatorSpec 来计算评分
        spec = SimulatorSpec(
            name="temp",
            description="temp",
            variables=variables,
            custom_code=code
        )

        standards = SimulatorQualityStandards()
        score = spec.calculate_quality_score(standards)
        score.threshold = threshold

        report = score.format_report()
        logger.info(f"Code quality score: {score.total_score}/100 (threshold: {threshold})")

        if not score.passed:
            logger.warning(f"Code quality below threshold. Issues: {score.issues}")

        return score.passed, score, report

    def _clean_simulator_code(self, response: str) -> str:
        """
        方案D：更强的代码清理
        移除AI可能添加的解释文字、注释等非代码内容
        """
        code = response.strip()

        # 1. 提取代码块 - 优先找包含 function setup 的代码块
        import re
        code_blocks = re.findall(r'```(?:javascript|js)?\s*\n(.*?)```', code, re.DOTALL)

        if code_blocks:
            # 优先选择包含 function setup 的代码块
            best_block = None
            for block in code_blocks:
                if 'function setup' in block and 'function update' in block:
                    best_block = block
                    break
            if not best_block:
                # 选择最长的代码块
                best_block = max(code_blocks, key=len)
            code = best_block
        else:
            # 没有代码块标记，尝试旧方法
            if '```javascript' in code:
                parts = code.split('```javascript')
                if len(parts) > 1:
                    code = parts[1].split('```')[0]
            elif '```js' in code:
                parts = code.split('```js')
                if len(parts) > 1:
                    code = parts[1].split('```')[0]
            elif '```' in code:
                parts = code.split('```')
                if len(parts) > 1:
                    code = parts[1].split('```')[0]

        # 2. 移除开头的解释文字（找到第一个有效代码行）
        lines = code.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            # 有效代码行的特征
            if (stripped.startswith('let ') or
                stripped.startswith('const ') or
                stripped.startswith('var ') or
                stripped.startswith('function ') or
                stripped.startswith('//') or
                stripped.startswith('/*') or
                stripped == ''):
                start_idx = i
                break

        # 3. 移除结尾的解释文字（找到最后一个 } 或有效代码行）
        end_idx = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            stripped = lines[i].strip()
            if stripped.endswith('}') or stripped.endswith(';') or stripped.startswith('//') or stripped == '':
                end_idx = i + 1
                break

        code = '\n'.join(lines[start_idx:end_idx])
        code = code.strip()

        # 4. 最终检查：如果清理后没有代码，尝试直接从原始响应中提取
        if not code or len([l for l in code.split('\n') if l.strip()]) < 10:
            # 尝试从原始响应中找 function setup 到最后一个 } 的范围
            raw_lines = response.split('\n')
            setup_start = -1
            last_brace = -1
            for i, line in enumerate(raw_lines):
                if 'function setup' in line and setup_start == -1:
                    # 往前找 let elements 或注释
                    setup_start = i
                    for j in range(i - 1, max(i - 10, -1), -1):
                        s = raw_lines[j].strip()
                        if s.startswith('let ') or s.startswith('const ') or s.startswith('//') or s.startswith('/*'):
                            setup_start = j
                            break
                # 匹配以 } 结尾的行（不只是独立的 }）
                if line.strip().endswith('}'):
                    last_brace = i

            if setup_start >= 0 and last_brace > setup_start and (last_brace - setup_start) >= 10:
                code = '\n'.join(raw_lines[setup_start:last_brace + 1])
                code = code.strip()
                logger.info(f"[_clean_simulator_code] Extracted code from raw response: {len(code.splitlines())} lines")
            else:
                logger.warning(f"[_clean_simulator_code] Failed to extract code (setup_start={setup_start}, last_brace={last_brace})")

        return code

    def _ensure_code_structure(self, code: str, variables: List[Dict]) -> str:
        """
        方案B：代码结构检查
        确保代码包含 setup 和 update 函数，缺少则抛出错误触发重试
        """
        has_setup = 'function setup' in code or 'setup(' in code
        has_update = 'function update' in code or 'update(' in code

        if has_setup and has_update:
            return code

        logger.warning(f"Code structure incomplete: has_setup={has_setup}, has_update={has_update}")

        # 缺少必要函数，抛出错误触发重试
        missing = []
        if not has_setup:
            missing.append('setup')
        if not has_update:
            missing.append('update')

        raise ValueError(f"missing_function:{','.join(missing)}")

    def _get_line_context(self, lines: List[str], line_num: int, context_lines: int = 2) -> tuple:
        """获取指定行的上下文"""
        start = max(0, line_num - context_lines)
        end = min(len(lines), line_num + context_lines + 1)

        before = '\n'.join(lines[start:line_num]) if line_num > 0 else ""
        current = lines[line_num] if line_num < len(lines) else ""
        after = '\n'.join(lines[line_num + 1:end]) if line_num + 1 < len(lines) else ""

        return before, current, after

    def _validate_js_syntax_detailed(self, code: str) -> tuple:
        """
        代码语法验证（详细版）
        返回 (is_valid, error: CodeSyntaxError | None)
        """
        lines = code.split('\n')

        # 1. 检查必要函数
        has_setup = 'function setup' in code or 'setup(' in code
        has_update = 'function update' in code or 'update(' in code

        if not has_setup:
            # 尝试定位应该添加 setup 的位置
            for i, line in enumerate(lines):
                if 'function' in line:
                    before, current, after = self._get_line_context(lines, i)
                    return False, CodeSyntaxError(
                        error_type=SyntaxErrorType.MISSING_FUNCTION,
                        message="缺少 setup(ctx) 函数",
                        line_number=i + 1,
                        context_before=before,
                        error_line=current,
                        context_after=after,
                        suggestion="在代码开头添加: function setup(ctx) { ... }"
                    )
            return False, CodeSyntaxError(
                error_type=SyntaxErrorType.MISSING_FUNCTION,
                message="缺少 setup(ctx) 函数",
                suggestion="代码必须包含 function setup(ctx) { ... } 函数"
            )

        if not has_update:
            for i, line in enumerate(lines):
                if 'function setup' in line:
                    before, current, after = self._get_line_context(lines, i)
                    return False, CodeSyntaxError(
                        error_type=SyntaxErrorType.MISSING_FUNCTION,
                        message="缺少 update(ctx) 函数",
                        line_number=i + 1,
                        context_before=before,
                        error_line=current,
                        context_after=after,
                        suggestion="在 setup 函数后添加: function update(ctx) { ... }"
                    )

        # 2. 检查括号匹配
        brackets = {'(': ')', '{': '}', '[': ']'}
        reverse_brackets = {v: k for k, v in brackets.items()}
        stack = []  # [(bracket_type, line_num, col)]
        in_string = False
        string_char = None
        escape_next = False

        for line_num, line in enumerate(lines):
            for col, char in enumerate(line):
                if escape_next:
                    escape_next = False
                    continue

                if char == '\\':
                    escape_next = True
                    continue

                if char in '"\'`':
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                    continue

                if in_string:
                    continue

                if char in brackets:
                    stack.append((char, line_num, col))
                elif char in brackets.values():
                    if not stack:
                        before, current, after = self._get_line_context(lines, line_num)
                        return False, CodeSyntaxError(
                            error_type=SyntaxErrorType.MISMATCHED_BRACKET,
                            message=f"多余的闭合括号 '{char}'，没有对应的开括号 '{reverse_brackets[char]}'",
                            line_number=line_num + 1,
                            column=col + 1,
                            context_before=before,
                            error_line=current,
                            context_after=after,
                            suggestion=f"删除多余的 '{char}' 或在前面添加对应的 '{reverse_brackets[char]}'"
                        )
                    expected = brackets[stack[-1][0]]
                    if char != expected:
                        open_bracket, open_line, open_col = stack[-1]
                        before, current, after = self._get_line_context(lines, line_num)
                        return False, CodeSyntaxError(
                            error_type=SyntaxErrorType.MISMATCHED_BRACKET,
                            message=f"括号不匹配: 第 {open_line + 1} 行的 '{open_bracket}' 期望 '{expected}'，但在第 {line_num + 1} 行遇到 '{char}'",
                            line_number=line_num + 1,
                            column=col + 1,
                            context_before=before,
                            error_line=current,
                            context_after=after,
                            suggestion=f"将 '{char}' 改为 '{expected}'，或检查第 {open_line + 1} 行的括号"
                        )
                    stack.pop()

        # 检查未闭合的括号
        if stack:
            open_bracket, open_line, open_col = stack[-1]
            before, current, after = self._get_line_context(lines, open_line)
            expected_close = brackets[open_bracket]
            return False, CodeSyntaxError(
                error_type=SyntaxErrorType.UNCLOSED_BRACKET,
                message=f"未闭合的括号 '{open_bracket}'，缺少对应的 '{expected_close}'",
                line_number=open_line + 1,
                column=open_col + 1,
                context_before=before,
                error_line=current,
                context_after=after,
                suggestion=f"在代码末尾或适当位置添加 '{expected_close}' 来闭合括号"
            )

        # 3. 检查 return 是否在函数外
        brace_depth = 0
        for line_num, line in enumerate(lines):
            stripped = line.strip()

            # 跳过注释
            if stripped.startswith('//') or stripped.startswith('/*'):
                continue

            # 计算括号深度
            for char in stripped:
                if char == '{':
                    brace_depth += 1
                elif char == '}':
                    brace_depth -= 1

            # 检查 return 是否在函数内
            if 'return ' in stripped and brace_depth <= 0:
                before, current, after = self._get_line_context(lines, line_num)
                return False, CodeSyntaxError(
                    error_type=SyntaxErrorType.RETURN_OUTSIDE_FUNCTION,
                    message="'return' 语句出现在函数外部",
                    line_number=line_num + 1,
                    context_before=before,
                    error_line=current,
                    context_after=after,
                    suggestion="将 return 语句移到函数内部，或删除多余的 return"
                )

        return True, None

    def _validate_js_syntax(self, code: str) -> tuple:
        """
        代码语法验证（兼容旧接口）
        返回 (is_valid, error_message)
        """
        is_valid, error = self._validate_js_syntax_detailed(code)
        if error:
            return False, error.format_report()
        return True, None

    def _validate_api_usage_detailed(self, code: str) -> tuple:
        """
        验证代码是否只使用了白名单内的API（详细版）
        返回 (is_valid, errors: List[CodeSyntaxError], invalid_apis: List[str])
        """
        lines = code.split('\n')
        errors = []
        invalid_apis_found = []

        # 匹配 ctx.xxx 模式
        api_pattern = r'ctx\.(\w+)'

        for line_num, line in enumerate(lines):
            matches = re.finditer(api_pattern, line)
            for match in matches:
                api = match.group(1)
                if api not in ALL_VALID_APIS and api != 'math':
                    if api not in invalid_apis_found:
                        invalid_apis_found.append(api)
                        before, current, after = self._get_line_context(lines, line_num)
                        errors.append(CodeSyntaxError(
                            error_type=SyntaxErrorType.INVALID_API,
                            message=f"无效的 API 调用: ctx.{api}",
                            line_number=line_num + 1,
                            column=match.start() + 1,
                            context_before=before,
                            error_line=current,
                            context_after=after,
                            suggestion=f"可用的 API: {', '.join(VALID_CREATE_APIS[:3])}... 请使用白名单内的 API"
                        ))

        if errors:
            return False, errors, invalid_apis_found
        return True, [], []

    def _validate_color_contrast(self, code: str) -> tuple:
        """
        验证代码中的颜色是否有足够对比度（深色背景需要亮色元素）
        返回 (is_valid, errors: List[CodeSyntaxError], dark_colors: List[str])
        """
        lines = code.split('\n')
        errors = []
        dark_colors_found = []

        # 深色背景色列表（与背景 #1e293b 相近的颜色）
        dark_colors = [
            '#000', '#000000',           # 黑色
            '#111', '#111111',
            '#1e293b',                   # 背景色
            '#0f172a',                   # 更深的背景
            '#1a1a1a', '#1f1f1f',
            '#222', '#222222',
            '#2d2d2d', '#333', '#333333',
            '#334155',                   # slate-700
            '#374151',                   # gray-700
            '#1f2937',                   # gray-800
            '#0d0d0d', '#0a0a0a',
            '#2c3e50',                   # 深蓝灰
            '#555', '#555555',           # 中灰（对比度不足）
            '#666', '#666666',           # 中灰
            '#444', '#444444',
        ]

        # 匹配颜色值的模式
        color_patterns = [
            r"color:\s*['\"]?(#[0-9a-fA-F]{3,6})['\"]?",  # color: '#xxx'
            r"createCircle\([^)]*,\s*['\"]?(#[0-9a-fA-F]{3,6})['\"]?\s*\)",  # createCircle(..., color)
            r"createRect\([^)]*,\s*['\"]?(#[0-9a-fA-F]{3,6})['\"]?",  # createRect(..., color, ...)
            r"createLine\([^)]*,\s*['\"]?(#[0-9a-fA-F]{3,6})['\"]?",  # createLine(..., color, ...)
            r"createCurve\([^)]*,\s*['\"]?(#[0-9a-fA-F]{3,6})['\"]?",  # createCurve(..., color, ...)
            r"setColor\([^)]*,\s*['\"]?(#[0-9a-fA-F]{3,6})['\"]?\s*\)",  # setColor(id, color)
        ]

        for line_num, line in enumerate(lines):
            for pattern in color_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    color = match.group(1).lower()
                    # 标准化3位颜色为6位
                    if len(color) == 4:  # #rgb
                        color = f"#{color[1]*2}{color[2]*2}{color[3]*2}"

                    if color in dark_colors:
                        if color not in dark_colors_found:
                            dark_colors_found.append(color)
                            before, current, after = self._get_line_context(lines, line_num)
                            errors.append(CodeSyntaxError(
                                error_type=SyntaxErrorType.LOW_CONTRAST,
                                message=f"颜色 {color} 与深色背景对比度不足，元素将不可见",
                                line_number=line_num + 1,
                                column=match.start() + 1,
                                context_before=before,
                                error_line=current,
                                context_after=after,
                                suggestion="使用亮色: #ffffff(白), #e2e8f0(浅灰), #60a5fa(蓝), #22c55e(绿)"
                            ))

        if errors:
            return False, errors, dark_colors_found
        return True, [], []

    def _validate_api_usage(self, code: str) -> tuple:
        """
        验证代码是否只使用了白名单内的API
        返回 (is_valid, error_message, invalid_apis)
        """
        # 匹配 ctx.xxx( 或 ctx.xxx 模式
        api_pattern = r'ctx\.(\w+)'
        api_calls = re.findall(api_pattern, code)

        # 过滤出无效的API调用
        invalid_apis = []
        forbidden_found = []

        for api in api_calls:
            # 先检查是否是禁用的API
            if api in FORBIDDEN_APIS:
                if api not in forbidden_found:
                    forbidden_found.append(api)
            elif api not in ALL_VALID_APIS:
                # 检查是否是 ctx.math.xxx 的情况
                if api != 'math':
                    if api not in invalid_apis:
                        invalid_apis.append(api)

        # 禁用API优先报错
        if forbidden_found:
            return False, f"Forbidden API: {', '.join(forbidden_found)}", forbidden_found

        if invalid_apis:
            return False, f"Invalid API: {', '.join(invalid_apis)}", invalid_apis

        return True, None, []

    def _auto_fix_unclosed_brackets(self, code: str) -> str:
        """
        方案3：自动补全未闭合的括号
        当代码被截断时，尝试补全缺失的闭合括号
        """
        # 分析括号状态
        brackets = {'(': ')', '{': '}', '[': ']'}
        stack = []
        in_string = False
        string_char = None
        escape_next = False

        for char in code:
            if escape_next:
                escape_next = False
                continue

            if char == '\\':
                escape_next = True
                continue

            if char in '"\'`':
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                continue

            if in_string:
                continue

            if char in brackets:
                stack.append(brackets[char])
            elif char in brackets.values():
                if stack and stack[-1] == char:
                    stack.pop()

        if not stack:
            return code

        # 补全缺失的闭合括号
        # 先清理代码末尾可能的不完整行
        lines = code.rstrip().split('\n')

        # 检查最后一行是否完整
        last_line = lines[-1].strip() if lines else ''
        if last_line and not last_line.endswith((';', '{', '}', ',', ')', ']')):
            # 最后一行不完整，可能是被截断的
            # 尝试找到最后一个完整的语句
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i].strip()
                if line.endswith((';', '{', '}')) or line == '':
                    lines = lines[:i+1]
                    break

        # 重新组合代码
        code = '\n'.join(lines)

        # 重新计算需要补全的括号
        stack = []
        in_string = False
        string_char = None
        escape_next = False

        for char in code:
            if escape_next:
                escape_next = False
                continue
            if char == '\\':
                escape_next = True
                continue
            if char in '"\'`':
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                continue
            if in_string:
                continue
            if char in brackets:
                stack.append(brackets[char])
            elif char in brackets.values():
                if stack and stack[-1] == char:
                    stack.pop()

        # 补全括号
        if stack:
            closing = ''.join(reversed(stack))
            code = code.rstrip()
            # 确保最后有换行
            if not code.endswith('\n'):
                code += '\n'
            code += closing

            logger.info(f"Auto-fixed by adding: {closing}")

        return code

    def _get_fallback_code(self, name: str, variables: List[Dict]) -> str:
        """生成教育性 fallback 模拟器代码 - 变量仪表盘"""
        var_reads = "\n".join([
            f"  const {v.get('name', f'var{i}')} = ctx.getVar('{v.get('name', f'var{i}')}');"
            for i, v in enumerate(variables)
        ])

        gauge_setup_lines = []
        gauge_update_lines = []
        for i, v in enumerate(variables):
            vname = v.get('name', f'var{i}')
            vlabel = v.get('label', vname)
            vmin = v.get('min', 0)
            vmax = v.get('max', 100)
            vdefault = v.get('default', 50)
            vunit = v.get('unit', '')
            y_offset = i * 80

            gauge_setup_lines.append(
                f"  elements.label{i} = ctx.createText('{vlabel}', 80, 140 + {y_offset}, {{fontSize: 14, color: '#94a3b8', align: 'left'}});\n"
                f"  elements.val{i} = ctx.createText('{vdefault}{vunit}', width - 80, 140 + {y_offset}, {{fontSize: 14, color: '#60a5fa', align: 'right'}});\n"
                f"  elements.barBg{i} = ctx.createRect(width/2, 165 + {y_offset}, width - 160, 16, '#1e293b', 8);\n"
                f"  elements.bar{i} = ctx.createRect(width/2, 165 + {y_offset}, (width-180)/2, 12, '#6366f1', 6);"
            )

            gauge_update_lines.append(
                f"  const norm{i} = ({vname} - {vmin}) / ({vmax - vmin if vmax != vmin else 1});\n"
                f"  const barW{i} = math.clamp(norm{i}, 0, 1) * (width - 180);\n"
                f"  ctx.setText(elements.val{i}, {vname}.toFixed(1) + '{vunit}');\n"
                f"  ctx.setScale(elements.bar{i}, barW{i} / ((width-180)/2), 1);\n"
                f"  ctx.setPosition(elements.bar{i}, 90 + barW{i}/2, 165 + {y_offset});"
            )

        gauge_setup = "\n".join(gauge_setup_lines)
        gauge_update = "\n".join(gauge_update_lines)

        return f'''// {name} - 变量仪表盘
let elements = {{}};

function setup(ctx) {{
  const {{ width, height }} = ctx;
  elements.title = ctx.createText('{name}', width/2, 35, {{
    fontSize: 22, fontWeight: 'bold', color: '#ffffff', align: 'center'
  }});
  elements.desc = ctx.createText('拖动下方滑块观察变量变化', width/2, 70, {{
    fontSize: 14, color: '#94a3b8', align: 'center'
  }});
  ctx.createLine(80, 100, width - 80, 100, {{color: '#334155', width: 1}});
{gauge_setup}
}}

function update(ctx) {{
  const {{ width, height, math, time }} = ctx;
{var_reads}
{gauge_update}
}}'''

    def _extract_json(self, response: str) -> str:
        """从响应中提取 JSON 字符串"""
        json_str = response

        # 尝试提取 ```json 块
        if '```json' in response:
            parts = response.split('```json')
            if len(parts) > 1:
                json_str = parts[1].split('```')[0]
        elif '```' in response:
            parts = response.split('```')
            if len(parts) > 1:
                json_str = parts[1].split('```')[0]
        elif '{' in response:
            # 找到最外层的 {}
            start = response.index('{')
            # 使用括号匹配找到正确的结束位置
            depth = 0
            end = start
            in_string = False
            escape_next = False

            for i in range(start, len(response)):
                char = response[i]

                if escape_next:
                    escape_next = False
                    continue

                if char == '\\':
                    escape_next = True
                    continue

                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue

                if not in_string:
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break

            json_str = response[start:end]

        return json_str.strip()

    def _parse_chapter(self, response: str) -> ChapterResult:
        """解析章节JSON，带修复逻辑（不使用部分提取）"""
        try:
            # 1. 提取 JSON
            json_str = self._extract_json(response)

            # 2. 尝试直接解析
            try:
                data = json.loads(json_str)
                logger.info("JSON parsed successfully on first attempt")
            except json.JSONDecodeError as e:
                logger.warning(f"Initial JSON parse failed: {e}, attempting repair...")

                # 3. 尝试修复后解析
                repaired = self.json_repair.repair(json_str)
                try:
                    data = json.loads(repaired)
                    logger.info("JSON repair successful")
                except json.JSONDecodeError as e2:
                    # 修复失败，直接抛出异常触发重试
                    logger.error(f"JSON repair failed: {e2}")
                    logger.error(f"Original error position: {e}")
                    # 记录问题区域用于调试
                    error_pos = e.pos if hasattr(e, 'pos') else 0
                    context_start = max(0, error_pos - 100)
                    context_end = min(len(json_str), error_pos + 100)
                    logger.error(f"Error context: ...{json_str[context_start:context_end]}...")
                    raise ValueError(f"JSON 解析失败，需要重新生成: {e2}")

            # 解析步骤
            script = []
            for step_data in data.get('script', []):
                step = ChapterStep(
                    step_id=step_data.get('step_id', f'step_{len(script)+1}'),
                    type=step_data.get('type', 'text_content'),
                    title=step_data.get('title', ''),
                    content=step_data.get('content'),
                    diagram_spec=step_data.get('diagram_spec'),
                    assessment_spec=step_data.get('assessment_spec')
                )

                # 解析模拟器
                if step.type == 'simulator' and 'simulator_spec' in step_data:
                    sim_data = step_data['simulator_spec']
                    step.simulator_spec = SimulatorSpec(
                        name=sim_data.get('name', ''),
                        description=sim_data.get('description', ''),
                        mode=sim_data.get('mode', 'custom'),
                        variables=sim_data.get('variables', []),
                        custom_code=sim_data.get('custom_code', '')
                    )

                script.append(step)

            return ChapterResult(
                lesson_id=data.get('lesson_id', 'lesson_1'),
                title=data.get('title', ''),
                order=data.get('order', 0),
                total_steps=len(script),
                rationale=data.get('rationale', ''),
                script=script,
                estimated_minutes=data.get('estimated_minutes', 30),
                learning_objectives=data.get('learning_objectives', []),
                complexity_level=data.get('complexity_level', 'standard')
            )

        except Exception as e:
            logger.error(f"Failed to parse chapter: {e}")
            logger.debug(f"Response preview: {response[:500]}...")
            raise ValueError(f"章节解析失败: {e}")

    def parse_streaming_response(self, full_response: str) -> ChapterResult:
        """解析流式响应的完整内容"""
        return self._parse_chapter(full_response)

    async def generate_single_step(
        self,
        step_type: str,
        step_context: Dict[str, Any],
        issues: List[str],
        suggestions: List[str],
        system_prompt: str
    ) -> ChapterStep:
        """
        单独重新生成某个步骤（单步重做功能）

        Args:
            step_type: 步骤类型 (text_content, simulator, assessment, illustrated_content)
            step_context: 步骤上下文信息
            issues: 审核发现的问题
            suggestions: 改进建议
            system_prompt: 系统提示词

        Returns:
            重新生成的步骤
        """
        # 构建重做提示词
        prompt = self._build_step_regeneration_prompt(
            step_type=step_type,
            step_context=step_context,
            issues=issues,
            suggestions=suggestions
        )

        response = await self.claude_service.generate_raw_response(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4000
        )

        return self._parse_single_step(response, step_type)

    def _build_step_regeneration_prompt(
        self,
        step_type: str,
        step_context: Dict[str, Any],
        issues: List[str],
        suggestions: List[str]
    ) -> str:
        """构建单步重做的提示词"""
        issues_text = "\n".join([f"  - {issue}" for issue in issues]) if issues else "  无"
        suggestions_text = "\n".join([f"  - {s}" for s in suggestions]) if suggestions else "  无"

        prompt = f"""请重新生成以下步骤，修复审核发现的问题。

【步骤类型】{step_type}

【原步骤信息】
标题：{step_context.get('title', '')}
内容摘要：{step_context.get('content_summary', '')}

【章节上下文】
课程：{step_context.get('course_title', '')}
章节：{step_context.get('chapter_title', '')}
学习目标：{step_context.get('learning_objectives', '')}

【审核发现的问题】
{issues_text}

【改进建议】
{suggestions_text}

"""

        # 根据步骤类型添加特定要求
        if step_type == 'simulator':
            prompt += """
【模拟器重做要求】
1. 修复所有审核指出的问题
2. 确保代码完整可运行（至少120行）
3. 必须有 setup(ctx) 和 update(ctx) 函数
4. 必须有丰富的视觉元素：标题、图例、状态面板
5. 必须有动画效果
6. 使用组合图形创建复杂对象

【输出格式】
```json
{
  "step_id": "step_X",
  "type": "simulator",
  "title": "模拟器标题",
  "content": "模拟器说明文字",
  "simulator_spec": {
    "mode": "custom",
    "name": "模拟器名称",
    "description": "详细描述",
    "variables": [
      {"name": "var1", "label": "变量1", "min": 0, "max": 100, "default": 50, "step": 1}
    ],
    "custom_code": ""
  }
}
```
注意：custom_code 留空，系统会自动生成代码。
"""
        elif step_type == 'text_content':
            prompt += """
【文本内容重做要求】
1. 修复所有审核指出的问题
2. 确保内容深度足够（至少300字）
3. 逻辑清晰，层次分明
4. 使用专业术语但要有解释

【输出格式】
```json
{
  "step_id": "step_X",
  "type": "text_content",
  "title": "内容标题",
  "content": "详细内容..."
}
```
"""
        elif step_type == 'assessment':
            prompt += """
【测评重做要求】
1. 修复所有审核指出的问题
2. 确保题目与学习目标对应
3. 选项设计合理，干扰项有意义
4. 解析详细清晰

【输出格式】
```json
{
  "step_id": "step_X",
  "type": "assessment",
  "title": "测评标题",
  "content": "测评说明",
  "assessment_spec": {
    "questions": [
      {
        "question_id": "q1",
        "type": "single_choice",
        "question": "问题内容",
        "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
        "correct_answer": "A",
        "explanation": "详细解析"
      }
    ]
  }
}
```
"""
        elif step_type == 'illustrated_content':
            prompt += """
【图文内容重做要求】
1. 修复所有审核指出的问题
2. 确保图文配合紧密
3. 图片描述清晰准确

【输出格式】
```json
{
  "step_id": "step_X",
  "type": "illustrated_content",
  "title": "图文标题",
  "content": "图文说明",
  "diagram_spec": {
    "type": "static_diagram",
    "description": "图片内容描述",
    "diagram_id": "diagram_X"
  }
}
```
"""

        prompt += "\n只输出JSON，不要有其他解释。"
        return prompt

    def _parse_single_step(self, response: str, step_type: str) -> ChapterStep:
        """解析单个步骤的响应"""
        try:
            json_str = self._extract_json(response)

            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Single step JSON parse failed: {e}, attempting repair...")
                repaired = self.json_repair.repair(json_str)
                data = json.loads(repaired)

            step = ChapterStep(
                step_id=data.get('step_id', 'step_regenerated'),
                type=data.get('type', step_type),
                title=data.get('title', ''),
                content=data.get('content'),
                diagram_spec=data.get('diagram_spec'),
                assessment_spec=data.get('assessment_spec')
            )

            # 解析模拟器
            if step.type == 'simulator' and 'simulator_spec' in data:
                sim_data = data['simulator_spec']
                step.simulator_spec = SimulatorSpec(
                    name=sim_data.get('name', ''),
                    description=sim_data.get('description', ''),
                    mode=sim_data.get('mode', 'custom'),
                    variables=sim_data.get('variables', []),
                    custom_code=sim_data.get('custom_code', '')
                )

            return step

        except Exception as e:
            logger.error(f"Failed to parse single step: {e}")
            raise ValueError(f"单步解析失败: {e}")


class GeneratorPromptBuilder:
    """生成器提示词构建器"""

    @staticmethod
    def build_system_prompt(processor_id: str) -> str:
        """构建系统提示词"""
        base_prompt = """你是一位专业的课程内容生成专家。你的任务是根据监督者的指令生成高质量的章节内容。

【你的职责】
1. 严格按照指令生成章节内容
2. 确保模拟器代码完整、可运行
3. 确保内容深度足够、逻辑清晰
4. 不要生成与已有内容重复的模拟器

【模拟器代码规范】
- 必须有 setup(ctx) 和 update(ctx) 函数
- 必须使用 ctx.getVar() 读取变量
- 必须有动画效果和文字标签
- 代码至少25行，逻辑完整

【输出要求】
- 直接输出JSON格式
- 不要有多余的解释
- 确保JSON格式正确
"""

        # 根据处理器类型添加特定指令
        processor_prompts = {
            'academic': """
【学术风格要求】
- 使用专业术语，但要有解释
- 引用相关理论和研究
- 逻辑严谨，论证充分
""",
            'practical': """
【实践风格要求】
- 注重实际应用
- 多用案例和示例
- 强调动手操作
""",
            'sports': """
【运动科学风格要求】
- 结合运动生物力学原理
- 使用运动场景的模拟器
- 强调技术动作分析
"""
        }

        return base_prompt + processor_prompts.get(processor_id, '')
