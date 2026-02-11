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
    ChapterOutline
)

logger = logging.getLogger(__name__)


class JSONRepairTool:
    """JSON 修复工具 - 处理常见的 JSON 格式错误"""

    @staticmethod
    def repair(json_str: str) -> str:
        """尝试修复常见的 JSON 错误"""
        original = json_str

        # 1. 移除 BOM 和不可见字符
        json_str = json_str.strip().lstrip('\ufeff')

        # 2. 修复未转义的换行符（在字符串内部）
        json_str = JSONRepairTool._fix_unescaped_newlines(json_str)

        # 3. 修复未转义的引号
        json_str = JSONRepairTool._fix_unescaped_quotes(json_str)

        # 4. 修复未转义的反斜杠
        json_str = JSONRepairTool._fix_unescaped_backslashes(json_str)

        # 5. 修复尾随逗号
        json_str = JSONRepairTool._fix_trailing_commas(json_str)

        # 6. 修复缺失的闭合括号
        json_str = JSONRepairTool._fix_unclosed_brackets(json_str)

        # 7. 修复未闭合的字符串
        json_str = JSONRepairTool._fix_unclosed_strings(json_str)

        if json_str != original:
            logger.info("JSON repair applied")

        return json_str

    @staticmethod
    def _fix_unescaped_newlines(s: str) -> str:
        """修复字符串中未转义的换行符"""
        result = []
        in_string = False
        escape_next = False
        i = 0

        while i < len(s):
            char = s[i]

            if escape_next:
                result.append(char)
                escape_next = False
                i += 1
                continue

            if char == '\\':
                escape_next = True
                result.append(char)
                i += 1
                continue

            if char == '"':
                in_string = not in_string
                result.append(char)
                i += 1
                continue

            if in_string and char == '\n':
                result.append('\\n')
                i += 1
                continue

            if in_string and char == '\r':
                i += 1
                continue

            if in_string and char == '\t':
                result.append('\\t')
                i += 1
                continue

            result.append(char)
            i += 1

        return ''.join(result)

    @staticmethod
    def _fix_unescaped_quotes(s: str) -> str:
        """修复 custom_code 中未转义的引号"""
        # 查找 custom_code 字段并修复其中的引号
        pattern = r'"custom_code"\s*:\s*"'
        match = re.search(pattern, s)
        if not match:
            return s

        start = match.end()
        # 找到 custom_code 值的结束位置
        depth = 0
        in_string = True
        escape_next = False
        end = start

        for i in range(start, len(s)):
            char = s[i]

            if escape_next:
                escape_next = False
                continue

            if char == '\\':
                escape_next = True
                continue

            if char == '"':
                # 检查这是否是 custom_code 字符串的结束
                # 结束标志：后面跟着 , 或 } 或空白+,/}
                remaining = s[i+1:i+20].lstrip()
                if remaining and remaining[0] in ',}':
                    end = i
                    break

        return s

    @staticmethod
    def _fix_unescaped_backslashes(s: str) -> str:
        """修复未转义的反斜杠"""
        # 在 JSON 字符串中，单独的反斜杠需要转义
        # 但要避免双重转义
        result = []
        i = 0
        in_string = False

        while i < len(s):
            char = s[i]

            if char == '"' and (i == 0 or s[i-1] != '\\'):
                in_string = not in_string
                result.append(char)
                i += 1
                continue

            if in_string and char == '\\':
                # 检查下一个字符
                if i + 1 < len(s):
                    next_char = s[i + 1]
                    # 有效的转义序列
                    if next_char in '"\\nrtbfu/':
                        result.append(char)
                        i += 1
                        continue
                    else:
                        # 无效的转义，添加额外的反斜杠
                        result.append('\\\\')
                        i += 1
                        continue

            result.append(char)
            i += 1

        return ''.join(result)

    @staticmethod
    def _fix_trailing_commas(s: str) -> str:
        """移除尾随逗号"""
        # 移除 ] 或 } 前的逗号
        s = re.sub(r',(\s*[\]}])', r'\1', s)
        return s

    @staticmethod
    def _fix_unclosed_brackets(s: str) -> str:
        """修复未闭合的括号"""
        open_braces = s.count('{') - s.count('}')
        open_brackets = s.count('[') - s.count(']')

        if open_braces > 0:
            s = s + '}' * open_braces
        if open_brackets > 0:
            s = s + ']' * open_brackets

        return s

    @staticmethod
    def _fix_unclosed_strings(s: str) -> str:
        """修复未闭合的字符串"""
        # 简单检查：如果引号数量为奇数，在末尾添加引号
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
            # 找到最后一个未闭合的字符串位置
            s = s.rstrip()
            if not s.endswith('"'):
                s = s + '"'

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
        system_prompt: str
    ) -> str:
        """
        单独生成模拟器代码（分步生成的第二步）

        Args:
            simulator_name: 模拟器名称
            simulator_description: 模拟器描述
            variables: 变量列表
            chapter_context: 章节上下文
            system_prompt: 系统提示词

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

【代码要求】
1. 必须有 setup(ctx) 函数初始化所有视觉元素
2. 必须有 update(ctx) 函数响应变量变化
3. 使用 ctx.getVar('变量名') 读取变量值
4. 代码至少 120 行，包含丰富的视觉元素
5. 必须有：标题、图例、状态面板、动画效果
6. 使用组合图形创建复杂对象（不要用单个圆形/矩形代表复杂物体）
7. 添加清晰的注释说明

【画布尺寸】1000 x 650 像素

【可用的绘图方法】
- ctx.createCircle(x, y, radius, color)
- ctx.createRect(x, y, width, height, color, borderRadius)
- ctx.createText(text, x, y, options)
- ctx.createLine(points, color, width)
- ctx.createPolygon(points, fillColor, strokeColor)
- ctx.createArc(x, y, radius, startAngle, endAngle, color)
- ctx.remove(element)
- ctx.setText(textElement, newText)

【重要】
只输出纯 JavaScript 代码，不要有 ```javascript 标记，不要有任何解释文字。
代码必须可以直接运行。"""

        response = await self.claude_service.generate_raw_response(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4000
        )

        # 清理响应，提取纯代码
        code = response.strip()
        if code.startswith('```javascript'):
            code = code[13:]
        if code.startswith('```js'):
            code = code[5:]
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]

        return code.strip()

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
        """解析章节JSON，带修复逻辑"""
        try:
            # 1. 提取 JSON
            json_str = self._extract_json(response)

            # 2. 尝试直接解析
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Initial JSON parse failed: {e}, attempting repair...")

                # 3. 尝试修复后解析
                repaired = self.json_repair.repair(json_str)
                try:
                    data = json.loads(repaired)
                    logger.info("JSON repair successful")
                except json.JSONDecodeError as e2:
                    # 4. 最后尝试：提取部分有效数据
                    logger.warning(f"Repair failed: {e2}, attempting partial extraction...")
                    data = self._extract_partial_data(json_str)
                    if not data:
                        raise ValueError(f"无法解析 JSON: {e}")

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

    def _extract_partial_data(self, json_str: str) -> Optional[Dict]:
        """尝试提取部分有效数据"""
        try:
            # 尝试提取基本字段
            data = {}

            # 提取 lesson_id
            match = re.search(r'"lesson_id"\s*:\s*"([^"]+)"', json_str)
            if match:
                data['lesson_id'] = match.group(1)

            # 提取 title
            match = re.search(r'"title"\s*:\s*"([^"]+)"', json_str)
            if match:
                data['title'] = match.group(1)

            # 提取 order
            match = re.search(r'"order"\s*:\s*(\d+)', json_str)
            if match:
                data['order'] = int(match.group(1))

            # 提取 rationale
            match = re.search(r'"rationale"\s*:\s*"([^"]+)"', json_str)
            if match:
                data['rationale'] = match.group(1)

            # 尝试提取 script 数组（简化版）
            data['script'] = []

            if data.get('title'):
                logger.info(f"Partial extraction successful: {data.get('title')}")
                return data

            return None

        except Exception as e:
            logger.error(f"Partial extraction failed: {e}")
            return None

    def parse_streaming_response(self, full_response: str) -> ChapterResult:
        """解析流式响应的完整内容"""
        return self._parse_chapter(full_response)


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
