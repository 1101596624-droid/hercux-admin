# ============================================
# processors/ca_ela.py - 加州英语语文 ELA/ELD 框架处理器
# ============================================
# 基于 California ELA/ELD Framework
# Activate → Interact → Collaborate → Extend → Reflect
# 参考: https://www.cde.ca.gov/ci/rl/cf/
# 核心理念: Meaning Making, Language Development, Content Knowledge,
#           Effective Expression, Foundational Skills

from typing import Dict, List, Any, Optional

from .base import BaseProcessor, ProcessorInfo, ProcessorRegistry
from .intelligent import ContentAnalysis, TeachingFormType


@ProcessorRegistry.register
class CAELAProcessor(BaseProcessor):
    """
    加州 ELA/ELD 框架处理器

    California ELA/ELD Framework 核心主题:
    - Meaning Making (意义建构): 通过阅读和倾听理解文本
    - Language Development (语言发展): 发展学术语言能力
    - Effective Expression (有效表达): 通过写作和口语表达思想
    - Content Knowledge (内容知识): 通过文本获取学科知识
    - Foundational Skills (基础技能): 阅读流畅性和词汇

    教学流程: Activate → Interact → Collaborate → Extend → Reflect
    适用: 语文、英语、文学、写作、阅读理解
    """

    processor_info = ProcessorInfo(
        id="ca_ela",
        name="CA ELA/ELD Framework",
        description="加州ELA框架：激活背景→深度阅读→协作探讨→拓展表达→反思评估",
        version="1.0.0",
        author="HERCU Studio",
        tags=["加州标准", "ELA", "语文", "阅读", "写作", "批判性思维"],
        color="#F59E0B",
        icon="book-open",
    )

    PHASES = [
        {
            "phase": "activate",
            "label": "Activate 激活背景",
            "step_type": "text_content",
            "purpose": "激活先验知识，建立文本背景，设定阅读目的，引入关键词汇",
            "prompt_guidance": "用一个与文本主题相关的问题或情境开场。介绍文本背景(作者、时代、体裁)。预教3-5个关键学术词汇。设定明确的阅读目的(Reading Purpose)。",
        },
        {
            "phase": "interact",
            "label": "Interact 深度阅读",
            "step_type": "illustrated_content",
            "purpose": "Close Reading精读策略，标注文本结构，分析修辞手法，可视化文本组织",
            "prompt_guidance": "引导Close Reading精读：(1)首读理解大意 (2)再读分析结构和修辞 (3)三读评价和批判。配合文本结构图(如故事山、论证结构图、因果链)帮助理解。标注关键段落和修辞手法。",
        },
        {
            "phase": "collaborate",
            "label": "Collaborate 协作探讨",
            "step_type": "ai_tutor",
            "purpose": "AI模拟学术讨论(Academic Discussion)，引导批判性思维和文本分析",
            "prompt_guidance": "AI导师引导学术讨论，使用Accountable Talk策略：(1)你认为作者的主要观点是什么？证据在哪里？(2)你同意作者的观点吗？为什么？(3)这个文本和你的经历有什么联系？(4)如果换一个视角，这个故事会怎样？培养Text-Dependent Analysis能力。",
        },
        {
            "phase": "extend",
            "label": "Extend 拓展表达",
            "step_type": "text_content",
            "purpose": "写作或口语表达任务，将阅读理解转化为有效的语言产出",
            "prompt_guidance": "设计一个与文本相关的写作/表达任务。可以是：(1)议论文：对文本观点发表看法 (2)分析文：分析文本的修辞策略 (3)创意写作：改写结局或换视角重述 (4)比较文：与另一文本对比。提供写作框架(Writing Frame)和评分标准(Rubric)。",
        },
        {
            "phase": "reflect",
            "label": "Reflect 反思评估",
            "step_type": "assessment",
            "purpose": "自我评估和元认知反思，检测阅读理解深度和语言运用能力",
            "prompt_guidance": "设计多层次评估：(1)文本理解题(Key Ideas & Details) (2)文本分析题(Craft & Structure) (3)知识整合题(Integration of Knowledge)。至少1道开放性问题要求学生引用文本证据(Text Evidence)支持观点。",
        },
    ]

    def analyze_content(self, content: str, context: Dict[str, Any] = None) -> ContentAnalysis:
        context = context or {}
        content_lower = content.lower()

        has_literature = any(kw in content_lower for kw in ["小说", "诗歌", "散文", "戏剧", "fiction", "poetry"])
        has_nonfiction = any(kw in content_lower for kw in ["议论", "说明", "新闻", "演讲", "nonfiction"])
        has_writing = any(kw in content_lower for kw in ["写作", "作文", "表达", "writing", "essay"])

        complexity = "standard"
        if has_literature and has_writing:
            complexity = "advanced"

        return ContentAnalysis(
            has_dynamic_process=False,
            has_structural_relationship=True,
            requires_hands_on_practice=has_writing,
            has_common_misconceptions=True,
            needs_personalized_guidance=True,
            is_gateway_to_next=True,
            complexity_level=complexity,
            recommended_forms=self.recommend_forms(None),
            rationale="CA ELA Framework: 激活背景→深度阅读→协作探讨→拓展表达→反思评估",
        )

    def recommend_forms(self, analysis: Any) -> List[str]:
        return [p["step_type"] for p in self.PHASES]

    def build_structure_prompt(
        self, source_material: str, course_title: str, context: Dict[str, Any] = None
    ) -> str:
        context = context or {}
        return f"""你是一位精通加州ELA/ELD框架的语文/英语课程设计师。

【课程标题】
{course_title}

【源素材】
{source_material}

【CA ELA/ELD Framework 核心主题】
1. Meaning Making (意义建构): 通过阅读理解文本深层含义
2. Language Development (语言发展): 发展学术语言和词汇
3. Effective Expression (有效表达): 写作和口语表达
4. Content Knowledge (内容知识): 通过文本获取知识
5. Foundational Skills (基础技能): 阅读流畅性

【教学流程】
每个课时遵循: Activate(激活) → Interact(阅读) → Collaborate(讨论) → Extend(表达) → Reflect(反思)

【Common Core ELA Standards 锚定标准】
- Reading: Key Ideas, Craft & Structure, Integration of Knowledge
- Writing: Arguments, Informative, Narrative, Research
- Speaking & Listening: Comprehension, Presentation
- Language: Conventions, Vocabulary

【输出格式】
```json
{{
  "title": "课程标题",
  "description": "课程描述",
  "estimated_hours": 预计学时,
  "lessons": [
    {{
      "title": "课时标题",
      "summary": "课时摘要",
      "learning_objectives": ["学习目标1", "学习目标2"],
      "text_type": "文本类型(narrative/informational/argumentative/poetry)",
      "ela_strand": "ELA领域(reading/writing/speaking/language)",
      "key_vocabulary": ["核心词汇1", "核心词汇2"],
      "recommended_forms": ["text_content", "illustrated_content", "ai_tutor", "text_content", "assessment"],
      "complexity_level": "simple/standard/advanced",
      "prerequisites": [],
      "estimated_minutes": 预计时长
    }}
  ]
}}
```
"""

    def build_lesson_prompt(
        self, source_material: str, course_title: str, lesson_info: Dict[str, Any],
        lesson_index: int, total_lessons: int, previous_summary: str = "",
        context: Dict[str, Any] = None,
    ) -> str:
        context = context or {}
        text_type = lesson_info.get("text_type", "")
        ela_strand = lesson_info.get("ela_strand", "")
        key_vocab = lesson_info.get("key_vocabulary", [])

        phase_instructions = "\n".join([
            f"**Step {i+1}: {p['label']}** (type: {p['step_type']})\n"
            f"  目的: {p['purpose']}\n"
            f"  要求: {p['prompt_guidance']}"
            for i, p in enumerate(self.PHASES)
        ])

        return f"""你是一位精通加州ELA/ELD框架的语文教师。请为以下课时生成完整的教学内容。

【课程信息】
- 课程标题：{course_title}
- 当前课时：第 {lesson_index + 1} 课 / 共 {total_lessons} 课
- 课时标题：{lesson_info.get('title', '')}
- 学习目标：{', '.join(lesson_info.get('learning_objectives', []))}
- 文本类型：{text_type}
- ELA领域：{ela_strand}
- 核心词汇：{', '.join(key_vocab) if key_vocab else '待定'}

【上一课时摘要】
{previous_summary if previous_summary else "（这是第一课）"}

【源素材】
{source_material}

【教学阶段详细要求】
{phase_instructions}

【输出格式】
```json
{{
  "title": "课时标题",
  "rationale": "CA ELA Framework教学设计理念",
  "learning_objectives": ["目标1", "目标2"],
  "complexity_level": "standard",
  "estimated_minutes": 预计时长,
  "script": [
    {{
      "step_id": "S001",
      "type": "text_content",
      "title": "Activate: [背景激活]",
      "content": {{
        "body": "背景介绍和词汇预教...",
        "key_points": ["关键词汇1及释义", "关键词汇2及释义"]
      }}
    }},
    {{
      "step_id": "S002",
      "type": "illustrated_content",
      "title": "Interact: [深度阅读]",
      "content": {{"body": "Close Reading精读引导...", "key_points": []}},
      "diagram_spec": {{
        "diagram_id": "DIAG-001",
        "type": "flowchart",
        "description": "文本结构可视化图"
      }}
    }},
    {{
      "step_id": "S003",
      "type": "ai_tutor",
      "title": "Collaborate: [学术讨论]",
      "ai_spec": {{
        "opening_message": "让我们一起深入讨论这篇文本...",
        "probing_questions": [],
        "diagnostic_focus": {{"key_concepts": [], "common_misconceptions": []}},
        "max_turns": 6
      }}
    }},
    {{
      "step_id": "S004",
      "type": "text_content",
      "title": "Extend: [写作表达]",
      "content": {{
        "body": "写作任务说明和框架...",
        "key_points": ["写作要求1", "写作要求2"]
      }}
    }},
    {{
      "step_id": "S005",
      "type": "assessment",
      "title": "Reflect: [反思评估]",
      "assessment_spec": {{
        "type": "quick_check",
        "questions": [],
        "pass_required": true
      }}
    }}
  ],
  "summary": "本课时摘要"
}}
```

【关键原则】
1. Activate要预教关键学术词汇，设定阅读目的
2. Interact要引导Close Reading，不是简单概括
3. Collaborate的AI讨论要求学生引用Text Evidence
4. Extend的写作任务要提供Writing Frame
5. Reflect要覆盖理解、分析、整合三个层次
"""

    def get_style_prompt(self) -> str:
        return """使用加州ELA/ELD框架风格：
- Activate: 激活背景知识，预教学术词汇
- Interact: Close Reading精读，分析文本结构和修辞
- Collaborate: 学术讨论，Text-Dependent Analysis
- Extend: 写作/表达任务，提供Writing Frame
- Reflect: 多层次评估，要求Text Evidence
- 贯穿Meaning Making和Language Development"""

    def process_lesson(self, raw_lesson: Dict[str, Any], lesson_info: Dict[str, Any]) -> Dict[str, Any]:
        script = raw_lesson.get("script", [])
        phase_labels = ["Activate", "Interact", "Collaborate", "Extend", "Reflect"]
        for i, step in enumerate(script[:5]):
            if i < len(phase_labels) and not step.get("title", "").startswith(phase_labels[i]):
                step["title"] = f"{phase_labels[i]}: {step.get('title', '')}"
        return raw_lesson
