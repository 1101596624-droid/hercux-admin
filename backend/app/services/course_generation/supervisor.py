"""
监督者 AI - 负责生成大纲、审核章节、决定是否重做
支持网络搜索获取最新信息
"""

import json
import logging
from typing import AsyncGenerator, Dict, Any, Optional, List
from datetime import datetime

from app.services.claude_service import ClaudeService
from .models import (
    GenerationState, CourseOutline, ChapterOutline, ChapterResult,
    ReviewResult, ReviewStatus, ChapterType, ChapterQualityStandards,
    ChapterStep, StepReviewResult, HTMLSimulatorSpec, HTMLSimulatorQualityStandards
)
from .generator import JSONRepairTool
from .standards_loader import get_standards_loader

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
    6. 搜索最新信息确保内容时效性
    """

    def __init__(self):
        self.claude_service = ClaudeService()
        self.quality_standards = ChapterQualityStandards()
        self.conversation_messages: List[Dict[str, str]] = []
        self._search_service = None
        self.standards_loader = get_standards_loader()  # 新增：标准加载器

    @property
    def search_service(self):
        """Lazy load search service"""
        if self._search_service is None:
            from app.services.tavily_service import get_tavily_service
            self._search_service = get_tavily_service()
        return self._search_service

    async def search_latest_info(self, topic: str) -> str:
        """搜索最新信息"""
        try:
            return await self.search_service.search_for_context(topic, "academic")
        except Exception as e:
            logger.warning(f"Search failed: {e}")
            return ""

    def _detect_source_chapters(self, source_material: str) -> int:
        """检测源材料中的章节数量"""
        import re
        patterns = [
            r'第[一二三四五六七八九十百\d]+[章节篇]',
            r'Chapter\s+\d+',
            r'CHAPTER\s+\d+',
            r'(?m)^#{1,2}\s+\d+[\.\s]',
            r'(?m)^\d+[\.\、]\s*[^\d\s]',
        ]
        chapter_titles = set()
        for pattern in patterns:
            matches = re.findall(pattern, source_material)
            for m in matches:
                chapter_titles.add(m.strip())
            if len(chapter_titles) >= 3:
                break
        return len(chapter_titles)

    async def generate_outline(
        self,
        state: GenerationState,
        system_prompt: str
    ) -> CourseOutline:
        """生成课程大纲"""

        # 搜索最新信息
        search_context = await self.search_latest_info(state.course_title)

        prompt = f"""你是一位资深的课程设计专家。请为以下课程生成详细的大纲。

【课程标题】
{state.course_title}

【源材料摘要】
{state.source_material[:8000]}

【源材料信息】
{state.source_info}

"""

        # 添加搜索结果
        if search_context:
            prompt += f"""
【最新网络信息】
以下是关于该主题的最新信息，请在设计课程时参考：
{search_context}

请注意：
- 确保课程内容反映最新的研究和发展
- 如果源材料与最新信息有冲突，以最新信息为准
- 在课程中适当引用最新数据和案例

"""

        # 课程风格描述
        style_descriptions = {
            'academic': '学术型课程：注重理论深度，章节应覆盖完整的学术体系，可以多章深入',
            'practical': '实践型课程：注重动手操作，章节围绕实际技能展开，精简高效',
            'sports': '运动科学课程：注重技术动作分析和生物力学原理，按技术环节划分章节',
            'default': '通用课程：根据知识结构合理组织章节',
        }
        style_hint = style_descriptions.get(state.processor_id, style_descriptions['default'])

        # 源材料长度信息
        material_length = len(state.source_material)

        # 对于大文件（>3万字），检测源材料中的章节数
        min_chapters_hint = ""
        detected_chapter_count = 0
        if material_length > 30000:
            detected_chapter_count = self._detect_source_chapters(state.source_material)
            if detected_chapter_count > 0:
                min_chapters_hint = f"""
【源材料章节检测】
检测到源材料本身包含约 {detected_chapter_count} 个章节/部分。
【强制要求】生成的课程章节数不得少于 {detected_chapter_count} 章。你必须完整、精确地覆盖源材料中的所有内容，不得遗漏或过度合并。
"""

        prompt += f"""【课程风格】
{style_hint}

【源材料规模】
源材料总字数约 {material_length} 字。
{min_chapters_hint}
"""

        prompt += """【要求】
1. 章节数量由你根据以下因素自主决定，不设固定范围：
   - 【最优先】课程风格：不同风格对章节粒度的要求不同
   - 【次优先】源材料内容量：材料越丰富，可划分的章节越多
   - 【参考】知识结构的自然分界：按内容的逻辑边界划分，不要为凑数而拆分或合并
   - 【强制】如果上方有"源材料章节检测"，生成的章节数不得少于检测到的数量
2. 【核心原则】课程必须完整、精确地表达源材料中的所有内容，不得遗漏任何重要知识点
3. 每章要有明确的学习目标和核心概念
4. 章节之间要有逻辑递进关系
5. 为每章建议合适的模拟器主题（用于可视化演示核心概念）
6. 模拟器主题要具体、可实现，且各章不重复
7. 【重要】确保内容反映最新的研究成果和行业动态

【章节标题要求 - 非常重要】
- 章节标题必须具体、专业，体现该章的核心内容
- 禁止使用泛化模板名称，以下名称绝对禁止使用：
  × 课程导入、核心概念、深入理解、总结测评
  × 基础知识、进阶内容、综合应用、知识拓展
  × 第一章、第二章（纯数字编号）
- 好的标题示例（以运动技术课程为例）：
  ✓ 助跑技术与节奏控制
  ✓ 起跳力学原理分析
  ✓ 过杆背弓技术详解
  ✓ 落地缓冲与安全防护
- 标题应该让学习者一眼就知道这章要学什么具体内容

【输出格式】
请以JSON格式输出：
{
    "title": "课程标题",
    "description": "课程描述（100-200字）",
    "total_chapters": 章节数量,
    "estimated_hours": 预计学时,
    "difficulty": "beginner/intermediate/advanced",
    "core_concepts": ["核心概念1", "核心概念2", "核心概念3"],
    "chapters": [
        {
            "index": 0,
            "title": "具体的章节标题",
            "chapter_type": "introduction",
            "recommended_forms": ["text_content", "simulator", "assessment"],
            "complexity_level": "simple",
            "key_concepts": ["概念1", "概念2"],
            "learning_objectives": ["目标1", "目标2"],
            "suggested_simulator": "建议的模拟器主题（具体描述要演示什么）"
        },
        {
            "index": 1,
            "title": "另一个具体的章节标题",
            "chapter_type": "core_content",
            "recommended_forms": ["text_content", "illustrated_content", "simulator"],
            "complexity_level": "standard",
            "key_concepts": ["概念3", "概念4"],
            "learning_objectives": ["目标3", "目标4"],
            "suggested_simulator": "另一个模拟器主题"
        }
    ]
}

注意：
- chapters 数组中列出所有章节，不要用省略号(...)
- 必须输出完整、可直接解析的JSON
- 不要在JSON中添加注释

请确保：
- 每章的 suggested_simulator 都不同，且与该章核心概念紧密相关
- 模拟器主题要具体到可以用代码实现（如"展示力的合成与分解"而非"物理模拟"）
- 同一课程内的图片（illustrated_content）和模拟器之间要有明显区别，不能视觉重复
"""

        # 记录对话
        self.conversation_messages.append({
            "role": "user",
            "content": prompt
        })

        response = await self.claude_service.generate_raw_response(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4000
        )

        self.conversation_messages.append({
            "role": "assistant",
            "content": response
        })

        # 解析大纲
        outline = self._parse_outline(response, state)
        state.outline = outline

        logger.info(f"Generated outline with {outline.total_chapters} chapters")
        return outline

    def _parse_outline(self, response: str, state: GenerationState) -> CourseOutline:
        """解析大纲JSON，带JSON修复"""
        course_title = state.course_title
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

            # 先尝试直接解析
            try:
                data = json.loads(json_str.strip())
            except json.JSONDecodeError as e:
                # 使用 JSONRepairTool 修复
                logger.warning(f"Outline JSON parse failed, trying repair: {e}")
                repaired = JSONRepairTool.repair(json_str)
                data = json.loads(repaired)
                logger.info("Outline JSON repaired successfully")

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
            # 根据源材料检测章节数和长度动态生成默认大纲
            material_len = len(state.source_material)
            detected = self._detect_source_chapters(state.source_material) if material_len > 30000 else 0

            if detected > 0:
                fallback_count = detected
            elif material_len < 2000:
                fallback_count = 3
            elif material_len < 5000:
                fallback_count = 4
            elif material_len < 10000:
                fallback_count = 5
            elif material_len < 50000:
                fallback_count = 6
            elif material_len < 100000:
                fallback_count = 8
            elif material_len < 200000:
                fallback_count = 10
            else:
                fallback_count = 12

            fallback_chapters = []
            # 循环使用的章节类型模板
            templates = [
                (ChapterType.INTRODUCTION, "simple", ["text_content"]),
                (ChapterType.CORE_CONTENT, "standard", ["text_content", "simulator"]),
                (ChapterType.CORE_CONTENT, "standard", ["text_content", "illustrated_content"]),
                (ChapterType.CORE_CONTENT, "standard", ["text_content", "simulator", "ai_tutor", "assessment"]),
                (ChapterType.CORE_CONTENT, "advanced", ["text_content", "simulator"]),
                (ChapterType.CORE_CONTENT, "standard", ["text_content", "illustrated_content", "ai_tutor", "assessment"]),
                (ChapterType.PRACTICE, "standard", ["text_content", "simulator", "ai_tutor", "assessment"]),
                (ChapterType.CORE_CONTENT, "advanced", ["text_content", "simulator"]),
                (ChapterType.CORE_CONTENT, "standard", ["text_content", "illustrated_content"]),
                (ChapterType.CORE_CONTENT, "standard", ["text_content", "simulator", "ai_tutor", "assessment"]),
                (ChapterType.PRACTICE, "standard", ["text_content", "simulator"]),
                (ChapterType.ASSESSMENT, "simple", ["text_content", "ai_tutor", "assessment"]),
            ]
            for i in range(fallback_count):
                t = templates[i] if i < len(templates) else templates[-1]
                fallback_chapters.append(ChapterOutline(
                    index=i, title=f"{course_title}第{i+1}部分",
                    chapter_type=t[0], complexity_level=t[1],
                    recommended_forms=t[2],
                    key_concepts=[], learning_objectives=[]
                ))

            return CourseOutline(
                title=course_title,
                description=f"关于{course_title}的课程",
                total_chapters=fallback_count,
                estimated_hours=max(1.0, fallback_count * 0.5),
                difficulty='intermediate',
                chapters=fallback_chapters,
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

{self._get_visualization_recommendations(state, chapter_outline)}

【课程整体信息】
- 课程描述：{outline.description}
- 核心概念：{', '.join(outline.core_concepts)}
- 难度级别：{outline.difficulty}

"""

        # 如果上次有 JSON 解析错误，添加修复指导
        if hasattr(state, 'last_json_error') and state.last_json_error:
            prompt += f"""
【重要 - JSON格式修复】
上次生成的内容无法解析为有效JSON，错误：{state.last_json_error}

监督者的修复指导：
{getattr(state, 'json_fix_guidance', '请确保输出纯净的JSON格式')}

请特别注意：
1. 直接输出JSON，不要有任何前缀文字或后缀说明
2. custom_code 中的代码字符串必须正确转义（引号用 \\"，换行用 \\n）
3. 确保所有括号正确闭合
4. 不要在JSON中使用注释

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
        """
        获取质量要求说明 - 骨架生成阶段专用

        注意：此阶段只生成结构骨架，不生成长文本和代码。
        代码质量要求已移至 generator.py 的代码生成阶段。
        文本质量要求已移至 service.py 的文本生成阶段。
        """
        return """
【质量要求 - 骨架生成阶段】

=== 章节结构要求 ===

1. 步骤数量：由你根据该章节的内容深度和课程风格自主决定，不设固定范围
2. 步骤类型由你自主搭配，可用类型：
   - text_content（纯文本讲解）
   - illustrated_content（图文讲解）
   - simulator（互动模拟器）
   - ai_tutor（AI导师苏格拉底式提问 - 检验学生理解深度）
   - assessment（测验）
3. 【重要】同一课程内的图片和模拟器必须有明显区别，不能重复相似的视觉内容
4. 【重要】每章建议在 assessment 前安排一个 ai_tutor 步骤，通过AI导师对话检验学生理解
5. 学习目标：至少 4 个，使用动词开头
6. 每个步骤的 key_points：3-5 个要点

=== 模拟器变量要求（重要）===

模拟器的 variables 数组必须完整定义：
- 必须定义 2-3 个变量（不要超过3个，每个变量必须有明确的视觉反馈）
- 每个变量必须包含：name, label, min, max, default, step, unit
- 变量之间应有逻辑关联
- 示例：
  {"name": "speed", "label": "速度", "min": 1, "max": 100, "default": 50, "step": 1, "unit": "m/s"}

=== 禁止事项 ===

- 不要有"待补充"、"..."、"暂无"、"略"等占位内容
- 不要在 key_points 中写空字符串
- 不要遗漏 variables 定义

=== 重要提醒 ===

本阶段只需输出结构骨架：
- body 字段留空（后续自动生成）
- description 字段简短（30字以内）
- explanation 字段留空（后续自动生成）
- rationale 字段留空（后续自动生成）
- custom_code 字段留空（后续自动生成）

"""

    def _get_output_format(self, chapter_index: int, chapter_outline: ChapterOutline) -> str:
        """获取输出格式说明 - 简化版, 所有长文本由后续步骤生成"""
        return f"""
【输出格式 - 简化骨架版】
为确保 JSON 解析成功，请输出简化的章节骨架。所有长文本内容将由系统后续自动生成。

{{
    "lesson_id": "lesson_{chapter_index + 1}",
    "title": "{chapter_outline.title}",
    "order": {chapter_index},
    "total_steps": 步骤数量,
    "rationale": "",
    "script": [
        {{
            "step_id": "step_1",
            "type": "text_content",
            "title": "步骤标题（简短）",
            "content": {{
                "body": "",
                "key_points": ["要点1", "要点2", "要点3"]
            }}
        }},
        {{
            "step_id": "step_2",
            "type": "illustrated_content",
            "title": "图文讲解：xxx",
            "content": {{
                "body": "",
                "key_points": ["要点1", "要点2"]
            }},
            "diagram_spec": {{
                "diagram_id": "diagram_1",
                "type": "static_diagram",
                "description": "图片描述（30字以内的关键词）",
                "style": "educational",
                "elements": ["元素1", "元素2"]
            }}
        }},
        {{
            "step_id": "step_3",
            "type": "simulator",
            "title": "互动模拟：xxx",
            "simulator_spec": {{
                "mode": "custom",
                "name": "模拟器名称",
                "description": "简短描述（30字以内）",
                "variables": [
                    {{"name": "var1", "label": "变量1", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "单位"}},
                    {{"name": "var2", "label": "变量2", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "单位"}}
                ],
                "custom_code": ""
            }}
        }},
        {{
            "step_id": "step_4",
            "type": "ai_tutor",
            "title": "AI导师：核心概念检测",
            "ai_spec": {{
                "mode": "proactive_assessment",
                "opening_message": "",
                "probing_questions": [{{"question":"问题","intent":"意图","expected_elements":["要素"]}}],
                "diagnostic_focus": {{"key_concepts":["概念"],"common_misconceptions":["误区"]}},
                "max_turns": 6
            }}
        }},
        {{
            "step_id": "step_5",
            "type": "assessment",
            "title": "知识检测",
            "assessment_spec": {{
                "type": "quick_check",
                "questions": [
                    {{
                        "question": "问题内容（简短）",
                        "options": ["A", "B", "C", "D"],
                        "correct": "A",
                        "explanation": ""
                    }}
                ],
                "pass_required": true
            }}
        }}
    ],
    "estimated_minutes": 预估时长,
    "learning_objectives": ["目标1", "目标2", "目标3"],
    "complexity_level": "{chapter_outline.complexity_level}"
}}

【极其重要 - 必须遵守】
1. 所有 body 字段必须为空字符串 ""
2. 所有 description 字段必须简短（30字以内）
3. 所有 explanation 字段必须为空字符串 ""
4. rationale 字段必须为空字符串 ""
5. custom_code 字段必须为空字符串 ""
6. 只填写结构信息：step_id、type、title、key_points、variables

【JSON 格式规范】
1. 使用英文双引号 " "，不要用中文引号
2. 不要在字符串中直接换行
3. 数组最后一个元素后不要加逗号

【章节结构要求】
- 步骤数量由你根据章节内容深度自主决定
- 步骤类型自主搭配（text_content、illustrated_content、simulator、ai_tutor、assessment）
- 同一课程内的图片和模拟器必须有明显区别

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

        # === 1. 步骤数量（不设硬限制，仅记录极端情况） ===
        if chapter.total_steps < 3:
            issues.append(f"步骤过少，只有{chapter.total_steps}步，内容可能不完整")
            content_score -= 15

        # === 2. 检查模拟器质量（使用统一评分系统）===
        simulators = [s for s in chapter.script if s.type == 'simulator']
        for i, step in enumerate(chapter.script):
            if step.type == 'simulator' and step.simulator_spec:
                # 使用统一的质量评分系统
                quality_score = step.simulator_spec.calculate_quality_score(self.quality_standards.simulator_standards)

                # 根据评分结果判断质量
                if not quality_score.passed:
                    simulator_issues.extend(quality_score.issues)
                    problematic_steps.append(i)
                    # 根据分数扣分
                    simulator_score -= (100 - quality_score.total_score)

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

        # === 4. 检查测验质量（不强制必须有，但有的话检查基本质量） ===
        assessments = [s for s in chapter.script if s.type == 'assessment']
        if assessments:
            # 检查测验是否有题目
            total_questions = sum(
                len(a.assessment_spec.get('questions', []))
                for a in assessments if a.assessment_spec
            )
            if total_questions == 0:
                issues.append("测验步骤没有题目内容")
                content_score -= 10

        # === 5. 检查图文区别性（不限数量，但要有区别） ===
        illustrated = [s for s in chapter.script if s.type == 'illustrated_content']
        if len(illustrated) > 1:
            # 检查图文步骤之间是否有明显区别
            diagram_descs = []
            for ill_step in illustrated:
                if ill_step.content and ill_step.content.get('diagram_description'):
                    diagram_descs.append(ill_step.content.get('diagram_description', ''))
            # 简单检查：如果描述完全相同则扣分
            if len(diagram_descs) > 1 and len(set(diagram_descs)) < len(diagram_descs):
                issues.append("多个图文步骤的图片描述相同，需要有明显区别")
                content_score -= 15

        # === 7. 检查与大纲的一致性 ===
        if chapter.title != chapter_outline.title:
            suggestions.append(f"章节标题与大纲不一致，大纲为'{chapter_outline.title}'")

        # === 8. 生成每个步骤的详细审核结果（用于单步重做）===
        step_reviews = []
        for i, step in enumerate(chapter.script):
            step_review = await self.review_single_step(state, chapter, i)
            step_reviews.append(step_review)

        # === 计算总分 ===
        content_score = max(0, content_score)
        simulator_score = max(0, simulator_score)
        overall_score = (content_score + simulator_score) // 2

        # === 生成建议 ===
        if simulator_issues:
            suggestions.append("请参考质量要求中的模拟器代码示例，确保代码至少200行且功能完整，包含标题、图例、状态面板")
        if content_score < 80:
            suggestions.append("请增加内容深度，每步至少200字，每步至少4个要点，整章至少1500字")

        # === 决定审核状态（专业级标准）===
        # 检查是否有步骤需要修改
        steps_needing_revision = [sr for sr in step_reviews if not sr.is_approved()]

        if overall_score >= 80 and not simulator_issues and not steps_needing_revision:
            status = ReviewStatus.APPROVED
            review_comment = "章节质量优秀，符合专业级标准，可以继续下一章"
        elif overall_score >= 60 and steps_needing_revision:
            # 有部分步骤需要修改，使用 NEEDS_REVISION 状态触发单步重做
            status = ReviewStatus.NEEDS_REVISION
            review_comment = f"章节有 {len(steps_needing_revision)} 个步骤需要修改"
        elif overall_score >= 60:
            status = ReviewStatus.NEEDS_REVISION
            review_comment = "章节需要修改部分内容以达到专业级标准"
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
            step_reviews=step_reviews,
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
                # HTML模拟器不再有variables字段

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
            response = await self.claude_service.generate_raw_response(
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

    async def analyze_json_error(
        self,
        raw_response: str,
        error_message: str,
        chapter_index: int
    ) -> str:
        """分析 JSON 解析错误并生成修复指导"""

        # 截取响应的关键部分
        response_preview = raw_response[:2000] if len(raw_response) > 2000 else raw_response
        response_end = raw_response[-500:] if len(raw_response) > 500 else ""

        prompt = f"""生成器返回的章节内容无法解析为有效的 JSON。请分析问题并给出修复指导。

【错误信息】
{error_message}

【响应开头】
{response_preview}

【响应结尾】
{response_end}

【常见问题】
1. JSON 字符串中包含未转义的引号或换行符
2. JSON 结构不完整（缺少闭合括号）
3. 在 JSON 外有多余的文字说明
4. custom_code 字段中的代码包含特殊字符未转义

请分析具体问题，并以简洁的指令形式给出修复建议（不超过200字）。
直接输出修复指令，不要有其他内容。"""

        try:
            response = await self.claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt="你是一位 JSON 格式专家，擅长诊断和修复 JSON 解析问题。",
                max_tokens=500
            )
            return response.strip()
        except Exception as e:
            logger.warning(f"Failed to analyze JSON error: {e}")
            return "请确保输出纯净的 JSON 格式，不要有任何额外文字。代码字符串中的引号和换行符必须正确转义。"

    def get_step_regeneration_context(
        self,
        state: GenerationState,
        chapter: ChapterResult,
        step_index: int,
        step_review: 'StepReviewResult'
    ) -> Dict[str, Any]:
        """
        获取单步重做的上下文信息

        Args:
            state: 生成状态
            chapter: 当前章节
            step_index: 步骤索引
            step_review: 步骤审核结果

        Returns:
            包含重做所需上下文的字典
        """
        step = chapter.script[step_index]

        # 构建上下文
        context = {
            'course_title': state.course_title,
            'chapter_title': chapter.title,
            'learning_objectives': ', '.join(chapter.learning_objectives),
            'title': step.title,
            'content_summary': ''
        }

        # 提取内容摘要
        if step.content:
            body = step.content.get('body', '')
            context['content_summary'] = body[:200] + '...' if len(body) > 200 else body

        # 如果是模拟器，添加模拟器信息
        if step.type == 'simulator' and step.simulator_spec:
            context['simulator_name'] = step.simulator_spec.name
            context['simulator_description'] = step.simulator_spec.description
            # HTML模拟器不再有variables字段

        return context

    async def review_single_step(
        self,
        state: GenerationState,
        chapter: ChapterResult,
        step_index: int
    ) -> 'StepReviewResult':
        """
        审核单个步骤

        Args:
            state: 生成状态
            chapter: 当前章节
            step_index: 步骤索引

        Returns:
            步骤审核结果
        """
        from .models import StepReviewResult

        step = chapter.script[step_index]
        issues = []
        suggestions = []
        score = 100

        # 根据步骤类型进行审核
        if step.type == 'text_content' or step.type == 'illustrated_content':
            # 检查内容长度
            if step.content:
                body = step.content.get('body', '')
                if len(body) < self.quality_standards.min_text_length:
                    issues.append(f"内容太短，只有{len(body)}字，至少需要{self.quality_standards.min_text_length}字")
                    score -= 20

                key_points = step.content.get('key_points', [])
                if len(key_points) < self.quality_standards.min_key_points:
                    issues.append(f"要点太少，只有{len(key_points)}个，至少需要{self.quality_standards.min_key_points}个")
                    score -= 10

                # 检查禁止内容
                for forbidden in self.quality_standards.forbidden_content:
                    if forbidden in body:
                        issues.append(f"包含占位内容：{forbidden}")
                        score -= 15
            else:
                issues.append("步骤缺少内容")
                score -= 30

            # 图文内容额外检查
            if step.type == 'illustrated_content':
                if not step.diagram_spec:
                    issues.append("图文内容缺少 diagram_spec")
                    score -= 20
                elif not step.diagram_spec.get('description'):
                    issues.append("图片描述为空")
                    score -= 15
                elif len(step.diagram_spec.get('description', '')) < 50:
                    issues.append("图片描述太短，至少需要50字")
                    suggestions.append("请详细描述图片内容，包括主题、场景、关键元素、视觉风格")
                    score -= 10

        elif step.type == 'simulator':
            if step.simulator_spec:
                # 使用统一的质量评分系统
                quality_score = step.simulator_spec.calculate_quality_score(self.quality_standards.simulator_standards)

                # 根据评分结果判断质量
                if not quality_score.passed:
                    issues.extend(quality_score.issues)
                    # 分数转换：quality_score是0-100分，我们的score也是0-100分
                    score = quality_score.total_score

                # 检查是否重复
                if step.simulator_spec.name in state.used_simulators:
                    issues.append(f"模拟器'{step.simulator_spec.name}'与前面章节重复")
                    score -= 30
            else:
                issues.append("模拟器步骤缺少 simulator_spec")
                score -= 40

        elif step.type == 'assessment':
            if step.assessment_spec:
                questions = step.assessment_spec.get('questions', [])
                if len(questions) < 2:
                    issues.append(f"测验题目太少，只有{len(questions)}道")
                    suggestions.append("至少需要2道测验题目")
                    score -= 15

                # 检查每道题的完整性
                for i, q in enumerate(questions):
                    if not q.get('question'):
                        issues.append(f"第{i+1}题缺少问题内容")
                        score -= 10
                    if not q.get('options') or len(q.get('options', [])) < 3:
                        issues.append(f"第{i+1}题选项不足")
                        score -= 5
                    if not q.get('explanation'):
                        issues.append(f"第{i+1}题缺少解析")
                        score -= 5
            else:
                issues.append("测评步骤缺少 assessment_spec")
                score -= 30

        # 确定状态
        score = max(0, score)
        if score >= 80:
            status = ReviewStatus.APPROVED
        elif score >= 50:
            status = ReviewStatus.NEEDS_REVISION
        else:
            status = ReviewStatus.REJECTED

        return StepReviewResult(
            step_index=step_index,
            step_type=step.type,
            status=status,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    # ==================== 碎片化检查系统 ====================

    async def check_chapter_skeleton(
        self,
        state: GenerationState,
        chapter: ChapterResult,
        chapter_index: int
    ) -> Dict[str, Any]:
        """
        检查章节骨架结构（碎片化检查第一步）

        在生成步骤内容之前，先检查章节的整体结构是否合理。

        Returns:
            {
                'approved': bool,
                'action': 'proceed' | 'revise' | 'regenerate',
                'issues': List[str],
                'suggestions': List[str],
                'revision_guidance': str  # 如果需要修改，提供具体指导
            }
        """
        issues = []
        suggestions = []
        chapter_outline = state.outline.chapters[chapter_index]

        # 1. 检查步骤数量（仅极端情况报警）
        if chapter.total_steps < 3:
            issues.append(f"步骤过少：{chapter.total_steps}步，内容可能不完整")

        # 2. 检查步骤类型分布
        type_counts = {}
        for step in chapter.script:
            type_counts[step.type] = type_counts.get(step.type, 0) + 1

        # 2. 检查步骤类型（不限数量，仅检查区别性）
        # 检查模拟器之间是否有区别
        sim_names = [s.simulator_spec.name for s in chapter.script
                     if s.type == 'simulator' and s.simulator_spec]
        if len(sim_names) > 1 and len(set(sim_names)) < len(sim_names):
            issues.append("同一章节内有重复的模拟器主题，需要有明显区别")

        # 检查图文之间是否有区别
        ill_titles = [s.title for s in chapter.script if s.type == 'illustrated_content']
        if len(ill_titles) > 1 and len(set(ill_titles)) < len(ill_titles):
            issues.append("同一章节内有重复的图文标题，需要有明显区别")

        # 3. 模拟器检查 (HTML格式已在生成时验证，此处跳过)
        # HTML模拟器使用完整的HTML/JS代码，不需要变量完整性检查

        # 4. 检查学习目标
        if len(chapter.learning_objectives) < 3:
            issues.append(f"学习目标不足：{len(chapter.learning_objectives)}个，至少需要3个")

        # 5. 检查与大纲一致性
        if chapter.title != chapter_outline.title:
            suggestions.append(f"章节标题与大纲不一致，建议使用：{chapter_outline.title}")

        # 决定行动
        if not issues:
            return {
                'approved': True,
                'action': 'proceed',
                'issues': [],
                'suggestions': suggestions,
                'revision_guidance': ''
            }
        elif len(issues) <= 3:
            # 小问题，可以修改
            return {
                'approved': False,
                'action': 'revise',
                'issues': issues,
                'suggestions': suggestions,
                'revision_guidance': self._generate_skeleton_revision_guidance(issues, suggestions)
            }
        else:
            # 问题太多，需要重新生成
            return {
                'approved': False,
                'action': 'regenerate',
                'issues': issues,
                'suggestions': suggestions,
                'revision_guidance': ''
            }

    def _generate_skeleton_revision_guidance(self, issues: List[str], suggestions: List[str]) -> str:
        """生成骨架修改指导"""
        guidance = "请修改章节骨架，解决以下问题：\n"
        for i, issue in enumerate(issues, 1):
            guidance += f"{i}. {issue}\n"
        if suggestions:
            guidance += "\n建议：\n"
            for s in suggestions:
                guidance += f"- {s}\n"
        return guidance

    async def check_step_immediately(
        self,
        state: GenerationState,
        chapter: ChapterResult,
        step_index: int,
        previous_errors: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        立即检查刚生成的步骤（碎片化检查核心方法）

        Args:
            state: 生成状态
            chapter: 当前章节
            step_index: 步骤索引
            previous_errors: 之前的错误记录（用于动态调整提示词）

        Returns:
            {
                'approved': bool,
                'action': 'proceed' | 'revise' | 'regenerate',
                'issues': List[str],
                'adjusted_prompt': str,  # 如果需要重试，提供调整后的提示词
                'error_type': str  # 错误类型分类
            }
        """
        step = chapter.script[step_index]
        issues = []
        error_type = None

        # 根据步骤类型进行检查
        if step.type == 'simulator':
            result = await self._check_simulator_step(state, step, previous_errors)
        elif step.type in ['text_content', 'illustrated_content']:
            result = await self._check_content_step(step, previous_errors)
        elif step.type == 'assessment':
            result = await self._check_assessment_step(step, previous_errors)
        else:
            result = {'approved': True, 'issues': [], 'error_type': None}

        # 如果检查不通过，生成调整后的提示词
        if not result['approved']:
            adjusted_prompt = self._generate_adjusted_prompt(
                step_type=step.type,
                issues=result['issues'],
                error_type=result.get('error_type'),
                previous_errors=previous_errors or []
            )
            result['adjusted_prompt'] = adjusted_prompt
            result['action'] = 'revise' if len(result['issues']) <= 2 else 'regenerate'
        else:
            result['action'] = 'proceed'
            result['adjusted_prompt'] = ''

        return result

    async def _check_simulator_step(
        self,
        state: GenerationState,
        step: 'ChapterStep',
        previous_errors: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """检查HTML模拟器步骤（使用统一质量评分系统）"""
        issues = []
        error_type = None

        if not step.simulator_spec:
            return {
                'approved': False,
                'issues': ['模拟器步骤缺少 simulator_spec'],
                'error_type': 'missing_spec'
            }

        spec = step.simulator_spec

        # 使用统一的质量评分系统
        quality_score = spec.calculate_quality_score(self.quality_standards.simulator_standards)

        # 如果未通过质量阈值，收集所有问题
        if not quality_score.passed:
            issues = quality_score.issues.copy()
            # 根据分数判断错误类型
            if quality_score.visual_score < 10:
                error_type = 'poor_visual_quality'
            elif quality_score.interaction_score < 5:
                error_type = 'insufficient_interaction'
            elif quality_score.canvas_score < 10:
                error_type = 'poor_canvas_usage'
            elif quality_score.structure_score < 10:
                error_type = 'poor_structure'
            else:
                error_type = 'low_quality_score'

        # 检查重复
        if spec.name in state.used_simulators:
            issues.append(f"模拟器'{spec.name}'与前面章节重复")
            if not error_type:
                error_type = 'duplicate_simulator'

        return {
            'approved': len(issues) == 0,
            'issues': issues,
            'error_type': error_type,
            'quality_score': quality_score.total_score
        }

    async def _check_content_step(
        self,
        step: 'ChapterStep',
        previous_errors: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """检查文本/图文内容步骤"""
        issues = []
        error_type = None

        if not step.content:
            return {
                'approved': False,
                'issues': ['步骤缺少内容'],
                'error_type': 'missing_content'
            }

        body = step.content.get('body', '')
        key_points = step.content.get('key_points', [])

        # 检查内容长度
        if len(body) < self.quality_standards.min_text_length:
            issues.append(f"内容太短：{len(body)}字，至少需要{self.quality_standards.min_text_length}字")
            error_type = 'short_content'

        # 检查要点
        if len(key_points) < self.quality_standards.min_key_points:
            issues.append(f"要点不足：{len(key_points)}个，至少需要{self.quality_standards.min_key_points}个")
            if not error_type:
                error_type = 'insufficient_keypoints'

        # 检查禁止内容
        for forbidden in self.quality_standards.forbidden_content:
            if forbidden in body:
                issues.append(f"包含占位内容：{forbidden}")
                error_type = 'placeholder_content'

        # 图文内容额外检查
        if step.type == 'illustrated_content':
            if not step.diagram_spec:
                issues.append("图文内容缺少 diagram_spec")
                error_type = 'missing_diagram'
            elif not step.diagram_spec.get('description'):
                issues.append("图片描述为空")
                error_type = 'empty_description'

        return {
            'approved': len(issues) == 0,
            'issues': issues,
            'error_type': error_type
        }

    async def _check_assessment_step(
        self,
        step: 'ChapterStep',
        previous_errors: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """检查测验步骤"""
        issues = []
        error_type = None

        if not step.assessment_spec:
            return {
                'approved': False,
                'issues': ['测验步骤缺少 assessment_spec'],
                'error_type': 'missing_spec'
            }

        questions = step.assessment_spec.get('questions', [])

        if len(questions) < 2:
            issues.append(f"题目不足：{len(questions)}道，至少需要2道")
            error_type = 'insufficient_questions'

        for i, q in enumerate(questions):
            if not q.get('question'):
                issues.append(f"第{i+1}题缺少问题内容")
                error_type = 'incomplete_question'
            if not q.get('options') or len(q.get('options', [])) < 3:
                issues.append(f"第{i+1}题选项不足")
                if not error_type:
                    error_type = 'insufficient_options'
            if not q.get('explanation'):
                issues.append(f"第{i+1}题缺少解析")
                if not error_type:
                    error_type = 'missing_explanation'

        return {
            'approved': len(issues) == 0,
            'issues': issues,
            'error_type': error_type
        }

    def _generate_adjusted_prompt(
        self,
        step_type: str,
        issues: List[str],
        error_type: str,
        previous_errors: List[Dict[str, Any]]
    ) -> str:
        """
        根据错误类型生成调整后的提示词（动态提示词调整核心方法）

        这是碎片化检查的关键：根据具体错误类型，生成针对性的修复指导。
        """
        prompt_additions = []

        # 基础问题描述
        prompt_additions.append("【重要 - 上次生成存在问题，请修正】")
        prompt_additions.append("问题列表：")
        for issue in issues:
            prompt_additions.append(f"  - {issue}")

        # 根据错误类型添加针对性指导
        if error_type == 'poor_visual_quality':
            prompt_additions.append("""
【视觉质量不足 - 配色和视觉设计问题】
模拟器的视觉质量评分过低。请注意：

1. **配色协调性**：
   - 避免使用过多高饱和度颜色（饱和度>0.6的颜色不超过2种）
   - 控制亮度对比，不要使用过于刺眼的颜色搭配
   - 推荐使用柔和色调：#3b82f6(蓝)、#10b981(绿)、#f59e0b(橙)、#8b5cf6(紫)

2. **视觉元素**：
   - 至少使用5种以上不同颜色
   - 添加文字标签说明(fillText)
   - 显示实时数据(textContent/innerText)

3. **禁止**：
   - 不要使用纯色高亮背景（如亮紫色背景）
   - 避免高饱和度颜色直接相邻
""")

        elif error_type == 'insufficient_interaction':
            prompt_additions.append("""
【交互性严重不足 - 必须添加拖动或点击交互】
模拟器缺少交互性。**至少需要2个拖动或点击交互**：

1. **拖动交互**（推荐）：
   - 使用 mousedown + mousemove + mouseup 事件
   - 示例：拖动一个元素改变位置或参数
   ```javascript
   let dragging = false;
   canvas.addEventListener('mousedown', (e) => {
       dragging = true;
   });
   canvas.addEventListener('mousemove', (e) => {
       if (dragging) {
           // 更新元素位置
       }
   });
   canvas.addEventListener('mouseup', () => {
       dragging = false;
   });
   ```

2. **点击交互**：
   - 使用 click 事件监听器
   - 示例：点击切换状态、点击显示/隐藏元素
   ```javascript
   canvas.addEventListener('click', (e) => {
       // 处理点击
   });
   ```

3. **配合动画**：
   - 交互必须有对应的动画反馈
   - 使用 requestAnimationFrame 实现平滑动画

**要求**：至少实现2个独立的交互元素！
""")

        elif error_type == 'poor_canvas_usage':
            prompt_additions.append("""
【Canvas API使用不足】
Canvas 2D API使用质量不足。请：

1. 增加 Canvas API 调用次数（至少60次 ctx. 调用）
2. 使用多样化的绘图方法：
   - fillRect, strokeRect（矩形）
   - arc（圆形）
   - beginPath, lineTo, stroke（路径）
   - fillText（文字）
   - save, restore（状态保存）

3. 实现动画：
   - function animate() {...}
   - requestAnimationFrame(animate)
   - 使用时间变量实现动态效果
""")

        elif error_type == 'poor_structure':
            prompt_additions.append("""
【HTML结构不完整】
HTML结构存在问题。必须包含：

1. <!DOCTYPE html>
2. 完整的 <html><head><body> 结构
3. <canvas> 元素
4. <style> 样式标签
5. <script> 脚本标签
6. 至少2个 <input type="range"> 控件

代码至少100行。
""")

        elif error_type == 'low_quality_score':
            prompt_additions.append("""
【综合质量不达标】
模拟器整体质量评分过低。请全面提升：

1. 结构完整性（20分）
2. Canvas使用质量（25分）
3. 视觉效果（20分）- 注意配色协调
4. 交互性（20分）- 至少2个拖动或点击交互
5. 教学价值（15分）

目标：总分至少75分（优质85+分）
""")

        elif error_type == 'invalid_api':
            prompt_additions.append("""
【API使用警告 - 严重错误】
你使用了不存在的API！只能使用以下白名单内的API：

【创建元素】
- ctx.createCircle(x, y, radius, color) → 创建圆形
- ctx.createRect(x, y, width, height, color, cornerRadius?) → 创建矩形
- ctx.createLine(points, color, lineWidth?) → 创建线条
- ctx.createText(text, x, y, style?) → 创建文本
- ctx.createCurve(points, color, lineWidth?, smooth?) → 创建曲线
- ctx.createPolygon(points, fillColor, strokeColor?) → 创建多边形

【操作元素】
- ctx.setPosition(id, x, y), ctx.setScale(id, sx, sy), ctx.setRotation(id, angle)
- ctx.setAlpha(id, alpha), ctx.setColor(id, color), ctx.setText(id, text)
- ctx.setVisible(id, visible), ctx.remove(id), ctx.clear()

【变量和属性】
- ctx.getVar('name'), ctx.setVar('name', value)
- ctx.width, ctx.height, ctx.time, ctx.deltaTime, ctx.math

【禁止使用】以下API都不存在：
createArc, drawArc, arc, createJPath, createPath, drawPath, createImage,
drawLine, drawCircle, drawRect, fillRect, strokeRect 等！
如需绘制弧形或路径，请使用 createCurve 配合计算好的点坐标。
""")

        elif error_type == 'unclosed_brackets':
            prompt_additions.append("""
【代码结构警告】
上次生成的代码括号不匹配，可能被截断。请：
1. 减少代码复杂度，控制在80-150行
2. 确保所有 { } ( ) [ ] 正确闭合
3. 在生成代码前先规划好结构
4. 避免过深的嵌套（最多3层）
""")

        elif error_type == 'missing_function':
            prompt_additions.append("""
【代码结构警告 - 缺少必要函数】
你生成的代码缺少必要的函数。模拟器代码必须同时包含两个函数：

1. function setup(ctx) { ... }
   - 初始化所有视觉元素
   - 只在开始时调用一次

2. function update(ctx) { ... }
   - 响应变量变化，更新显示
   - 每帧调用，必须实现！

【完整代码模板】
// 全局变量
let elements = {};

function setup(ctx) {
  // 初始化所有元素
  elements.title = ctx.createText('标题', 500, 30, {fontSize: 24});
  elements.circle = ctx.createCircle(500, 300, 50, '#3498db');
}

function update(ctx) {
  // 读取变量并更新显示
  const value = ctx.getVar('变量名');
  ctx.setPosition(elements.circle, 500, 300 + value);
  ctx.setText(elements.title, '当前值: ' + value.toFixed(1));
}

【重要】setup和update两个函数缺一不可！代码必须完整包含这两个函数！
""")

        elif error_type == 'short_code':
            prompt_additions.append("""
【代码长度不足 - 优先补全内容完整性】
代码行数不足，请按以下优先级补充：

【第一优先：内容完整性】
1. setup() 函数必须完整初始化所有视觉元素
2. update() 函数必须响应所有变量变化
3. 必须包含：标题、图例、变量数值显示
4. 所有变量都要有对应的视觉反馈
5. 核心动画逻辑必须完整实现

【第二优先：功能丰富度】
- 添加参考线、刻度线帮助理解数值
- 添加状态文字说明当前情况
- 关键数值实时显示在图形旁边

【第三优先：视觉质量】
- 使用 ctx.math.lerp 实现平滑过渡
- 添加辅助视觉元素增强表现力

【代码至少80行，确保功能完整】
""")

        elif error_type == 'short_content':
            prompt_additions.append("""
【内容深度不足】
文本内容需要更详细的讲解。请：
1. 每个概念都要有详细解释
2. 包含具体的例子和应用场景
3. 使用清晰的逻辑结构
4. 内容至少200字
""")

        elif error_type == 'insufficient_variables':
            prompt_additions.append("""
【变量定义不足】
模拟器需要足够的交互变量。请：
1. 定义2-3个有意义的变量（不要超过3个）
2. 每个变量必须包含：name, label, min, max, default, step, unit
3. 变量之间应有逻辑关联
4. 变量范围要合理
""")

        elif error_type == 'duplicate_simulator':
            prompt_additions.append("""
【模拟器重复】
此模拟器主题已在前面章节使用。请：
1. 设计一个全新的模拟器主题
2. 展示不同的概念或现象
3. 使用不同的可视化方式
""")

        elif error_type == 'low_contrast':
            prompt_additions.append("""
【颜色对比度警告 - 元素不可见】
你生成的代码使用了深色，与深色背景(#1e293b)融合导致元素不可见。请严格遵守：

【颜色规范】
画布背景是深色(#1e293b)，所有元素必须使用亮色：
- 标题文字：#ffffff（白色）
- 普通文字/标签：#e2e8f0（浅灰白）
- 数值显示：#60a5fa（亮蓝色）
- 主要图形：#3b82f6（蓝）、#22c55e（绿）、#f59e0b（橙）、#ef4444（红）
- 辅助线条：#64748b（中灰色）

【禁止使用的颜色】
- #000000, #111111, #1e293b, #0f172a（黑色/深蓝）
- #222222, #333333, #334155, #374151（深灰）
- 任何亮度低于50%的颜色

【示例】
```javascript
// 正确 - 使用亮色
ctx.createText('标题', 500, 30, { color: '#ffffff' });
ctx.createCircle(300, 300, 50, '#3b82f6');

// 错误 - 使用深色（不可见）
ctx.createText('标题', 500, 30, { color: '#000000' });
ctx.createCircle(300, 300, 50, '#1e293b');
```
""")

        elif error_type == 'out_of_bounds':
            prompt_additions.append("""
【画布边界警告 - 元素超出画布】
你生成的代码中有元素超出了画布边界。请严格遵守：

【边界约束 - 使用比例计算】
- 画布尺寸通过 ctx.width / ctx.height 获取，不同端尺寸不同
- 安全区域：x 在 [width*0.12, width*0.95]，y 在 [55, height-35]
- 所有坐标必须用 width/height 比例计算，禁止硬编码绝对坐标
- 数据面板不要贴右边界，放在 width*0.85 以内

【坐标限制】
所有动态坐标必须使用 math.clamp 限制范围：
```javascript
// 示例：限制坐标在安全区域内
const safeX = math.clamp(calculatedX, width*0.12, width*0.95);
const safeY = math.clamp(calculatedY, 55, height - 35);
ctx.setPosition(elementId, safeX, safeY);
```

【文字显示约束】
- 左对齐文字：x >= width*0.12
- 居中文字：x = width/2
- 右对齐文字：x <= width*0.9
- 长文字要考虑宽度，避免超出右边界

【主要内容区域】
建议将所有主要元素放置在：x: width*0.12 ~ width*0.95, y: 55 ~ height-35
""")

        # 添加历史错误分析
        if previous_errors:
            error_types = [e.get('error_type') for e in previous_errors if e.get('error_type')]
            if len(set(error_types)) < len(error_types):
                # 有重复错误
                prompt_additions.append("""
【警告 - 重复错误】
你多次犯了相同的错误。请仔细阅读上述指导，确保这次不再出现同样的问题。
""")

        return '\n'.join(prompt_additions)

    async def get_revision_or_regenerate_decision(
        self,
        state: GenerationState,
        chapter: ChapterResult,
        step_index: int,
        check_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        让AI决定是修改还是重新生成（用户要求的新功能）

        Returns:
            {
                'decision': 'revise' | 'regenerate',
                'reason': str,
                'revision_plan': str  # 如果选择修改，提供修改计划
            }
        """
        step = chapter.script[step_index]
        issues = check_result.get('issues', [])

        prompt = f"""作为课程生成监督者，你需要决定如何处理以下问题。

【当前步骤】
类型：{step.type}
标题：{step.title}

【发现的问题】
{chr(10).join(f'- {issue}' for issue in issues)}

【选项】
1. 修改（revise）：在现有基础上修改，保留好的部分
2. 重新生成（regenerate）：完全重新生成这个步骤

请分析问题的严重程度，选择最合适的处理方式。

以JSON格式输出：
{{
    "decision": "revise" 或 "regenerate",
    "reason": "选择这个方案的原因",
    "revision_plan": "如果选择修改，说明具体要修改什么（选择重新生成则留空）"
}}
"""

        try:
            response = await self.claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt="你是一位课程质量监督专家，擅长判断内容问题的最佳解决方案。",
                max_tokens=500
            )

            # 解析响应
            json_str = response
            if '{' in response:
                start = response.index('{')
                end = response.rindex('}') + 1
                json_str = response[start:end]

            result = json.loads(json_str)
            return {
                'decision': result.get('decision', 'regenerate'),
                'reason': result.get('reason', ''),
                'revision_plan': result.get('revision_plan', '')
            }
        except Exception as e:
            logger.warning(f"Failed to get AI decision: {e}")
            # 默认根据问题数量决定
            return {
                'decision': 'revise' if len(issues) <= 2 else 'regenerate',
                'reason': '基于问题数量的默认决策',
                'revision_plan': ''
            }

    def _get_visualization_recommendations(
        self,
        state: GenerationState,
        chapter_outline: ChapterOutline
    ) -> str:
        """
        生成可视化元素和配色推荐（基于标准文档）

        Args:
            state: 生成状态
            chapter_outline: 章节大纲

        Returns:
            推荐信息的文本
        """
        try:
            # 识别学科（基于课程标题和关键词）
            subject = self._detect_subject(state.course_title, chapter_outline.key_concepts)

            # 获取学科配色方案
            color_scheme = self.standards_loader.get_subject_color_scheme(subject)

            # 获取推荐的可视化元素
            viz_elements = self.standards_loader.get_recommended_elements_for_subject(subject)

            # 构建推荐文本
            recommendation = f"""
【可视化设计推荐】（基于学科：{subject}）

=== 配色方案 ===
学科：{color_scheme.get('name', subject)}
设计理念：{color_scheme.get('philosophy', '严谨专业的学科配色')}

主色：{color_scheme.get('primary', '#3B82F6')}
次色：{color_scheme.get('secondary', '#10B981')}
强调色：{color_scheme.get('accent', '#F59E0B')}
成功色：{color_scheme.get('success', '#10B981')}
警告色：{color_scheme.get('danger', '#EF4444')}
中性色：{color_scheme.get('neutral', '#6B7280')}
高亮色：{color_scheme.get('highlight', '#FBBF24')}

特定用途颜色：
"""
            # 添加use_cases中的颜色
            use_cases = color_scheme.get('use_cases', {})
            for use_case, color in list(use_cases.items())[:6]:  # 只显示前6个
                recommendation += f"  - {use_case}: {color}\n"

            recommendation += """
=== 推荐可视化元素 ===
"""
            # 添加每个推荐元素的说明
            if viz_elements:
                for elem_id in viz_elements[:5]:  # 只显示前5个
                    elem = self.standards_loader.get_visualization_element(elem_id)
                    if elem:
                        recommendation += f"- {elem.get('name', elem_id)}（{elem_id}）: {elem.get('description', '可视化元素')}\n"
            else:
                recommendation += "- 使用圆形、矩形、线条等基础图形\n- 添加文字标签和数据显示\n- 实现交互控制和动画效果\n"

            recommendation += """
=== 画布约束（重要）===
- 画布尺寸由 ctx.width 和 ctx.height 动态获取，不同端尺寸不同
- 所有坐标必须使用比例计算，如: x = width * 0.5, y = height * 0.3
- 安全绘制区域: x在[width*0.12, width*0.95], y在[55, height-35]
- 动态坐标必须用 ctx.math.clamp() 限制范围
- 禁止硬编码绝对坐标（如 x=500），否则在不同端会超出边界

=== 视觉质量要求 ===
- 颜色对比度 >= 4.5:1（背景是深色#1e293b，元素必须使用亮色）
- 禁止使用深色（#000000, #111111, #1e293b等），否则元素不可见
- 使用缓动函数实现平滑动画（推荐 easeOutBack, easeInOutElastic）
- 每个视觉元素要有明确的教学意义

"""
            return recommendation

        except Exception as e:
            logger.warning(f"Failed to generate visualization recommendations: {e}")
            # 返回默认推荐
            return """
【可视化设计推荐】

=== 基础配色 ===
主色：#3B82F6（蓝色）
次色：#10B981（绿色）
强调色：#F59E0B（橙色）

=== 推荐元素 ===
- 使用圆形、矩形、线条等基础图形组合
- 添加文字标签说明
- 实现平滑动画效果

"""

    def _detect_subject(self, course_title: str, key_concepts: List[str]) -> str:
        """
        识别课程所属学科

        Args:
            course_title: 课程标题
            key_concepts: 核心概念列表

        Returns:
            学科ID（physics, chemistry, biology, mathematics, etc.）
        """
        # 将标题和概念合并
        text = f"{course_title} {' '.join(key_concepts)}".lower()

        # 学科关键词映射
        subject_keywords = {
            'physics': ['物理', '力学', '运动', '能量', '电磁', '光学', 'physics', 'force', 'motion', 'energy'],
            'chemistry': ['化学', '反应', '分子', '原子', '化合', 'chemistry', 'reaction', 'molecule', 'atom'],
            'biology': ['生物', '细胞', '基因', '进化', '生态', 'biology', 'cell', 'gene', 'evolution', '生命'],
            'mathematics': ['数学', '函数', '方程', '几何', '代数', 'math', 'function', 'equation', 'geometry'],
            'history': ['历史', '朝代', '事件', '文化', 'history', 'dynasty', 'event', '年代'],
            'geography': ['地理', '地形', '气候', '地球', 'geography', 'terrain', 'climate', 'earth'],
            'computer_science': ['编程', '算法', '计算机', '代码', 'programming', 'algorithm', 'computer', 'code'],
            'medicine': ['医学', '疾病', '治疗', '人体', 'medicine', 'disease', 'treatment', 'anatomy']
        }

        # 计算每个学科的匹配分数
        scores = {}
        for subject, keywords in subject_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[subject] = score

        # 返回得分最高的学科，如果没有匹配则返回physics作为默认
        if scores:
            return max(scores, key=scores.get)
        else:
            return 'physics'

    def recommend_interaction_types(
        self,
        simulator_name: str,
        simulator_description: str,
        variables: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        为模拟器推荐合适的交互类型

        Args:
            simulator_name: 模拟器名称
            simulator_description: 模拟器描述
            variables: 变量列表

        Returns:
            推荐的交互类型列表（包含详细信息）
        """
        try:
            # 加载所有交互类型
            interaction_types = self.standards_loader.get_interaction_types()
            all_types = interaction_types.get('interaction_types', [])

            # 基础推荐：slider（变量控制）- 所有模拟器都需要
            recommended = []

            # 分析文本关键词
            text = f"{simulator_name} {simulator_description}".lower()

            # 推荐逻辑
            recommendations = {
                'click': ['点击', '选择', '切换', 'click', 'select', 'toggle', '按钮', '开关'],
                'drag': ['拖动', '移动', '位置', 'drag', 'move', 'position', '拖拽'],
                'hover': ['悬停', '提示', '查看', 'hover', 'tooltip', 'info', '详情'],
                'play_pause': ['动画', '播放', '时间', 'animation', 'play', 'time', '演示'],
                'timeline_scrub': ['时间线', '进度', '历史', 'timeline', 'progress', 'history', '演变'],
                'pinch_zoom': ['缩放', '放大', '查看', 'zoom', 'scale', 'view', '细节'],
                'rotate': ['旋转', '3d', '视角', 'rotate', '3d', 'angle', '角度'],
                'key_press': ['键盘', '控制', '快捷', 'keyboard', 'control', 'shortcut'],
                'dropdown_select': ['模式', '类型', '选项', 'mode', 'type', 'option', '切换'],
                'text_input': ['输入', '参数', '搜索', 'input', 'parameter', 'search', '自定义']
            }

            for type_id, keywords in recommendations.items():
                if any(kw in text for kw in keywords):
                    type_info = self.standards_loader.get_interaction_type(type_id)
                    if type_info:
                        recommended.append({
                            'id': type_id,
                            'name': type_info['name'],
                            'description': type_info['description'],
                            'difficulty': type_info['difficulty'],
                            'priority': 'recommended'
                        })

            # 如果没有推荐，添加默认的基础交互
            if not recommended:
                for default_id in ['click', 'hover']:
                    type_info = self.standards_loader.get_interaction_type(default_id)
                    if type_info:
                        recommended.append({
                            'id': default_id,
                            'name': type_info['name'],
                            'description': type_info['description'],
                            'difficulty': type_info['difficulty'],
                            'priority': 'default'
                        })

            # 限制推荐数量（最多3个）
            return recommended[:3]

        except Exception as e:
            logger.warning(f"Failed to recommend interaction types: {e}")
            return []

    def generate_interaction_recommendation_text(
        self,
        simulator_name: str,
        simulator_description: str,
        variables: List[Dict[str, Any]]
    ) -> str:
        """
        生成交互方式推荐的文本（用于提示词）

        Args:
            simulator_name: 模拟器名称
            simulator_description: 模拟器描述
            variables: 变量列表

        Returns:
            推荐文本
        """
        recommendations = self.recommend_interaction_types(
            simulator_name,
            simulator_description,
            variables
        )

        if not recommendations:
            return ""

        text = "\n【推荐交互方式】\n"
        text += "基于模拟器特性，推荐以下交互方式：\n\n"

        for rec in recommendations:
            text += f"- **{rec['name']}** ({rec['id']})：{rec['description']}\n"
            text += f"  难度：{rec['difficulty']}，优先级：{rec['priority']}\n"

        text += "\n提示：可根据实际需求选择1-2种交互方式，保持界面简洁。\n"

        return text

    async def evaluate_aesthetic_quality(
        self,
        code: str,
        simulator_name: str,
        subject: str = 'physics'
    ) -> Dict[str, Any]:
        """
        评估模拟器代码的美学质量

        Args:
            code: 模拟器代码
            simulator_name: 模拟器名称
            subject: 学科

        Returns:
            {
                'overall_score': 0-100,
                'color_score': 0-25,
                'composition_score': 0-25,
                'animation_score': 0-25,
                'refinement_score': 0-25,
                'issues': List[str],
                'suggestions': List[str]
            }
        """
        try:
            score = {
                'overall_score': 0,
                'color_score': 0,
                'composition_score': 0,
                'animation_score': 0,
                'refinement_score': 0,
                'issues': [],
                'suggestions': []
            }

            # === 1. 配色评估 (0-25分) ===
            color_scheme = self.standards_loader.get_subject_color_scheme(subject)
            recommended_colors = [
                color_scheme['base_colors']['primary'],
                color_scheme['base_colors']['secondary'],
                color_scheme['base_colors']['accent']
            ]

            # 检查是否使用了推荐配色
            colors_used = 0
            for color in recommended_colors:
                if color.lower() in code.lower():
                    colors_used += 1

            score['color_score'] = min(25, colors_used * 8)

            # 检查是否使用了深色（不可见）
            forbidden_colors = ['#000000', '#111111', '#1e293b', '#0f172a', '#1a1a1a']
            for dark_color in forbidden_colors:
                if dark_color in code:
                    score['issues'].append(f"使用了深色{dark_color}，在深色背景下不可见")
                    score['color_score'] -= 10

            # 检查对比度
            if '#ffffff' in code or '#e2e8f0' in code or '#f8fafc' in code:
                score['color_score'] += 5  # 有亮色文字

            # === 2. 构图评估 (0-25分) ===
            # 检查是否有标题
            if 'title' in code.lower() or '标题' in code:
                score['composition_score'] += 5
            else:
                score['issues'].append("缺少标题")

            # 检查是否有图例或状态面板
            if 'legend' in code.lower() or 'panel' in code.lower() or '图例' in code or '面板' in code:
                score['composition_score'] += 5
            else:
                score['issues'].append("缺少图例或状态面板")

            # 检查是否有足够的文字标注
            text_count = code.count('createText')
            if text_count >= 6:
                score['composition_score'] += 10
            elif text_count >= 3:
                score['composition_score'] += 5
            else:
                score['issues'].append(f"文字标注太少（{text_count}个）")

            # 检查层次感
            if code.count('createCircle') + code.count('createRect') >= 10:
                score['composition_score'] += 5

            # === 3. 动画评估 (0-25分) ===
            # 检查是否使用了缓动函数
            easing_functions = ['lerp', 'easeIn', 'easeOut', 'easeInOut', 'easeOutBack']
            has_easing = any(ease in code for ease in easing_functions)

            if has_easing:
                score['animation_score'] += 10
                score['suggestions'].append("很好地使用了缓动函数")
            else:
                score['issues'].append("建议使用缓动函数（lerp, easeOut等）实现平滑动画")

            # 检查动画类型
            animation_types = 0
            if 'setPosition' in code or '.x =' in code or '.y =' in code:
                animation_types += 1
            if 'setColor' in code or 'setAlpha' in code:
                animation_types += 1
            if 'setScale' in code or 'setRotation' in code:
                animation_types += 1
            if 'setGlow' in code:
                animation_types += 1

            score['animation_score'] += min(10, animation_types * 3)

            # 检查时间驱动动画
            if 'ctx.time' in code or 'math.sin' in code or 'math.cos' in code:
                score['animation_score'] += 5

            # === 4. 精致度评估 (0-25分) ===
            # 检查圆角使用
            if 'cornerRadius' in code:
                score['refinement_score'] += 5
                score['suggestions'].append("使用了圆角，视觉更柔和")
            else:
                score['suggestions'].append("建议为矩形添加圆角（cornerRadius）")

            # 检查发光效果
            if 'setGlow' in code:
                score['refinement_score'] += 5
                score['suggestions'].append("使用了发光效果，增强视觉吸引力")

            # 检查代码组织
            if '// ===' in code or '// ---' in code or code.count('\n\n') >= 3:
                score['refinement_score'] += 5

            # 检查变量命名
            import re
            var_names = re.findall(r'\b(?:let|const)\s+(\w+)', code)
            meaningful = sum(1 for name in var_names if len(name) > 2 and not name.startswith('_'))
            if meaningful >= 8:
                score['refinement_score'] += 5

            # 检查注释
            comment_count = code.count('//') + code.count('/*')
            if comment_count >= 6:
                score['refinement_score'] += 5
            elif comment_count < 3:
                score['issues'].append("注释太少")

            # === 计算总分 ===
            score['color_score'] = max(0, min(25, score['color_score']))
            score['composition_score'] = max(0, min(25, score['composition_score']))
            score['animation_score'] = max(0, min(25, score['animation_score']))
            score['refinement_score'] = max(0, min(25, score['refinement_score']))

            score['overall_score'] = (
                score['color_score'] +
                score['composition_score'] +
                score['animation_score'] +
                score['refinement_score']
            )

            # 生成总体建议
            if score['overall_score'] >= 80:
                score['suggestions'].insert(0, "✓ 美学质量优秀，视觉呈现精致")
            elif score['overall_score'] >= 60:
                score['suggestions'].insert(0, "良好，但仍有提升空间")
            else:
                score['suggestions'].insert(0, "需要改进视觉设计")

            return score

        except Exception as e:
            logger.error(f"Failed to evaluate aesthetic quality: {e}")
            return {
                'overall_score': 0,
                'color_score': 0,
                'composition_score': 0,
                'animation_score': 0,
                'refinement_score': 0,
                'issues': [str(e)],
                'suggestions': []
            }
