"""
生成者 AI - 负责根据监督者的指令生成单个章节
"""

import json
import logging
from typing import AsyncGenerator, Dict, Any, Optional, List

from app.services.claude_service import ClaudeService
from .models import (
    GenerationState, ChapterResult, ChapterStep, SimulatorSpec,
    ChapterOutline
)

logger = logging.getLogger(__name__)


class ChapterGenerator:
    """
    章节生成器

    职责：
    1. 根据监督者的指令生成单个章节
    2. 每次都是新对话，无状态
    3. 专注于内容生成，不做审核
    """

    def __init__(self):
        self.claude_service = ClaudeService()

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

    def _parse_chapter(self, response: str) -> ChapterResult:
        """解析章节JSON"""
        try:
            # 提取JSON
            json_str = response
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0]
            elif '{' in response:
                start = response.index('{')
                end = response.rindex('}') + 1
                json_str = response[start:end]

            data = json.loads(json_str.strip())

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
