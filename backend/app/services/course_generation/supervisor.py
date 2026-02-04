"""
监督者 AI - 负责生成大纲、审核章节、决定是否重做
"""

import json
import logging
from typing import AsyncGenerator, Dict, Any, Optional, List
from datetime import datetime

from app.services.claude_service import ClaudeService
from .models import (
    GenerationState, CourseOutline, ChapterOutline, ChapterResult,
    ReviewResult, ReviewStatus, ChapterType, ChapterQualityStandards,
    SimulatorQualityStandards, SimulatorSpec, ChapterStep
)

logger = logging.getLogger(__name__)


class CourseSupervisor:
    """
    课程生成监督者

    职责：
    1. 生成课程大纲
    2. 分配章节生成任务
    3. 审核生成的章节
    4. 决定是否需要重做
    5. 维护全局状态
    """

    def __init__(self):
        self.claude_service = ClaudeService()
        self.quality_standards = ChapterQualityStandards()
        self.conversation_messages: List[Dict[str, str]] = []

    async def generate_outline(
        self,
        state: GenerationState,
        system_prompt: str
    ) -> CourseOutline:
        """生成课程大纲"""

        prompt = f"""你是一位资深的课程设计专家。请为以下课程生成详细的大纲。

【课程标题】
{state.course_title}

【源材料摘要】
{state.source_material[:8000]}

【源材料信息】
{state.source_info}

【要求】
1. 根据源材料的内容深度，合理划分章节（4-8章）
2. 每章要有明确的学习目标和核心概念
3. 章节之间要有逻辑递进关系
4. 为每章建议合适的模拟器主题（用于可视化演示核心概念）
5. 模拟器主题要具体、可实现，且各章不重复

【输出格式】
请以JSON格式输出：
{{
    "title": "课程标题",
    "description": "课程描述（100-200字）",
    "total_chapters": 章节数量,
    "estimated_hours": 预计学时,
    "difficulty": "beginner/intermediate/advanced",
    "core_concepts": ["核心概念1", "核心概念2", ...],
    "chapters": [
        {{
            "index": 0,
            "title": "章节标题",
            "chapter_type": "introduction/core_content/practice/assessment/summary",
            "recommended_forms": ["text_content", "simulator", "assessment"],
            "complexity_level": "simple/standard/advanced",
            "key_concepts": ["概念1", "概念2"],
            "learning_objectives": ["目标1", "目标2"],
            "suggested_simulator": "建议的模拟器主题（具体描述要演示什么）"
        }}
    ]
}}

请确保：
- 每章的 suggested_simulator 都不同，且与该章核心概念紧密相关
- 模拟器主题要具体到可以用代码实现（如"展示力的合成与分解"而非"物理模拟"）
"""

        # 记录对话
        self.conversation_messages.append({
            "role": "user",
            "content": prompt
        })

        response = await self.claude_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4000
        )

        self.conversation_messages.append({
            "role": "assistant",
            "content": response
        })

        # 解析大纲
        outline = self._parse_outline(response, state.course_title)
        state.outline = outline

        logger.info(f"Generated outline with {outline.total_chapters} chapters")
        return outline

    def _parse_outline(self, response: str, course_title: str) -> CourseOutline:
        """解析大纲JSON"""
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

            chapters = []
            for ch_data in data.get('chapters', []):
                chapter_type_str = ch_data.get('chapter_type', 'core_content')
                try:
                    chapter_type = ChapterType(chapter_type_str)
                except ValueError:
                    chapter_type = ChapterType.CORE_CONTENT

                chapters.append(ChapterOutline(
                    index=ch_data.get('index', len(chapters)),
                    title=ch_data.get('title', f'第{len(chapters)+1}章'),
                    chapter_type=chapter_type,
                    recommended_forms=ch_data.get('recommended_forms', ['text_content']),
                    complexity_level=ch_data.get('complexity_level', 'standard'),
                    key_concepts=ch_data.get('key_concepts', []),
                    learning_objectives=ch_data.get('learning_objectives', []),
                    suggested_simulator=ch_data.get('suggested_simulator')
                ))

            return CourseOutline(
                title=data.get('title', course_title),
                description=data.get('description', ''),
                total_chapters=len(chapters),
                estimated_hours=data.get('estimated_hours', 2.0),
                difficulty=data.get('difficulty', 'intermediate'),
                chapters=chapters,
                core_concepts=data.get('core_concepts', [])
            )

        except Exception as e:
            logger.error(f"Failed to parse outline: {e}")
            # 返回默认大纲
            return CourseOutline(
                title=course_title,
                description=f"关于{course_title}的课程",
                total_chapters=4,
                estimated_hours=2.0,
                difficulty='intermediate',
                chapters=[
                    ChapterOutline(
                        index=0, title="课程导入", chapter_type=ChapterType.INTRODUCTION,
                        recommended_forms=["text_content"], complexity_level="simple",
                        key_concepts=[], learning_objectives=[]
                    ),
                    ChapterOutline(
                        index=1, title="核心概念", chapter_type=ChapterType.CORE_CONTENT,
                        recommended_forms=["text_content", "simulator"], complexity_level="standard",
                        key_concepts=[], learning_objectives=[]
                    ),
                    ChapterOutline(
                        index=2, title="深入理解", chapter_type=ChapterType.CORE_CONTENT,
                        recommended_forms=["text_content", "simulator", "assessment"], complexity_level="standard",
                        key_concepts=[], learning_objectives=[]
                    ),
                    ChapterOutline(
                        index=3, title="总结测评", chapter_type=ChapterType.ASSESSMENT,
                        recommended_forms=["text_content", "assessment"], complexity_level="simple",
                        key_concepts=[], learning_objectives=[]
                    ),
                ],
                core_concepts=[]
            )

    def get_chapter_generation_prompt(
        self,
        state: GenerationState,
        chapter_index: int,
        previous_rejection: Optional[ReviewResult] = None
    ) -> str:
        """生成章节生成任务的提示词"""

        outline = state.outline
        chapter_outline = outline.chapters[chapter_index]

        # 基础信息
        prompt = f"""【章节生成任务】

你需要为课程"{outline.title}"生成第{chapter_index + 1}章的内容。

【章节信息】
- 标题：{chapter_outline.title}
- 类型：{chapter_outline.chapter_type.value}
- 复杂度：{chapter_outline.complexity_level}
- 核心概念：{', '.join(chapter_outline.key_concepts) if chapter_outline.key_concepts else '见下方'}
- 学习目标：{', '.join(chapter_outline.learning_objectives) if chapter_outline.learning_objectives else '见下方'}
- 建议模拟器主题：{chapter_outline.suggested_simulator or '根据内容自行设计'}

【课程整体信息】
- 课程描述：{outline.description}
- 核心概念：{', '.join(outline.core_concepts)}
- 难度级别：{outline.difficulty}

"""

        # 添加禁止重复的内容
        if state.used_simulators:
            prompt += f"""
【禁止重复 - 已使用的模拟器】
以下模拟器主题已在前面章节使用，本章必须使用不同的模拟器：
{chr(10).join(f'- {s}' for s in state.used_simulators)}

"""

        if state.covered_topics:
            prompt += f"""
【禁止重复 - 已讲解的主题】
以下主题已在前面章节讲解，本章应聚焦新内容：
{chr(10).join(f'- {t}' for t in state.covered_topics)}

"""

        # 如果是重做，添加上次被拒绝的原因
        if previous_rejection:
            prompt += f"""
【重要 - 上次提交被拒绝】
上次生成的内容存在以下问题，请务必修正：

{previous_rejection.get_rejection_reason()}

监督者的具体建议：
{chr(10).join(f'- {s}' for s in previous_rejection.suggestions) if previous_rejection.suggestions else '无'}

"""

        # 添加源材料
        prompt += f"""
【源材料（相关部分）】
{state.source_material[:6000]}

"""

        # 添加质量要求
        prompt += self._get_quality_requirements()

        # 添加输出格式
        prompt += self._get_output_format(chapter_index, chapter_outline)

        return prompt

    def _get_quality_requirements(self) -> str:
        """获取质量要求说明"""
        return """
【质量要求 - 必须严格遵守】

=== 模拟器质量标准（最重要）===

1. 代码结构要求：
   - 必须有 setup(ctx) 函数：初始化所有视觉元素
   - 必须有 update(ctx) 函数：每帧更新，响应变量变化
   - 代码至少 25 行，逻辑完整

2. 变量要求：
   - 必须定义 2-5 个变量（variables 数组）
   - 每个变量必须在 update 中通过 ctx.getVar() 读取
   - 变量变化必须导致视觉效果变化（这是模拟器的核心价值！）

3. 视觉要求：
   - 至少使用 3 种视觉元素（圆、矩形、文本、线条等）
   - 必须有动画效果（位置、大小、旋转等随时间或变量变化）
   - 必须有文字标签说明当前状态
   - 使用清晰的颜色区分不同元素

4. 教学要求：
   - 模拟器必须直观展示核心概念
   - 变量与视觉效果之间要有清晰的因果关系
   - 用户拖动滑块时，应该能立即看到效果变化

5. 禁止事项：
   - 不要使用 console.log、alert、document、window
   - 不要使用 setTimeout、setInterval（用 ctx.time 实现动画）
   - 不要写空的或占位的代码

=== 模拟器代码示例 ===

```javascript
// 存储元素ID
let elements = {};

function setup(ctx) {
  const { width, height } = ctx;

  // 标题
  elements.title = ctx.createText('力的合成演示', width/2, 30, {
    fontSize: 20, fontWeight: 'bold', color: '#ffffff'
  });

  // 原点
  elements.origin = ctx.createCircle(width/2, height/2, 8, '#ffffff');

  // 力向量1（蓝色）
  elements.force1 = ctx.createLine([
    {x: width/2, y: height/2},
    {x: width/2 + 100, y: height/2}
  ], '#3B82F6', 3);

  // 力向量2（绿色）
  elements.force2 = ctx.createLine([
    {x: width/2, y: height/2},
    {x: width/2, y: height/2 - 80}
  ], '#10B981', 3);

  // 合力（红色）
  elements.resultant = ctx.createLine([
    {x: width/2, y: height/2},
    {x: width/2 + 100, y: height/2 - 80}
  ], '#EF4444', 4);

  // 数值显示
  elements.f1Label = ctx.createText('F1: 100N', width/2 + 120, height/2, {
    fontSize: 14, color: '#3B82F6'
  });
  elements.f2Label = ctx.createText('F2: 80N', width/2 + 20, height/2 - 100, {
    fontSize: 14, color: '#10B981'
  });
  elements.resultLabel = ctx.createText('合力: 128N', width/2 + 130, height/2 - 50, {
    fontSize: 14, color: '#EF4444'
  });
}

function update(ctx) {
  const { width, height, math } = ctx;
  const f1 = ctx.getVar('force1');  // 力1大小
  const f2 = ctx.getVar('force2');  // 力2大小
  const angle = ctx.getVar('angle'); // 夹角

  // 计算向量终点
  const rad = math.degToRad(angle);
  const x1 = width/2 + f1;
  const y1 = height/2;
  const x2 = width/2 + f2 * math.cos(rad);
  const y2 = height/2 - f2 * math.sin(rad);

  // 计算合力
  const rx = f1 + f2 * math.cos(rad);
  const ry = f2 * math.sin(rad);
  const resultant = math.sqrt(rx*rx + ry*ry);

  // 更新力向量1
  ctx.remove(elements.force1);
  elements.force1 = ctx.createLine([
    {x: width/2, y: height/2},
    {x: x1, y: y1}
  ], '#3B82F6', 3);

  // 更新力向量2
  ctx.remove(elements.force2);
  elements.force2 = ctx.createLine([
    {x: width/2, y: height/2},
    {x: x2, y: y2}
  ], '#10B981', 3);

  // 更新合力
  ctx.remove(elements.resultant);
  elements.resultant = ctx.createLine([
    {x: width/2, y: height/2},
    {x: width/2 + rx, y: height/2 - ry}
  ], '#EF4444', 4);

  // 更新标签
  ctx.setText(elements.f1Label, `F1: ${f1.toFixed(0)}N`);
  ctx.setText(elements.f2Label, `F2: ${f2.toFixed(0)}N`);
  ctx.setText(elements.resultLabel, `合力: ${resultant.toFixed(1)}N`);

  // 更新标签位置
  ctx.setPosition(elements.f1Label, x1 + 20, y1);
  ctx.setPosition(elements.f2Label, x2 + 20, y2 - 20);
}
```

=== 内容质量标准 ===

1. 每章 5-8 个步骤
2. 每步正文至少 100 字，内容充实
3. 每步至少 2 个要点
4. 必须有测验题目（至少2题）
5. 不要有"待补充"、"..."等占位内容

"""

    def _get_output_format(self, chapter_index: int, chapter_outline: ChapterOutline) -> str:
        """获取输出格式说明"""
        return f"""
【输出格式】
请以JSON格式输出完整的章节内容：

{{
    "lesson_id": "lesson_{chapter_index + 1}",
    "title": "{chapter_outline.title}",
    "order": {chapter_index},
    "total_steps": 步骤数量,
    "rationale": "本章设计理念（50-100字）",
    "script": [
        {{
            "step_id": "step_1",
            "type": "text_content",
            "title": "步骤标题",
            "content": {{
                "body": "正文内容（至少100字）",
                "key_points": ["要点1", "要点2"]
            }}
        }},
        {{
            "step_id": "step_2",
            "type": "simulator",
            "title": "互动模拟：xxx",
            "simulator_spec": {{
                "mode": "custom",
                "name": "模拟器名称（具体描述功能）",
                "description": "模拟器描述",
                "variables": [
                    {{"name": "var1", "label": "变量1", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "单位"}},
                    {{"name": "var2", "label": "变量2", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "单位"}}
                ],
                "custom_code": "完整的模拟器代码（参考上面的示例）"
            }}
        }},
        {{
            "step_id": "step_3",
            "type": "assessment",
            "title": "知识检测",
            "assessment_spec": {{
                "type": "quick_check",
                "questions": [
                    {{
                        "question": "问题内容",
                        "options": ["选项A", "选项B", "选项C", "选项D"],
                        "correct": "A",
                        "explanation": "答案解释"
                    }}
                ],
                "pass_required": true
            }}
        }}
    ],
    "estimated_minutes": 预估时长,
    "learning_objectives": ["学习目标1", "学习目标2"],
    "complexity_level": "{chapter_outline.complexity_level}"
}}

请直接输出JSON，不要有其他内容。
"""

    async def review_chapter(
        self,
        state: GenerationState,
        chapter: ChapterResult,
        chapter_index: int
    ) -> ReviewResult:
        """审核生成的章节"""

        issues = []
        suggestions = []
        simulator_issues = []
        problematic_steps = []

        content_score = 100
        simulator_score = 100

        chapter_outline = state.outline.chapters[chapter_index]

        # === 1. 检查步骤数量 ===
        if chapter.total_steps < self.quality_standards.min_steps:
            issues.append(f"步骤太少，只有{chapter.total_steps}步，至少需要{self.quality_standards.min_steps}步")
            content_score -= 20
        elif chapter.total_steps > self.quality_standards.max_steps:
            issues.append(f"步骤太多，有{chapter.total_steps}步，最多{self.quality_standards.max_steps}步")
            content_score -= 10

        # === 2. 检查是否有模拟器 ===
        simulators = [s for s in chapter.script if s.type == 'simulator']
        if self.quality_standards.must_have_simulator and not simulators:
            if chapter_outline.chapter_type in [ChapterType.CORE_CONTENT, ChapterType.PRACTICE]:
                issues.append("核心内容章节必须包含模拟器")
                content_score -= 30

        # === 3. 检查模拟器质量 ===
        for i, step in enumerate(chapter.script):
            if step.type == 'simulator' and step.simulator_spec:
                sim_issues = step.simulator_spec.validate(self.quality_standards.simulator_standards)
                if sim_issues:
                    simulator_issues.extend(sim_issues)
                    problematic_steps.append(i)
                    simulator_score -= len(sim_issues) * 10

                # 检查是否与已使用的模拟器重复
                if step.simulator_spec.name in state.used_simulators:
                    simulator_issues.append(f"模拟器'{step.simulator_spec.name}'与前面章节重复")
                    simulator_score -= 30

        # === 4. 检查内容质量 ===
        for i, step in enumerate(chapter.script):
            if step.type in ['text_content', 'illustrated_content']:
                if step.content:
                    body = step.content.get('body', '')
                    if len(body) < self.quality_standards.min_text_length:
                        issues.append(f"步骤{i+1}内容太短，只有{len(body)}字")
                        problematic_steps.append(i)
                        content_score -= 10

                    key_points = step.content.get('key_points', [])
                    if len(key_points) < self.quality_standards.min_key_points:
                        issues.append(f"步骤{i+1}要点太少")
                        content_score -= 5

                    # 检查禁止内容
                    for forbidden in self.quality_standards.forbidden_content:
                        if forbidden in body:
                            issues.append(f"步骤{i+1}包含占位内容：{forbidden}")
                            content_score -= 15

        # === 5. 检查测验 ===
        assessments = [s for s in chapter.script if s.type == 'assessment']
        if self.quality_standards.must_have_assessment and not assessments:
            issues.append("章节缺少测验题目")
            content_score -= 15

        # === 6. 检查与大纲的一致性 ===
        if chapter.title != chapter_outline.title:
            suggestions.append(f"章节标题与大纲不一致，大纲为'{chapter_outline.title}'")

        # === 计算总分 ===
        content_score = max(0, content_score)
        simulator_score = max(0, simulator_score)
        overall_score = (content_score + simulator_score) // 2

        # === 生成建议 ===
        if simulator_issues:
            suggestions.append("请参考质量要求中的模拟器代码示例，确保代码完整且功能正确")
        if content_score < 80:
            suggestions.append("请增加内容深度，每步至少100字，并确保要点完整")

        # === 决定审核状态 ===
        if overall_score >= 70 and not simulator_issues:
            status = ReviewStatus.APPROVED
            review_comment = "章节质量合格，可以继续下一章"
        elif overall_score >= 50:
            status = ReviewStatus.NEEDS_REVISION
            review_comment = "章节需要修改部分内容"
        else:
            status = ReviewStatus.REJECTED
            review_comment = "章节质量不达标，需要重新生成"

        return ReviewResult(
            status=status,
            chapter_index=chapter_index,
            issues=issues,
            suggestions=suggestions,
            simulator_issues=simulator_issues,
            problematic_steps=problematic_steps,
            content_score=content_score,
            simulator_score=simulator_score,
            overall_score=overall_score,
            review_comment=review_comment
        )

    async def ai_review_chapter(
        self,
        state: GenerationState,
        chapter: ChapterResult,
        chapter_index: int
    ) -> ReviewResult:
        """使用AI进行更深入的审核"""

        # 先进行规则审核
        rule_review = await self.review_chapter(state, chapter, chapter_index)

        # 如果规则审核已经不通过，直接返回
        if rule_review.overall_score < 50:
            return rule_review

        # 使用AI进行语义审核
        chapter_outline = state.outline.chapters[chapter_index]

        prompt = f"""请审核以下章节内容是否符合要求。

【章节大纲要求】
- 标题：{chapter_outline.title}
- 核心概念：{', '.join(chapter_outline.key_concepts)}
- 学习目标：{', '.join(chapter_outline.learning_objectives)}
- 建议模拟器：{chapter_outline.suggested_simulator}

【生成的章节内容】
标题：{chapter.title}
设计理念：{chapter.rationale}
步骤数：{chapter.total_steps}

步骤内容：
"""
        for i, step in enumerate(chapter.script):
            prompt += f"\n{i+1}. [{step.type}] {step.title}"
            if step.type == 'simulator' and step.simulator_spec:
                prompt += f"\n   模拟器：{step.simulator_spec.name}"
                prompt += f"\n   变量：{[v.get('label') for v in step.simulator_spec.variables]}"

        prompt += f"""

【已使用的模拟器（不能重复）】
{', '.join(state.used_simulators) if state.used_simulators else '无'}

【审核要点】
1. 内容是否与大纲要求一致？
2. 模拟器是否能有效展示核心概念？
3. 模拟器是否与前面章节重复？
4. 内容深度是否足够？
5. 学习目标是否能达成？

请以JSON格式输出审核结果：
{{
    "approved": true/false,
    "score": 0-100,
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"],
    "comment": "总体评价"
}}
"""

        try:
            response = await self.claude_service.generate(
                prompt=prompt,
                system_prompt="你是一位严格的课程质量审核专家。",
                max_tokens=1000
            )

            # 解析AI审核结果
            json_str = response
            if '{' in response:
                start = response.index('{')
                end = response.rindex('}') + 1
                json_str = response[start:end]

            ai_review = json.loads(json_str)

            # 合并规则审核和AI审核结果
            combined_issues = rule_review.issues + ai_review.get('issues', [])
            combined_suggestions = rule_review.suggestions + ai_review.get('suggestions', [])

            ai_score = ai_review.get('score', 70)
            combined_score = (rule_review.overall_score + ai_score) // 2

            if ai_review.get('approved', True) and combined_score >= 70:
                status = ReviewStatus.APPROVED
            elif combined_score >= 50:
                status = ReviewStatus.NEEDS_REVISION
            else:
                status = ReviewStatus.REJECTED

            return ReviewResult(
                status=status,
                chapter_index=chapter_index,
                issues=combined_issues,
                suggestions=combined_suggestions,
                simulator_issues=rule_review.simulator_issues,
                problematic_steps=rule_review.problematic_steps,
                content_score=rule_review.content_score,
                simulator_score=rule_review.simulator_score,
                overall_score=combined_score,
                review_comment=ai_review.get('comment', rule_review.review_comment)
            )

        except Exception as e:
            logger.warning(f"AI review failed: {e}, using rule-based review only")
            return rule_review

    def check_context_compressed(self, response: str) -> bool:
        """检查监督者的上下文是否被压缩"""
        # 检查响应中是否有表明上下文丢失的迹象
        compression_indicators = [
            "我不记得",
            "请提供更多上下文",
            "之前的对话",
            "我没有看到",
            "请重新说明",
            "I don't have context",
            "previous conversation"
        ]
        return any(indicator in response for indicator in compression_indicators)

    def restore_context(self, state: GenerationState) -> str:
        """恢复监督者的上下文"""
        return f"""【上下文恢复】

由于对话较长，我需要重新向你说明当前的课程生成状态。

{state.get_context_summary()}

请继续监督课程生成工作。当前需要生成第{state.current_chapter_index + 1}章。
"""
