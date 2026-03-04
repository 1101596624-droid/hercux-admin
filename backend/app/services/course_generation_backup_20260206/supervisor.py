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
    6. 搜索最新信息确保内容时效性
    """

    def __init__(self):
        self.claude_service = ClaudeService()
        self.quality_standards = ChapterQualityStandards()
        self.conversation_messages: List[Dict[str, str]] = []
        self._search_service = None

    @property
    def search_service(self):
        """Lazy load search service"""
        if self._search_service is None:
            from app.services.deepseek_search_service import get_search_service
            self._search_service = get_search_service()
        return self._search_service

    async def search_latest_info(self, topic: str) -> str:
        """搜索最新信息"""
        try:
            return await self.search_service.search_for_context(topic, "academic")
        except Exception as e:
            logger.warning(f"Search failed: {e}")
            return ""

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

        prompt += """【要求】
1. 根据源材料的内容深度，合理划分章节（4-8章）
2. 每章要有明确的学习目标和核心概念
3. 章节之间要有逻辑递进关系
4. 为每章建议合适的模拟器主题（用于可视化演示核心概念）
5. 模拟器主题要具体、可实现，且各章不重复
6. 【重要】确保内容反映最新的研究成果和行业动态

【输出格式】
请以JSON格式输出：
{
    "title": "课程标题",
    "description": "课程描述（100-200字）",
    "total_chapters": 章节数量,
    "estimated_hours": 预计学时,
    "difficulty": "beginner/intermediate/advanced",
    "core_concepts": ["核心概念1", "核心概念2", ...],
    "chapters": [
        {
            "index": 0,
            "title": "章节标题",
            "chapter_type": "introduction/core_content/practice/assessment/summary",
            "recommended_forms": ["text_content", "simulator", "assessment"],
            "complexity_level": "simple/standard/advanced",
            "key_concepts": ["概念1", "概念2"],
            "learning_objectives": ["目标1", "目标2"],
            "suggested_simulator": "建议的模拟器主题（具体描述要演示什么）"
        }
    ]
}

请确保：
- 每章的 suggested_simulator 都不同，且与该章核心概念紧密相关
- 模拟器主题要具体到可以用代码实现（如"展示力的合成与分解"而非"物理模拟"）
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
        """获取质量要求说明 - 2026-02-06 专业级全面升级版"""
        return """
【质量要求 - 必须严格遵守（专业级全面升级版）】

=== 模拟器质量标准（最重要 - 严格执行）===

【画布尺寸】1000 x 650 像素

1. 代码结构要求（专业级）：
   - 必须有 setup(ctx) 函数：初始化所有视觉元素
   - 必须有 update(ctx) 函数：每帧更新，响应变量变化
   - 【专业级】代码至少 200 行，逻辑完整，视觉丰富
   - 【专业级】必须有至少 3 个辅助函数（如 drawObject、updateStats、createBackground 等）
   - 【专业级】代码必须有至少 10 处注释说明各部分功能
   - 代码结构清晰，变量命名规范

2. 变量要求（专业级）：
   - 【专业级】必须定义 4-8 个变量（variables 数组）
   - 每个变量必须在 update 中通过 ctx.getVar() 读取
   - 变量变化必须导致明显的视觉效果变化
   - 【专业级】每个变量必须有合理的 min/max/default/step 设置
   - 【专业级】变量的 label 必须清晰描述其作用和单位
   - 变量之间应有逻辑关联，形成完整的交互体验

3. 【专业级】视觉质量要求 - 禁止简陋图形：
   - 【严禁】只用简单的圆形或矩形代表复杂对象
   - 必须使用组合图形创建有辨识度的视觉元素
   - 【专业级】每个主要对象至少由 4-6 个基础图形组合而成
   - 必须使用多层次颜色增加视觉深度
   - 【专业级】必须使用至少 7 种不同的图形类型（circle, rect, text, line, curve, polygon, arc, path）
   - 【专业级】整个模拟器至少包含 25 个图形元素
   - 【专业级】使用至少 6 种不同颜色区分不同元素
   - 【专业级】必须有至少 8 个文字元素（标题、标签、数据显示等）
   - 【专业级】必须有背景装饰（网格线、渐变背景、边框等）
   - 【专业级】必须有状态/数据显示面板
   - 【专业级】必须有清晰的标题和图例
   - 【专业级】必须有坐标轴或刻度线增强可读性
   - 【专业级】必须有进度条或状态指示器

4. 动画要求（专业级）：
   - 必须有流畅的动画效果（位置、大小、旋转变化）
   - 使用 ctx.time 创建周期性动画
   - 【专业级】对象移动要平滑（使用 math.lerp 插值）
   - 【专业级】数值变化要有视觉反馈（颜色变化、大小变化等）
   - 【专业级】必须有至少 2 种不同类型的动画效果（位置动画+颜色动画、缩放动画+旋转动画等）
   - 动画要有节奏感，不能过快或过慢

5. 教学要求（专业级）：
   - 模拟器必须直观展示核心概念
   - 变量与视觉效果之间要有清晰的因果关系
   - 用户拖动滑块时，应该能立即看到效果变化
   - 【专业级】必须有图例说明各元素含义
   - 【专业级】必须有实时数据显示（数值、百分比、状态等）
   - 【专业级】必须有提示信息帮助用户理解
   - 模拟器应能帮助用户建立直观的概念理解

6. 禁止事项（严格执行）：
   - 不要使用 console.log、alert、document、window
   - 不要使用 setTimeout、setInterval（用 ctx.time 实现动画）
   - 不要使用 fetch、XMLHttpRequest、localStorage
   - 不要写空的或占位的代码
   - 【严禁】用单个圆形代表动物、人物等复杂对象
   - 【严禁】用单个矩形代表建筑、车辆等复杂对象
   - 【严禁】纯色背景无任何装饰
   - 【严禁】没有数据显示面板
   - 【严禁】没有标题和图例
   - 【严禁】代码少于200行

=== 模拟器代码示例（狼群捕猎策略模拟）===

```javascript
let elements = {};
let wolves = [];
let prey = null;

function setup(ctx) {
  const { width, height } = ctx;

  // 背景网格
  for (let x = 0; x < width; x += 50) {
    ctx.createLine([{x: x, y: 0}, {x: x, y: height}], '#2a3a4a', 1);
  }
  for (let y = 0; y < height; y += 50) {
    ctx.createLine([{x: 0, y: y}, {x: width, y: y}], '#2a3a4a', 1);
  }

  // 标题和图例
  elements.title = ctx.createText('狼群协作捕猎模拟', width/2, 30, {
    fontSize: 24, fontWeight: 'bold', color: '#ffffff'
  });

  // 图例背景
  ctx.createRect(120, 580, 200, 80, '#1a2a3a', 8);
  ctx.createCircle(50, 560, 8, '#6366f1');
  ctx.createText('狼群', 80, 560, { fontSize: 14, color: '#a5b4fc' });
  ctx.createCircle(50, 590, 10, '#f59e0b');
  ctx.createText('猎物', 80, 590, { fontSize: 14, color: '#fcd34d' });

  // 创建猎物（鹿）- 组合图形
  prey = {
    x: width * 0.7,
    y: height * 0.4,
    body: null,
    head: null,
    legs: [],
    antlers: []
  };

  // 创建狼群
  const wolfCount = 5;
  for (let i = 0; i < wolfCount; i++) {
    const angle = (i / wolfCount) * Math.PI * 2;
    wolves.push({
      x: width * 0.3 + Math.cos(angle) * 80,
      y: height * 0.5 + Math.sin(angle) * 80,
      body: null,
      head: null,
      tail: null,
      legs: []
    });
  }

  // 状态面板
  ctx.createRect(width - 150, 100, 260, 160, '#1e293b', 12);
  elements.statusTitle = ctx.createText('狩猎状态', width - 150, 50, {
    fontSize: 16, fontWeight: 'bold', color: '#94a3b8'
  });
  elements.distanceLabel = ctx.createText('距离: 0m', width - 150, 80, {
    fontSize: 14, color: '#60a5fa'
  });
  elements.energyLabel = ctx.createText('狼群体力: 100%', width - 150, 110, {
    fontSize: 14, color: '#34d399'
  });
  elements.successLabel = ctx.createText('成功率: 0%', width - 150, 140, {
    fontSize: 14, color: '#fbbf24'
  });

  // 能量条背景
  ctx.createRect(width - 150, 170, 200, 16, '#374151', 8);
  elements.energyBar = ctx.createRect(width - 200, 170, 150, 12, '#10b981', 6);
}

function update(ctx) {
  const { width, height, math, time } = ctx;
  const packSize = ctx.getVar('packSize');
  const aggressiveness = ctx.getVar('aggressiveness');
  const preySpeed = ctx.getVar('preySpeed');

  // 清除旧的狼和猎物图形
  wolves.forEach(wolf => {
    if (wolf.body) ctx.remove(wolf.body);
    if (wolf.head) ctx.remove(wolf.head);
    if (wolf.tail) ctx.remove(wolf.tail);
    wolf.legs.forEach(leg => ctx.remove(leg));
    wolf.legs = [];
  });

  if (prey.body) ctx.remove(prey.body);
  if (prey.head) ctx.remove(prey.head);
  prey.legs.forEach(leg => ctx.remove(leg));
  prey.antlers.forEach(a => ctx.remove(a));
  prey.legs = [];
  prey.antlers = [];

  // 猎物逃跑动画
  const escapeAngle = time * 0.5;
  prey.x = width * 0.6 + math.sin(escapeAngle) * 100 * (preySpeed / 50);
  prey.y = height * 0.4 + math.cos(escapeAngle * 0.7) * 60;

  // 绘制猎物（鹿）- 详细图形
  // 身体
  prey.body = ctx.createRect(prey.x, prey.y, 60, 35, '#d97706', 15);
  // 头部
  prey.head = ctx.createCircle(prey.x + 35, prey.y - 10, 12, '#f59e0b');
  // 腿
  for (let i = 0; i < 4; i++) {
    const legX = prey.x - 20 + (i % 2) * 40;
    const legY = prey.y + 25 + math.sin(time * 8 + i) * 5;
    prey.legs.push(ctx.createRect(legX, legY, 6, 25, '#b45309', 2));
  }
  // 鹿角
  prey.antlers.push(ctx.createLine([
    {x: prey.x + 40, y: prey.y - 20},
    {x: prey.x + 50, y: prey.y - 40},
    {x: prey.x + 55, y: prey.y - 35}
  ], '#92400e', 3));
  prey.antlers.push(ctx.createLine([
    {x: prey.x + 45, y: prey.y - 22},
    {x: prey.x + 60, y: prey.y - 38}
  ], '#92400e', 3));

  // 狼群追击
  const activeWolves = math.min(packSize, wolves.length);
  for (let i = 0; i < activeWolves; i++) {
    const wolf = wolves[i];

    // 计算追击方向
    const dx = prey.x - wolf.x;
    const dy = prey.y - wolf.y;
    const dist = math.sqrt(dx * dx + dy * dy);

    // 包围策略
    const surroundAngle = (i / activeWolves) * math.PI * 2 + time * 0.3;
    const targetX = prey.x - math.cos(surroundAngle) * (150 - aggressiveness);
    const targetY = prey.y - math.sin(surroundAngle) * (150 - aggressiveness);

    // 平滑移动
    wolf.x = math.lerp(wolf.x, targetX, 0.02 * aggressiveness / 50);
    wolf.y = math.lerp(wolf.y, targetY, 0.02 * aggressiveness / 50);

    // 绘制狼 - 详细图形
    const runPhase = time * 6 + i;

    // 身体（椭圆形）
    wolf.body = ctx.createRect(wolf.x, wolf.y, 45, 22, '#4b5563', 10);

    // 头部
    wolf.head = ctx.createCircle(wolf.x + 25, wolf.y - 5, 10, '#6b7280');

    // 耳朵
    ctx.createPolygon([
      {x: wolf.x + 20, y: wolf.y - 12},
      {x: wolf.x + 25, y: wolf.y - 25},
      {x: wolf.x + 30, y: wolf.y - 12}
    ], '#4b5563', '#374151');

    // 尾巴
    wolf.tail = ctx.createLine([
      {x: wolf.x - 20, y: wolf.y},
      {x: wolf.x - 35, y: wolf.y - 10 + math.sin(runPhase) * 8}
    ], '#4b5563', 6);

    // 腿（跑动动画）
    for (let j = 0; j < 4; j++) {
      const legX = wolf.x - 15 + (j % 2) * 30;
      const legOffset = math.sin(runPhase + j * math.PI / 2) * 8;
      wolf.legs.push(ctx.createRect(legX, wolf.y + 15 + legOffset, 5, 18, '#374151', 2));
    }

    // 眼睛（发光效果）
    ctx.createCircle(wolf.x + 28, wolf.y - 7, 3, '#fef08a');
  }

  // 计算统计数据
  let totalDist = 0;
  for (let i = 0; i < activeWolves; i++) {
    const dx = prey.x - wolves[i].x;
    const dy = prey.y - wolves[i].y;
    totalDist += math.sqrt(dx * dx + dy * dy);
  }
  const avgDist = activeWolves > 0 ? totalDist / activeWolves : 0;
  const energy = math.max(0, 100 - aggressiveness * 0.5 - time * 2);
  const successRate = math.min(95, packSize * 10 + aggressiveness * 0.5 - preySpeed * 0.3);

  // 更新状态显示
  ctx.setText(elements.distanceLabel, `平均距离: ${avgDist.toFixed(0)}m`);
  ctx.setText(elements.energyLabel, `狼群体力: ${energy.toFixed(0)}%`);
  ctx.setText(elements.successLabel, `预测成功率: ${math.max(0, successRate).toFixed(0)}%`);

  // 更新能量条
  ctx.remove(elements.energyBar);
  const barWidth = math.max(0, energy * 1.5);
  const barColor = energy > 60 ? '#10b981' : energy > 30 ? '#f59e0b' : '#ef4444';
  elements.energyBar = ctx.createRect(width - 200 + barWidth/2 - 75, 170, barWidth, 12, barColor, 6);
}
```

=== 内容质量标准（专业级）===

1. 【专业级】每章 7-12 个步骤，内容充实完整
2. 【专业级】每步正文至少 200 字，内容有深度有见解
3. 【专业级】每步至少 4 个要点，覆盖关键知识点
4. 【专业级】整章总字数至少 1500 字
5. 【专业级】每章必须有测验题目（至少 3 道）
6. 【专业级】每章必须有至少 2 个图文内容步骤
7. 【专业级】每章必须有总结步骤
8. 【专业级】必须有明确的学习目标（至少 3 个）
9. 【专业级】必须有设计理念说明（至少 50 字）
10. 不要有"待补充"、"..."、"暂无"、"略"、"以此类推"、"不再赘述"等占位内容

=== 图文内容标准（illustrated_content）- 专业级 ===

1. 【专业级】每章必须包含 2 个以上 illustrated_content 类型步骤
2. 【专业级】diagram_spec.description 必须详细描述图片内容（至少 80 字）
3. 描述应包含：主题、场景、关键元素、视觉风格、教学目的、色彩方案
4. 图片类型可以是：概念示意图、流程图、动作分解图、对比图、数据可视化图、场景图
5. 图片内容必须与该步骤的教学内容紧密相关
6. 【专业级】描述要具体到可以直接用于 AI 图片生成
7. 【专业级】必须列出至少 3 个图片关键元素（elements 数组）

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
            "type": "illustrated_content",
            "title": "图文讲解：xxx",
            "content": {{
                "body": "配合图片的讲解内容（至少100字）",
                "key_points": ["要点1", "要点2"]
            }},
            "diagram_spec": {{
                "diagram_id": "diagram_1",
                "type": "static_diagram",
                "description": "详细描述需要生成的图片内容，包括：主题、场景、元素、风格等。描述越详细，生成的图片越准确。例如：一张展示篮球运动员投篮姿势的示意图，包含正确的手臂角度、膝盖弯曲度和眼睛注视方向",
                "style": "educational",
                "elements": ["元素1", "元素2", "元素3"]
            }}
        }},
        {{
            "step_id": "step_3",
            "type": "simulator",
            "title": "互动模拟：xxx",
            "simulator_spec": {{
                "mode": "custom",
                "name": "模拟器名称（具体描述功能）",
                "description": "详细描述模拟器要展示什么概念、有什么交互效果（至少50字）",
                "variables": [
                    {{"name": "var1", "label": "变量1说明", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "单位"}},
                    {{"name": "var2", "label": "变量2说明", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "单位"}},
                    {{"name": "var3", "label": "变量3说明", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "单位"}},
                    {{"name": "var4", "label": "变量4说明", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "单位"}}
                ],
                "custom_code": ""
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

【极其重要 - 模拟器代码分步生成】
为避免JSON格式错误，模拟器的 custom_code 字段请留空（""）！
系统会在后续步骤自动根据 name、description 和 variables 生成完整代码。
你只需要：
1. 提供清晰的模拟器名称（name）
2. 提供详细的模拟器描述（description），说明要展示什么概念、有什么视觉效果
3. 定义 4-6 个有意义的变量（variables），每个变量要有合理的范围和单位
4. custom_code 留空字符串 ""

【重要 - 图文内容要求】
每章至少包含 1-2 个 illustrated_content 类型的步骤，用于展示：
- 概念示意图
- 动作分解图
- 流程图
- 对比图
- 数据可视化图

diagram_spec.description 必须详细描述图片内容，这将用于 AI 图片生成。

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
            issues.append("章节缺少测验题目（必须有）")
            content_score -= 20
        elif assessments:
            # 检查测验题目数量
            total_questions = sum(
                len(a.assessment_spec.get('questions', []))
                for a in assessments if a.assessment_spec
            )
            if hasattr(self.quality_standards, 'min_assessment_questions'):
                if total_questions < self.quality_standards.min_assessment_questions:
                    issues.append(f"测验题目太少，只有{total_questions}道，至少需要{self.quality_standards.min_assessment_questions}道")
                    content_score -= 10

        # === 6. 检查图文内容 ===
        illustrated = [s for s in chapter.script if s.type == 'illustrated_content']
        if hasattr(self.quality_standards, 'must_have_illustrated') and self.quality_standards.must_have_illustrated:
            if not illustrated:
                issues.append("章节缺少图文内容（illustrated_content）")
                content_score -= 15
            elif hasattr(self.quality_standards, 'min_illustrated_steps'):
                if len(illustrated) < self.quality_standards.min_illustrated_steps:
                    issues.append(f"图文内容太少，只有{len(illustrated)}个，至少需要{self.quality_standards.min_illustrated_steps}个")
                    content_score -= 10

        # === 7. 检查与大纲的一致性 ===
        if chapter.title != chapter_outline.title:
            suggestions.append(f"章节标题与大纲不一致，大纲为'{chapter_outline.title}'")

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
        if overall_score >= 80 and not simulator_issues:
            status = ReviewStatus.APPROVED
            review_comment = "章节质量优秀，符合专业级标准，可以继续下一章"
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
