"""
Studio Generation Service - AI-powered course generation
"""

import json
import uuid
import asyncio
import logging
import re
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from app.core.config import settings
from app.services.llm_factory import get_llm_service, Message
from app.services.gemini_service import gemini_service
from app.services.storage_service import storage_service
from app.services.studio.templates import get_template, ALL_TEMPLATES
from app.services.studio.sdl_compiler import SDLCompiler, SDLValidator, SDLAutoFixer
from app.services.studio.validators import validate_simulator_spec, get_fix_prompt

logger = logging.getLogger(__name__)


# Default processors
DEFAULT_PROCESSORS = [
    {
        "id": "default",
        "name": "通用课程",
        "description": "适用于大多数主题的通用课程生成器，平衡理论与实践",
        "version": "1.0.0",
        "author": "HERCU Team",
        "tags": ["official", "general"],
        "color": "#3B82F6",
        "icon": "Sparkles",
        "enabled": True,
        "display_order": 0,
        "is_official": True,
        "is_custom": False,
        "system_prompt": """你是一位专业的课程设计师。根据提供的源材料，创建结构化的课程内容。

课程设计原则：
1. 循序渐进：从基础概念到高级应用
2. 理论与实践结合：每个概念都配有实际例子
3. 互动性：包含测验和练习
4. 清晰的学习目标：每节课都有明确的学习成果

输出格式要求：严格按照JSON格式输出课程结构。"""
    },
    {
        "id": "academic",
        "name": "学术深度",
        "description": "适合学术研究和深度学习，强调理论基础和批判性思维",
        "version": "1.0.0",
        "author": "HERCU Team",
        "tags": ["official", "academic"],
        "color": "#8B5CF6",
        "icon": "GraduationCap",
        "enabled": True,
        "display_order": 1,
        "is_official": True,
        "is_custom": False,
        "system_prompt": """你是一位学术课程设计专家。创建具有学术深度的课程内容。

学术课程特点：
1. 严谨的理论框架
2. 引用和参考文献
3. 批判性思维训练
4. 研究方法论介绍
5. 深度案例分析

输出格式要求：严格按照JSON格式输出课程结构。"""
    },
    {
        "id": "practical",
        "name": "实战导向",
        "description": "注重实际应用和动手能力，适合技能培训",
        "version": "1.0.0",
        "author": "HERCU Team",
        "tags": ["official", "practical"],
        "color": "#10B981",
        "icon": "Wrench",
        "enabled": True,
        "display_order": 2,
        "is_official": True,
        "is_custom": False,
        "system_prompt": """你是一位实战培训专家。创建以实践为导向的课程内容。

实战课程特点：
1. 项目驱动学习
2. 大量动手练习
3. 真实场景模拟
4. 即学即用的技能
5. 常见问题和解决方案

输出格式要求：严格按照JSON格式输出课程结构。"""
    }
]


class StudioGenerationService:
    """Studio course generation service"""

    def __init__(self):
        self.claude_service = get_llm_service()

    async def generate_course_stream(
        self,
        course_title: str,
        source_material: str,
        source_info: str,
        processor_id: str,
        processor_prompt: Optional[str] = None,
        resume_from_lesson: Optional[int] = None,
        completed_lessons: Optional[List[Any]] = None,
        lessons_outline: Optional[List[Any]] = None,
        existing_meta: Optional[Any] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream course generation with SSE events

        Yields SSE events:
        - phase: Generation phase update
        - structure: Course structure (meta, outline)
        - lesson_start: Starting a new lesson
        - chunk: Content chunk
        - lesson_complete: Lesson completed
        - complete: Generation complete
        - error: Error occurred
        """
        try:
            # Phase 1: Analyzing source material
            yield {
                "event": "phase",
                "data": {
                    "phase": 1,
                    "message": "正在分析源材料...",
                    "processor": {"id": processor_id}
                }
            }

            # Get processor system prompt
            system_prompt = processor_prompt or self._get_default_processor_prompt(processor_id)

            # If resuming, skip structure generation
            if resume_from_lesson is not None and lessons_outline and existing_meta:
                meta = existing_meta
                outline = lessons_outline
                total_lessons = len(outline)
            else:
                # Generate course structure
                yield {
                    "event": "phase",
                    "data": {
                        "phase": 1,
                        "message": "正在生成课程结构...",
                        "processor": {"id": processor_id}
                    }
                }

                structure = await self._generate_course_structure(
                    course_title, source_material, source_info, system_prompt
                )

                meta = structure.get("meta", {})
                outline = structure.get("lessons_outline", [])
                total_lessons = len(outline)

                # Emit structure event
                yield {
                    "event": "structure",
                    "data": {
                        "meta": meta,
                        "lessons_count": total_lessons,
                        "lessons_outline": outline,
                        "processor": {"id": processor_id}
                    }
                }

            # Phase 2: Generating lessons
            yield {
                "event": "phase",
                "data": {
                    "phase": 2,
                    "message": "正在生成课时内容...",
                    "processor": {"id": processor_id}
                }
            }

            # Determine starting lesson
            start_lesson = resume_from_lesson if resume_from_lesson is not None else 0
            all_lessons = list(completed_lessons) if completed_lessons else []

            # Check if all lessons are already completed
            if start_lesson >= total_lessons and all_lessons:
                logger.info(f"All {total_lessons} lessons already completed, skipping generation")
            else:
                # Generate each lesson
                for i in range(start_lesson, total_lessons):
                    lesson_outline = outline[i] if i < len(outline) else {"title": f"课时 {i+1}"}

                    # Emit lesson start
                    yield {
                        "event": "lesson_start",
                        "data": {
                            "index": i,
                            "total": total_lessons,
                            "title": lesson_outline.get("title", f"课时 {i+1}"),
                            "recommended_forms": lesson_outline.get("recommended_forms", []),
                            "complexity_level": lesson_outline.get("complexity_level", "standard")
                        }
                    }

                    # Generate lesson content with streaming chunks
                    full_response = ""
                    async for chunk in self._generate_lesson_stream(
                        course_title=course_title,
                        source_material=source_material,
                        lesson_outline=lesson_outline,
                        lesson_index=i,
                        total_lessons=total_lessons,
                        system_prompt=system_prompt,
                        previous_lessons=all_lessons
                    ):
                        full_response += chunk
                        # Yield chunk event for typewriter effect
                        yield {
                            "event": "chunk",
                            "data": {
                                "content": chunk,
                                "phase": 2,
                                "lesson_index": i
                            }
                        }

                    # Parse the complete response
                    lesson = self._parse_lesson_json(full_response, lesson_outline, i)

                    # Validate and enrich lesson content
                    lesson = await self._validate_and_enrich_lesson(
                        lesson, course_title, source_material, system_prompt
                    )

                    # Stream each step as it's generated
                    for step_idx, step in enumerate(lesson.get("script", [])):
                        yield {
                            "event": "step_complete",
                            "data": {
                                "lesson_index": i,
                                "step_index": step_idx,
                                "step": step,
                                "total_steps": len(lesson.get("script", []))
                            }
                        }

                    all_lessons.append(lesson)

                    # Emit lesson complete
                    yield {
                        "event": "lesson_complete",
                        "data": {
                            "index": i,
                            "total": total_lessons,
                            "lesson": lesson
                        }
                    }

            # Generate edges between lessons
            edges = self._generate_edges(all_lessons)

            # AI 评估课程难度
            yield {
                "event": "phase",
                "data": {
                    "phase": 3,
                    "message": "正在评估课程难度...",
                    "processor": {"id": processor_id}
                }
            }
            difficulty = await self._evaluate_course_difficulty(
                course_title, all_lessons, source_material
            )

            # Build final package
            package_id = str(uuid.uuid4())
            package = {
                "id": package_id,
                "version": "2.0.0",
                "meta": {
                    "title": course_title,
                    "description": meta.get("description", ""),
                    "source_info": source_info,
                    "total_lessons": total_lessons,
                    "estimated_hours": sum(l.get("estimated_minutes", 30) for l in all_lessons) / 60,
                    "style": processor_id,
                    "difficulty": difficulty,
                    "created_at": datetime.utcnow().isoformat()
                },
                "lessons": all_lessons,
                "edges": edges,
                "global_ai_config": {
                    "tutor_persona": "专业但友好的导师，善于用生活化的比喻解释复杂概念",
                    "fallback_responses": [
                        "这是个好问题，让我们一起来探讨。",
                        "你的思考很有深度，我来补充一些观点。"
                    ]
                }
            }

            # Emit complete
            yield {
                "event": "complete",
                "data": {
                    "package": package
                }
            }

        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            yield {
                "event": "error",
                "data": {
                    "message": str(e)
                }
            }

    async def _generate_course_structure(
        self,
        course_title: str,
        source_material: str,
        source_info: str,
        system_prompt: str
    ) -> Dict[str, Any]:
        """Generate course structure (meta and outline)"""

        prompt = f"""基于以下源材料，为课程"{course_title}"生成课程结构。

源材料信息：{source_info}

源材料内容（摘要）：
{source_material[:8000]}

请生成课程结构，包括：
1. 课程描述
2. 课时大纲（每个课时的标题、推荐教学形式、复杂度级别）

以JSON格式输出：
{{
    "meta": {{
        "description": "课程描述",
        "estimated_hours": 预估学时数
    }},
    "lessons_outline": [
        {{
            "title": "课时标题",
            "recommended_forms": ["text_content", "simulator", "assessment"],
            "complexity_level": "standard"
        }}
    ]
}}

注意：推荐教学形式只能使用 text_content、simulator、assessment、illustrated_content，不要使用 video。

只输出JSON，不要其他内容。"""

        response = await self.claude_service.generate_raw_response(
            prompt=f"{system_prompt}\n\n{prompt}",
            temperature=0.7,
            max_tokens=4000
        )

        # Parse JSON from response
        try:
            # Try to extract JSON from response
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]

            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            logger.warning("Failed to parse structure JSON, using default")
            return {
                "meta": {
                    "description": f"关于{course_title}的课程",
                    "estimated_hours": 2
                },
                "lessons_outline": [
                    {"title": "课程介绍", "recommended_forms": ["text_content"], "complexity_level": "simple"},
                    {"title": "核心概念", "recommended_forms": ["text_content", "assessment"], "complexity_level": "standard"},
                    {"title": "实践应用", "recommended_forms": ["text_content", "practice"], "complexity_level": "standard"},
                    {"title": "总结与测验", "recommended_forms": ["assessment"], "complexity_level": "simple"}
                ]
            }

    async def _generate_lesson_stream(
        self,
        course_title: str,
        source_material: str,
        lesson_outline: Dict[str, Any],
        lesson_index: int,
        total_lessons: int,
        system_prompt: str,
        previous_lessons: List[Any]
    ) -> AsyncGenerator[str, None]:
        """流式生成单个课时内容"""

        lesson_title = lesson_outline.get("title", f"课时 {lesson_index + 1}")
        recommended_forms = lesson_outline.get("recommended_forms", ["text_content"])
        complexity = lesson_outline.get("complexity_level", "standard")

        # Build detailed context from previous lessons to avoid repetition
        prev_context = ""
        used_simulators = []
        covered_topics = []
        if previous_lessons:
            prev_titles = [l.get("title", "") for l in previous_lessons[-3:]]
            prev_context = f"前面已完成的课时：{', '.join(prev_titles)}\n"

            # Collect used simulators and topics from ALL previous lessons
            for prev_lesson in previous_lessons:
                # Get lesson title as covered topic
                if prev_lesson.get("title"):
                    covered_topics.append(prev_lesson.get("title"))

                # Extract simulators from script
                for step in prev_lesson.get("script", []):
                    if step.get("type") == "simulator":
                        sim_spec = step.get("simulator_spec", {})
                        sim_name = sim_spec.get("name", step.get("title", ""))
                        if sim_name and sim_name not in used_simulators:
                            used_simulators.append(sim_name)
                        # Also track preset IDs
                        preset_id = sim_spec.get("presetId") or sim_spec.get("preset_id")
                        if preset_id and preset_id not in used_simulators:
                            used_simulators.append(preset_id)

            if used_simulators:
                prev_context += f"【已使用的模拟器，请勿重复】：{', '.join(used_simulators)}\n"
            if covered_topics:
                prev_context += f"【已讲解的主题，请勿重复】：{', '.join(covered_topics)}\n"

        # 模板列表
        template_list = """
=== 田径类 ===
- sports_sprint_start: 短跑起跑技术
- sports_jump_approach: J形助跑跳高
- sports_long_jump: 跳远技术分析
- sports_shot_put: 铅球投掷技术
- sports_hurdles: 跨栏技术分析
- sports_relay_race: 接力赛跑技术
- sports_discus_throw: 铁饼投掷技术
- sports_pole_vault: 撑杆跳高技术
- sports_javelin_throw: 标枪投掷技术

=== 球类运动 ===
- sports_basketball_shooting: 篮球投篮技术
- sports_basketball_dunk: 篮球扣篮技术
- sports_football_kick: 足球射门技术
- sports_football_bicycle_kick: 足球倒钩射门技术
- sports_tennis_serve: 网球发球技术
- sports_volleyball_spike: 排球扣球技术
- sports_badminton_smash: 羽毛球扣杀技术
- sports_table_tennis_serve: 乒乓球发球技术
- sports_golf_swing: 高尔夫挥杆技术
- sports_hockey_shot: 曲棍球射门技术

=== 游泳和体操 ===
- sports_swimming_stroke: 游泳泳姿分析
- sports_gymnastics_vault: 体操跳马技术
- sports_gymnastics_floor_flip: 体操自由操空翻技术
- sports_gymnastics_high_bar: 体操单杠大回环技术

=== 武术和格斗 ===
- sports_taekwondo_kick: 跆拳道踢腿技术
- sports_boxing_punch: 拳击出拳技术
- sports_fencing_lunge: 击剑弓步刺技术

=== 冬季运动 ===
- sports_skiing_slalom: 高山滑雪回转技术
- sports_figure_skating_spin: 花样滑冰旋转技术
- sports_figure_skating_jump: 花样滑冰跳跃技术

=== 水上运动 ===
- sports_diving_platform: 跳水技术分析
- sports_diving_twist: 跳水转体技术
- sports_rowing_technique: 赛艇划桨技术

=== 其他运动 ===
- sports_archery_shot: 射箭技术分析
- sports_cycling_sprint: 自行车冲刺技术
- sports_weightlifting_snatch: 举重抓举技术
- sports_yoga_pose: 瑜伽体式分析

=== 物理学 ===
- physics_force_composition: 力的合成与分解
- physics_projectile_motion: 抛体运动分析
- physics_circuit: 电路原理模拟
- physics_pendulum: 单摆运动分析

=== 艺术 ===
- art_color_wheel: 色彩理论模拟
- art_composition: 构图原理模拟
"""
        # 从系统设置获取 AI 生成参数
        from app.core.system_settings import get_course_settings
        course_settings = get_course_settings()
        ai_steps = course_settings.ai_generation_steps
        min_content_len = course_settings.ai_content_min_length

        prompt = f"""为课程"{course_title}"生成第{lesson_index + 1}课时的详细内容。

课时标题：{lesson_title}
推荐教学形式：{', '.join(recommended_forms)}
复杂度级别：{complexity}
{prev_context}

源材料（相关部分）：
{source_material[:6000]}

【生成要求】
- 步骤数量：请生成 {ai_steps} 个左右的步骤
- 每个步骤的正文内容至少 {min_content_len} 字
- 【重要】不要重复前面课时已经讲解过的内容和已使用的模拟器
- 每个课时应该讲解不同的知识点，模拟器应该展示不同的概念

请生成完整的课时内容，以JSON格式输出：
{{
    "lesson_id": "lesson_{lesson_index + 1}",
    "title": "{lesson_title}",
    "order": {lesson_index},
    "total_steps": 步骤数量,
    "rationale": "课时设计理念",
    "script": [
        {{
            "step_id": "step_1",
            "type": "text_content",
            "title": "步骤标题",
            "content": {{
                "body": "正文内容（至少60字，精准讲解该知识点，无废话）",
                "key_points": ["要点1", "要点2"]
            }}
        }},
        {{
            "step_id": "step_2",
            "type": "illustrated_content",
            "title": "图文讲解",
            "content": {{
                "body": "配合图片的文字说明（至少100字）",
                "key_points": ["要点1", "要点2"]
            }},
            "diagram_spec": {{
                "type": "static_diagram",
                "description": "详细描述需要生成的图片内容，包括要展示的元素、布局、颜色等",
                "annotations": [
                    {{"position": "左侧", "text": "标注说明1"}},
                    {{"position": "右侧", "text": "标注说明2"}}
                ],
                "design_notes": "图片设计要求和风格说明"
            }}
        }},
        {{
            "step_id": "step_3",
            "type": "simulator",
            "title": "互动模拟",
            "simulator_spec": {{
                "mode": "custom",
                "name": "模拟器名称",
                "description": "模拟器描述",
                "variables": [
                    {{"name": "speed", "label": "速度", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "m/s"}},
                    {{"name": "amplitude", "label": "振幅", "min": 10, "max": 50, "default": 30, "step": 1, "unit": "px"}}
                ],
                "custom_code": "// 存储元素ID\\nlet elements = {{}};\\n\\nfunction setup(ctx) {{\\n  const {{ width, height }} = ctx;\\n  ctx.createText('标题', width/2, 30, {{fontSize: 24, fontWeight: 'bold', color: '#ffffff'}});\\n  elements.ball = ctx.createCircle(width/2, height/2, 20, '#fbbf24');\\n}}\\n\\nfunction update(ctx) {{\\n  const speed = ctx.getVar('speed');\\n  const amplitude = ctx.getVar('amplitude');\\n  const x = ctx.width/2 + ctx.math.sin(ctx.time * speed * 0.1) * amplitude;\\n  ctx.setPosition(elements.ball, x, ctx.height/2);\\n}}"
            }}
        }},
        {{
            "step_id": "step_4",
            "type": "assessment",
            "title": "知识检测",
            "assessment_spec": {{
                "type": "quick_check",
                "questions": [
                    {{
                        "question": "问题",
                        "options": ["A", "B", "C", "D"],
                        "correct": "A",
                        "explanation": "解释"
                    }}
                ],
                "pass_required": true
            }}
        }}
    ],
    "estimated_minutes": 预估时长,
    "prerequisites": [],
    "learning_objectives": ["学习目标1", "学习目标2"],
    "complexity_level": "{complexity}"
}}

【模拟器设计规范 - 自定义代码模式】

【核心目的】模拟器用于帮助用户理解变量之间的关系！
用户通过拖动滑块改变自变量，观察因变量的变化，从而理解物理概念之间的关系。

【重要】simulator 必须使用 mode: "custom" 和 custom_code 字段！

simulator_spec 必须包含：
1. "mode": "custom" - 必须设置为custom
2. "name": "模拟器名称"
3. "description": "模拟器描述"
4. "variables": 变量数组（用于生成滑块控件）
5. "custom_code": JavaScript代码字符串

【画布规格】800x500像素

【变量定义格式】
"variables": [
  {{"name": "speed", "label": "速度", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "m/s"}},
  {{"name": "amplitude", "label": "振幅", "min": 10, "max": 50, "default": 30, "step": 1, "unit": "px"}}
]

【代码结构要求 - 非常重要】custom_code 必须定义 setup 和 update 函数：

【关键规则】
1. 所有数组变量必须在代码顶部初始化为空数组 []，例如：let nodes = [];
2. 所有对象变量必须在代码顶部初始化为空对象 {{}}，例如：let elements = {{}};
3. 不要使用未定义的变量，所有变量必须先声明再使用
4. 使用 push() 前必须确保数组已初始化

```javascript
// 【必须】在顶部初始化所有变量
let elements = {{}};  // 对象用于存储单个元素ID
let nodes = [];       // 数组用于存储多个元素

function setup(ctx) {{
  const {{ width, height }} = ctx;
  // 创建标题
  ctx.createText('标题', width/2, 30, {{fontSize: 24, fontWeight: 'bold', color: '#ffffff'}});
  // 创建元素并存储ID
  elements.ball = ctx.createCircle(width/2, height/2, 20, '#fbbf24');
  // 创建多个元素时使用数组
  for (let i = 0; i < 5; i++) {{
    const id = ctx.createCircle(100 + i * 50, 200, 10, '#3b82f6');
    nodes.push({{ id, x: 100 + i * 50 }});  // nodes 已在顶部初始化为 []
  }}
}}

function update(ctx) {{
  // 获取变量值
  const speed = ctx.getVar('speed');
  const amplitude = ctx.getVar('amplitude');
  // 计算位置
  const x = ctx.width/2 + ctx.math.sin(ctx.time * speed * 0.1) * amplitude;
  ctx.setPosition(elements.ball, x, ctx.height/2);
}}
```

【可用的 ctx API】

画布信息：
- ctx.width: 800
- ctx.height: 500
- ctx.time: 当前时间（秒）
- ctx.deltaTime: 帧间隔（秒）

创建元素（返回元素ID）：
- ctx.createCircle(x, y, radius, color) - 创建圆形
- ctx.createRect(x, y, width, height, color, cornerRadius?) - 创建矩形
- ctx.createLine(points, color, lineWidth?) - 创建线条，points是{{x,y}}数组
- ctx.createText(text, x, y, style?) - 创建文本，style可选{{fontSize, fontFamily, color, fontWeight, align}}
- ctx.createCurve(points, color, lineWidth?, smooth?) - 创建曲线
- ctx.createPolygon(points, fillColor, strokeColor?) - 创建多边形

操作元素：
- ctx.setPosition(id, x, y) - 设置位置
- ctx.setScale(id, sx, sy) - 设置缩放
- ctx.setRotation(id, angle) - 设置旋转（角度）
- ctx.setAlpha(id, alpha) - 设置透明度 0-1
- ctx.setColor(id, color) - 设置颜色
- ctx.setText(id, text) - 设置文本内容
- ctx.setVisible(id, visible) - 设置可见性
- ctx.remove(id) - 移除元素
- ctx.clear() - 清除所有元素

变量操作：
- ctx.getVar(name) - 获取变量值
- ctx.setVar(name, value) - 设置变量值

数学工具 ctx.math：
- sin, cos, tan, abs, floor, ceil, round, sqrt, pow, min, max, random
- PI: 圆周率
- lerp(a, b, t): 线性插值
- clamp(value, min, max): 限制范围
- wave(t, frequency?, amplitude?): 波形函数

【完整示例 - 波浪传导模拟器】
{{
  "step_id": "step_3",
  "type": "simulator",
  "title": "躯干波浪传导",
  "simulator_spec": {{
    "mode": "custom",
    "name": "躯干波浪传导模拟",
    "description": "展示波浪如何从颈椎传导到腰椎",
    "variables": [
      {{"name": "speed", "label": "传导速度", "min": 1, "max": 5, "default": 2, "step": 0.1, "unit": ""}},
      {{"name": "amplitude", "label": "波浪幅度", "min": 10, "max": 50, "default": 30, "step": 1, "unit": "px"}}
    ],
    "custom_code": "let nodes = [];\\nlet lineId = null;\\n\\nfunction setup(ctx) {{\\n  const {{ width, height }} = ctx;\\n  ctx.createText('躯干波浪传导', width/2, 30, {{fontSize: 24, fontWeight: 'bold', color: '#ffffff'}});\\n  ctx.createText('颈椎', 100, 100, {{fontSize: 14, color: '#94a3b8'}});\\n  ctx.createText('腰椎', 100, 420, {{fontSize: 14, color: '#94a3b8'}});\\n  const nodeCount = 20;\\n  const startY = 80;\\n  const endY = 420;\\n  const spacing = (endY - startY) / (nodeCount - 1);\\n  for (let i = 0; i < nodeCount; i++) {{\\n    const y = startY + i * spacing;\\n    const id = ctx.createCircle(width/2, y, 8, '#fbbf24');\\n    nodes.push({{ id, baseX: width/2, y, index: i }});\\n  }}\\n}}\\n\\nfunction update(ctx) {{\\n  const speed = ctx.getVar('speed');\\n  const amplitude = ctx.getVar('amplitude');\\n  nodes.forEach((node, i) => {{\\n    const phase = i * 0.3;\\n    const offset = ctx.math.sin(ctx.time * speed - phase) * amplitude;\\n    ctx.setPosition(node.id, node.baseX + offset, node.y);\\n    const alpha = 0.5 + ctx.math.abs(offset) / amplitude * 0.5;\\n    ctx.setAlpha(node.id, alpha);\\n  }});\\n}}"
  }}
}}

【其他步骤要求】
- text_content: body至少60字
- illustrated_content: 必须有diagram_spec
- 不要使用video类型

只输出JSON，不要其他内容。

【可用模板列表】
{template_list}"""

        # 使用流式生成
        async for chunk in self.claude_service.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=20000
        ):
            yield chunk

    def _parse_lesson_json(
        self,
        response: str,
        lesson_outline: Dict[str, Any],
        lesson_index: int
    ) -> Dict[str, Any]:
        """解析课时 JSON - 增强版，尽可能保留所有生成的步骤"""
        lesson_title = lesson_outline.get("title", f"课时 {lesson_index + 1}")
        complexity = lesson_outline.get("complexity_level", "standard")

        def extract_steps_from_partial_json(content: str) -> List[Dict]:
            """从不完整的 JSON 中提取已完成的步骤"""
            steps = []
            # 查找 script 数组
            script_match = re.search(r'"script"\s*:\s*\[', content)
            if not script_match:
                return steps

            script_start = script_match.end()
            depth = 1
            step_start = -1
            in_string = False
            escape = False

            i = script_start
            while i < len(content) and depth > 0:
                char = content[i]

                if escape:
                    escape = False
                    i += 1
                    continue

                if char == '\\':
                    escape = True
                    i += 1
                    continue

                if char == '"':
                    in_string = not in_string
                    i += 1
                    continue

                if in_string:
                    i += 1
                    continue

                if char == '{':
                    if depth == 1:
                        step_start = i
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 1 and step_start >= 0:
                        # 找到一个完整的步骤对象
                        step_str = content[step_start:i + 1]
                        try:
                            step = json.loads(step_str)
                            if isinstance(step, dict) and step.get("step_id") and step.get("type"):
                                steps.append(step)
                        except json.JSONDecodeError:
                            pass
                        step_start = -1
                elif char == '[':
                    depth += 1
                elif char == ']':
                    depth -= 1

                i += 1

            return steps

        try:
            json_str = response.strip()

            # 尝试多种方式提取 JSON
            # 方式1: 提取 ```json ... ``` 代码块
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            # 方式2: 提取 ``` ... ``` 代码块
            elif "```" in json_str:
                parts = json_str.split("```")
                if len(parts) >= 2:
                    json_str = parts[1]
                    # 如果第一行是语言标识符，跳过它
                    lines = json_str.split('\n')
                    if lines and lines[0].strip() in ['json', 'JSON', '']:
                        json_str = '\n'.join(lines[1:])

            # 方式3: 查找第一个 { 和最后一个 }
            json_str = json_str.strip()
            if not json_str.startswith('{'):
                first_brace = json_str.find('{')
                if first_brace != -1:
                    json_str = json_str[first_brace:]

            if not json_str.endswith('}'):
                last_brace = json_str.rfind('}')
                if last_brace != -1:
                    json_str = json_str[:last_brace + 1]

            # 尝试解析完整 JSON
            lesson = json.loads(json_str.strip())

            # 验证必要字段
            if not isinstance(lesson, dict):
                raise ValueError("Parsed result is not a dict")

            # 确保有 script 字段且不为空
            script = lesson.get("script", [])
            if not script or not isinstance(script, list):
                # 尝试从原始响应中提取步骤
                logger.warning(f"Lesson {lesson_index + 1} has empty script, trying to extract steps from raw response")
                extracted_steps = extract_steps_from_partial_json(response)
                if extracted_steps:
                    lesson["script"] = extracted_steps
                    script = extracted_steps
                    logger.info(f"Extracted {len(extracted_steps)} steps from partial JSON")
                else:
                    logger.warning(f"Could not extract any steps, using fallback")
                    return self._create_fallback_lesson(lesson_title, lesson_index, complexity)

            # Ensure required fields
            lesson["lesson_id"] = lesson.get("lesson_id", f"lesson_{lesson_index + 1}")
            lesson["title"] = lesson.get("title", lesson_title)
            lesson["order"] = lesson_index
            lesson["total_steps"] = len(script)

            # 验证并修复模拟器内容
            lesson = self._validate_and_fix_simulators(lesson)

            logger.info(f"Successfully parsed lesson {lesson_index + 1} with {len(script)} steps")
            return lesson

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse lesson JSON for lesson {lesson_index + 1}: {e}")

            # 尝试从原始响应中提取步骤
            extracted_steps = extract_steps_from_partial_json(response)
            if extracted_steps:
                logger.info(f"Recovered {len(extracted_steps)} steps from failed JSON parse")
                # 尝试提取其他字段
                title_match = re.search(r'"title"\s*:\s*"([^"]+)"', response)
                rationale_match = re.search(r'"rationale"\s*:\s*"([^"]+)"', response)

                return {
                    "lesson_id": f"lesson_{lesson_index + 1}",
                    "title": title_match.group(1) if title_match else lesson_title,
                    "order": lesson_index,
                    "total_steps": len(extracted_steps),
                    "rationale": rationale_match.group(1).replace('\\n', '\n') if rationale_match else f"本课时围绕{lesson_title}展开",
                    "script": extracted_steps,
                    "estimated_minutes": len(extracted_steps) * 5,
                    "prerequisites": [],
                    "learning_objectives": lesson_outline.get("learning_objectives", [f"理解{lesson_title}的核心概念"]),
                    "complexity_level": complexity
                }

            # 完全无法提取，使用 fallback
            logger.warning(f"Could not recover any steps, using fallback for lesson {lesson_index + 1}")
            logger.debug(f"Response preview: {response[:500]}...")
            return self._create_fallback_lesson(lesson_title, lesson_index, complexity)

    async def _generate_lesson_with_steps(
        self,
        course_title: str,
        source_material: str,
        lesson_outline: Dict[str, Any],
        lesson_index: int,
        total_lessons: int,
        system_prompt: str,
        previous_lessons: List[Any],
        chunk_callback=None
    ) -> Dict[str, Any]:
        """生成课时内容（用于步骤流式输出）"""

        lesson_title = lesson_outline.get("title", f"课时 {lesson_index + 1}")
        recommended_forms = lesson_outline.get("recommended_forms", ["text_content"])
        complexity = lesson_outline.get("complexity_level", "standard")

        # Build detailed context from previous lessons to avoid repetition
        prev_context = ""
        used_simulators = []
        covered_topics = []
        if previous_lessons:
            prev_titles = [l.get("title", "") for l in previous_lessons[-3:]]
            prev_context = f"前面已完成的课时：{', '.join(prev_titles)}\n"

            # Collect used simulators and topics from ALL previous lessons
            for prev_lesson in previous_lessons:
                # Get lesson title as covered topic
                if prev_lesson.get("title"):
                    covered_topics.append(prev_lesson.get("title"))

                # Extract simulators from script
                for step in prev_lesson.get("script", []):
                    if step.get("type") == "simulator":
                        sim_spec = step.get("simulator_spec", {})
                        sim_name = sim_spec.get("name", step.get("title", ""))
                        if sim_name and sim_name not in used_simulators:
                            used_simulators.append(sim_name)
                        # Also track preset IDs
                        preset_id = sim_spec.get("presetId") or sim_spec.get("preset_id")
                        if preset_id and preset_id not in used_simulators:
                            used_simulators.append(preset_id)

            if used_simulators:
                prev_context += f"【已使用的模拟器，请勿重复】：{', '.join(used_simulators)}\n"
            if covered_topics:
                prev_context += f"【已讲解的主题，请勿重复】：{', '.join(covered_topics)}\n"

        # 模板列表
        template_list = """
=== 田径类 ===
- sports_sprint_start: 短跑起跑技术
- sports_jump_approach: J形助跑跳高
- sports_long_jump: 跳远技术分析
- sports_shot_put: 铅球投掷技术
- sports_hurdles: 跨栏技术分析
- sports_relay_race: 接力赛跑技术
- sports_discus_throw: 铁饼投掷技术
- sports_pole_vault: 撑杆跳高技术
- sports_javelin_throw: 标枪投掷技术

=== 球类运动 ===
- sports_basketball_shooting: 篮球投篮技术
- sports_basketball_dunk: 篮球扣篮技术
- sports_football_kick: 足球射门技术
- sports_football_bicycle_kick: 足球倒钩射门技术
- sports_tennis_serve: 网球发球技术
- sports_volleyball_spike: 排球扣球技术
- sports_badminton_smash: 羽毛球扣杀技术
- sports_table_tennis_serve: 乒乓球发球技术
- sports_golf_swing: 高尔夫挥杆技术
- sports_hockey_shot: 曲棍球射门技术

=== 游泳和体操 ===
- sports_swimming_stroke: 游泳泳姿分析
- sports_gymnastics_vault: 体操跳马技术
- sports_gymnastics_floor_flip: 体操自由操空翻技术
- sports_gymnastics_high_bar: 体操单杠大回环技术

=== 武术和格斗 ===
- sports_taekwondo_kick: 跆拳道踢腿技术
- sports_boxing_punch: 拳击出拳技术
- sports_fencing_lunge: 击剑弓步刺技术

=== 冬季运动 ===
- sports_skiing_slalom: 高山滑雪回转技术
- sports_figure_skating_spin: 花样滑冰旋转技术
- sports_figure_skating_jump: 花样滑冰跳跃技术

=== 水上运动 ===
- sports_diving_platform: 跳水技术分析
- sports_diving_twist: 跳水转体技术
- sports_rowing_technique: 赛艇划桨技术

=== 其他运动 ===
- sports_archery_shot: 射箭技术分析
- sports_cycling_sprint: 自行车冲刺技术
- sports_weightlifting_snatch: 举重抓举技术
- sports_yoga_pose: 瑜伽体式分析

=== 物理学 ===
- physics_force_composition: 力的合成与分解
- physics_projectile_motion: 抛体运动分析
- physics_circuit: 电路原理模拟
- physics_pendulum: 单摆运动分析

=== 艺术 ===
- art_color_wheel: 色彩理论模拟
- art_composition: 构图原理模拟
"""

        prompt = f"""为课程"{course_title}"生成第{lesson_index + 1}课时的详细内容。

课时标题：{lesson_title}
推荐教学形式：{', '.join(recommended_forms)}
复杂度级别：{complexity}
{prev_context}

源材料（相关部分）：
{source_material[:6000]}

请生成完整的课时内容，以JSON格式输出：
{{
    "lesson_id": "lesson_{lesson_index + 1}",
    "title": "{lesson_title}",
    "order": {lesson_index},
    "total_steps": 步骤数量,
    "rationale": "课时设计理念",
    "script": [
        {{
            "step_id": "step_1",
            "type": "text_content",
            "title": "步骤标题",
            "content": {{
                "body": "正文内容（至少60字，精准讲解该知识点，无废话）",
                "key_points": ["要点1", "要点2"]
            }}
        }},
        {{
            "step_id": "step_2",
            "type": "illustrated_content",
            "title": "图文讲解",
            "content": {{
                "body": "配合图片的文字说明（至少100字）",
                "key_points": ["要点1", "要点2"]
            }},
            "diagram_spec": {{
                "type": "static_diagram",
                "description": "详细描述需要生成的图片内容，包括要展示的元素、布局、颜色等",
                "annotations": [
                    {{"position": "左侧", "text": "标注说明1"}},
                    {{"position": "右侧", "text": "标注说明2"}}
                ],
                "design_notes": "图片设计要求和风格说明"
            }}
        }},
        {{
            "step_id": "step_3",
            "type": "simulator",
            "title": "互动模拟",
            "simulator_spec": {{
                "mode": "custom",
                "name": "模拟器名称",
                "description": "模拟器描述",
                "variables": [
                    {{"name": "speed", "label": "速度", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "m/s"}},
                    {{"name": "amplitude", "label": "振幅", "min": 10, "max": 50, "default": 30, "step": 1, "unit": "px"}}
                ],
                "custom_code": "// 存储元素ID\\nlet elements = {{}};\\n\\nfunction setup(ctx) {{\\n  const {{ width, height }} = ctx;\\n  ctx.createText('标题', width/2, 30, {{fontSize: 24, fontWeight: 'bold', color: '#ffffff'}});\\n  elements.ball = ctx.createCircle(width/2, height/2, 20, '#fbbf24');\\n}}\\n\\nfunction update(ctx) {{\\n  const speed = ctx.getVar('speed');\\n  const amplitude = ctx.getVar('amplitude');\\n  const x = ctx.width/2 + ctx.math.sin(ctx.time * speed * 0.1) * amplitude;\\n  ctx.setPosition(elements.ball, x, ctx.height/2);\\n}}"
            }}
        }},
        {{
            "step_id": "step_4",
            "type": "assessment",
            "title": "知识检测",
            "assessment_spec": {{
                "type": "quick_check",
                "questions": [
                    {{
                        "question": "问题",
                        "options": ["A", "B", "C", "D"],
                        "correct": "A",
                        "explanation": "解释"
                    }}
                ],
                "pass_required": true
            }}
        }}
    ],
    "estimated_minutes": 预估时长,
    "prerequisites": [],
    "learning_objectives": ["学习目标1", "学习目标2"],
    "complexity_level": "{complexity}"
}}

【模拟器设计规范 - 自定义代码模式】

【核心目的】模拟器用于帮助用户理解变量之间的关系！
用户通过拖动滑块改变自变量，观察因变量的变化，从而理解物理概念之间的关系。

【重要】simulator 必须使用 mode: "custom" 和 custom_code 字段！

simulator_spec 必须包含：
1. "mode": "custom" - 必须设置为custom
2. "name": "模拟器名称"
3. "description": "模拟器描述"
4. "variables": 变量数组（用于生成滑块控件）
5. "custom_code": JavaScript代码字符串

【画布规格】800x500像素

【变量定义格式】
"variables": [
  {{"name": "speed", "label": "速度", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "m/s"}},
  {{"name": "amplitude", "label": "振幅", "min": 10, "max": 50, "default": 30, "step": 1, "unit": "px"}}
]

【代码结构要求 - 非常重要】custom_code 必须定义 setup 和 update 函数：

【关键规则】
1. 所有数组变量必须在代码顶部初始化为空数组 []，例如：let nodes = [];
2. 所有对象变量必须在代码顶部初始化为空对象 {{}}，例如：let elements = {{}};
3. 不要使用未定义的变量，所有变量必须先声明再使用
4. 使用 push() 前必须确保数组已初始化

```javascript
// 【必须】在顶部初始化所有变量
let elements = {{}};  // 对象用于存储单个元素ID
let nodes = [];       // 数组用于存储多个元素

function setup(ctx) {{
  const {{ width, height }} = ctx;
  // 创建标题
  ctx.createText('标题', width/2, 30, {{fontSize: 24, fontWeight: 'bold', color: '#ffffff'}});
  // 创建元素并存储ID
  elements.ball = ctx.createCircle(width/2, height/2, 20, '#fbbf24');
  // 创建多个元素时使用数组
  for (let i = 0; i < 5; i++) {{
    const id = ctx.createCircle(100 + i * 50, 200, 10, '#3b82f6');
    nodes.push({{ id, x: 100 + i * 50 }});  // nodes 已在顶部初始化为 []
  }}
}}

function update(ctx) {{
  // 获取变量值
  const speed = ctx.getVar('speed');
  const amplitude = ctx.getVar('amplitude');
  // 计算位置
  const x = ctx.width/2 + ctx.math.sin(ctx.time * speed * 0.1) * amplitude;
  ctx.setPosition(elements.ball, x, ctx.height/2);
}}
```

【可用的 ctx API】

画布信息：
- ctx.width: 800
- ctx.height: 500
- ctx.time: 当前时间（秒）
- ctx.deltaTime: 帧间隔（秒）

创建元素（返回元素ID）：
- ctx.createCircle(x, y, radius, color) - 创建圆形
- ctx.createRect(x, y, width, height, color, cornerRadius?) - 创建矩形
- ctx.createLine(points, color, lineWidth?) - 创建线条，points是{{x,y}}数组
- ctx.createText(text, x, y, style?) - 创建文本，style可选{{fontSize, fontFamily, color, fontWeight, align}}
- ctx.createCurve(points, color, lineWidth?, smooth?) - 创建曲线
- ctx.createPolygon(points, fillColor, strokeColor?) - 创建多边形

操作元素：
- ctx.setPosition(id, x, y) - 设置位置
- ctx.setScale(id, sx, sy) - 设置缩放
- ctx.setRotation(id, angle) - 设置旋转（角度）
- ctx.setAlpha(id, alpha) - 设置透明度 0-1
- ctx.setColor(id, color) - 设置颜色
- ctx.setText(id, text) - 设置文本内容
- ctx.setVisible(id, visible) - 设置可见性
- ctx.remove(id) - 移除元素
- ctx.clear() - 清除所有元素

变量操作：
- ctx.getVar(name) - 获取变量值
- ctx.setVar(name, value) - 设置变量值

数学工具 ctx.math：
- sin, cos, tan, abs, floor, ceil, round, sqrt, pow, min, max, random
- PI: 圆周率
- lerp(a, b, t): 线性插值
- clamp(value, min, max): 限制范围
- wave(t, frequency?, amplitude?): 波形函数

【完整示例 - 波浪传导模拟器】
{{
  "step_id": "step_3",
  "type": "simulator",
  "title": "躯干波浪传导",
  "simulator_spec": {{
    "mode": "custom",
    "name": "躯干波浪传导模拟",
    "description": "展示波浪如何从颈椎传导到腰椎",
    "variables": [
      {{"name": "speed", "label": "传导速度", "min": 1, "max": 5, "default": 2, "step": 0.1, "unit": ""}},
      {{"name": "amplitude", "label": "波浪幅度", "min": 10, "max": 50, "default": 30, "step": 1, "unit": "px"}}
    ],
    "custom_code": "let nodes = [];\\nlet lineId = null;\\n\\nfunction setup(ctx) {{\\n  const {{ width, height }} = ctx;\\n  ctx.createText('躯干波浪传导', width/2, 30, {{fontSize: 24, fontWeight: 'bold', color: '#ffffff'}});\\n  ctx.createText('颈椎', 100, 100, {{fontSize: 14, color: '#94a3b8'}});\\n  ctx.createText('腰椎', 100, 420, {{fontSize: 14, color: '#94a3b8'}});\\n  const nodeCount = 20;\\n  const startY = 80;\\n  const endY = 420;\\n  const spacing = (endY - startY) / (nodeCount - 1);\\n  for (let i = 0; i < nodeCount; i++) {{\\n    const y = startY + i * spacing;\\n    const id = ctx.createCircle(width/2, y, 8, '#fbbf24');\\n    nodes.push({{ id, baseX: width/2, y, index: i }});\\n  }}\\n}}\\n\\nfunction update(ctx) {{\\n  const speed = ctx.getVar('speed');\\n  const amplitude = ctx.getVar('amplitude');\\n  nodes.forEach((node, i) => {{\\n    const phase = i * 0.3;\\n    const offset = ctx.math.sin(ctx.time * speed - phase) * amplitude;\\n    ctx.setPosition(node.id, node.baseX + offset, node.y);\\n    const alpha = 0.5 + ctx.math.abs(offset) / amplitude * 0.5;\\n    ctx.setAlpha(node.id, alpha);\\n  }});\\n}}"
  }}
}}

【其他步骤要求】
- text_content: body至少60字
- illustrated_content: 必须有diagram_spec
- 不要使用video类型

只输出JSON，不要其他内容。

【可用模板列表】
{template_list}"""

        response = await self.claude_service.generate_raw_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=20000
        )

        # Parse the lesson JSON
        lesson = self._parse_lesson_json(response, lesson_outline, lesson_index)

        # Validate and enrich lesson content
        lesson = await self._validate_and_enrich_lesson(
            lesson, course_title, source_material, system_prompt
        )

        return lesson

    async def _generate_lesson(
        self,
        course_title: str,
        source_material: str,
        lesson_outline: Dict[str, Any],
        lesson_index: int,
        total_lessons: int,
        system_prompt: str,
        previous_lessons: List[Any]
    ) -> Dict[str, Any]:
        """Generate a single lesson"""

        lesson_title = lesson_outline.get("title", f"课时 {lesson_index + 1}")
        recommended_forms = lesson_outline.get("recommended_forms", ["text_content"])
        complexity = lesson_outline.get("complexity_level", "standard")

        # Build detailed context from previous lessons to avoid repetition
        prev_context = ""
        used_simulators = []
        covered_topics = []
        if previous_lessons:
            prev_titles = [l.get("title", "") for l in previous_lessons[-3:]]
            prev_context = f"前面已完成的课时：{', '.join(prev_titles)}\n"

            # Collect used simulators and topics from ALL previous lessons
            for prev_lesson in previous_lessons:
                # Get lesson title as covered topic
                if prev_lesson.get("title"):
                    covered_topics.append(prev_lesson.get("title"))

                # Extract simulators from script
                for step in prev_lesson.get("script", []):
                    if step.get("type") == "simulator":
                        sim_spec = step.get("simulator_spec", {})
                        sim_name = sim_spec.get("name", step.get("title", ""))
                        if sim_name and sim_name not in used_simulators:
                            used_simulators.append(sim_name)
                        # Also track preset IDs
                        preset_id = sim_spec.get("presetId") or sim_spec.get("preset_id")
                        if preset_id and preset_id not in used_simulators:
                            used_simulators.append(preset_id)

            if used_simulators:
                prev_context += f"【已使用的模拟器，请勿重复】：{', '.join(used_simulators)}\n"
            if covered_topics:
                prev_context += f"【已讲解的主题，请勿重复】：{', '.join(covered_topics)}\n"

        # 模板列表
        template_list = """
=== 田径类 ===
- sports_sprint_start: 短跑起跑技术
- sports_jump_approach: J形助跑跳高
- sports_long_jump: 跳远技术分析
- sports_shot_put: 铅球投掷技术
- sports_hurdles: 跨栏技术分析
- sports_relay_race: 接力赛跑技术
- sports_discus_throw: 铁饼投掷技术
- sports_pole_vault: 撑杆跳高技术
- sports_javelin_throw: 标枪投掷技术

=== 球类运动 ===
- sports_basketball_shooting: 篮球投篮技术
- sports_basketball_dunk: 篮球扣篮技术
- sports_football_kick: 足球射门技术
- sports_football_bicycle_kick: 足球倒钩射门技术
- sports_tennis_serve: 网球发球技术
- sports_volleyball_spike: 排球扣球技术
- sports_badminton_smash: 羽毛球扣杀技术
- sports_table_tennis_serve: 乒乓球发球技术
- sports_golf_swing: 高尔夫挥杆技术
- sports_hockey_shot: 曲棍球射门技术

=== 游泳和体操 ===
- sports_swimming_stroke: 游泳泳姿分析
- sports_gymnastics_vault: 体操跳马技术
- sports_gymnastics_floor_flip: 体操自由操空翻技术
- sports_gymnastics_high_bar: 体操单杠大回环技术

=== 武术和格斗 ===
- sports_taekwondo_kick: 跆拳道踢腿技术
- sports_boxing_punch: 拳击出拳技术
- sports_fencing_lunge: 击剑弓步刺技术

=== 冬季运动 ===
- sports_skiing_slalom: 高山滑雪回转技术
- sports_figure_skating_spin: 花样滑冰旋转技术
- sports_figure_skating_jump: 花样滑冰跳跃技术

=== 水上运动 ===
- sports_diving_platform: 跳水技术分析
- sports_diving_twist: 跳水转体技术
- sports_rowing_technique: 赛艇划桨技术

=== 其他运动 ===
- sports_archery_shot: 射箭技术分析
- sports_cycling_sprint: 自行车冲刺技术
- sports_weightlifting_snatch: 举重抓举技术
- sports_yoga_pose: 瑜伽体式分析

=== 物理学 ===
- physics_force_composition: 力的合成与分解
- physics_projectile_motion: 抛体运动分析
- physics_circuit: 电路原理模拟
- physics_pendulum: 单摆运动分析

=== 艺术 ===
- art_color_wheel: 色彩理论模拟
- art_composition: 构图原理模拟
"""

        prompt = f"""为课程"{course_title}"生成第{lesson_index + 1}课时的详细内容。

课时标题：{lesson_title}
推荐教学形式：{', '.join(recommended_forms)}
复杂度级别：{complexity}
{prev_context}

源材料（相关部分）：
{source_material[:6000]}

请生成完整的课时内容，以JSON格式输出：
{{
    "lesson_id": "lesson_{lesson_index + 1}",
    "title": "{lesson_title}",
    "order": {lesson_index},
    "total_steps": 步骤数量,
    "rationale": "课时设计理念",
    "script": [
        {{
            "step_id": "step_1",
            "type": "text_content",
            "title": "步骤标题",
            "content": {{
                "body": "正文内容（至少60字，精准讲解该知识点，无废话）",
                "key_points": ["要点1", "要点2"]
            }}
        }},
        {{
            "step_id": "step_2",
            "type": "illustrated_content",
            "title": "图文讲解",
            "content": {{
                "body": "配合图片的文字说明（至少100字）",
                "key_points": ["要点1", "要点2"]
            }},
            "diagram_spec": {{
                "type": "static_diagram",
                "description": "详细描述需要生成的图片内容，包括要展示的元素、布局、颜色等",
                "annotations": [
                    {{"position": "左侧", "text": "标注说明1"}},
                    {{"position": "右侧", "text": "标注说明2"}}
                ],
                "design_notes": "图片设计要求和风格说明"
            }}
        }},
        {{
            "step_id": "step_3",
            "type": "simulator",
            "title": "互动模拟",
            "simulator_spec": {{
                "mode": "custom",
                "name": "模拟器名称",
                "description": "模拟器描述",
                "variables": [
                    {{"name": "speed", "label": "速度", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "m/s"}},
                    {{"name": "amplitude", "label": "振幅", "min": 10, "max": 50, "default": 30, "step": 1, "unit": "px"}}
                ],
                "custom_code": "// 存储元素ID\\nlet elements = {{}};\\n\\nfunction setup(ctx) {{\\n  const {{ width, height }} = ctx;\\n  ctx.createText('标题', width/2, 30, {{fontSize: 24, fontWeight: 'bold', color: '#ffffff'}});\\n  elements.ball = ctx.createCircle(width/2, height/2, 20, '#fbbf24');\\n}}\\n\\nfunction update(ctx) {{\\n  const speed = ctx.getVar('speed');\\n  const amplitude = ctx.getVar('amplitude');\\n  const x = ctx.width/2 + ctx.math.sin(ctx.time * speed * 0.1) * amplitude;\\n  ctx.setPosition(elements.ball, x, ctx.height/2);\\n}}"
            }}
        }},
        {{
            "step_id": "step_4",
            "type": "assessment",
            "title": "知识检测",
            "assessment_spec": {{
                "type": "quick_check",
                "questions": [
                    {{
                        "question": "问题",
                        "options": ["A", "B", "C", "D"],
                        "correct": "A",
                        "explanation": "解释"
                    }}
                ],
                "pass_required": true
            }}
        }}
    ],
    "estimated_minutes": 预估时长,
    "prerequisites": [],
    "learning_objectives": ["学习目标1", "学习目标2"],
    "complexity_level": "{complexity}"
}}

【模拟器设计规范 - 自定义代码模式】

【核心目的】模拟器用于帮助用户理解变量之间的关系！
用户通过拖动滑块改变自变量，观察因变量的变化，从而理解物理概念之间的关系。

【重要】simulator 必须使用 mode: "custom" 和 custom_code 字段！

simulator_spec 必须包含：
1. "mode": "custom" - 必须设置为custom
2. "name": "模拟器名称"
3. "description": "模拟器描述"
4. "variables": 变量数组（用于生成滑块控件）
5. "custom_code": JavaScript代码字符串

【画布规格】800x500像素

【变量定义格式】
"variables": [
  {{"name": "speed", "label": "速度", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "m/s"}},
  {{"name": "amplitude", "label": "振幅", "min": 10, "max": 50, "default": 30, "step": 1, "unit": "px"}}
]

【代码结构要求 - 非常重要】custom_code 必须定义 setup 和 update 函数：

【关键规则】
1. 所有数组变量必须在代码顶部初始化为空数组 []，例如：let nodes = [];
2. 所有对象变量必须在代码顶部初始化为空对象 {{}}，例如：let elements = {{}};
3. 不要使用未定义的变量，所有变量必须先声明再使用
4. 使用 push() 前必须确保数组已初始化

```javascript
// 【必须】在顶部初始化所有变量
let elements = {{}};  // 对象用于存储单个元素ID
let nodes = [];       // 数组用于存储多个元素

function setup(ctx) {{
  const {{ width, height }} = ctx;
  // 创建标题
  ctx.createText('标题', width/2, 30, {{fontSize: 24, fontWeight: 'bold', color: '#ffffff'}});
  // 创建元素并存储ID
  elements.ball = ctx.createCircle(width/2, height/2, 20, '#fbbf24');
  // 创建多个元素时使用数组
  for (let i = 0; i < 5; i++) {{
    const id = ctx.createCircle(100 + i * 50, 200, 10, '#3b82f6');
    nodes.push({{ id, x: 100 + i * 50 }});  // nodes 已在顶部初始化为 []
  }}
}}

function update(ctx) {{
  // 获取变量值
  const speed = ctx.getVar('speed');
  const amplitude = ctx.getVar('amplitude');
  // 计算位置
  const x = ctx.width/2 + ctx.math.sin(ctx.time * speed * 0.1) * amplitude;
  ctx.setPosition(elements.ball, x, ctx.height/2);
}}
```

【可用的 ctx API】

画布信息：
- ctx.width: 800
- ctx.height: 500
- ctx.time: 当前时间（秒）
- ctx.deltaTime: 帧间隔（秒）

创建元素（返回元素ID）：
- ctx.createCircle(x, y, radius, color) - 创建圆形
- ctx.createRect(x, y, width, height, color, cornerRadius?) - 创建矩形
- ctx.createLine(points, color, lineWidth?) - 创建线条，points是{{x,y}}数组
- ctx.createText(text, x, y, style?) - 创建文本，style可选{{fontSize, fontFamily, color, fontWeight, align}}
- ctx.createCurve(points, color, lineWidth?, smooth?) - 创建曲线
- ctx.createPolygon(points, fillColor, strokeColor?) - 创建多边形

操作元素：
- ctx.setPosition(id, x, y) - 设置位置
- ctx.setScale(id, sx, sy) - 设置缩放
- ctx.setRotation(id, angle) - 设置旋转（角度）
- ctx.setAlpha(id, alpha) - 设置透明度 0-1
- ctx.setColor(id, color) - 设置颜色
- ctx.setText(id, text) - 设置文本内容
- ctx.setVisible(id, visible) - 设置可见性
- ctx.remove(id) - 移除元素
- ctx.clear() - 清除所有元素

变量操作：
- ctx.getVar(name) - 获取变量值
- ctx.setVar(name, value) - 设置变量值

数学工具 ctx.math：
- sin, cos, tan, abs, floor, ceil, round, sqrt, pow, min, max, random
- PI: 圆周率
- lerp(a, b, t): 线性插值
- clamp(value, min, max): 限制范围
- wave(t, frequency?, amplitude?): 波形函数

【完整示例 - 波浪传导模拟器】
{{
  "step_id": "step_3",
  "type": "simulator",
  "title": "躯干波浪传导",
  "simulator_spec": {{
    "mode": "custom",
    "name": "躯干波浪传导模拟",
    "description": "展示波浪如何从颈椎传导到腰椎",
    "variables": [
      {{"name": "speed", "label": "传导速度", "min": 1, "max": 5, "default": 2, "step": 0.1, "unit": ""}},
      {{"name": "amplitude", "label": "波浪幅度", "min": 10, "max": 50, "default": 30, "step": 1, "unit": "px"}}
    ],
    "custom_code": "let nodes = [];\\nlet lineId = null;\\n\\nfunction setup(ctx) {{\\n  const {{ width, height }} = ctx;\\n  ctx.createText('躯干波浪传导', width/2, 30, {{fontSize: 24, fontWeight: 'bold', color: '#ffffff'}});\\n  ctx.createText('颈椎', 100, 100, {{fontSize: 14, color: '#94a3b8'}});\\n  ctx.createText('腰椎', 100, 420, {{fontSize: 14, color: '#94a3b8'}});\\n  const nodeCount = 20;\\n  const startY = 80;\\n  const endY = 420;\\n  const spacing = (endY - startY) / (nodeCount - 1);\\n  for (let i = 0; i < nodeCount; i++) {{\\n    const y = startY + i * spacing;\\n    const id = ctx.createCircle(width/2, y, 8, '#fbbf24');\\n    nodes.push({{ id, baseX: width/2, y, index: i }});\\n  }}\\n}}\\n\\nfunction update(ctx) {{\\n  const speed = ctx.getVar('speed');\\n  const amplitude = ctx.getVar('amplitude');\\n  nodes.forEach((node, i) => {{\\n    const phase = i * 0.3;\\n    const offset = ctx.math.sin(ctx.time * speed - phase) * amplitude;\\n    ctx.setPosition(node.id, node.baseX + offset, node.y);\\n    const alpha = 0.5 + ctx.math.abs(offset) / amplitude * 0.5;\\n    ctx.setAlpha(node.id, alpha);\\n  }});\\n}}"
  }}
}}

【其他步骤要求】
- text_content: body至少60字
- illustrated_content: 必须有diagram_spec
- 不要使用video类型

只输出JSON，不要其他内容。

【可用模板列表】
{template_list}"""

        response = await self.claude_service.generate_raw_response(
            prompt=f"{system_prompt}\n\n{prompt}",
            temperature=0.7,
            max_tokens=20000
        )

        # Parse JSON from response
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]

            lesson = json.loads(json_str.strip())
            # Ensure required fields
            lesson["lesson_id"] = lesson.get("lesson_id", f"lesson_{lesson_index + 1}")
            lesson["title"] = lesson.get("title", lesson_title)
            lesson["order"] = lesson_index
            lesson["total_steps"] = len(lesson.get("script", []))

            # 检查并补充内容不足的非习题步骤
            lesson = await self._validate_and_enrich_lesson(
                lesson, course_title, source_material, system_prompt
            )

            return lesson
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse lesson JSON for lesson {lesson_index + 1}, regenerating...")
            # 解析失败时，尝试重新生成一次
            return await self._regenerate_lesson_content(
                course_title, source_material, lesson_title, lesson_index, complexity, system_prompt
            )

    async def _validate_and_enrich_lesson(
        self,
        lesson: Dict[str, Any],
        course_title: str,
        source_material: str,
        system_prompt: str
    ) -> Dict[str, Any]:
        """检查课时内容，对内容不足的步骤进行补充，生成图片，处理视频和模拟器"""
        # 从系统设置获取最小内容长度
        from app.core.system_settings import get_course_settings
        course_settings = get_course_settings()
        MIN_CONTENT_LENGTH = course_settings.ai_content_min_length

        script = lesson.get("script", [])
        lesson_title = lesson.get("title", "")

        # 需要跳过的习题类型
        ASSESSMENT_TYPES = ["assessment", "quiz", "practice", "exercise", "quick_check"]

        # 需要检查内容的文本类型
        TEXT_CONTENT_TYPES = ["text_content", "case_study", "concept", "explanation",
                              "introduction", "summary", "discussion", "reflection"]

        # 记录需要删除的步骤索引
        steps_to_delete = []

        for i, step in enumerate(script):
            step_type = step.get("type", "")
            step_title = step.get("title", f"步骤 {i+1}")

            # 1. 跳过习题类型的步骤
            if step_type in ASSESSMENT_TYPES:
                continue

            # 2. 处理视频步骤 - 转换为模拟器
            if step_type == "video":
                logger.info(f"Converting video step '{step_title}' to simulator")
                # 将视频步骤转换为模拟器步骤
                step["type"] = "simulator"
                video_spec = step.get("video_spec", {})
                step["simulator_spec"] = {
                    "type": "interactive",
                    "scenario": {
                        "description": video_spec.get("description", step_title)
                    }
                }
                # 删除 video_spec
                if "video_spec" in step:
                    del step["video_spec"]
                # 增强模拟器配置
                enhanced_step = await self._enhance_simulator_spec(
                    step, course_title, lesson_title, source_material, system_prompt
                )
                # 如果课题深度不足，标记为删除
                if enhanced_step is None:
                    steps_to_delete.append(i)
                    logger.info(f"Marking video->simulator step '{step_title}' for deletion due to shallow topic")
                else:
                    script[i] = enhanced_step
                continue

            # 3. 处理模拟器步骤 - 生成自定义代码
            if step_type == "simulator":
                logger.info(f"[CustomCode] Processing simulator step: {step_title}")
                logger.info(f"[CustomCode] Before enhance - simulator_spec keys: {list(step.get('simulator_spec', {}).keys())}")

                enhanced_step = await self._enhance_simulator_spec(
                    step, course_title, lesson_title, source_material, system_prompt
                )

                # 如果课题深度不足，标记为删除
                if enhanced_step is None:
                    steps_to_delete.append(i)
                    logger.info(f"Marking simulator step '{step_title}' for deletion due to shallow topic")
                else:
                    # 确保 custom_code 存在
                    sim_spec = enhanced_step.get("simulator_spec", {})
                    if sim_spec.get("mode") != "custom" or not sim_spec.get("custom_code"):
                        logger.error(f"[CustomCode] ERROR: custom_code missing after enhance for {step_title}!")
                    else:
                        logger.info(f"[CustomCode] SUCCESS: custom_code added for {step_title}")
                    script[i] = enhanced_step
                continue

            # 4. 处理图文内容 - 检查内容并生成图片
            if step_type == "illustrated_content":
                # 先检查文本内容
                content = step.get("content", {})
                body = content.get("body", "")
                if len(body) < MIN_CONTENT_LENGTH:
                    logger.info(f"Illustrated step '{step_title}' content too short ({len(body)} chars), enriching...")
                    enriched_content = await self._enrich_step_content(
                        course_title=course_title,
                        lesson_title=lesson_title,
                        step_title=step_title,
                        current_body=body,
                        source_material=source_material,
                        system_prompt=system_prompt
                    )
                    if "content" not in step:
                        step["content"] = {}
                    step["content"]["body"] = enriched_content

                # 再处理图片生成
                step = await self._process_illustrated_content(
                    step, course_title, lesson_title
                )
                script[i] = step
                continue

            # 5. 检查所有文本类型步骤的内容长度
            # 获取内容 - 支持多种内容结构
            body = ""
            content = step.get("content", {})

            if isinstance(content, dict):
                body = content.get("body", "") or content.get("text", "") or content.get("description", "")
            elif isinstance(content, str):
                body = content

            # 如果 content 为空，检查其他可能的字段
            if not body:
                body = step.get("body", "") or step.get("text", "") or step.get("description", "")

            # 如果内容太短，需要补充
            if len(body) < MIN_CONTENT_LENGTH:
                logger.info(f"Step '{step_title}' (type: {step_type}) content too short ({len(body)} chars), enriching...")

                enriched_content = await self._enrich_step_content(
                    course_title=course_title,
                    lesson_title=lesson_title,
                    step_title=step_title,
                    current_body=body,
                    source_material=source_material,
                    system_prompt=system_prompt
                )

                # 更新步骤内容 - 确保使用正确的结构
                if "content" not in step or not isinstance(step.get("content"), dict):
                    step["content"] = {}
                step["content"]["body"] = enriched_content

                # 如果原来没有 key_points，添加默认的
                if "key_points" not in step["content"]:
                    step["content"]["key_points"] = [
                        f"理解{step_title}的核心概念",
                        "掌握相关的基本原理"
                    ]

                script[i] = step

        # 删除标记为删除的步骤（从后往前删除以保持索引正确）
        for idx in reversed(steps_to_delete):
            deleted_step = script.pop(idx)
            logger.info(f"Deleted shallow topic step: {deleted_step.get('title', 'Unknown')}")

        lesson["script"] = script
        return lesson

    async def _process_illustrated_content(
        self,
        step: Dict[str, Any],
        course_title: str,
        lesson_title: str
    ) -> Dict[str, Any]:
        """处理图文内容，生成所需图片"""
        diagram_spec = step.get("diagram_spec")
        step_title = step.get("title", "图文内容")

        if diagram_spec:
            # 检查是否已有图片
            if not diagram_spec.get("image_url"):
                logger.info(f"Generating image for illustrated content: {step_title}")

                try:
                    # 调用 Gemini 生成图片
                    image_data = await gemini_service.generate_diagram(
                        diagram_spec=diagram_spec,
                        course_title=course_title,
                        lesson_title=lesson_title
                    )

                    if image_data:
                        # 保存图片
                        diagram_id = diagram_spec.get("diagram_id", str(uuid.uuid4())[:8])
                        filename = f"diagram_{diagram_id}.png"

                        # 使用 storage_service 保存
                        image_info = await self._save_generated_image(
                            image_data, filename, "diagrams"
                        )

                        if image_info:
                            diagram_spec["image_url"] = image_info["file_url"]
                            diagram_spec["image_generated"] = True
                            logger.info(f"Image generated and saved: {image_info['file_url']}")
                        else:
                            logger.warning(f"Failed to save image for: {step_title}")
                            diagram_spec["image_url"] = None
                            diagram_spec["image_generated"] = False
                    else:
                        logger.warning(f"Failed to generate image for: {step_title}")
                        diagram_spec["image_url"] = None
                        diagram_spec["image_generated"] = False

                except Exception as e:
                    logger.error(f"Error generating image for {step_title}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    diagram_spec["image_url"] = None
                    diagram_spec["image_generated"] = False

                # 确保更新 step 中的 diagram_spec（无论成功还是失败）
                step["diagram_spec"] = diagram_spec
        else:
            # 如果没有 diagram_spec，创建一个默认的
            logger.warning(f"No diagram_spec found for illustrated_content: {step_title}, creating default")
            step["diagram_spec"] = {
                "type": "static_diagram",
                "description": step_title,
                "image_url": None,
                "image_generated": False
            }

        return step

    async def _save_generated_image(
        self,
        image_data: bytes,
        filename: str,
        category: str = "images",
        target_width: int = 800,
        target_height: int = 600
    ) -> Optional[Dict[str, Any]]:
        """
        保存生成的图片，自动转换格式并裁剪到目标尺寸

        Args:
            image_data: 图片二进制数据
            filename: 文件名
            category: 存储类别
            target_width: 目标宽度
            target_height: 目标高度
        """
        try:
            from PIL import Image
            import io
            from pathlib import Path

            # 打开图片
            image = Image.open(io.BytesIO(image_data))

            # 转换为 RGB (处理 RGBA、P 等模式)
            if image.mode == "RGBA":
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            # 智能裁剪到目标比例
            image = self._smart_crop_resize(image, target_width, target_height)

            # 确保目录存在
            storage_dir = storage_service.directories.get(category, storage_service.directories["images"])
            storage_dir.mkdir(parents=True, exist_ok=True)

            # 生成唯一文件名 (统一使用 .jpg 格式)
            unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
            if not unique_filename.endswith('.jpg'):
                unique_filename = unique_filename.rsplit('.', 1)[0] + '.jpg'

            file_path = storage_dir / unique_filename

            # 保存为 JPEG 格式，优化质量和大小
            image.save(file_path, "JPEG", quality=85, optimize=True)

            # 返回文件信息 (使用 /upload/ 前缀匹配静态文件挂载路径)
            return {
                "filename": unique_filename,
                "file_path": str(file_path),
                "file_url": f"/upload/{category}/{unique_filename}",
                "width": image.size[0],
                "height": image.size[1]
            }

        except Exception as e:
            logger.error(f"Failed to save generated image: {e}")
            return None

    def _smart_crop_resize(self, image, target_width: int, target_height: int):
        """
        智能调整图片大小（不裁剪，保持完整内容）

        使用拉伸/压缩方式适应目标尺寸，不丢失任何内容
        """
        from PIL import Image

        # 直接缩放到目标尺寸（拉伸/压缩以适应画布）
        image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)

        return image

    def _mark_video_pending(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """标记视频为待处理状态"""
        video_spec = step.get("video_spec", {})
        video_spec["status"] = "pending"
        video_spec["placeholder"] = True
        step["video_spec"] = video_spec
        return step

    async def _enhance_simulator_spec(
        self,
        step: Dict[str, Any],
        course_title: str,
        lesson_title: str,
        source_material: str,
        system_prompt: str
    ) -> Optional[Dict[str, Any]]:
        """增强模拟器规格，确保使用自定义代码模式

        Returns:
            增强后的步骤，如果课题深度不足则返回 None（表示应删除此步骤）
        """
        simulator_spec = step.get("simulator_spec", {})
        step_title = step.get("title", "模拟器")

        logger.info(f"[CustomCode] _enhance_simulator_spec called for: {step_title}")

        # 检查是否已有自定义代码
        if simulator_spec.get("mode") == "custom" and simulator_spec.get("custom_code"):
            logger.info(f"[CustomCode] Using existing custom code for: {step_title}")
            custom_code = simulator_spec.get("custom_code", "")
            variables = simulator_spec.get("variables", [])

            # 验证代码
            from app.services.studio.custom_code_generator import validate_custom_code
            is_valid, error_msg = validate_custom_code(custom_code)

            if is_valid:
                # 代码有效，保持自定义代码模式
                simulator_spec["mode"] = "custom"
                simulator_spec["custom_code"] = custom_code
                simulator_spec["variables"] = variables
                step["simulator_spec"] = simulator_spec
                logger.info(f"[CustomCode] Valid custom code for: {step_title}")
                return step
            else:
                logger.warning(f"[CustomCode] Custom code validation failed: {error_msg}, will regenerate")

        # 如果没有有效的自定义代码，使用 AI 生成
        logger.info(f"[CustomCode] Generating custom code for: {step_title}")

        # 获取模拟器描述
        sim_name = simulator_spec.get("name", step_title)
        sim_description = simulator_spec.get("description", f"展示{step_title}的交互式模拟")
        existing_variables = simulator_spec.get("variables", [])

        # 使用 AI 生成代码
        generated = await self._generate_custom_code(
            topic=sim_name,
            description=sim_description,
            variables=existing_variables,
            course_title=course_title,
            lesson_title=lesson_title,
            source_material=source_material
        )

        if generated and generated.get("success"):
            simulator_spec["mode"] = "custom"
            simulator_spec["custom_code"] = generated["code"]
            simulator_spec["variables"] = generated.get("variables", existing_variables)
            step["simulator_spec"] = simulator_spec
            logger.info(f"[CustomCode] Successfully generated custom code for: {step_title}")
            return step
        else:
            # 生成失败，使用默认的简单模拟器代码
            logger.warning(f"[CustomCode] Failed to generate code, using default for: {step_title}")
            default_code = self._get_default_custom_code(step_title, sim_description)
            simulator_spec["mode"] = "custom"
            simulator_spec["custom_code"] = default_code
            simulator_spec["variables"] = [
                {"name": "speed", "label": "速度", "min": 1, "max": 10, "default": 3, "step": 0.5, "unit": ""},
                {"name": "amplitude", "label": "幅度", "min": 10, "max": 100, "default": 50, "step": 5, "unit": "px"}
            ]
            step["simulator_spec"] = simulator_spec
            return step

    async def _generate_custom_code(
        self,
        topic: str,
        description: str,
        variables: list,
        course_title: str,
        lesson_title: str,
        source_material: str
    ) -> Optional[Dict[str, Any]]:
        """使用 AI 生成自定义模拟器代码"""
        from app.services.studio.custom_code_generator import (
            CUSTOM_CODE_SYSTEM_PROMPT,
            get_custom_code_prompt,
            validate_custom_code
        )

        try:
            user_prompt = get_custom_code_prompt(topic, description, variables)

            # 添加课程上下文
            context_prompt = f"""
课程: {course_title}
课时: {lesson_title}
主题: {topic}

相关材料摘要:
{source_material[:2000]}

{user_prompt}
"""

            response = await self.claude_service.generate_raw_response(
                prompt=context_prompt,
                system_prompt=CUSTOM_CODE_SYSTEM_PROMPT,
                temperature=0.7,
                max_tokens=4000
            )

            code = response.strip()

            # 移除可能的markdown代码块标记
            if code.startswith("```"):
                lines = code.split("\n")
                code = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

            # 验证代码
            is_valid, error_msg = validate_custom_code(code)
            if not is_valid:
                logger.warning(f"[CustomCode] Generated code validation failed: {error_msg}")
                return None

            return {
                "success": True,
                "code": code,
                "variables": variables
            }

        except Exception as e:
            logger.error(f"[CustomCode] Failed to generate code: {e}")
            return None

    def _get_default_custom_code(self, step_title: str, description: str) -> str:
        """生成默认的自定义模拟器代码"""
        return f'''// {step_title} - 默认模拟器
let elements = {{}};

function setup(ctx) {{
  const {{ width, height }} = ctx;

  // 创建标题
  ctx.createText('{step_title}', width/2, 30, {{
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff'
  }});

  // 创建说明文字
  ctx.createText('拖动滑块调整参数', width/2, 60, {{
    fontSize: 14,
    color: '#94a3b8'
  }});

  // 创建主要演示元素
  elements.main = ctx.createCircle(width/2, height/2, 30, '#fbbf24');

  // 创建轨迹线
  const points = [];
  for (let i = 0; i < 10; i++) {{
    points.push({{ x: 100 + i * 70, y: height/2 }});
  }}
  elements.track = ctx.createLine(points, '#334155', 2);
}}

function update(ctx) {{
  const speed = ctx.getVar('speed') || 3;
  const amplitude = ctx.getVar('amplitude') || 50;

  // 计算位置
  const x = ctx.width/2 + ctx.math.sin(ctx.time * speed) * amplitude * 2;
  const y = ctx.height/2 + ctx.math.cos(ctx.time * speed * 0.5) * amplitude;

  // 更新元素位置
  ctx.setPosition(elements.main, x, y);

  // 根据速度调整透明度
  const alpha = 0.5 + ctx.math.abs(ctx.math.sin(ctx.time * speed)) * 0.5;
  ctx.setAlpha(elements.main, alpha);
}}
'''

    def _match_template_by_content(
        self,
        course_title: str,
        lesson_title: str,
        step_title: str,
        source_material: str
    ) -> Optional[Dict[str, Any]]:
        """根据课程内容智能匹配最合适的模板"""
        combined_text = f"{course_title} {lesson_title} {step_title} {source_material}".lower()

        # 关键词到模板的映射
        keyword_template_map = {
            # 游泳相关
            ("游泳", "蛙泳", "自由泳", "蝶泳", "仰泳", "划水", "打腿", "换气"): "sports_swimming_stroke",
            # 跳高相关
            ("跳高", "助跑", "起跳", "过杆", "背越式"): "sports_jump_approach",
            # 短跑相关
            ("短跑", "起跑", "冲刺", "百米", "起跑器"): "sports_sprint_start",
            # 跳远相关
            ("跳远", "三级跳", "踏板"): "sports_long_jump",
            # 铅球相关
            ("铅球", "投掷", "推铅球"): "sports_shot_put",
            # 篮球相关
            ("篮球", "投篮", "三分", "罚球"): "sports_basketball_shooting",
            ("扣篮", "灌篮"): "sports_basketball_dunk",
            # 足球相关
            ("足球", "射门", "踢球"): "sports_football_kick",
            ("倒钩", "倒挂金钩"): "sports_football_bicycle_kick",
            # 网球相关
            ("网球", "发球", "正手", "反手"): "sports_tennis_serve",
            # 排球相关
            ("排球", "扣球", "拦网"): "sports_volleyball_spike",
            # 羽毛球相关
            ("羽毛球", "杀球", "高远球"): "sports_badminton_smash",
            # 乒乓球相关
            ("乒乓球", "发球", "旋转"): "sports_table_tennis_serve",
            # 体操相关
            ("体操", "跳马", "鞍马"): "sports_gymnastics_vault",
            ("空翻", "翻腾", "自由体操"): "sports_gymnastics_floor_flip",
            ("单杠", "高低杠"): "sports_gymnastics_high_bar",
            # 跳水相关
            ("跳水", "跳台", "跳板"): "sports_diving_platform",
            ("转体", "翻腾"): "sports_diving_twist",
            # 滑冰相关
            ("滑冰", "花样滑冰", "旋转"): "sports_figure_skating_spin",
            ("跳跃", "阿克塞尔"): "sports_figure_skating_jump",
            # 跨栏相关
            ("跨栏", "栏架"): "sports_hurdles",
            # 接力相关
            ("接力", "交接棒"): "sports_relay_race",
            # 铁饼相关
            ("铁饼", "掷铁饼"): "sports_discus_throw",
            # 撑杆跳相关
            ("撑杆跳", "撑竿跳"): "sports_pole_vault",
            # 标枪相关
            ("标枪", "掷标枪"): "sports_javelin_throw",
            # 高尔夫相关
            ("高尔夫", "挥杆"): "sports_golf_swing",
            # 曲棍球相关
            ("曲棍球", "冰球"): "sports_hockey_shot",
            # 滑雪相关
            ("滑雪", "回转"): "sports_skiing_slalom",
            # 赛艇相关
            ("赛艇", "划船", "皮划艇"): "sports_rowing_technique",
            # 射箭相关
            ("射箭", "弓箭"): "sports_archery_shot",
            # 击剑相关
            ("击剑", "剑术"): "sports_fencing_lunge",
            # 自行车相关
            ("自行车", "骑行", "冲刺"): "sports_cycling_sprint",
            # 举重相关
            ("举重", "抓举", "挺举"): "sports_weightlifting_snatch",
            # 瑜伽相关
            ("瑜伽", "体式"): "sports_yoga_pose",
            # 跆拳道相关
            ("跆拳道", "踢腿"): "sports_taekwondo_kick",
            # 拳击相关
            ("拳击", "出拳"): "sports_boxing_punch",
            # 物理相关
            ("力", "牛顿", "合力", "分力"): "physics_force_composition",
            ("抛物线", "抛体", "平抛", "斜抛"): "physics_projectile_motion",
            ("电路", "电阻", "电流", "电压"): "physics_circuit",
            ("单摆", "摆动", "周期"): "physics_pendulum",
        }

        # 遍历关键词映射，找到匹配的模板
        for keywords, template_id in keyword_template_map.items():
            if any(kw in combined_text for kw in keywords):
                template = get_template(template_id)
                if template:
                    logger.info(f"[SDL] Matched template '{template_id}' by keywords: {keywords}")
                    return template

        return None

    def _upgrade_basic_shapes(
        self,
        elements: List[Dict[str, Any]],
        course_title: str,
        lesson_title: str,
        step_title: str
    ) -> List[Dict[str, Any]]:
        """检查并升级基础形状为语义形状"""
        combined_text = f"{course_title} {lesson_title} {step_title}".lower()

        # 基础形状到语义形状的映射规则
        shape_upgrade_rules = {
            # 运动相关
            ("游泳", "泳", "划水", "蛙泳", "蝶泳", "自由泳"): "swimmer",
            ("跑步", "短跑", "冲刺", "起跑"): "runner",
            ("跳", "跳高", "跳远", "跳跃"): "jumper",
            ("人", "运动员", "选手"): "person",
            # 球类
            ("足球", "射门"): "football",
            ("篮球", "投篮"): "basketball",
            ("排球", "扣球"): "volleyball",
            ("球",): "ball",
            # 器械
            ("杠铃", "举重"): "barbell",
            ("跨栏", "栏架"): "hurdle",
            ("跳板", "跳水"): "diving_board",
            ("球门",): "goal",
            ("篮筐",): "basket",
            # 场地
            ("泳池", "泳道", "游泳池"): "pool_lane",
            ("跑道", "赛道"): "track_lane",
            ("水", "水面", "水中"): "water",
        }

        # 确定应该使用的语义形状
        target_shape = None
        for keywords, shape_type in shape_upgrade_rules.items():
            if any(kw in combined_text for kw in keywords):
                target_shape = shape_type
                break

        if not target_shape:
            target_shape = "person"  # 默认使用人物形状

        # 检查并替换基础形状
        basic_shapes = {"circle", "rectangle", "rect", "ellipse", "line"}
        upgraded_elements = []

        for elem in elements:
            elem_type = elem.get("type", "").lower()
            elem_layer = elem.get("layer", "content")

            # 只替换内容层的基础形状，保留背景层
            if elem_type in basic_shapes and elem_layer == "content" and elem.get("animated", False):
                logger.info(f"[SDL] Upgrading basic shape '{elem_type}' to semantic shape '{target_shape}'")
                # 替换为语义形状
                upgraded_elem = elem.copy()
                upgraded_elem["type"] = target_shape
                # 移除基础形状特有的属性
                if "size" in upgraded_elem:
                    del upgraded_elem["size"]
                upgraded_elements.append(upgraded_elem)
            else:
                upgraded_elements.append(elem)

        return upgraded_elements

    async def _generate_sdl_scene(
        self,
        course_title: str,
        lesson_title: str,
        step_title: str,
        sim_type: str,
        scenario_desc: str,
        source_material: str,
        system_prompt: str
    ) -> Dict[str, Any]:
        """生成 SDL 格式的场景配置"""
        logger.info(f"Generating SDL scene for: {step_title}")

        # 使用SDL编译器生成带有开始和重置按钮的场景
        return self._get_default_sdl_scene(step_title, scenario_desc)

    def _get_default_sdl_scene(self, step_title: str, scenario_desc: str = "") -> Dict[str, Any]:
        """使用SDL编译器生成默认场景，包含开始和重置按钮"""
        # 根据标题智能选择语义形状
        title_lower = step_title.lower()
        if any(kw in title_lower for kw in ["游泳", "泳", "划水"]):
            element_type = "swimmer"
            element_name = "游泳者"
            bg_color = "#0c4a6e"
        elif any(kw in title_lower for kw in ["跑", "冲刺", "起跑"]):
            element_type = "runner"
            element_name = "跑步者"
            bg_color = "#1e293b"
        elif any(kw in title_lower for kw in ["跳", "跳高", "跳远"]):
            element_type = "jumper"
            element_name = "跳跃者"
            bg_color = "#1e293b"
        elif any(kw in title_lower for kw in ["球", "投篮", "射门"]):
            element_type = "ball"
            element_name = "球"
            bg_color = "#1e293b"
        else:
            element_type = "person"
            element_name = "演示人物"
            bg_color = "#0f172a"

        # 创建AI输入格式
        ai_input = {
            "scene": {
                "title": step_title,
                "description": scenario_desc or f"{step_title}的交互模拟",
                "background_color": bg_color
            },
            "elements": [
                {
                    "id": "demo_element",
                    "name": element_name,
                    "type": element_type,
                    "position": {"x": 200, "y": 250},
                    "color": "#fbbf24",
                    "layer": "content",
                    "animated": True
                }
            ],
            "phases": [
                {
                    "name": "阶段一",
                    "description": "第一阶段演示",
                    "animation": {
                        "target": "demo_element",
                        "keyframes": [
                            {"position": {"x": 200, "y": 250}},
                            {"position": {"x": 400, "y": 250}}
                        ],
                        "duration": 1500
                    }
                },
                {
                    "name": "阶段二",
                    "description": "第二阶段演示",
                    "animation": {
                        "target": "demo_element",
                        "keyframes": [
                            {"position": {"x": 400, "y": 250}},
                            {"position": {"x": 600, "y": 250}}
                        ],
                        "duration": 1500
                    }
                }
            ]
        }

        # 使用SDL编译器生成
        compiler = SDLCompiler()
        validator = SDLValidator()
        fixer = SDLAutoFixer()

        sdl = compiler.compile(ai_input)

        # 验证并修复
        sdl = fixer.fix_and_validate(sdl, validator)

        logger.info(f"[SDL] Generated scene with {len(sdl.get('elements', []))} elements, "
                   f"{len(sdl.get('interactions', []))} interactions")

        return sdl

    def _check_topic_depth(self, step_title: str, scenario_desc: str) -> bool:
        """检查模拟器课题深度是否足够，返回 True 表示适合做模拟器

        注意：始终返回 True，确保所有模拟器都能正常显示 SDL 场景
        """
        # 始终允许生成模拟器，确保 SDL 场景能正常显示
        logger.info(f"Topic depth check passed for: {step_title}")
        return True

    def _validate_and_fix_pixi_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证并修复模拟器配置，确保：
        1. 所有有动画的元素必须有 phase 属性
        2. 按钮必须有 isPhaseButton 和 targetPhase
        3. 元素位置合理
        4. 没有重复的动画
        """
        if not config or "elements" not in config:
            return config

        elements = config.get("elements", [])
        phases_list = config.get("phases", {}).get("list", [])

        # 收集所有阶段
        found_phases = set()
        for el in elements:
            if el.get("phase"):
                found_phases.add(el["phase"])
            if el.get("targetPhase"):
                found_phases.add(el["targetPhase"])

        # 如果没有定义 phases，从元素中收集
        if not phases_list and found_phases:
            phases_list = list(found_phases)
            if "phases" not in config:
                config["phases"] = {}
            config["phases"]["list"] = phases_list
            config["phases"]["initial"] = "none"

        fixed_elements = []
        for el in elements:
            # 修复1：有动画但没有 phase 的元素，移除动画
            if el.get("animation") and not el.get("phase"):
                logger.warning(f"Element '{el.get('id')}' has animation but no phase, removing animation")
                del el["animation"]

            # 修复2：检测并标记按钮
            is_button = el.get("isPhaseButton", False)
            if not is_button and el.get("type") == "zone" and el.get("y", 0) > 400 and el.get("label"):
                btn_keywords = ['开始', '查看', '完成', '提交', '确认', '重置', '报告', '演示', '场景', '阶段', '步骤', '流程']
                if any(kw in el.get("label", "") for kw in btn_keywords):
                    is_button = True
                    el["isPhaseButton"] = True
                    logger.info(f"Auto-detected button: {el.get('label')}")

            # 修复3：按钮必须有 targetPhase
            if is_button and not el.get("targetPhase"):
                # 尝试从 label 推断 targetPhase
                label = el.get("label", "")
                if label in phases_list:
                    el["targetPhase"] = label
                elif phases_list:
                    # 按钮顺序对应阶段顺序
                    btn_index = len([e for e in fixed_elements if e.get("isPhaseButton")])
                    if btn_index < len(phases_list):
                        el["targetPhase"] = phases_list[btn_index]
                logger.info(f"Set targetPhase for button '{label}': {el.get('targetPhase')}")

            # 修复4：按钮不应该有动画
            if is_button and el.get("animation"):
                logger.warning(f"Button '{el.get('id')}' should not have animation, removing")
                del el["animation"]

            # 修复5：按钮不应该有 phase（按钮始终可见）
            if is_button and el.get("phase"):
                logger.warning(f"Button '{el.get('id')}' should not have phase, removing")
                del el["phase"]

            fixed_elements.append(el)

        config["elements"] = fixed_elements

        # 验证结果
        buttons = [e for e in fixed_elements if e.get("isPhaseButton")]
        animated = [e for e in fixed_elements if e.get("animation")]
        phased = [e for e in fixed_elements if e.get("phase")]

        logger.info(f"Pixi config validated: {len(buttons)} buttons, {len(animated)} animated, {len(phased)} phased elements")

        # 最终检查：所有有动画的元素必须有 phase
        for el in animated:
            if not el.get("phase"):
                logger.error(f"CRITICAL: Element '{el.get('id')}' still has animation without phase!")

        return config

    async def _generate_pixi_config(
        self,
        course_title: str,
        lesson_title: str,
        step_title: str,
        sim_type: str,
        scenario_desc: str,
        source_material: str,
        system_prompt: str,
        require_complex: bool = False
    ) -> Dict[str, Any]:
        """使用 AI 生成 Pixi.js 高质量模拟器配置"""

        prompt = f"""你是一个专业的教育游戏视觉设计师。为课程"{course_title}"的"{lesson_title}"课时设计一个精美的 Pixi.js 交互模拟器。

【任务背景】
模拟器标题：{step_title}
场景描述：{scenario_desc}

【核心原则：图标必须严格匹配内容含义】
每个元素的 texture（图标类型）必须精确反映其 label（标签）的含义。
每个元素的 animation（动画效果）必须符合其代表的动作或状态。

【阶段控制系统】
如果模拟器需要分步展示（如动作分解、流程演示），必须使用阶段控制：

1. 在 phases 中定义阶段：
   "phases": {{ "initial": "all", "list": ["助跑", "起跳", "过杆", "落地", "all"] }}

2. 给每个内容元素添加 phase 属性，指定它属于哪个阶段：
   "phase": "助跑"  // 只在"助跑"阶段显示

3. 在底部添加阶段切换按钮：
   {{
     "id": "btn_phase1",
     "type": "zone",
     "shape": "roundedRect",
     "x": 100, "y": 470,
     "width": 80, "height": 35,
     "fill": "#8B5CF6", "alpha": 0.9,
     "isPhaseButton": true,
     "targetPhase": "助跑",
     "label": "助跑",
     "labelStyle": {{ "fontSize": 14, "color": "#ffffff", "fontWeight": "bold" }}
   }}

【图标与动画匹配规则】

田径跳高场景（如果涉及跳高、助跑、起跳等）：
| 标签内容 | texture | animation | 说明 |
|---------|---------|-----------|------|
| 起跑点/起跑位置 | startPoint | pulse | 蹲踞式起跑姿势 |
| 弧线转弯/转弯点 | curvePoint | float | 身体倾斜转弯 |
| 起跳点/起跳位置 | takeoffPoint | shake | 起跳瞬间蓄力 |
| 横杆/跳高杆 | highJumpBar | 无 | 静态横杆 |
| 落地垫/海绵垫 | landingMat | 无 | 静态垫子 |
| 直线助跑/直线跑 | runningPath | 无 | 直线路径 |
| 弧线助跑/J形跑 | arcPath | 无 | 弧线路径 |
| 起跳姿势/蹬地 | jumperTakeoff | pulse | 起跳动作 |
| 背弓/过杆姿势 | jumperArch | float | 背弓过杆 |
| 落地姿势/着垫 | jumperLanding | 无 | 落地动作 |

运动/体育场景：
| 标签内容 | texture | animation |
|---------|---------|-----------|
| 跑步/奔跑 | running | float |
| 跳跃/跳起 | jumping | pulse |
| 游泳 | swimming | float |
| 骑行 | cycling | rotate |

人体/解剖场景：
| 标签内容 | texture | animation |
|---------|---------|-----------|
| 骨骼/骨头 | bone | 无 |
| 肌肉 | muscle | pulse |
| 关节 | joint | rotate |
| 心脏 | heart | pulse |
| 大脑/思维 | brain | pulse |
| 肺/呼吸 | lung | pulse |

科学/实验场景：
| 标签内容 | texture | animation |
|---------|---------|-----------|
| 实验/化学 | flask | float |
| 原子/分子 | atom | rotate |
| 机械/齿轮 | gear | rotate |
| 观察/研究 | microscope | 无 |

教育/学习场景：
| 标签内容 | texture | animation |
|---------|---------|-----------|
| 知识/学习 | book | pulse |
| 想法/创意 | lightbulb | pulse |
| 思考/认知 | brain | pulse |
| 目标/精准 | target | pulse |

【画布规格】
- 尺寸：800 x 500 像素
- 背景：深色渐变 ["#1a1a2e", "#16213e"]

【元素布局】
- 顶部 (y: 30-50)：标题和说明文字
- 中央区域 (y: 100-400)：主要内容元素
- 底部 (y: 460-480)：阶段切换按钮（如果需要分步展示）

【JSON 配置格式 - 带阶段控制】
```json
{{
  "renderer": "pixi",
  "canvas_size": {{ "width": 800, "height": 500 }},
  "background": {{ "type": "gradient", "colors": ["#1a1a2e", "#16213e"] }},
  "phases": {{ "initial": "all", "list": ["助跑", "起跳", "落地", "all"] }},
  "elements": [
    {{
      "id": "title",
      "type": "text",
      "x": 400, "y": 30,
      "label": "背跃式跳高动作分解",
      "labelStyle": {{ "fontSize": 18, "color": "#22d3ee", "fontWeight": "bold" }}
    }},
    {{
      "id": "runner",
      "type": "sprite",
      "texture": "startPoint",
      "x": 150, "y": 250,
      "scale": 1.5,
      "tint": "#22C55E",
      "shadow": true,
      "label": "起跑姿势",
      "phase": "助跑",
      "animation": {{ "type": "pulse", "speed": 0.5 }}
    }},
    {{
      "id": "btn_run",
      "type": "zone",
      "shape": "roundedRect",
      "x": 120, "y": 470,
      "width": 80, "height": 35,
      "fill": "#8B5CF6", "alpha": 0.9,
      "isPhaseButton": true,
      "targetPhase": "助跑",
      "label": "助跑",
      "labelStyle": {{ "fontSize": 14, "color": "#ffffff", "fontWeight": "bold" }}
    }},
    {{
      "id": "btn_all",
      "type": "zone",
      "shape": "roundedRect",
      "x": 680, "y": 470,
      "width": 100, "height": 35,
      "fill": "#EF4444", "alpha": 0.9,
      "isPhaseButton": true,
      "targetPhase": "all",
      "label": "完整演示",
      "labelStyle": {{ "fontSize": 14, "color": "#ffffff", "fontWeight": "bold" }}
    }}
  ]
}}
```

【严格要求】
1. texture 必须与 label 的含义完全匹配（起跑点用 startPoint，不能用 star）
2. animation 必须符合动作特性（跳跃用 pulse，旋转用 rotate，漂浮用 float）
3. 禁止使用 circle/rect/star/diamond/hexagon 等简单几何图形
4. label 必须是具体的中文名称，不能是"概念1"这样的占位符
5. 如果是动作分解/流程演示类模拟器，必须使用阶段控制系统
6. 阶段按钮必须设置 isPhaseButton: true 和 targetPhase
7. 内容元素必须设置 phase 属性指定所属阶段
8. 只输出 JSON，不要任何其他文字

请根据场景描述 "{scenario_desc}" 生成配置："""

        try:
            response = await self.claude_service.generate_raw_response(
                prompt=f"{system_prompt}\n\n{prompt}",
                temperature=0.7,
                max_tokens=4000
            )

            # 解析 JSON
            json_str = response.strip()
            if json_str.startswith("```"):
                json_str = json_str.split("```")[1] if "```" in json_str[3:] else json_str[3:]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                json_str = json_str.strip()
            if json_str.endswith("```"):
                json_str = json_str[:-3].strip()

            config = json.loads(json_str)

            if isinstance(config, dict) and "elements" in config:
                return config

        except Exception as e:
            logger.error(f"Failed to generate Pixi config: {e}")

        # 返回默认高质量配置
        return self._get_default_pixi_config(step_title, scenario_desc)

    def _get_default_pixi_config(self, step_title: str, scenario_desc: str = "") -> Dict[str, Any]:
        """获取默认的高质量 Pixi 配置 - 按按钮播放动画类型"""
        return {
            "renderer": "pixi",
            "canvas_size": {"width": 800, "height": 500},
            "background": {
                "type": "gradient",
                "colors": ["#1a1a2e", "#16213e"]
            },
            "phases": {
                "initial": "准备",
                "list": ["准备", "动作一", "动作二", "动作三", "all"]
            },
            "elements": [
                # 标题
                {
                    "id": "title",
                    "type": "text",
                    "x": 400,
                    "y": 30,
                    "label": step_title,
                    "labelStyle": {"fontSize": 20, "color": "#22d3ee", "fontWeight": "bold"}
                },
                # 说明文字
                {
                    "id": "instruction",
                    "type": "text",
                    "x": 400,
                    "y": 60,
                    "label": "点击下方按钮查看不同阶段的动作演示",
                    "labelStyle": {"fontSize": 14, "color": "#94a3b8"}
                },
                # 中央演示区域
                {
                    "id": "demo_area",
                    "type": "zone",
                    "shape": "roundedRect",
                    "x": 400,
                    "y": 250,
                    "width": 600,
                    "height": 280,
                    "fill": "#1e293b",
                    "alpha": 0.5,
                    "border": {"color": "#334155", "width": 2}
                },
                # 阶段1内容
                {
                    "id": "phase1_content",
                    "type": "sprite",
                    "texture": "target",
                    "x": 400,
                    "y": 250,
                    "scale": 2.0,
                    "tint": "#22C55E",
                    "phase": "准备",
                    "animation": {"type": "pulse", "speed": 0.5}
                },
                {
                    "id": "phase1_text",
                    "type": "text",
                    "x": 400,
                    "y": 350,
                    "label": "准备阶段",
                    "phase": "准备",
                    "labelStyle": {"fontSize": 16, "color": "#e2e8f0"}
                },
                # 阶段2内容
                {
                    "id": "phase2_content",
                    "type": "sprite",
                    "texture": "running",
                    "x": 400,
                    "y": 250,
                    "scale": 2.0,
                    "tint": "#3B82F6",
                    "phase": "动作一",
                    "animation": {"type": "float", "speed": 0.6}
                },
                {
                    "id": "phase2_text",
                    "type": "text",
                    "x": 400,
                    "y": 350,
                    "label": "动作一",
                    "phase": "动作一",
                    "labelStyle": {"fontSize": 16, "color": "#e2e8f0"}
                },
                # 阶段3内容
                {
                    "id": "phase3_content",
                    "type": "sprite",
                    "texture": "jumping",
                    "x": 400,
                    "y": 250,
                    "scale": 2.0,
                    "tint": "#F59E0B",
                    "phase": "动作二",
                    "animation": {"type": "pulse", "speed": 0.7}
                },
                {
                    "id": "phase3_text",
                    "type": "text",
                    "x": 400,
                    "y": 350,
                    "label": "动作二",
                    "phase": "动作二",
                    "labelStyle": {"fontSize": 16, "color": "#e2e8f0"}
                },
                # 阶段4内容
                {
                    "id": "phase4_content",
                    "type": "sprite",
                    "texture": "trophy",
                    "x": 400,
                    "y": 250,
                    "scale": 2.0,
                    "tint": "#EF4444",
                    "phase": "动作三",
                    "animation": {"type": "pulse", "speed": 0.5}
                },
                {
                    "id": "phase4_text",
                    "type": "text",
                    "x": 400,
                    "y": 350,
                    "label": "动作三",
                    "phase": "动作三",
                    "labelStyle": {"fontSize": 16, "color": "#e2e8f0"}
                },
                # 按钮1 - 准备
                {
                    "id": "btn_phase1",
                    "type": "zone",
                    "shape": "roundedRect",
                    "x": 120,
                    "y": 465,
                    "width": 80,
                    "height": 35,
                    "fill": "#22C55E",
                    "alpha": 0.9,
                    "isPhaseButton": True,
                    "targetPhase": "准备",
                    "label": "准备",
                    "labelStyle": {"fontSize": 14, "color": "#ffffff", "fontWeight": "bold"}
                },
                # 按钮2 - 动作一
                {
                    "id": "btn_phase2",
                    "type": "zone",
                    "shape": "roundedRect",
                    "x": 220,
                    "y": 465,
                    "width": 80,
                    "height": 35,
                    "fill": "#3B82F6",
                    "alpha": 0.9,
                    "isPhaseButton": True,
                    "targetPhase": "动作一",
                    "label": "动作一",
                    "labelStyle": {"fontSize": 14, "color": "#ffffff", "fontWeight": "bold"}
                },
                # 按钮3 - 动作二
                {
                    "id": "btn_phase3",
                    "type": "zone",
                    "shape": "roundedRect",
                    "x": 320,
                    "y": 465,
                    "width": 80,
                    "height": 35,
                    "fill": "#F59E0B",
                    "alpha": 0.9,
                    "isPhaseButton": True,
                    "targetPhase": "动作二",
                    "label": "动作二",
                    "labelStyle": {"fontSize": 14, "color": "#ffffff", "fontWeight": "bold"}
                },
                # 按钮4 - 动作三
                {
                    "id": "btn_phase4",
                    "type": "zone",
                    "shape": "roundedRect",
                    "x": 420,
                    "y": 465,
                    "width": 80,
                    "height": 35,
                    "fill": "#EF4444",
                    "alpha": 0.9,
                    "isPhaseButton": True,
                    "targetPhase": "动作三",
                    "label": "动作三",
                    "labelStyle": {"fontSize": 14, "color": "#ffffff", "fontWeight": "bold"}
                },
                # 按钮5 - 完整演示
                {
                    "id": "btn_all",
                    "type": "zone",
                    "shape": "roundedRect",
                    "x": 680,
                    "y": 465,
                    "width": 100,
                    "height": 35,
                    "fill": "#8B5CF6",
                    "alpha": 0.9,
                    "isPhaseButton": True,
                    "targetPhase": "all",
                    "label": "完整演示",
                    "labelStyle": {"fontSize": 14, "color": "#ffffff", "fontWeight": "bold"}
                }
            ],
            "effects": {
                "gridLines": True
            }
        }

    async def _generate_simulator_elements(
        self,
        course_title: str,
        lesson_title: str,
        step_title: str,
        sim_type: str,
        scenario_desc: str,
        source_material: str,
        system_prompt: str
    ) -> List[Dict[str, Any]]:
        """使用 AI 生成模拟器的 SVG 元素配置 - 按按钮播放动画类型"""
        # 不再使用 AI 生成，直接返回默认的按钮动画配置
        return self._get_default_simulator_elements(step_title)

    def _get_default_simulator_elements(self, step_title: str) -> List[Dict[str, Any]]:
        """获取默认的模拟器元素配置 - 按按钮播放动画类型"""
        return [
            # 标题
            {
                "id": "title",
                "type": "text",
                "x": 400,
                "y": 35,
                "props": {
                    "text": step_title,
                    "fontSize": 20,
                    "fontWeight": "bold",
                    "fill": "#1e293b",
                    "textAnchor": "middle"
                }
            },
            # 说明文字
            {
                "id": "instruction",
                "type": "text",
                "x": 400,
                "y": 65,
                "props": {
                    "text": "点击下方按钮查看不同阶段的动作演示",
                    "fontSize": 13,
                    "fill": "#64748b",
                    "textAnchor": "middle"
                }
            },
            # 中央演示区域
            {
                "id": "demo_area",
                "type": "rect",
                "x": 100,
                "y": 100,
                "props": {
                    "width": 600,
                    "height": 300,
                    "fill": "#f1f5f9",
                    "fillOpacity": 0.5,
                    "stroke": "#cbd5e1",
                    "strokeWidth": 2,
                    "rx": 16
                }
            },
            # 按钮1
            {
                "id": "btn_1",
                "type": "rect",
                "x": 150,
                "y": 430,
                "props": {
                    "width": 100,
                    "height": 40,
                    "fill": "#22C55E",
                    "rx": 8
                },
                "label": "阶段一",
                "clickable": True
            },
            # 按钮2
            {
                "id": "btn_2",
                "type": "rect",
                "x": 280,
                "y": 430,
                "props": {
                    "width": 100,
                    "height": 40,
                    "fill": "#3B82F6",
                    "rx": 8
                },
                "label": "阶段二",
                "clickable": True
            },
            # 按钮3
            {
                "id": "btn_3",
                "type": "rect",
                "x": 410,
                "y": 430,
                "props": {
                    "width": 100,
                    "height": 40,
                    "fill": "#F59E0B",
                    "rx": 8
                },
                "label": "阶段三",
                "clickable": True
            },
            # 按钮4 - 完整演示
            {
                "id": "btn_all",
                "type": "rect",
                "x": 540,
                "y": 430,
                "props": {
                    "width": 120,
                    "height": 40,
                    "fill": "#8B5CF6",
                    "rx": 8
                },
                "label": "完整演示",
                "clickable": True
            }
        ]

    async def _enrich_step_content(
        self,
        course_title: str,
        lesson_title: str,
        step_title: str,
        current_body: str,
        source_material: str,
        system_prompt: str
    ) -> str:
        """为内容不足的步骤生成补充内容"""

        prompt = f"""你正在为课程"{course_title}"的"{lesson_title}"课时补充内容。

当前步骤标题：{step_title}
当前内容（需要扩充）：{current_body}

源材料参考：
{source_material[:4000]}

请为这个步骤生成详细的教学内容，要求：
1. 内容至少60字，精准无废话
2. 详细讲解该知识点的核心概念
3. 可以包含例子、解释、应用场景等
4. 保持与课程整体风格一致
5. 直接输出正文内容，不要JSON格式，不要标题

请直接输出补充后的完整正文内容："""

        response = await self.claude_service.generate_raw_response(
            prompt=f"{system_prompt}\n\n{prompt}",
            temperature=0.7,
            max_tokens=2000
        )

        # 清理响应，去除可能的代码块标记
        content = response.strip()
        if content.startswith("```"):
            content = content.split("```")[1] if "```" in content[3:] else content[3:]
            content = content.strip()

        # 如果生成的内容仍然太短，返回一个更详细的默认内容
        if len(content) < 100:
            content = f"""在本节中，我们将深入探讨{step_title}的核心概念和实际应用。

{step_title}是{lesson_title}中的重要组成部分。理解这一概念对于掌握整个课程内容至关重要。

首先，让我们了解{step_title}的基本定义和背景。这个概念在实际应用中有着广泛的用途，无论是在理论研究还是实践操作中都扮演着重要角色。

通过学习本节内容，你将能够：
- 理解{step_title}的核心原理
- 掌握相关的基本技能
- 将所学知识应用到实际场景中

接下来，我们将通过具体的例子和详细的解释，帮助你更好地理解和掌握这些知识点。"""

        return content

    async def _regenerate_lesson_content(
        self,
        course_title: str,
        source_material: str,
        lesson_title: str,
        lesson_index: int,
        complexity: str,
        system_prompt: str
    ) -> Dict[str, Any]:
        """当JSON解析失败时，重新生成课时内容"""

        prompt = f"""为课程"{course_title}"生成"{lesson_title}"的详细教学内容。

这是第{lesson_index + 1}课时，复杂度级别：{complexity}

源材料参考：
{source_material[:5000]}

请生成完整的课时内容，必须严格按照以下JSON格式输出（不要添加任何其他文字）：

{{
    "lesson_id": "lesson_{lesson_index + 1}",
    "title": "{lesson_title}",
    "order": {lesson_index},
    "total_steps": 3,
    "rationale": "本课时的设计理念说明",
    "script": [
        {{
            "step_id": "step_1",
            "type": "text_content",
            "title": "概念介绍",
            "content": {{
                "body": "这里是精准的教学内容，至少60字，讲解核心概念...",
                "key_points": ["要点1", "要点2", "要点3"]
            }}
        }},
        {{
            "step_id": "step_2",
            "type": "text_content",
            "title": "深入理解",
            "content": {{
                "body": "这里是进一步的讲解内容，至少60字...",
                "key_points": ["要点1", "要点2"]
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
                        "question": "关于本课时内容的问题？",
                        "options": ["选项A", "选项B", "选项C", "选项D"],
                        "correct": "A",
                        "explanation": "答案解释"
                    }}
                ],
                "pass_required": true
            }}
        }}
    ],
    "estimated_minutes": 15,
    "prerequisites": [],
    "learning_objectives": ["学习目标1", "学习目标2"],
    "complexity_level": "{complexity}"
}}"""

        response = await self.claude_service.generate_raw_response(
            prompt=f"{system_prompt}\n\n{prompt}",
            temperature=0.5,  # 降低温度以获得更稳定的JSON输出
            max_tokens=20000
        )

        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]

            lesson = json.loads(json_str.strip())
            lesson["lesson_id"] = lesson.get("lesson_id", f"lesson_{lesson_index + 1}")
            lesson["title"] = lesson.get("title", lesson_title)
            lesson["order"] = lesson_index
            lesson["total_steps"] = len(lesson.get("script", []))
            return lesson
        except json.JSONDecodeError:
            logger.error(f"Failed to regenerate lesson {lesson_index + 1}, using fallback")
            # 最终的 fallback，生成有实质内容的课时
            return self._create_fallback_lesson(lesson_title, lesson_index, complexity)

    def _generate_edges(self, lessons: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate edges between lessons"""
        edges = []
        for i in range(len(lessons) - 1):
            edges.append({
                "id": f"edge_{i}",
                "from": lessons[i].get("lesson_id", f"lesson_{i + 1}"),
                "to": lessons[i + 1].get("lesson_id", f"lesson_{i + 2}"),
                "type": "sequential"
            })
        return edges

    def _validate_and_fix_simulators(self, lesson: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证并修复课时中的模拟器内容

        检查每个 simulator 类型的步骤，验证其内容是否完整，
        如果有问题则记录警告并尝试补充默认值
        """
        script = lesson.get("script", [])
        if not script:
            return lesson

        fixed_script = []
        for step in script:
            if step.get("type") == "simulator":
                simulator_spec = step.get("simulator_spec", {})

                # 验证模拟器规格
                is_valid, result = validate_simulator_spec(simulator_spec)

                if not is_valid:
                    logger.warning(f"Simulator validation failed for step {step.get('step_id')}: {result.errors}")

                    # 尝试修复常见问题
                    simulator_spec = self._fix_simulator_spec(simulator_spec, result)
                    step["simulator_spec"] = simulator_spec

                    # 添加验证警告到步骤元数据
                    step["_validation_warnings"] = result.warnings
                    step["_validation_suggestions"] = result.suggestions

                elif result.warnings:
                    logger.info(f"Simulator warnings for step {step.get('step_id')}: {result.warnings}")
                    step["_validation_warnings"] = result.warnings

            fixed_script.append(step)

        lesson["script"] = fixed_script
        return lesson

    def _fix_simulator_spec(self, spec: Dict[str, Any], result) -> Dict[str, Any]:
        """
        尝试修复模拟器规格中的常见问题
        """
        sim_type = spec.get("type", "custom")

        # 确保基础字段存在
        if not spec.get("simulator_id"):
            spec["simulator_id"] = f"SIM-{uuid.uuid4().hex[:8]}"

        if not spec.get("name"):
            spec["name"] = spec.get("title", "交互模拟器")

        if not spec.get("description") or len(spec.get("description", "")) < 10:
            spec["description"] = f"这是一个{spec.get('name', '交互')}模拟器，帮助你理解相关概念。"

        if not spec.get("instructions"):
            spec["instructions"] = ["观察模拟器的变化", "尝试调整参数", "思考变量之间的关系"]

        # 根据类型修复特定字段
        if sim_type == "custom":
            self._fix_custom_simulator(spec)
        elif sim_type == "timeline":
            self._fix_timeline_simulator(spec)
        elif sim_type == "decision":
            self._fix_decision_simulator(spec)
        elif sim_type == "comparison":
            self._fix_comparison_simulator(spec)
        elif sim_type == "concept-map":
            self._fix_concept_map_simulator(spec)

        return spec

    def _fix_custom_simulator(self, spec: Dict[str, Any]):
        """修复理科模拟器"""
        inputs = spec.get("inputs", [])
        outputs = spec.get("outputs", [])

        # 确保至少有一个输入
        if not inputs:
            spec["inputs"] = [{
                "id": "param1",
                "name": "param1",
                "label": "参数1",
                "type": "slider",
                "defaultValue": 50,
                "min": 0,
                "max": 100,
                "step": 1,
                "unit": ""
            }]

        # 确保至少有一个输出
        if not outputs:
            spec["outputs"] = [{
                "id": "result1",
                "name": "result1",
                "label": "结果",
                "type": "number",
                "unit": "",
                "formula": "input.param1 * 2"
            }]

        # 修复输入字段
        for inp in spec.get("inputs", []):
            if not inp.get("id"):
                inp["id"] = inp.get("name", f"input_{uuid.uuid4().hex[:4]}")
            if not inp.get("name"):
                inp["name"] = inp.get("id")
            if not inp.get("label"):
                inp["label"] = inp.get("name", "参数")
            if not inp.get("type"):
                inp["type"] = "slider"
            if inp.get("min") is None:
                inp["min"] = 0
            if inp.get("max") is None:
                inp["max"] = 100

        # 修复输出字段
        for out in spec.get("outputs", []):
            if not out.get("id"):
                out["id"] = out.get("name", f"output_{uuid.uuid4().hex[:4]}")
            if not out.get("name"):
                out["name"] = out.get("id")
            if not out.get("label"):
                out["label"] = out.get("name", "结果")
            if not out.get("formula"):
                # 尝试生成一个简单的公式
                first_input = spec.get("inputs", [{}])[0]
                input_name = first_input.get("name", "param1")
                out["formula"] = f"input.{input_name}"

    def _fix_timeline_simulator(self, spec: Dict[str, Any]):
        """修复时间线模拟器"""
        timeline = spec.get("timeline", {})
        if not timeline:
            spec["timeline"] = {
                "title": spec.get("name", "时间线"),
                "events": []
            }
            timeline = spec["timeline"]

        if not timeline.get("title"):
            timeline["title"] = spec.get("name", "时间线")

        events = timeline.get("events", [])
        if not events:
            timeline["events"] = [
                {"id": "e1", "year": "阶段1", "title": "事件1", "description": "事件描述", "category": "默认", "highlight": True},
                {"id": "e2", "year": "阶段2", "title": "事件2", "description": "事件描述", "category": "默认", "highlight": False},
                {"id": "e3", "year": "阶段3", "title": "事件3", "description": "事件描述", "category": "默认", "highlight": False},
            ]

        # 修复每个事件
        for i, event in enumerate(timeline.get("events", [])):
            if not event.get("id"):
                event["id"] = f"e{i+1}"
            if not event.get("year"):
                event["year"] = f"阶段{i+1}"
            if not event.get("title"):
                event["title"] = f"事件{i+1}"
            if not event.get("description"):
                event["description"] = "事件描述待补充"

    def _fix_decision_simulator(self, spec: Dict[str, Any]):
        """修复决策模拟器"""
        decision = spec.get("decision", {})
        if not decision:
            spec["decision"] = {
                "title": spec.get("name", "决策情景"),
                "scenario": "请根据情景做出选择",
                "question": "你会如何选择？",
                "options": [],
                "analysis": ""
            }
            decision = spec["decision"]

        if not decision.get("title"):
            decision["title"] = spec.get("name", "决策情景")
        if not decision.get("scenario"):
            decision["scenario"] = "请根据情景做出选择"
        if not decision.get("question"):
            decision["question"] = "你会如何选择？"

        options = decision.get("options", [])
        if len(options) < 2:
            decision["options"] = [
                {"id": "opt1", "label": "选项A", "result": "选择A的结果", "isOptimal": True},
                {"id": "opt2", "label": "选项B", "result": "选择B的结果", "isOptimal": False},
                {"id": "opt3", "label": "选项C", "result": "选择C的结果", "isOptimal": False},
            ]

        # 确保有最优选项
        has_optimal = any(opt.get("isOptimal") for opt in decision.get("options", []))
        if not has_optimal and decision.get("options"):
            decision["options"][0]["isOptimal"] = True

        # 修复每个选项
        for i, opt in enumerate(decision.get("options", [])):
            if not opt.get("id"):
                opt["id"] = f"opt{i+1}"
            if not opt.get("label"):
                opt["label"] = f"选项{chr(65+i)}"
            if not opt.get("result"):
                opt["result"] = f"选择{opt.get('label', '')}的结果"

    def _fix_comparison_simulator(self, spec: Dict[str, Any]):
        """修复对比模拟器"""
        comparison = spec.get("comparison", {})
        if not comparison:
            spec["comparison"] = {
                "title": spec.get("name", "对比分析"),
                "dimensions": ["维度1", "维度2", "维度3"],
                "items": [],
                "conclusion": ""
            }
            comparison = spec["comparison"]

        if not comparison.get("title"):
            comparison["title"] = spec.get("name", "对比分析")

        dimensions = comparison.get("dimensions", [])
        if len(dimensions) < 2:
            comparison["dimensions"] = ["维度1", "维度2", "维度3"]
            dimensions = comparison["dimensions"]

        items = comparison.get("items", [])
        if len(items) < 2:
            comparison["items"] = [
                {"id": "item1", "name": "对象A", "attributes": {d: f"A的{d}" for d in dimensions}},
                {"id": "item2", "name": "对象B", "attributes": {d: f"B的{d}" for d in dimensions}},
            ]

        # 修复每个对比项
        for i, item in enumerate(comparison.get("items", [])):
            if not item.get("id"):
                item["id"] = f"item{i+1}"
            if not item.get("name"):
                item["name"] = f"对象{chr(65+i)}"
            if not item.get("attributes"):
                item["attributes"] = {d: f"{item.get('name', '')}的{d}" for d in dimensions}

    def _fix_concept_map_simulator(self, spec: Dict[str, Any]):
        """修复概念图模拟器"""
        concept_map = spec.get("concept_map", {})
        if not concept_map:
            spec["concept_map"] = {
                "title": spec.get("name", "概念关系图"),
                "nodes": [],
                "relations": []
            }
            concept_map = spec["concept_map"]

        if not concept_map.get("title"):
            concept_map["title"] = spec.get("name", "概念关系图")

        nodes = concept_map.get("nodes", [])
        if len(nodes) < 3:
            concept_map["nodes"] = [
                {"id": "n1", "label": "核心概念", "description": "核心概念描述", "category": "核心"},
                {"id": "n2", "label": "相关概念1", "description": "相关概念描述", "category": "相关"},
                {"id": "n3", "label": "相关概念2", "description": "相关概念描述", "category": "相关"},
                {"id": "n4", "label": "应用概念", "description": "应用概念描述", "category": "应用"},
            ]

        relations = concept_map.get("relations", [])
        if len(relations) < 2:
            concept_map["relations"] = [
                {"from_id": "n1", "to": "n2", "label": "包含"},
                {"from_id": "n1", "to": "n3", "label": "包含"},
                {"from_id": "n2", "to": "n4", "label": "应用于"},
            ]

        # 修复每个节点
        for i, node in enumerate(concept_map.get("nodes", [])):
            if not node.get("id"):
                node["id"] = f"n{i+1}"
            if not node.get("label"):
                node["label"] = f"概念{i+1}"

        # 修复每个关系
        for i, rel in enumerate(concept_map.get("relations", [])):
            # 处理 from/from_id 字段名差异
            if not rel.get("from_id") and rel.get("from"):
                rel["from_id"] = rel.pop("from")

    def _create_fallback_lesson(
        self,
        lesson_title: str,
        lesson_index: int,
        complexity: str
    ) -> Dict[str, Any]:
        """创建有实质内容的 fallback 课时"""
        return {
            "lesson_id": f"lesson_{lesson_index + 1}",
            "title": lesson_title,
            "order": lesson_index,
            "total_steps": 5,
            "rationale": f"本课时围绕{lesson_title}展开，帮助学习者建立系统的知识框架。",
            "script": [
                {
                    "step_id": "step_1",
                    "type": "text_content",
                    "title": f"{lesson_title} - 概述与背景",
                    "content": {
                        "body": f"""在本节中，我们将深入学习{lesson_title}的核心内容。

{lesson_title}是本课程的重要组成部分，理解这一概念对于掌握整体知识体系至关重要。

首先，让我们了解{lesson_title}的基本定义和背景。这个主题在理论和实践中都有着广泛的应用价值。

学习本节内容，你将能够：
- 理解{lesson_title}的核心原理和基本概念
- 掌握相关的分析方法和思维框架
- 将所学知识应用到实际问题解决中

接下来，我们将通过系统的讲解和具体的案例，帮助你深入理解这些知识点。请认真阅读并思考每个要点，这将为后续的学习打下坚实的基础。""",
                        "key_points": [
                            f"理解{lesson_title}的基本概念",
                            "掌握核心原理和方法",
                            "学会实际应用"
                        ]
                    }
                },
                {
                    "step_id": "step_2",
                    "type": "text_content",
                    "title": f"{lesson_title} - 核心原理",
                    "content": {
                        "body": f"""现在让我们深入探讨{lesson_title}的核心原理。

理解核心原理是掌握任何知识的关键。{lesson_title}的核心原理包含以下几个重要方面：

第一，基础理论框架。每个学科都有其独特的理论基础，{lesson_title}也不例外。我们需要首先建立起对基本概念的清晰认识。

第二，关键要素分析。在{lesson_title}中，有几个关键要素需要特别关注。这些要素相互关联，共同构成了完整的知识体系。

第三，实践应用方法。理论知识最终要服务于实践。了解如何将{lesson_title}的原理应用到实际场景中，是学习的重要目标。

通过对这些核心原理的学习，你将建立起扎实的知识基础，为后续的深入学习做好准备。""",
                        "key_points": [
                            "掌握基础理论框架",
                            "理解关键要素及其关系",
                            "学会实践应用方法"
                        ]
                    }
                },
                {
                    "step_id": "step_3",
                    "type": "text_content",
                    "title": f"{lesson_title} - 案例分析",
                    "content": {
                        "body": f"""让我们通过具体案例来加深对{lesson_title}的理解。

案例学习是将理论知识转化为实践能力的重要途径。通过分析真实或模拟的案例，我们可以更好地理解{lesson_title}在实际中的应用。

在这个案例中，我们将看到{lesson_title}的原理是如何被运用的。首先，我们需要识别问题的关键特征，然后运用所学的方法进行分析。

案例分析的步骤：
1. 明确问题背景和目标
2. 收集和整理相关信息
3. 运用{lesson_title}的原理进行分析
4. 得出结论并验证

通过这个案例，你应该能够更清楚地看到理论与实践之间的联系，并学会如何在类似情境中应用所学知识。""",
                        "key_points": [
                            "通过案例理解理论应用",
                            "掌握案例分析的基本步骤",
                            "建立理论与实践的联系"
                        ]
                    }
                },
                {
                    "step_id": "step_4",
                    "type": "text_content",
                    "title": f"{lesson_title} - 总结与拓展",
                    "content": {
                        "body": f"""让我们对{lesson_title}的学习内容进行总结，并探讨一些拓展方向。

本课时的主要内容回顾：
- 我们学习了{lesson_title}的基本概念和背景
- 深入理解了核心原理和关键要素
- 通过案例分析加深了对实际应用的认识

{lesson_title}是一个值得深入研究的领域。在掌握了基础知识之后，你可以进一步探索以下方向：

1. 深入研究相关的高级主题
2. 尝试将所学知识应用到实际项目中
3. 阅读更多相关的学术文献和案例
4. 与他人讨论和交流学习心得

记住，学习是一个持续的过程。保持好奇心和求知欲，不断探索和实践，你将在{lesson_title}领域取得更大的进步。""",
                        "key_points": [
                            "回顾本课时的核心内容",
                            "了解进一步学习的方向",
                            "建立持续学习的意识"
                        ]
                    }
                },
                {
                    "step_id": "step_5",
                    "type": "assessment",
                    "title": "知识检测",
                    "assessment_spec": {
                        "type": "quick_check",
                        "questions": [
                            {
                                "question": f"关于{lesson_title}，以下哪项描述最准确？",
                                "options": [
                                    "它是本课程的核心概念之一",
                                    "它与本课程内容无关",
                                    "它只在特定情况下适用",
                                    "它已经过时不再重要"
                                ],
                                "correct": "A",
                                "explanation": f"{lesson_title}是本课程的重要组成部分，理解它对于掌握整体知识体系非常关键。"
                            },
                            {
                                "question": f"学习{lesson_title}时，以下哪种方法最有效？",
                                "options": [
                                    "结合理论学习和案例分析",
                                    "只看理论不做练习",
                                    "跳过基础直接学高级内容",
                                    "死记硬背所有概念"
                                ],
                                "correct": "A",
                                "explanation": "结合理论学习和案例分析是最有效的学习方法，可以帮助你更好地理解和应用知识。"
                            }
                        ],
                        "pass_required": True
                    }
                }
            ],
            "estimated_minutes": 25,
            "prerequisites": [],
            "learning_objectives": [
                f"理解{lesson_title}的核心概念和背景",
                f"掌握{lesson_title}的基本原理",
                f"学会将{lesson_title}应用到实际场景"
            ],
            "complexity_level": complexity
        }

    def _get_default_processor_prompt(self, processor_id: str) -> str:
        """Get default processor system prompt"""
        for p in DEFAULT_PROCESSORS:
            if p["id"] == processor_id:
                return p.get("system_prompt", "")
        return DEFAULT_PROCESSORS[0].get("system_prompt", "")

    async def _evaluate_course_difficulty(
        self,
        course_title: str,
        lessons: List[Dict[str, Any]],
        source_material: str
    ) -> str:
        """
        AI 评估课程难度等级

        难度等级：
        - entry: 入门 - 零基础可学，概念简单直观
        - beginner: 基础 - 需要少量前置知识，内容较为基础
        - intermediate: 进阶 - 需要一定基础，涉及较复杂概念
        - advanced: 高级 - 需要扎实基础，内容深入专业
        - expert: 专家 - 需要丰富经验，涉及前沿或高度专业内容
        """
        try:
            # 构建课程摘要
            lesson_summaries = []
            for lesson in lessons[:5]:  # 最多取5个课时
                title = lesson.get("title", "")
                steps = lesson.get("script", [])
                step_types = [s.get("type", "") for s in steps]
                complexity = lesson.get("complexity_level", "standard")
                lesson_summaries.append(f"- {title} (复杂度: {complexity}, 步骤类型: {', '.join(step_types[:3])})")

            lessons_text = "\n".join(lesson_summaries)

            prompt = f"""请评估以下课程的难度等级。

课程标题：{course_title}

课时概览：
{lessons_text}

源材料摘要：
{source_material[:2000]}

难度等级说明：
- entry (入门): 零基础可学，概念简单直观，适合完全没有相关背景的学习者
- beginner (基础): 需要少量前置知识，内容较为基础，适合初学者
- intermediate (进阶): 需要一定基础，涉及较复杂概念，适合有一定经验的学习者
- advanced (高级): 需要扎实基础，内容深入专业，适合有丰富经验的学习者
- expert (专家): 需要丰富经验，涉及前沿或高度专业内容，适合专业人士

请根据课程内容的复杂度、所需前置知识、概念深度等因素，选择最合适的难度等级。

只输出一个单词（entry/beginner/intermediate/advanced/expert），不要其他内容。"""

            response = await self.claude_service.generate_raw_response(
                prompt=prompt,
                temperature=0.3,
                max_tokens=50
            )

            # 解析响应
            difficulty = response.strip().lower()
            valid_difficulties = ["entry", "beginner", "intermediate", "advanced", "expert"]

            if difficulty in valid_difficulties:
                logger.info(f"[Difficulty] Course '{course_title}' evaluated as: {difficulty}")
                return difficulty
            else:
                # 如果响应不是有效的难度等级，尝试从响应中提取
                for d in valid_difficulties:
                    if d in difficulty:
                        logger.info(f"[Difficulty] Course '{course_title}' evaluated as: {d} (extracted)")
                        return d

                # 默认返回 intermediate
                logger.warning(f"[Difficulty] Invalid response '{difficulty}', defaulting to intermediate")
                return "intermediate"

        except Exception as e:
            logger.error(f"[Difficulty] Failed to evaluate difficulty: {e}")
            return "intermediate"


# Singleton instance
_studio_service: Optional[StudioGenerationService] = None


def get_studio_service() -> StudioGenerationService:
    """Get studio service instance"""
    global _studio_service
    if _studio_service is None:
        _studio_service = StudioGenerationService()
    return _studio_service
