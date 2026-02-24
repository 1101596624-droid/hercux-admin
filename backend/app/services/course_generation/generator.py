"""
生成者 AI - 负责根据监督者的指令生成单个章节
支持分步生成和 JSON 修复
"""

import json
import logging
import re
from typing import AsyncGenerator, Dict, Any, Optional, List

from app.services.llm_factory import get_llm_service
from .models import (
    GenerationState, ChapterResult, ChapterStep,
    ChapterOutline, CodeSyntaxError, SyntaxErrorType,
    HTMLSimulatorSpec, HTMLSimulatorQualityScore
)
from .standards_loader import get_standards_loader
from .template_service import TemplateService

logger = logging.getLogger(__name__)

# Canvas 2D API白名单 (2026-02-11: HTML格式使用Canvas 2D API)
CANVAS_2D_DRAWING_APIS = [
    # 基础矩形绘制
    'fillRect', 'strokeRect', 'clearRect',
    # 路径绘制
    'beginPath', 'closePath', 'moveTo', 'lineTo', 'arc', 'arcTo',
    'quadraticCurveTo', 'bezierCurveTo', 'rect', 'ellipse',
    # 填充和描边
    'fill', 'stroke', 'clip',
    # 文本
    'fillText', 'strokeText', 'measureText',
    # 图像
    'drawImage', 'createImageData', 'getImageData', 'putImageData',
    # 渐变和图案
    'createLinearGradient', 'createRadialGradient', 'createPattern',
    'addColorStop',
    # 变换
    'save', 'restore', 'scale', 'rotate', 'translate',
    'transform', 'setTransform', 'resetTransform',
    # 像素操作
    'createImageData', 'getImageData', 'putImageData',
]

CANVAS_2D_PROPERTIES = [
    'fillStyle', 'strokeStyle', 'lineWidth', 'lineCap', 'lineJoin',
    'miterLimit', 'lineDashOffset', 'font', 'textAlign', 'textBaseline',
    'direction', 'globalAlpha', 'globalCompositeOperation',
    'shadowBlur', 'shadowColor', 'shadowOffsetX', 'shadowOffsetY',
]

ANIMATION_APIS = ['requestAnimationFrame', 'cancelAnimationFrame']

# 所有有效的API（Canvas 2D API）
ALL_VALID_APIS = CANVAS_2D_DRAWING_APIS + CANVAS_2D_PROPERTIES + ANIMATION_APIS

# 禁止使用的API（常见错误写法）
FORBIDDEN_APIS = [
    # 简写形式（不存在）
    'rect', 'circle', 'line', 'text', 'polygon', 'curve',
    # draw前缀的错误写法（不存在）
    'drawRect', 'drawCircle', 'drawLine', 'drawText',
    # 不存在的方法
    'fillCircle', 'strokeCircle',  # Canvas没有这些
    'createPath', 'path',
    'updateText', 'updateCircle', 'updateRect', 'updateLine',
    'update', 'create',  # 单独的关键词
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

    def __init__(self, db=None):
        self.claude_service = get_llm_service()
        self.json_repair = JSONRepairTool()
        self.standards_loader = get_standards_loader()  # 新增：标准加载器
        self.db = db  # 数据库会话，用于模板学习

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

    # 旧的 generate_simulator_code 方法已删除（2026-02-11）
    # 现在统一使用 generate_simulator_code_progressive（async generator版本）

    async def generate_simulator_code_progressive(
        self,
        simulator_name: str,
        simulator_description: str,
        chapter_context: str,
        system_prompt: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        生产者-监督者架构生成HTML模拟器代码（async generator）

        HTML模拟器直接生成完整的HTML/JS代码，不需要variables配置

        Yields:
            {"type": "progress", "round": N, "max_rounds": 3, "stage": str, "message": str}
            {"type": "result", "code": str, "score": int, "source": "generated"|"fallback"}
        """
        max_rounds = 3
        best_code = None
        best_score = 0
        history = []

        for round_num in range(1, max_rounds + 1):
            logger.info(f"[Simulator Gen] Round {round_num}/{max_rounds} for '{simulator_name}'")

            # ========== 生产者生成代码 ==========
            if round_num == 1:
                yield {"type": "progress", "round": round_num, "max_rounds": max_rounds,
                       "stage": "generating", "message": f"正在生成HTML模拟器代码 (第{round_num}轮)..."}
                code = await self._producer_generate(
                    simulator_name=simulator_name,
                    simulator_description=simulator_description,
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
                           "stage": "generating", "message": f"重新生成HTML模拟器代码 (第{round_num}轮)..."}
                    code = await self._producer_generate(
                        simulator_name=simulator_name,
                        simulator_description=simulator_description,
                        system_prompt=system_prompt,
                        history=history
                    )
                else:
                    logger.info(f"[Producer] Decision: fix existing code")
                    yield {"type": "progress", "round": round_num, "max_rounds": max_rounds,
                           "stage": "fixing", "message": f"修复HTML模拟器代码 (第{round_num}轮)..."}
                    code = await self._producer_fix_code(
                        code=best_code,
                        issues=history[-1]['issues'] if history else [],
                        simulator_name=simulator_name,
                        system_prompt=system_prompt
                    )

            if not code:
                logger.warning(f"[Round {round_num}] Producer returned empty code")
                continue

            # ========== 监督者审核打分 ==========
            yield {"type": "progress", "round": round_num, "max_rounds": max_rounds,
                   "stage": "reviewing", "message": f"审核HTML模拟器代码 (第{round_num}轮)..."}

            # 1. 规则打分（80分）
            rule_score, rule_issues = self._supervisor_review(code)

            # 2. Agent打分（20分）
            yield {"type": "progress", "round": round_num, "max_rounds": max_rounds,
                   "stage": "agent_scoring", "message": f"Agent评估模拟器质量..."}
            agent_score, agent_feedback = await self._agent_review(code, simulator_name, simulator_description)

            # 3. 合并评分
            total_score = rule_score + agent_score

            # 4. AI监督者决策
            yield {"type": "progress", "round": round_num, "max_rounds": max_rounds,
                   "stage": "supervisor_decision", "message": f"AI监督者决策中..."}
            decision, reason = await self._supervisor_decision(
                code=code,
                simulator_name=simulator_name,
                rule_score=rule_score,
                agent_score=agent_score,
                agent_feedback=agent_feedback,
                rule_issues=rule_issues,
                round_num=round_num
            )

            logger.info(f"[Supervisor] Rule={rule_score}/60, Agent={agent_score}/40, Total={total_score}/100")
            logger.info(f"[Supervisor] Decision={decision}, Reason={reason}")

            history.append({
                'round': round_num,
                'rule_score': rule_score,
                'agent_score': agent_score,
                'total_score': total_score,
                'agent_feedback': agent_feedback,
                'issues': rule_issues,
                'decision': decision,
                'decision_reason': reason,
                'code_lines': len([l for l in code.split('\n') if l.strip()])
            })

            if total_score > best_score:
                best_score = total_score
                best_code = code

            # AI监督者决策
            if decision == 'accept':
                logger.info(f"[Simulator Gen] Supervisor accepted with score {total_score}/100")

                # 布局修复功能已删除（2026-02-15）
                # 原因：布局修复会破坏代码结构（删除DOCTYPE等必要元素）
                # 改为在生成提示词中要求AI直接生成符合规范的布局

                yield {"type": "result", "code": self._auto_fix_colors(code), "score": total_score, "source": "generated"}
                return
            elif decision == 'reject' and round_num < max_rounds:
                logger.warning(f"[Round {round_num}] Supervisor rejected (完全重做), reason: {reason}")
                continue
            elif decision == 'fix' and round_num < max_rounds:
                logger.info(f"[Round {round_num}] Supervisor requested fix (在当前基础上修复), reason: {reason}")
                # TODO: 实现基于当前代码的修复逻辑
                # 当前先继续生成，后续可以添加修复提示词
                continue
            else:
                # 最后一轮或其他情况
                logger.warning(f"[Round {round_num}] Score {total_score}/100, decision={decision}")

        # 所有轮次结束
        if best_code and best_score >= 40:
            logger.warning(f"[Simulator Gen] Using best code with score {best_score}/100")
            yield {"type": "result", "code": self._auto_fix_colors(best_code), "score": best_score, "source": "generated"}
        else:
            logger.error(f"[Simulator Gen] All rounds failed, returning empty HTML")
            # 返回一个简单的错误提示HTML，而不是fallback代码
            error_html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>{simulator_name}</title></head>
<body style="display:flex;align-items:center;justify-content:center;height:100vh;background:#0f172a;color:#ef4444;font-family:sans-serif;">
<div style="text-align:center;">
<h2>模拟器生成失败</h2>
<p>{simulator_name}</p>
<p style="color:#94a3b8;">请重试或联系管理员</p>
</div>
</body>
</html>"""
            yield {"type": "result", "code": error_html, "score": 0, "source": "fallback"}

    async def _fetch_learning_templates(self, subject: str, topic: str) -> str:
        """
        从数据库获取高质量模板并提取学习模式 (2026-02-11)

        Args:
            subject: 学科名称 (如 "physics", "mathematics")
            topic: 主题名称 (如 "projectile_motion", "matrix_operations")

        Returns:
            格式化的学习上下文字符串，包含API使用模式、颜色方案等
        """
        if not self.db:
            logger.warning("[Template Learning] No database session, skipping template learning")
            return ""

        try:
            template_service = TemplateService(self.db)

            # 获取相似的高质量模板 (最多2个，避免prompt过长)
            templates = await template_service.get_similar_templates(
                subject=subject,
                topic=topic,
                min_quality_score=75.0,
                limit=2
            )

            if not templates:
                logger.info(f"[Template Learning] No templates found for {subject}/{topic}")
                return ""

            # 分析模板模式
            patterns = await template_service.analyze_template_patterns(templates)

            # 格式化为学习上下文
            learning_context = template_service.format_learning_context(patterns, templates)

            logger.info(
                f"[Template Learning] Loaded {len(templates)} templates, "
                f"avg score {patterns['avg_quality_score']:.1f}"
            )

            return "\n" + learning_context + "\n"

        except Exception as e:
            logger.error(f"[Template Learning] Error fetching templates: {e}")
            return ""

    async def _producer_generate(
        self,
        simulator_name: str,
        simulator_description: str,
        system_prompt: str,
        history: Optional[List[Dict]] = None,
        subject: str = "physics",  # 学科，用于模板学习
        topic: str = ""  # 主题，用于模板学习
    ) -> Optional[str]:
        """生产者：生成完整HTML模拟器 (2026-02-10: 改为HTML格式，2026-02-11: 集成模板学习)"""

        # 获取模板学习上下文
        learning_context = await self._fetch_learning_templates(subject, topic)

        # 构建历史问题提示
        history_hint = ""
        if history:
            history_hint = "\n【之前的问题 - 必须避免】\n"
            for h in history:
                history_hint += f"- 第{h['round']}轮 ({h['total_score']}分): {', '.join(h['issues'][:3])}\n"

        prompt = f"""生成完整HTML模拟器。只输出完整的HTML代码，不要任何markdown标记或解释。

【模拟器】{simulator_name}
【描述】{simulator_description}
【画布尺寸限制 - 严格遵守】
- Canvas元素: <canvas id="canvas" width="1600" height="900"></canvas>
- 画布总尺寸: 1600×900 (16:9标准比例)
- 画布总面积: 1,440,000 平方像素

【绘制安全区域 - 极其重要,必须严格遵守】

⚠️ 图形元素安全区域 (圆形、矩形、线条、路径等):
- X坐标范围: [300, 1300]  (左右各留300px边距)
- Y坐标范围: [300, 600]   (上下各留300px边距)
- 安全区域尺寸: 1000×300
- 适用于: ctx.arc(), ctx.fillRect(), ctx.strokeRect(), ctx.lineTo(), ctx.moveTo(), ctx.bezierCurveTo() 等所有绘图操作

⚠️ UI元素安全区域 (文字框、按钮、滑块、数值显示等):
- X坐标范围: [100, 1500]  (左右各留100px边距)
- Y坐标范围: [100, 800]   (上下各留100px边距)
- 安全区域尺寸: 1400×700
- 适用于: ctx.fillText(), ctx.strokeText(), HTML控件的绝对定位等

⚠️ 推荐使用画布中心作为参考点:
- 中心点: (800, 450)
- 示例: 绘制中心圆形 → ctx.arc(800, 450, 150, 0, Math.PI*2)  // 半径150,在300px边距内
- 示例: 右上角文字框 → position: absolute; top: 120px; right: 120px;  // 距离边缘至少100px

【图形尺寸与布局约束 - 精致设计原则】

⚠️ 单个图形元素尺寸限制 (极其重要):
- 任何单个图形元素(圆形、矩形、多边形等)不得占据超过安全区域的40%
- 图形安全区域: 1000×300 = 300,000 平方像素
- 单个图形最大面积: 120,000 平方像素 (40%)
- 示例限制:
  * 圆形最大半径: √(120000/π) ≈ 195px
  * 矩形最大尺寸: 400×300px 或 600×200px (面积≤120,000)
  * 如果绘制单位圆等教学图形,半径建议≤180px,确保周围有足够空间放置标注和其他元素

⚠️ 【新增】所有元素总面积限制 (2026-02-15):
- 模拟器内所有可见元素(图形+UI控件+文字框)的面积总和不得超过画布面积的3/4
- 画布面积: 1600×900 = 1,440,000 平方像素
- 最大允许总面积: 1,080,000 平方像素 (75%)
- 计算方法:
  * 圆形面积 = π × r²
  * 矩形面积 = 宽 × 高
  * 文字框面积 = 宽 × 高 (估算)
  * 控件面板面积 = 宽 × 高
- 设计建议: 保持布局简洁,避免过度拥挤,留白空间有助于视觉清晰度

⚠️ 布局与排版原则:
- 主图形应居中或偏左,右侧留出空间放置信息面板/说明文字
- 多个图形元素应合理分布,避免拥挤
- 图形与文字标注之间保持至少30px间距
- 坐标轴、网格线等辅助元素应清晰但不抢眼(线宽1-2px,中灰色)

⚠️ 精致设计要求:
- 图形边缘平滑,线条粗细适中(2-3px为主要元素,1px为辅助线)
- 使用适当的阴影和渐变增强立体感(可选,不要过度)
- 文字标注字号适中(14-18px),位置精确,不与图形重叠
- 交互元素(拖动点、按钮)视觉明显,尺寸≥20px
- 整体视觉平衡,留白充足,不要填满整个画布


【配色原则 - 教学适用性】
✅ 必须遵守:
- 背景与前景对比度充足（文字清晰可读，对比度≥4.5:1）
- 网格线/辅助线清晰可见（使用中灰色如 #64748B、#94A3B8，不要用浅灰 #E2E8F0）
- 交互元素视觉明显（拖动手柄≥20px，按钮清晰，高对比度）
- 整体协调专业，适合长时间学习

✅ 推荐做法:
- 根据学科选择合适配色（物理-蓝色，生物-绿色，化学-多彩，数学-对比色）
- 使用2-3种主色，避免过多颜色造成混乱
- 重点元素用对比色突出（如红色标注关键点）
- 背景使用学科主题渐变色（非纯白），搭配淡色装饰纹理
  * 物理: #EFF6FF→#F8FAFC (浅蓝) + 横线/网格
  * 数学: #EEF2FF→#F5F3FF (靛蓝) + 方格纸/正弦波
  * 化学: #FFFBEB→#FFF7ED (暖黄) + 六边形分子网格
  * 生物: #ECFDF5→#F0FDF4 (浅绿) + 细胞圆/水波纹
  * 计算机: #F1F5F9→#E2E8F0 (冷灰) + 数字网格
- 控件面板区域使用半透明白色: rgba(255,255,255,0.92)
- 数据面板(drawPanel)使用与背景互补的学术风格配色，不要用白底:
  * drawPanel(ctx,x,y,w,h,title,bgColor,borderColor) — 支持自定义背景色和边框色
  * 蓝色背景 → 暖琥珀面板: bg='rgba(255,237,213,0.82)', bc='rgba(194,120,50,0.35)'
  * 天蓝背景 → 暖桃面板: bg='rgba(254,226,210,0.82)', bc='rgba(194,100,40,0.35)'
  * 暖黄背景 → 冷蓝面板: bg='rgba(219,234,254,0.82)', bc='rgba(59,130,246,0.35)'
  * 靛蓝背景 → 暖金面板: bg='rgba(254,249,195,0.82)', bc='rgba(161,98,7,0.30)'
  * 冷灰背景 → 暖米面板: bg='rgba(255,241,224,0.82)', bc='rgba(180,130,70,0.30)'
  * 绿色背景 → 玫瑰面板: bg='rgba(255,228,230,0.82)', bc='rgba(190,60,50,0.30)'
  * 紫色背景 → 青柠面板: bg='rgba(236,252,203,0.82)', bc='rgba(77,124,15,0.30)'
  * 青色背景 → 珊瑚面板: bg='rgba(255,228,225,0.82)', bc='rgba(190,60,50,0.30)'

❌ 禁止:
- 极低对比度（浅灰on白色，如 #E2E8F0 on #FFFFFF）
- 刺眼的高饱和度渐变（如紫红渐变）
- 过暗的背景（深色背景影响阅读，除非特殊需要）
{history_hint}
{learning_context}

【HTML标准结构 - 完整输出】
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{simulator_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif;
            background: #F8FAFC;
            color: #334155;
            overflow: hidden;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        #canvas {{
            display: block;
            background: #FFFFFF;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .controls {{
            margin-top: 20px;
            background: #FFFFFF;
            padding: 15px 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 1px solid #E2E8F0;
            display: flex;
            gap: 20px;
            align-items: center;
        }}
        .control-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .control-group label {{
            font-size: 12px;
            color: #64748B;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
        }}
        .value-display {{
            color: #2563EB;
            font-weight: 600;
            font-size: 14px;
        }}
        input[type="range"] {{
            width: 120px;
            height: 6px;
            background: rgba(100, 116, 139, 0.3);
            border-radius: 3px;
            outline: none;
            cursor: pointer;
        }}
        input[type="range"]::-webkit-slider-thumb {{
            appearance: none;
            width: 20px;
            height: 20px;
            background: #2563EB;
            border-radius: 50%%;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        button {{
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 600;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            background: #2563EB;
            color: #FFFFFF;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.2s;
        }}
        button:hover {{
            background: #1D4ED8;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        button:active {{
            transform: translateY(1px);
        }}
    </style>
</head>
<body>
    <canvas id="canvas" width="1600" height="900"></canvas>
    <div class="controls">
        <!-- 变量控制HTML将在这里生成 -->
    </div>
    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        let variables = {{/* 变量初始值 */}};

        // 变量监听器将在这里生成

        function animate() {{
            // 清屏 - 使用学科主题渐变背景（非纯白）
            // 物理: #EFF6FF→#F8FAFC  数学: #EEF2FF→#F5F3FF  化学: #FFFBEB→#FFF7ED
            // 生物: #ECFDF5→#F0FDF4  计算机: #F1F5F9→#E2E8F0
            const bg = ctx.createLinearGradient(0, 0, 0, 790);
            bg.addColorStop(0, '/* 学科主题色上 */');
            bg.addColorStop(1, '/* 学科主题色下 */');
            ctx.fillStyle = bg;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            // 可选: 添加淡色装饰纹理（网格/波纹/分子等，透明度≤0.06）
            // 控件面板区域
            ctx.fillStyle = 'rgba(255,255,255,0.92)';
            ctx.fillRect(0, 790, canvas.width, 110);

            // 在这里实现可视化逻辑
            // 使用 Canvas 2D API 绘制内容
            // 根据 variables 对象的值进行动态绘制

            requestAnimationFrame(animate);
        }}
        animate();
    </script>
</body>
</html>

【Canvas 2D API 参考 - 只能用这些标准API】

绘制形状：
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(x, y)
  ctx.arc(x, y, radius, startAngle, endAngle)
  ctx.quadraticCurveTo(cpx, cpy, x, y)
  ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x, y)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()
  ctx.fillRect(x, y, width, height)
  ctx.strokeRect(x, y, width, height)

文本：
  ctx.font = '16px Arial'
  ctx.textAlign = 'center' | 'left' | 'right'
  ctx.textBaseline = 'middle' | 'top' | 'bottom'
  ctx.fillText(text, x, y)
  ctx.strokeText(text, x, y)

样式：
  ctx.fillStyle = '#3B82F6'
  ctx.strokeStyle = '#60A5FA'
  ctx.lineWidth = 2
  ctx.lineCap = 'round' | 'butt' | 'square'
  ctx.lineJoin = 'round' | 'miter' | 'bevel'
  ctx.globalAlpha = 0.8
  ctx.shadowBlur = 10
  ctx.shadowColor = '#3B82F6'
  ctx.shadowOffsetX = 5
  ctx.shadowOffsetY = 5

变换：
  ctx.save()
  ctx.restore()
  ctx.translate(x, y)
  ctx.rotate(angle)  // 弧度
  ctx.scale(sx, sy)

【推荐配色方案 - 灵活选择】
根据学科特点选择合适配色:

物理/数学（理性学科）:
  主色: '#2563EB', '#3B82F6', '#60A5FA' (蓝色系)
  辅助: '#334155', '#64748B' (深灰)
  强调: '#EF4444' (红色)

生物/医学（生命学科）:
  主色: '#10B981', '#34D399', '#6EE7B7' (绿色系)
  辅助: '#334155', '#64748B' (深灰)
  强调: '#EF4444' (红色)

化学（多元素）:
  多彩配色: '#3B82F6'(蓝), '#10B981'(绿), '#F59E0B'(橙), '#EF4444'(红)
  用不同颜色区分不同元素/状态

历史/地理（人文学科）:
  主色: '#F59E0B', '#FBBF24' (橙黄色系)
  辅助: '#334155', '#64748B' (深灰)
  强调: '#EF4444' (红色)

通用颜色:
  文本色: '#0F172A', '#334155', '#64748B' (深色文字)
  背景色: '#FFFFFF', '#F8FAFC', '#F1F5F9' (浅色背景)
  网格/辅助线: '#94A3B8', '#64748B' (中灰色，清晰可见）
  成功: '#10B981' | 警告: '#F59E0B' | 错误: '#EF4444'

【核心要求】
1. 完整HTML文档（DOCTYPE + head + body）
2. 所有代码在单个文件中（self-contained）
3. 使用Canvas 2D API绘制（不使用外部库）
4. 使用requestAnimationFrame动画循环
5. 至少2个交互元素（滑块/按钮/拖动），必须视觉明显:
   - 滑块手柄≥20px
   - 按钮清晰可见，有hover效果
   - 拖动手柄用圆形标识，直径≥24px
   - 所有交互元素必须有清晰的视觉反馈
6. 实时显示数值变化
7. 画布尺寸：width="1600" height="900" (16:9标准比例,严格遵守,不可超出)
8. 配色协调美观，对比度充足
9. 代码清晰注释适当

【禁止项】
❌ 外部库（Three.js, D3.js等）
❌ 外部CSS文件（<link rel="stylesheet">标签）
❌ 外部字体文件（Google Fonts, fonts.font.im等,禁止<link>加载字体）
❌ 外部JavaScript文件（<script src="">标签）
❌ 所有CSS必须在<style>标签内，所有JS必须在<script>标签内
❌ 只使用系统字体: 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif
❌ eval(), Function(), setTimeout
❌ fetch(), XMLHttpRequest, localStorage
❌ 不要markdown代码块标记（```html等）
❌ 不要任何解释文字

【质量标准】
- 视觉清晰：配色协调、对比度充足（≥4.5:1）、网格线清晰可见
- 交互性：至少2个交互元素，视觉明显（大尺寸、高对比），实时响应
- 教育性：清晰展示概念，计算准确
- 代码质量：结构清晰，注释适当

【严格输出格式要求】（任务#7增强）
❌ 禁止：
- 不要输出 ``` 或 ```html 标记
- 不要输出任何解释文字
- 不要输出"这是一个HTML模拟器"等说明
- 不要输出JSON格式
- 不要输出多个HTML文件选项

✅ 必须：
- 直接以 <!DOCTYPE html> 开头
- 以 </html> 结尾
- 完整的单个HTML文件
- 所有CSS在<style>标签中
- 所有JavaScript在<script>标签中

【输出格式示例】
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{simulator_name}</title>
    <style>
        /* CSS样式 */
    </style>
</head>
<body>
    <canvas id="canvas" width="1600" height="900"></canvas>
    <div class="controls">
        <!-- 交互控件 -->
    </div>
    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        function animate() {{
            // 清屏
            ctx.fillStyle = '#0F172A';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 绘制内容

            requestAnimationFrame(animate);
        }}
        animate();
    </script>
</body>
</html>

【学习参考】
系统已导入24个标准HTML模拟器模板（质量分75分）供学习：
- 物理：圆周运动、抛体运动、弹簧振子
- 生物：细胞分裂、DNA复制、酶活性
- 化学：电子轨道、分子结构、化学平衡
- 医学：血液循环、免疫应答、神经信号
- 计算机：二叉树遍历、排序算法、图搜索
- 数学：傅里叶变换、参数曲线、矩阵运算
- 历史：事件因果、贸易路线、朝代时间轴
- 地理：水循环、气候带、板块运动

这些模板存储在 simulator_templates 表中，可作为实现参考。"""

        try:
            response = await self.claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=6000
            )
            logger.info(f"[Producer] Raw response length: {len(response)}, first 200 chars: {response[:200]}")
            cleaned = self._clean_simulator_code(response)
            if cleaned:
                logger.info(f"[Producer] Cleaned code: {len(cleaned.splitlines())} lines")
            else:
                logger.warning(f"[Producer] Cleaned code is empty! Raw response last 200 chars: {response[-200:]}")
            return cleaned
        except Exception as e:
            logger.error(f"[Producer] Generate error: {e}")
            return None

    async def _producer_decide_action(
        self,
        history: List[Dict],
        system_prompt: str
    ) -> str:
        """生产者：根据历史问题决定重做还是修改（2026-02-11: 适配HTML格式）"""
        if not history:
            return 'regenerate'

        last = history[-1]

        # HTML结构性问题 → 必须重做
        html_structural_keywords = [
            '缺少完整HTML结构',           # 没有DOCTYPE
            '缺少canvas元素',             # 核心元素缺失
            '缺少script脚本',             # 没有JS逻辑
            '代码严重不足', '代码太短',    # 代码量不够
            '元素太少',                   # 视觉元素不足
            '缺少动画循环',               # 无requestAnimationFrame
            '缺少交互控件',               # 没有input range
            '致命语法错误',               # 重复声明、括号不匹配等
            '括号错误',
        ]
        for issue in last['issues']:
            if any(kw in issue for kw in html_structural_keywords):
                return 'regenerate'

        # 分数太低 → 重做
        if last['total_score'] < 50:
            return 'regenerate'

        # 连续两轮但分数没有提升 → 重做
        if len(history) >= 2:
            prev = history[-2]
            if last['total_score'] <= prev['total_score']:
                return 'regenerate'

        # 表面问题（颜色、文本显示不足）→ 修改
        return 'fix'
        return 'fix'

    async def _producer_fix_code(
        self,
        code: str,
        issues: List[str],
        simulator_name: str,
        system_prompt: str,
        similar_failures: Optional[List[Dict]] = None
    ) -> Optional[str]:
        """
        生产者：修复现有代码（任务#7增强）

        增强功能：
        - 问题分类（critical/major/minor）
        - 检索相似失败案例
        - 定制化修复prompt
        - Agent反馈集成
        """
        if not code:
            return None

        # 1. 问题分类
        issue_category = self._classify_issues(issues)

        # 2. 检索相似失败案例（如果提供）
        pattern_solutions = []
        if similar_failures:
            pattern_solutions = self._extract_pattern_solutions(similar_failures)

        # 3. 构建定制化修复prompt
        prompt = self._build_fix_prompt(
            code=code,
            issues=issues,
            issue_category=issue_category,
            simulator_name=simulator_name,
            pattern_solutions=pattern_solutions
        )

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

    def _classify_issues(self, issues: List[str]) -> str:
        """
        问题分类（任务#7新增）

        Returns:
            'critical' | 'major' | 'minor'
        """
        critical_keywords = ['缺少完整HTML结构', '缺少canvas元素', '缺少script脚本',
                            '致命语法错误', '代码严重不足', '括号错误']

        major_keywords = ['缺少Canvas绘图调用', '缺少动画循环', '缺少交互控件',
                         '代码太短', '缺少事件监听器']

        critical_count = sum(1 for issue in issues if any(kw in issue for kw in critical_keywords))
        major_count = sum(1 for issue in issues if any(kw in issue for kw in major_keywords))

        if critical_count > 0:
            return 'critical'
        elif major_count >= 2:
            return 'major'
        else:
            return 'minor'

    def _extract_pattern_solutions(self, similar_failures: List[Dict]) -> List[str]:
        """
        从相似失败案例中提取解决方案（任务#7新增）

        Args:
            similar_failures: [{'issue': str, 'solution': str, 'success_rate': float}]

        Returns:
            解决方案列表
        """
        solutions = []
        for failure in similar_failures:
            if failure.get('success_rate', 0) >= 0.7:  # 只使用成功率>=70%的方案
                solutions.append(failure.get('solution', ''))

        return solutions[:3]  # 最多返回3个方案

    def _build_fix_prompt(
        self,
        code: str,
        issues: List[str],
        issue_category: str,
        simulator_name: str,
        pattern_solutions: List[str]
    ) -> str:
        """
        构建定制化修复prompt（任务#7新增）

        根据问题严重程度和已知解决方案构建不同的prompt
        """
        # 格式化问题列表
        issues_text = self._format_issues(issues)

        # 格式化解决方案
        solutions_text = self._format_pattern_solutions(pattern_solutions)

        # 根据问题严重程度选择修复策略
        fix_strategy = self._suggest_fix_strategy(issue_category)

        # 增强：严格输出要求和格式示例（任务#7缺陷4）
        prompt = f"""修复以下HTML模拟器代码。只输出修复后的完整HTML代码，不要任何解释。

【模拟器】{simulator_name}

【原代码】
{code[:2000]}{"..." if len(code) > 2000 else ""}

【需要修复的问题】（严重程度：{issue_category}）
{issues_text}

{solutions_text}

【修复策略】
{fix_strategy}

【修复要求】
1. 保持完整的HTML结构（<!DOCTYPE html>...）
2. 使用Canvas 2D API绘制图形
3. 只用亮色系（与深色背景形成对比）
4. 保持交互控件的响应性
5. 确保代码清晰注释适当

【修复原则】
- 保持原有布局和视觉元素的相对位置关系
- 修复问题时不要打乱已有的空间布局
- 所有坐标使用响应式计算，避免硬编码
- 保持动画的流畅性
- 如果有语法错误，修正但保持原有逻辑
- 如果有"重复声明变量"错误，删除重复的声明
- 如果有"中文标点"错误，将代码中的中文标点替换为英文标点

【严格输出格式要求】
❌ 禁止：
- 不要输出 ``` 或 ```html 标记
- 不要输出任何解释文字
- 不要输出"这是修复后的代码"等说明

✅ 必须：
- 直接以 <!DOCTYPE html> 开头
- 以 </html> 结尾
- 完整的单个HTML文件

【输出示例格式】
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{simulator_name}</title>
    <style>
        /* CSS样式 */
    </style>
</head>
<body>
    <canvas id="canvas" width="1600" height="900"></canvas>
    <script>
        // JavaScript代码
    </script>
</body>
</html>

现在请直接输出修复后的完整HTML代码："""

        return prompt

    def _format_issues(self, issues: List[str]) -> str:
        """格式化问题列表"""
        if not issues:
            return "  无"
        return '\n'.join([f"  - {issue}" for issue in issues])

    def _format_pattern_solutions(self, pattern_solutions: List[str]) -> str:
        """格式化解决方案"""
        if not pattern_solutions:
            return ""

        solutions_text = "\n【已知有效解决方案】\n"
        for i, solution in enumerate(pattern_solutions, 1):
            solutions_text += f"{i}. {solution}\n"

        return solutions_text

    def _suggest_fix_strategy(self, issue_category: str) -> str:
        """根据问题严重程度建议修复策略"""
        strategies = {
            'critical': """
【关键修复策略】
- 问题严重，需要重点检查代码结构
- 确保HTML文档结构完整（DOCTYPE, html, head, body）
- 确保canvas元素和script标签存在
- 修复所有致命语法错误（括号匹配、变量声明等）
- 代码至少40行以上
            """,
            'major': """
【主要修复策略】
- 问题较多，需要增强功能完整性
- 添加足够的Canvas绘图调用（至少8个）
- 实现requestAnimationFrame动画循环
- 添加交互控件（input range）和事件监听
- 增加代码量到60行以上
            """,
            'minor': """
【次要修复策略】
- 问题较少，进行细节优化
- 优化颜色对比度（使用亮色）
- 完善数学运算逻辑
- 优化动画清屏操作
- 改进代码注释和格式
            """
        }

        return strategies.get(issue_category, strategies['major'])

    async def generate_step_with_learning(
        self,
        step_type: str,
        step_context: Dict[str, Any],
        subject: str,
        topic: str,
        system_prompt: str
    ) -> tuple:
        """
        集成学习检索的步骤生成（任务#10）

        流程：
        1. 检索相似模式 → 注入prompt → 生成内容 → 评分 → 记录应用

        Args:
            step_type: 步骤类型 ('text_content', 'illustrated_content', 'assessment', 'ai_tutor', 'simulator')
            step_context: 步骤上下文信息（title, content_summary, learning_objectives等）
            subject: 学科
            topic: 主题
            system_prompt: 系统提示词

        Returns:
            (content: str, quality_score: float, agent_feedback: str)
        """
        if not self.db:
            logger.warning("[generate_step_with_learning] No database session, skipping learning retrieval")
            return await self._generate_step_without_learning(step_type, step_context, system_prompt)

        try:
            from app.services.learning.template_service import UnifiedTemplateService

            template_service = UnifiedTemplateService(self.db)

            # 1. 检索相似模式
            query_text = f"{step_context.get('title', '')} {step_context.get('content_summary', '')}"
            similar_patterns = await template_service.get_similar_patterns_by_vector(
                query_text=query_text,
                step_type=step_type,
                subject=subject,
                min_confidence=0.7,
                limit=3
            )

            logger.info(f"[Learning] Found {len(similar_patterns)} similar patterns for {step_type}")

            # 2. 构建增强的prompt
            enhanced_prompt = self._build_prompt_with_patterns(
                step_type=step_type,
                step_context=step_context,
                patterns=similar_patterns
            )

            # 3. 生成内容
            response = await self.claude_service.generate_raw_response(
                prompt=enhanced_prompt,
                system_prompt=system_prompt,
                max_tokens=4000
            )

            # 4. 清理和解析内容
            if step_type == 'simulator':
                content = self._clean_simulator_code(response)
            else:
                content = response

            # 5. Agent评分
            agent_score, agent_feedback = await self._evaluate_step_quality(
                step_type=step_type,
                content=content,
                step_context=step_context
            )

            # 6. 记录模式应用
            for pattern in similar_patterns:
                await template_service.record_pattern_application(
                    pattern_id=pattern.id,
                    step_type=step_type,
                    subject=subject,
                    topic=topic,
                    original_input=step_context,
                    applied_strategy=pattern.strategy,
                    result_quality=agent_score,
                    success=agent_score >= 24  # 40分满分，24分及以上算成功（60%通过率）
                )

            logger.info(f"[Learning] Generated {step_type} with quality score {agent_score}/20")
            return content, agent_score, agent_feedback

        except Exception as e:
            logger.error(f"[Learning] Error in generate_step_with_learning: {e}")
            # 降级到无学习增强的生成
            return await self._generate_step_without_learning(step_type, step_context, system_prompt)

    async def _generate_step_without_learning(
        self,
        step_type: str,
        step_context: Dict[str, Any],
        system_prompt: str
    ) -> tuple:
        """无学习增强的基础生成（fallback）"""
        # 构建基础prompt
        basic_prompt = self._build_basic_prompt(step_type, step_context)

        # 生成内容
        response = await self.claude_service.generate_raw_response(
            prompt=basic_prompt,
            system_prompt=system_prompt,
            max_tokens=4000
        )

        # 清理内容
        if step_type == 'simulator':
            content = self._clean_simulator_code(response)
        else:
            content = response

        # 基础评分（不使用Agent）
        return content, 12.0, "基础生成，未使用学习增强"

    def _build_prompt_with_patterns(
        self,
        step_type: str,
        step_context: Dict[str, Any],
        patterns: List[Any]
    ) -> str:
        """
        构建包含学习模式的增强prompt（任务#10）

        Args:
            step_type: 步骤类型
            step_context: 步骤上下文
            patterns: 相似模式列表（GenerationPattern对象）

        Returns:
            增强的prompt字符串
        """
        # 基础prompt
        base_prompt = self._build_basic_prompt(step_type, step_context)

        # 如果没有模式，返回基础prompt
        if not patterns:
            return base_prompt

        # 构建学习模式部分
        learning_section = "\n\n【学习参考 - 成功模式】\n"
        learning_section += "系统已从历史高质量内容中提取了以下成功模式，请参考应用：\n\n"

        for i, pattern in enumerate(patterns, 1):
            learning_section += f"{i}. {pattern.pattern_name}\n"
            learning_section += f"   类型：{pattern.pattern_type}\n"
            learning_section += f"   策略：{pattern.strategy}\n"
            if pattern.example_data:
                learning_section += f"   示例：{str(pattern.example_data)[:200]}...\n"
            learning_section += f"   成功率：{pattern.success_count}/{pattern.application_count} ({pattern.confidence*100:.1f}%)\n\n"

        # 将学习部分插入到基础prompt中
        enhanced_prompt = base_prompt + learning_section

        return enhanced_prompt

    def _build_basic_prompt(
        self,
        step_type: str,
        step_context: Dict[str, Any]
    ) -> str:
        """
        构建基础prompt（无学习增强）

        Args:
            step_type: 步骤类型
            step_context: 步骤上下文

        Returns:
            基础prompt字符串
        """
        title = step_context.get('title', '')
        content_summary = step_context.get('content_summary', '')
        learning_objectives = step_context.get('learning_objectives', [])
        objectives_text = "\n".join([f"  - {obj}" for obj in learning_objectives]) if learning_objectives else "  未提供"

        if step_type == 'text_content':
            return f"""生成高质量教学文本内容。

【内容信息】
标题：{title}
内容摘要：{content_summary}
学习目标：
{objectives_text}

【要求】
1. 内容深度足够（至少300字）
2. 逻辑清晰，层次分明
3. 使用专业术语但要有解释
4. 结合实例说明抽象概念

请直接输出文本内容，不要额外解释。"""

        elif step_type == 'illustrated_content':
            return f"""生成图文配合的教学内容。

【内容信息】
标题：{title}
内容摘要：{content_summary}
学习目标：
{objectives_text}

【要求】
1. 文字说明清晰（200-400字）
2. 图片描述详细（包括元素、标注、颜色等）
3. 图文紧密配合，互补增强

请输出JSON格式：
{{
    "text_content": "文字说明...",
    "diagram_description": "图片详细描述..."
}}"""

        elif step_type == 'assessment':
            return f"""生成高质量测验题目。

【测验信息】
标题：{title}
内容摘要：{content_summary}
学习目标：
{objectives_text}

【要求】
1. 题目数量：3-5道单选题
2. 难度适中，题干清晰
3. 选项设计合理，干扰项有意义
4. 解析详细清晰

请输出JSON格式的题目列表。"""

        elif step_type == 'ai_tutor':
            return f"""生成AI导师对话内容。

【导师信息】
标题：{title}
内容摘要：{content_summary}
学习目标：
{objectives_text}

【要求】
1. 初始引导语友好清晰
2. 预设5-8个引导性问题
3. 循序渐进，启发思考
4. 避免直接给答案

请输出JSON格式的AI导师配置。"""

        elif step_type == 'simulator':
            return f"""生成完整HTML模拟器。

【模拟器信息】
标题：{title}
描述：{content_summary}
学习目标：
{objectives_text}

【要求】
1. 完整HTML文档（<!DOCTYPE html>...）
2. 使用Canvas 2D API绘制
3. 至少2个交互控件
4. 动画流畅，代码清晰

只输出完整HTML代码，不要markdown标记。"""

        else:
            return f"""生成{step_type}类型的内容。

【内容信息】
标题：{title}
描述：{content_summary}
学习目标：
{objectives_text}

请生成高质量的教学内容。"""

    async def _evaluate_step_quality(
        self,
        step_type: str,
        content: str,
        step_context: Dict[str, Any]
    ) -> tuple:
        """
        评估步骤内容质量

        Args:
            step_type: 步骤类型
            content: 生成的内容
            step_context: 步骤上下文

        Returns:
            (agent_score: float, feedback: str)
        """
        try:
            if step_type == 'text_content':
                return await self._agent_review_text_content(
                    content=content,
                    title=step_context.get('title', ''),
                    learning_objectives=step_context.get('learning_objectives', [])
                )

            elif step_type == 'assessment':
                # 需要解析questions
                import json
                try:
                    data = json.loads(content)
                    questions = data.get('questions', [])
                except:
                    questions = []

                return await self._agent_review_assessment(
                    questions=questions,
                    title=step_context.get('title', ''),
                    learning_objectives=step_context.get('learning_objectives', [])
                )

            elif step_type == 'illustrated_content':
                # 需要解析diagram_description
                import json
                try:
                    data = json.loads(content)
                    text_content = data.get('text_content', '')
                    diagram_desc = data.get('diagram_description', '')
                except:
                    text_content = content[:1000]
                    diagram_desc = '图片描述'

                return await self._agent_review_illustrated_content(
                    content=text_content,
                    diagram_description=diagram_desc,
                    title=step_context.get('title', ''),
                    learning_objectives=step_context.get('learning_objectives', [])
                )

            elif step_type == 'ai_tutor':
                # 需要解析initial_prompt和questions
                import json
                try:
                    data = json.loads(content)
                    initial_prompt = data.get('initial_prompt', '')
                    question_patterns = data.get('question_patterns', [])
                except:
                    initial_prompt = content[:500]
                    question_patterns = []

                return await self._agent_review_ai_tutor(
                    initial_prompt=initial_prompt,
                    question_patterns=question_patterns,
                    title=step_context.get('title', ''),
                    learning_objectives=step_context.get('learning_objectives', [])
                )

            elif step_type == 'simulator':
                return await self._agent_review(
                    code=content,
                    simulator_name=step_context.get('title', ''),
                    simulator_description=step_context.get('content_summary', '')
                )

            else:
                return 12.0, f"未知步骤类型: {step_type}"

        except Exception as e:
            logger.error(f"[Evaluate] Error evaluating {step_type}: {e}")
            return 12.0, f"评估异常: {str(e)}"

    def _supervisor_review(self, code: str) -> tuple:
        """
        监督者：审核代码并打分（任务#6增强）

        评分标准（满分80，Agent占20）：
        - 可运行性: 30分（HTML结构、脚本正确、语法验证）
        - 内容完整: 30分（视觉元素、交互功能、Canvas API检测）
        - 表达深度: 10分（代码行数、元素丰富度）
        - 渲染质量: 10分（颜色对比、动画循环、交互响应）

        硬性规则（0分，强制重新生成）：
        - 画布尺寸超出1600×900
        - 交互元素少于2个

        Returns:
            (score, issues)
        """
        score = 60  # 从60分开始（Agent评分占40分，2026-02-15调整）
        issues = []

        # ========== 硬性规则检查 (违反=0分) ==========

        # 0. 必要元素检查（2026-02-15新增）
        required_elements = {
            'DOCTYPE': '<!doctype html>' in code.lower(),
            'html标签': '<html' in code.lower(),
            'head标签': '<head>' in code.lower(),
            'body标签': '<body>' in code.lower(),
            'canvas标签': '<canvas' in code.lower(),
            'script标签': '<script>' in code.lower() or '<script ' in code.lower(),
        }

        missing_elements = [name for name, exists in required_elements.items() if not exists]
        if missing_elements:
            return 0, [f"❌ 致命错误：缺少必要元素 {', '.join(missing_elements)}"]

        # 1. 画布尺寸检查
        canvas_size_valid, canvas_issues = self._check_canvas_size(code)
        if not canvas_size_valid:
            return 0, canvas_issues

        # 2. 交互元素数量检查
        interaction_count_valid, interaction_issues = self._check_interaction_count(code)
        if not interaction_count_valid:
            return 0, interaction_issues

        # ========== 常规评分 ==========

        # === 可运行性 (30分) ===
        # 检查HTML结构（已在必要元素检查中处理，这里不再扣分）
        has_html_tag = '<!DOCTYPE html>' in code and '<html' in code
        has_canvas = '<canvas' in code
        has_script = '<script>' in code or '<script ' in code

        # Canvas API使用检测（任务#6新增）
        canvas_api_usage = self._detect_canvas_api_usage(code)
        if not canvas_api_usage['has_drawing_calls']:
            score -= 10
            issues.append("缺少Canvas绘图调用（fillRect/arc/beginPath等）")

        # 语法验证（重复声明、中文标点等致命问题）
        syntax_valid, syntax_error = self._validate_js_syntax_detailed(code)
        if not syntax_valid and syntax_error:
            if syntax_error.error_type in (SyntaxErrorType.DUPLICATE_DECLARATION, SyntaxErrorType.CHINESE_PUNCTUATION):
                score -= 20
                issues.append(f"致命语法错误: {syntax_error.message}")
            elif syntax_error.error_type in (SyntaxErrorType.UNCLOSED_BRACKET, SyntaxErrorType.MISMATCHED_BRACKET):
                score -= 15
                issues.append(f"括号错误: {syntax_error.message}")

        # === 内容完整 (30分) ===
        # 检查是否有文本显示元素
        has_text_display = bool(re.search(r'<(span|div|p)[^>]*id=["\'][^"\']+["\'][^>]*>', code))
        if not has_text_display:
            score -= 8
            issues.append("缺少文本显示元素")

        # 检查交互控件
        has_controls = bool(re.search(r'<input[^>]*type=["\']range["\']', code))
        if not has_controls:
            score -= 8
            issues.append("缺少交互控件(range input)")

        # 交互响应检测（任务#6新增）
        has_event_listeners = self._detect_interaction_response(code)
        if not has_event_listeners:
            score -= 7
            issues.append("缺少交互事件监听器（addEventListener）")

        # === 表达深度 (10分) ===
        code_lines = len([l for l in code.split('\n') if l.strip()])
        if code_lines < 30:
            # 代码太短，降低严厉度（任务#6：30→40行）
            return 0, [f"代码严重不足: {code_lines}行(需30+)"]
        elif code_lines < 40:
            score -= 8
            issues.append(f"代码太短: {code_lines}行(建议40+)")
        elif code_lines < 60:
            score -= 4
            issues.append(f"代码偏短: {code_lines}行(建议60+)")

        # 检查元素丰富度
        if not canvas_api_usage['is_rich']:
            score -= 5
            issues.append(f"Canvas绘图元素较少: {canvas_api_usage['draw_count']}个(建议8+)")

        # === 渲染质量 (10分) ===
        color_valid, _, dark_colors = self._validate_color_contrast(code)
        if not color_valid:
            score -= 3
            issues.append(f"深色: {', '.join(dark_colors[:3])}")

        # 动画循环检测（任务#6增强）
        animation_check = self._detect_animation_loop(code)
        if not animation_check['has_raf']:
            score -= 3
            issues.append("缺少动画循环(requestAnimationFrame)")
        elif not animation_check['has_clear']:
            score -= 1
            issues.append("动画循环中缺少清屏操作")

        has_math = bool(re.search(r'Math\.(sin|cos|PI|abs|sqrt|pow)', code))
        if not has_math:
            score -= 2
            issues.append("缺少数学运算(Math.sin/cos等)")

        # 检查是否使用了 emoji 或 Unicode 特殊字符代替图形
        emoji_pattern = re.findall(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FA6F]', code)
        if emoji_pattern:
            score -= 5
            issues.append("使用了emoji/Unicode特殊字符，应使用Canvas 2D API绘制")

        return max(0, score), issues

    def _check_canvas_size(self, code: str) -> tuple:
        """
        硬性规则：检查画布尺寸是否符合要求（1600×900）

        检查项：
        1. canvas标签的width和height属性
        2. 所有绘图坐标是否在画布范围内

        Returns:
            (is_valid: bool, issues: list)
        """
        import re

        issues = []

        # 1. 检查canvas标签尺寸
        canvas_match = re.search(r'<canvas[^>]*width\s*=\s*["\']?(\d+)["\']?[^>]*height\s*=\s*["\']?(\d+)["\']?', code)
        if not canvas_match:
            canvas_match = re.search(r'<canvas[^>]*height\s*=\s*["\']?(\d+)["\']?[^>]*width\s*=\s*["\']?(\d+)["\']?', code)
            if canvas_match:
                width, height = int(canvas_match.group(2)), int(canvas_match.group(1))
            else:
                issues.append("【硬性规则违反】无法检测到canvas标签的width和height属性")
                return False, issues
        else:
            width, height = int(canvas_match.group(1)), int(canvas_match.group(2))

        if width != 1600 or height != 900:
            issues.append(f"【硬性规则违反】画布尺寸错误: {width}×{height}，要求1600×900")
            return False, issues

        # 注意: 坐标范围检查已移除,因为无法可靠检测变量坐标
        # 改为在prompt中强调坐标必须在画布范围内
        return True, []

    def _check_interaction_count(self, code: str) -> tuple:
        """
        硬性规则：检查交互元素数量（至少2个）

        检查项：
        1. addEventListener调用
        2. on*事件属性（onclick, onmousemove等）

        Returns:
            (is_valid: bool, issues: list)
        """
        import re

        issues = []
        interaction_count = 0

        # 1. 统计addEventListener
        event_listeners = re.findall(r'addEventListener\s*\(\s*["\'](\w+)["\']', code)
        interaction_count += len(event_listeners)

        # 2. 统计on*事件属性
        inline_events = re.findall(r'\bon(click|mousemove|mousedown|mouseup|keydown|keyup|touchstart|touchend|touchmove)\s*=', code, re.IGNORECASE)
        interaction_count += len(inline_events)

        if interaction_count < 2:
            issues.append(f"【硬性规则违反】交互元素不足: 检测到{interaction_count}个，要求至少2个")
            return False, issues

        return True, []

    def _detect_canvas_api_usage(self, code: str) -> Dict[str, Any]:
        """
        检测Canvas API使用情况（任务#6新增）

        Returns:
            {
                'has_drawing_calls': bool,
                'draw_count': int,
                'is_rich': bool (>=8个绘图调用)
            }
        """
        import re

        drawing_apis = ['fillRect', 'strokeRect', 'arc', 'fillText', 'strokeText',
                       'beginPath', 'lineTo', 'moveTo', 'quadraticCurveTo', 'bezierCurveTo']

        draw_count = 0
        for api in drawing_apis:
            draw_count += len(re.findall(rf'\b{api}\b', code))

        return {
            'has_drawing_calls': draw_count > 0,
            'draw_count': draw_count,
            'is_rich': draw_count >= 8
        }

    def _detect_animation_loop(self, code: str) -> Dict[str, Any]:
        """
        检测动画循环实现（任务#6新增）

        Returns:
            {
                'has_raf': bool,  # 是否有requestAnimationFrame
                'has_clear': bool  # 是否有清屏操作
            }
        """
        import re

        has_raf = 'requestAnimationFrame' in code
        has_clear = bool(re.search(r'(fillRect\s*\(0\s*,\s*0|clearRect)', code))

        return {
            'has_raf': has_raf,
            'has_clear': has_clear
        }

    def _detect_interaction_response(self, code: str) -> bool:
        """
        检测交互响应实现（任务#6新增）

        检查是否有事件监听器（addEventListener或oninput）
        """
        return 'addEventListener' in code or 'oninput' in code

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

    def validate_html_quality(self, code: str, threshold: int = 70) -> tuple:
        """
        验证HTML模拟器质量评分 (2026-02-11)

        Args:
            code: HTML代码
            threshold: 质量阈值 (默认70)

        Returns:
            (passed: bool, score: HTMLSimulatorQualityScore, report: str)
        """
        from .models import HTMLSimulatorSpec, HTMLSimulatorQualityStandards

        # 创建HTMLSimulatorSpec来计算评分
        spec = HTMLSimulatorSpec(
            name="temp",
            description="temp",
            html_content=code
        )

        try:
            # 验证HTML结构
            standards = HTMLSimulatorQualityStandards()
            spec.validate(standards)
        except ValueError as e:
            # 结构验证失败
            logger.warning(f"HTML structure validation failed: {e}")
            # 返回0分
            from .models import HTMLSimulatorQualityScore
            failed_score = HTMLSimulatorQualityScore(
                structure_score=0,
                canvas_usage_score=0,
                visual_quality_score=0,
                interaction_score=0,
                educational_value_score=0
            )
            failed_score.issues.append(f"Structure validation failed: {str(e)}")
            return False, failed_score, failed_score.format_report()

        # 计算质量评分
        standards = HTMLSimulatorQualityStandards()
        score = spec.calculate_quality_score(standards)
        score.threshold = threshold

        report = score.format_report()
        logger.info(f"HTML quality score: {score.total_score}/100 (threshold: {threshold})")

        if not score.passed:
            logger.warning(f"HTML quality below threshold. Issues: {score.issues}")

        return score.passed, score, report

    def _clean_simulator_code(self, response: str) -> str:
        """
        清理AI响应，提取HTML代码（2026-02-11: 适配HTML格式，任务#6增强）

        支持的格式：
        1. 直接的HTML代码（以<!DOCTYPE开头）
        2. Markdown代码块包裹的HTML（```html ... ```）
        3. JSON包裹的HTML（{"code": "..."}）

        增强功能（任务#6）：
        - 统一清理流程
        - 支持多层嵌套提取
        """
        import re
        import json as _json

        code = response.strip()
        original_response = response

        # 步骤1: 移除markdown包装器
        code = self._remove_markdown_wrapper(code)

        # 步骤2: 提取JSON包裹的内容
        code = self._extract_from_json_wrapper(code)

        # 步骤3: 提取HTML内容
        extracted = self._extract_html_content(code)

        if extracted:
            logger.info(f"[_clean_simulator_code] Successfully extracted HTML: {len(extracted.splitlines())} lines")
            return extracted.strip()

        # 完全失败，返回原始响应
        logger.warning(f"[_clean_simulator_code] Failed to extract HTML, returning original response: {len(original_response)} chars")
        return original_response.strip()

    def _remove_markdown_wrapper(self, code: str) -> str:
        """移除markdown代码块包装器"""
        import re

        # 移除 ```html ... ``` 或 ``` ... ```
        html_blocks = re.findall(r'```html\s*\n(.*?)```', code, re.DOTALL | re.IGNORECASE)
        if html_blocks:
            return max(html_blocks, key=len)

        code_blocks = re.findall(r'```[a-z]*\s*\n(.*?)```', code, re.DOTALL | re.IGNORECASE)
        if code_blocks:
            # 优先选择包含DOCTYPE或<html>的块
            for block in code_blocks:
                if '<!DOCTYPE' in block.upper() or '<HTML' in block.upper():
                    return block
            # 否则返回最长的块
            return max(code_blocks, key=len) if code_blocks else code

        return code

    def _extract_from_json_wrapper(self, code: str) -> str:
        """从JSON包装器中提取内容"""
        import json as _json

        try:
            parsed = _json.loads(code)
            if isinstance(parsed, dict):
                # 尝试多个可能的键名
                for key in ['code', 'html_content', 'content', 'html']:
                    if key in parsed and isinstance(parsed[key], str) and len(parsed[key]) > 100:
                        return parsed[key]
        except (ValueError, _json.JSONDecodeError):
            pass

        return code

    def _extract_html_content(self, code: str) -> Optional[str]:
        """提取HTML内容"""
        import re

        # 查找<!DOCTYPE html>或<html的位置
        doctype_match = re.search(r'<!DOCTYPE\s+html>', code, re.IGNORECASE)
        html_match = re.search(r'<html[^>]*>', code, re.IGNORECASE)

        start_pos = None
        if doctype_match:
            start_pos = doctype_match.start()
        elif html_match:
            start_pos = html_match.start()

        if start_pos is not None:
            # 找到</html>的结束位置
            end_match = re.search(r'</html>', code[start_pos:], re.IGNORECASE)
            if end_match:
                end_pos = start_pos + end_match.end()
                return code[start_pos:end_pos]
            else:
                # 没有找到</html>，取到末尾
                return code[start_pos:]

        # 如果没有找到HTML标记，尝试移除解释文字
        lines = code.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if '<' in stripped or '{' in stripped or stripped.startswith('//') or stripped == '':
                start_idx = i
                break

        end_idx = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            stripped = lines[i].strip()
            if '>' in stripped or '}' in stripped or stripped.startswith('//') or stripped == '':
                end_idx = i + 1
                break

        if start_idx < end_idx:
            result = '\n'.join(lines[start_idx:end_idx]).strip()
            if len(result) > 100:
                return result

        return None

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

        # 4. 检查重复的 let/const 声明（同一作用域）
        dup_error = self._check_duplicate_declarations(code, lines)
        if dup_error:
            return False, dup_error

        # 5. 检查代码区域（非字符串、非注释）中的中文标点
        punct_error = self._check_chinese_punctuation_in_code(code, lines)
        if punct_error:
            return False, punct_error

        return True, None

    def _check_duplicate_declarations(self, code: str, lines: list) -> Optional[CodeSyntaxError]:
        """检查同一作用域内的重复 let/const 声明"""
        # 按函数分段追踪声明
        current_func = None
        brace_depth = 0
        declarations = {}  # {func_name: {var_name: first_line_num}}

        for line_num, line in enumerate(lines):
            stripped = line.strip()

            # 跳过注释
            if stripped.startswith('//') or stripped.startswith('/*'):
                continue

            # 检测函数边界
            if 'function setup' in stripped:
                current_func = 'setup'
                brace_depth = 0
                declarations.setdefault('setup', {})
            elif 'function update' in stripped:
                current_func = 'update'
                brace_depth = 0
                declarations.setdefault('update', {})

            # 追踪大括号深度
            brace_depth += stripped.count('{') - stripped.count('}')

            # 只检查函数体顶层作用域（brace_depth == 1）的声明
            if current_func and brace_depth == 1:
                # 跳过 for/if/while 等块级语句内的声明
                if stripped.startswith(('for', 'if', 'while', 'switch', '//')):
                    continue
                m = re.match(r'(let|const)\s+(\w+)', stripped)
                if m:
                    var_name = m.group(2)
                    func_decls = declarations.get(current_func, {})
                    if var_name in func_decls:
                        first_line = func_decls[var_name]
                        before, current, after = self._get_line_context(lines, line_num)
                        return CodeSyntaxError(
                            error_type=SyntaxErrorType.DUPLICATE_DECLARATION,
                            message=f"在 {current_func}() 中重复声明变量 '{var_name}'（首次在第 {first_line + 1} 行）",
                            line_number=line_num + 1,
                            context_before=before,
                            error_line=current,
                            context_after=after,
                            suggestion=f"删除重复的 '{m.group(1)} {var_name}'，或将第二次改为赋值: {var_name} = ..."
                        )
                    func_decls[var_name] = line_num
                    declarations[current_func] = func_decls

        return None

    def _check_chinese_punctuation_in_code(self, code: str, lines: list) -> Optional[CodeSyntaxError]:
        """检查代码区域（非字符串、非注释）中的中文标点"""
        chinese_punct = re.compile(r'[，。；：（）【】！？]')

        for line_num, line in enumerate(lines):
            # 去除单行注释
            clean = re.sub(r'//[^\n]*', '', line)
            # 去除字符串内容（单引号、双引号、反引号）
            clean = re.sub(r"'[^']*'|\"[^\"]*\"|`[^`]*`", '', clean)
            found = chinese_punct.findall(clean)
            if found:
                before, current, after = self._get_line_context(lines, line_num)
                return CodeSyntaxError(
                    error_type=SyntaxErrorType.CHINESE_PUNCTUATION,
                    message=f"代码中包含中文标点: {''.join(found)}",
                    line_number=line_num + 1,
                    context_before=before,
                    error_line=current,
                    context_after=after,
                    suggestion=f"将中文标点替换为英文标点: ，→, ；→; ：→: （→( ）→) 。→."
                )

        return None

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
                            suggestion=f"可用的 Canvas 2D API: {', '.join(CANVAS_2D_DRAWING_APIS[:5])}... 请使用标准Canvas 2D API"
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

    # _get_fallback_code 方法已删除（2026-02-11）- 不再使用ctx API fallback

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
            steps = []
            for step_data in data.get('steps', data.get('script', [])):
                step = ChapterStep(
                    step_id=step_data.get('step_id', f'step_{len(steps)+1}'),
                    type=step_data.get('type', 'text_content'),
                    title=step_data.get('title', ''),
                    content=step_data.get('content'),
                    diagram_spec=step_data.get('diagram_spec'),
                    assessment_spec=step_data.get('assessment_spec'),
                    ai_spec=step_data.get('ai_spec')
                )

                # 解析HTML模拟器
                if step.type == 'simulator' and 'simulator_spec' in step_data:
                    sim_data = step_data['simulator_spec']
                    step.simulator_spec = HTMLSimulatorSpec(
                        name=sim_data.get('name', ''),
                        description=sim_data.get('description', ''),
                        html_content=sim_data.get('html_content', ''),
                        mode=sim_data.get('mode', 'html')
                    )

                # ai_tutor 默认值补全
                if step.type == 'ai_tutor' and step.ai_spec:
                    if 'max_turns' not in step.ai_spec:
                        step.ai_spec['max_turns'] = 6
                    if 'mode' not in step.ai_spec:
                        step.ai_spec['mode'] = 'proactive_assessment'

                steps.append(step)

            return ChapterResult(
                lesson_id=data.get('lesson_id', 'lesson_1'),
                title=data.get('title', ''),
                order=data.get('order', 0),
                total_steps=len(steps),
                rationale=data.get('rationale', ''),
                steps=steps,
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

            # 解析HTML模拟器
            if step.type == 'simulator' and 'simulator_spec' in data:
                sim_data = data['simulator_spec']
                step.simulator_spec = HTMLSimulatorSpec(
                    name=sim_data.get('name', ''),
                    description=sim_data.get('description', ''),
                    html_content=sim_data.get('html_content', ''),
                    mode=sim_data.get('mode', 'html')
                )

            return step

        except Exception as e:
            logger.error(f"Failed to parse single step: {e}")
            raise ValueError(f"单步解析失败: {e}")

    async def _agent_review(self, code: str, simulator_name: str, simulator_description: str) -> tuple:
        """
        Agent评审：评估模拟器的教学有效性、用户体验、创新性（满分40，2026-02-15调整）

        评分维度：
        - 教学有效性(0-16): 概念演示清晰度、因果关系展示
        - 用户体验(0-12): 界面美观、操作流畅、反馈及时
        - 创新性(0-12): 独特视角、巧妙设计、记忆点

        Returns:
            (agent_score: int, feedback: str)
        """
        # 提取代码片段（避免发送过长内容）
        code_sample = code[:3000] + "..." if len(code) > 3000 else code

        prompt = f"""你是一位专业的教育技术评估专家。请评估以下HTML模拟器的质量。

【模拟器信息】
名称：{simulator_name}
描述：{simulator_description}

【代码片段】（前3000字符）
{code_sample}

【评估任务】
请从以下三个维度给出评分（总分40分，2026-02-15权重提升）：

1. 教学有效性 (0-16分)
   - 概念演示是否清晰？是否直观展示了核心原理？
   - 因果关系是否明确？用户能否理解变量如何影响结果？

2. 用户体验 (0-12分)
   - 界面是否美观？颜色搭配是否合理？
   - 操作是否流畅？是否有清晰的视觉反馈？

3. 创新性 (0-12分)
   - 是否有独特的视角或创新的展示方式？
   - 是否有助于记忆和理解？

【输出格式】
请输出JSON格式：
{{
    "教学有效性分": 12,
    "用户体验分": 8,
    "创新性分": 6,
    "总分": 26,
    "评价": "简要说明优点和不足（50-150字）"
}}"""

        try:
            response = await self.claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt="你是教育技术评估专家，专门评估教学模拟器质量。请客观公正地评分，并给出建设性意见。",
                max_tokens=500
            )

            # 解析JSON
            import json
            import re

            # 尝试提取JSON
            json_match = re.search(r'\{[^{}]*"总分"[^{}]*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                agent_score = data.get('总分', 0)
                feedback = data.get('评价', '')
                logger.info(f"[Agent] Score: {agent_score}/40, Feedback: {feedback[:100]}")
                return agent_score, feedback
            else:
                logger.warning(f"[Agent] Failed to parse JSON from response: {response[:200]}")
                return 20, "Agent评估解析失败，使用默认分数"

        except Exception as e:
            logger.error(f"[Agent] Review error: {e}")
            return 20, f"Agent评估异常: {str(e)}"

    async def _agent_review_text_content(
        self,
        content: str,
        title: str,
        learning_objectives: List[str]
    ) -> tuple:
        """
        Agent评审：评估文本内容质量（任务#8，满分20）

        评分维度：
        - 内容深度(0-8): 概念覆盖、逻辑层次、专业准确
        - 准确性(0-7): 科学准确、无错误、引用可靠
        - 清晰度(0-5): 语言流畅、易理解、结构清晰

        Args:
            content: 文本内容
            title: 内容标题
            learning_objectives: 学习目标列表

        Returns:
            (agent_score: int, feedback: str)
        """
        content_sample = content[:2000] + "..." if len(content) > 2000 else content
        objectives_text = "\n".join([f"  - {obj}" for obj in learning_objectives]) if learning_objectives else "  未提供"

        prompt = f"""你是一位专业的教育内容评估专家。请评估以下文本内容的质量。

【内容信息】
标题：{title}
学习目标：
{objectives_text}

【内容片段】（前2000字符）
{content_sample}

【评估任务】
请从以下三个维度给出评分（总分20分）：

1. 内容深度 (0-8分)
   - 概念覆盖是否全面？
   - 逻辑层次是否清晰？
   - 是否有足够的专业深度？

2. 准确性 (0-7分)
   - 内容是否科学准确？
   - 是否有事实错误或逻辑漏洞？
   - 专业术语使用是否正确？

3. 清晰度 (0-5分)
   - 语言表达是否流畅？
   - 是否易于理解？
   - 结构组织是否清晰？

【输出格式】
请输出JSON格式：
{{
    "内容深度分": 6,
    "准确性分": 5,
    "清晰度分": 4,
    "总分": 15,
    "评价": "简要说明优点和不足（50-150字）"
}}"""

        try:
            response = await self.claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt="你是教育内容评估专家，专门评估教学文本质量。请客观公正地评分，并给出建设性意见。",
                max_tokens=500
            )

            agent_score, feedback = self._parse_agent_score(response, default_score=24)
            logger.info(f"[Agent Text] Score: {agent_score}/40, Feedback: {feedback[:100]}")
            return agent_score, feedback

        except Exception as e:
            logger.error(f"[Agent Text] Review error: {e}")
            return 12, f"Agent评估异常: {str(e)}"

    async def _agent_review_assessment(
        self,
        questions: List[Dict],
        title: str,
        learning_objectives: List[str]
    ) -> tuple:
        """
        Agent评审：评估测验题目质量（任务#8，满分20）

        评分维度：
        - 题目质量(0-8): 难度适中、题干清晰、选项合理
        - 区分度(0-7): 能有效区分不同水平学生
        - 目标对齐(0-5): 与学习目标紧密对应

        Args:
            questions: 题目列表 [{'question': str, 'options': List[str], 'correct_answer': str}]
            title: 测验标题
            learning_objectives: 学习目标列表

        Returns:
            (agent_score: int, feedback: str)
        """
        questions_text = self._format_questions(questions[:3])  # 只评估前3题
        objectives_text = "\n".join([f"  - {obj}" for obj in learning_objectives]) if learning_objectives else "  未提供"

        prompt = f"""你是一位专业的教育测评评估专家。请评估以下测验题目的质量。

【测验信息】
标题：{title}
学习目标：
{objectives_text}

【题目内容】（前3题）
{questions_text}

【评估任务】
请从以下三个维度给出评分（总分20分）：

1. 题目质量 (0-8分)
   - 难度是否适中？
   - 题干是否清晰无歧义？
   - 选项设计是否合理（干扰项有意义）？

2. 区分度 (0-7分)
   - 能否有效区分不同水平的学生？
   - 是否避免了过于简单或过难的题目？
   - 干扰项是否具有诊断价值？

3. 目标对齐 (0-5分)
   - 题目是否紧扣学习目标？
   - 是否覆盖了关键知识点？
   - 题型是否适合评估目标？

【输出格式】
请输出JSON格式：
{{
    "题目质量分": 6,
    "区分度分": 5,
    "目标对齐分": 4,
    "总分": 15,
    "评价": "简要说明优点和不足（50-150字）"
}}"""

        try:
            response = await self.claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt="你是教育测评评估专家，专门评估测验题目质量。请客观公正地评分，并给出建设性意见。",
                max_tokens=500
            )

            agent_score, feedback = self._parse_agent_score(response, default_score=12)
            logger.info(f"[Agent Assessment] Score: {agent_score}/20, Feedback: {feedback[:100]}")
            return agent_score, feedback

        except Exception as e:
            logger.error(f"[Agent Assessment] Review error: {e}")
            return 12, f"Agent评估异常: {str(e)}"

    def _parse_agent_score(self, response: str, default_score: int = 20) -> tuple:
        """
        解析Agent返回的JSON评分（任务#8新增）

        Args:
            response: Agent响应文本
            default_score: 解析失败时的默认分数

        Returns:
            (score: int, feedback: str)
        """
        import json
        import re

        try:
            # 尝试提取JSON
            json_match = re.search(r'\{[^{}]*"总分"[^{}]*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                score = data.get('总分', default_score)
                feedback = data.get('评价', '')
                return score, feedback
            else:
                logger.warning(f"[Parse Agent Score] No JSON found in response")
                return default_score, "Agent评估解析失败，使用默认分数"

        except Exception as e:
            logger.error(f"[Parse Agent Score] Error: {e}")
            return default_score, f"解析异常: {str(e)}"

    def _format_questions(self, questions: List[Dict]) -> str:
        """
        格式化题目列表（任务#8新增）

        Args:
            questions: 题目列表

        Returns:
            格式化的题目文本
        """
        if not questions:
            return "  无题目"

        formatted = []
        for i, q in enumerate(questions, 1):
            question_text = q.get('question', '')
            options = q.get('options', [])
            correct = q.get('correct_answer', '')

            formatted.append(f"\n题目{i}：{question_text}")
            for opt in options:
                formatted.append(f"  {opt}")
            formatted.append(f"  正确答案：{correct}")

        return '\n'.join(formatted)

    async def _agent_review_illustrated_content(
        self,
        content: str,
        diagram_description: str,
        title: str,
        learning_objectives: List[str]
    ) -> tuple:
        """
        Agent评审：评估图文内容质量（任务#9，满分20）

        评分维度：
        - 图文配合(0-8): 图片与文字紧密对应、互补增强
        - 可视化效果(0-7): 图示清晰、信息丰富、美观
        - 教学价值(0-5): 有助于理解、记忆、应用

        Args:
            content: 文字说明
            diagram_description: 图片描述
            title: 内容标题
            learning_objectives: 学习目标列表

        Returns:
            (agent_score: int, feedback: str)
        """
        content_sample = content[:1500] + "..." if len(content) > 1500 else content
        diagram_sample = diagram_description[:500] + "..." if len(diagram_description) > 500 else diagram_description
        objectives_text = "\n".join([f"  - {obj}" for obj in learning_objectives]) if learning_objectives else "  未提供"

        prompt = f"""你是一位专业的教育可视化评估专家。请评估以下图文内容的质量。

【内容信息】
标题：{title}
学习目标：
{objectives_text}

【文字说明】
{content_sample}

【图片描述】
{diagram_sample}

【评估任务】
请从以下三个维度给出评分（总分20分）：

1. 图文配合 (0-8分)
   - 图片与文字是否紧密对应？
   - 图文是否互补增强（图片展示文字难以表达的内容）？
   - 是否存在冗余或脱节？

2. 可视化效果 (0-7分)
   - 图示是否清晰易懂？
   - 信息是否丰富（标注、箭头、颜色等）？
   - 视觉设计是否美观专业？

3. 教学价值 (0-5分)
   - 是否有助于理解抽象概念？
   - 是否有助于记忆关键信息？
   - 是否有助于实际应用？

【输出格式】
请输出JSON格式：
{{
    "图文配合分": 6,
    "可视化效果分": 5,
    "教学价值分": 4,
    "总分": 15,
    "评价": "简要说明优点和不足（50-150字）"
}}"""

        try:
            response = await self.claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt="你是教育可视化评估专家，专门评估图文教学内容质量。请客观公正地评分，并给出建设性意见。",
                max_tokens=500
            )

            agent_score, feedback = self._parse_agent_score(response, default_score=12)
            logger.info(f"[Agent Illustrated] Score: {agent_score}/20, Feedback: {feedback[:100]}")
            return agent_score, feedback

        except Exception as e:
            logger.error(f"[Agent Illustrated] Review error: {e}")
            return 12, f"Agent评估异常: {str(e)}"

    async def _agent_review_ai_tutor(
        self,
        initial_prompt: str,
        question_patterns: List[str],
        title: str,
        learning_objectives: List[str]
    ) -> tuple:
        """
        Agent评审：评估AI导师内容质量（任务#9，满分20）

        评分维度：
        - 对话质量(0-8): 引导性问题设计、对话流畅自然
        - 引导性(0-7): 循序渐进、启发思考、避免直接给答案
        - 适应性(0-5): 能应对不同回答、个性化调整

        Args:
            initial_prompt: 初始引导语
            question_patterns: 预设问题模式列表
            title: AI导师标题
            learning_objectives: 学习目标列表

        Returns:
            (agent_score: int, feedback: str)
        """
        prompt_sample = initial_prompt[:1000] + "..." if len(initial_prompt) > 1000 else initial_prompt
        patterns_text = "\n".join([f"  - {p}" for p in question_patterns[:5]]) if question_patterns else "  未提供"
        objectives_text = "\n".join([f"  - {obj}" for obj in learning_objectives]) if learning_objectives else "  未提供"

        prompt = f"""你是一位专业的AI教育对话系统评估专家。请评估以下AI导师内容的质量。

【AI导师信息】
标题：{title}
学习目标：
{objectives_text}

【初始引导语】
{prompt_sample}

【预设问题模式】
{patterns_text}

【评估任务】
请从以下三个维度给出评分（总分20分）：

1. 对话质量 (0-8分)
   - 引导性问题设计是否合理？
   - 对话是否流畅自然？
   - 语言表达是否清晰友好？

2. 引导性 (0-7分)
   - 是否循序渐进引导学生思考？
   - 是否启发学生自主探索？
   - 是否避免直接给出答案？

3. 适应性 (0-5分)
   - 能否应对学生的不同回答？
   - 是否有个性化调整机制？
   - 是否能诊断学生的理解程度？

【输出格式】
请输出JSON格式：
{{
    "对话质量分": 6,
    "引导性分": 5,
    "适应性分": 4,
    "总分": 15,
    "评价": "简要说明优点和不足（50-150字）"
}}"""

        try:
            response = await self.claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt="你是AI教育对话系统评估专家，专门评估AI导师教学质量。请客观公正地评分，并给出建设性意见。",
                max_tokens=500
            )

            agent_score, feedback = self._parse_agent_score(response, default_score=12)
            logger.info(f"[Agent AI Tutor] Score: {agent_score}/20, Feedback: {feedback[:100]}")
            return agent_score, feedback

        except Exception as e:
            logger.error(f"[Agent AI Tutor] Review error: {e}")
            return 12, f"Agent评估异常: {str(e)}"

    async def _supervisor_decision(
        self,
        code: str,
        simulator_name: str,
        rule_score: int,
        agent_score: int,
        agent_feedback: str,
        rule_issues: List[str],
        round_num: int
    ) -> tuple:
        """
        AI监督者决策：综合规则分、Agent分和意见，决定是否采纳

        Returns:
            (decision: str, reason: str)
            decision: "accept" | "reject" | "fix"

        决策说明（2026-02-15更新）：
        - accept: 接受当前代码
        - reject: 完全重新生成（丢弃当前代码）
        - fix: 在当前代码基础上修复问题
        """
        total_score = rule_score + agent_score

        prompt = f"""你是课程生成系统的AI监督者，负责决定是否采纳当前生成的模拟器代码。

【模拟器信息】
名称：{simulator_name}
当前轮次：第{round_num}轮（最多3轮）

【评分情况】
规则评分：{rule_score}/60（基于代码规则检查，2026-02-15调整）
Agent评分：{agent_score}/40（Agent评估教学效果，权重提升到40%）
总分：{total_score}/100
通过阈值：75分（2026-02-15更新）

【规则检查发现的问题】
{chr(10).join(f"- {issue}" for issue in rule_issues) if rule_issues else "无明显问题"}

【Agent评价意见】
{agent_feedback}

【决策任务】
请综合考虑以下因素做出决策：
1. 总分是否达到75分阈值？（已从74分提高到75分）
2. 规则问题是否严重（如结构缺失、致命错误）？
3. Agent的评价是否指出重大教学缺陷？
4. 当前是第几轮？（第3轮需更宽容）
5. 问题的性质：结构性问题 vs 细节问题

【决策选项】⚠️ 2026-02-15更新
- "accept": 接受当前代码（总分≥75且无重大问题）
- "reject": 完全重新生成（总分<65或有致命结构错误，丢弃当前代码从头开始）
- "fix": 在当前代码基础上修复（65≤总分<75，有可修复的细节问题）

【决策指南】
- 总分<75分 → 必须选择 "reject" 或 "fix"，不能accept
- 结构性问题（缺少必要元素、逻辑错误）→ 选择 "reject" 重做
- 细节问题（布局、颜色、交互优化）→ 选择 "fix" 修复
- 如果总分=0（缺少必要元素）→ 必须选择 "reject"
- 第3轮时，如果总分≥70，可以选择 "accept"（放宽标准）

【输出格式】
请输出JSON格式：
{{
    "decision": "accept",
    "reason": "简要说明决策理由（30-100字）"
}}"""

        try:
            response = await self.claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt="你是AI监督者，负责质量把关。请客观评估，既要保证质量，也要避免过于严苛。对于结构性问题选择reject重做，对于细节问题选择fix修复。",
                max_tokens=300
            )

            # 解析JSON
            import json
            import re

            json_match = re.search(r'\{[^{}]*"decision"[^{}]*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                decision = data.get('decision', 'fix')
                reason = data.get('reason', '')

                # 验证决策合法性（revise改为fix）
                if decision == 'revise':
                    decision = 'fix'  # 兼容旧版本
                if decision not in ['accept', 'reject', 'fix']:
                    logger.warning(f"[Supervisor] Invalid decision '{decision}', using 'fix'")
                    decision = 'fix'

                # 特殊规则：总分=0必须reject
                if total_score == 0 and decision != 'reject':
                    logger.warning(f"[Supervisor] Total score is 0, forcing 'reject' decision")
                    decision = 'reject'
                    reason = "总分为0（缺少必要元素），必须重新生成"

                logger.info(f"[Supervisor] Decision={decision}, Reason={reason}")
                return decision, reason
            else:
                logger.warning(f"[Supervisor] Failed to parse decision: {response[:200]}")
                # 默认决策
                if total_score == 0:
                    return 'reject', '总分为0，必须重新生成'
                elif total_score >= 75:
                    return 'accept', '总分达标，默认通过'
                elif total_score >= 65:
                    return 'fix', '分数接近阈值，建议修复'
                else:
                    return 'reject', '分数过低，需要重新生成'

        except Exception as e:
            logger.error(f"[Supervisor] Decision error: {e}")
            # 出错时使用简单规则
            if total_score == 0:
                return 'reject', '总分为0，必须重新生成'
            elif total_score >= 75:
                return 'accept', f'异常处理：总分{total_score}达标'
            else:
                return 'reject', f'异常处理：总分{total_score}不达标'

    def should_evaluate_with_agent(
        self,
        step_type: str,
        rule_score: float,
        similar_samples: Optional[List[Dict]] = None
    ) -> tuple:
        """
        智能决策是否需要Agent评估（任务#5）

        策略：
        1. 样本充足度检查（>=5个相似样本，方差<100）
        2. 基于规则分估算Agent分
        3. 概率跳过逻辑（预估总分>=50时，50%概率跳过）

        Args:
            step_type: 步骤类型
            rule_score: 规则打分（0-80）
            similar_samples: 相似样本列表（包含历史评分数据）

        Returns:
            (should_evaluate: bool, reason: str)
        """
        # 1. 样本充足度检查
        sample_count = self._count_samples(similar_samples)

        if sample_count < 5:
            logger.info(f"[Smart Decision] Sample insufficient ({sample_count}<5), MUST evaluate with Agent")
            return True, f"样本不足({sample_count}<5)，必须Agent评估"

        # 2. 检查分数方差
        scores = [s.get('total_score', 0) for s in similar_samples if 'total_score' in s]
        if not scores:
            logger.info(f"[Smart Decision] No historical scores, MUST evaluate")
            return True, "无历史评分数据，必须Agent评估"

        variance = self._calculate_variance(scores)
        if variance >= 100:
            logger.info(f"[Smart Decision] High variance ({variance:.1f}>=100), MUST evaluate")
            return True, f"分数方差大({variance:.1f}>=100)，必须Agent评估"

        # 3. 估算Agent分
        estimated_agent_score = self._estimate_agent_score(rule_score, similar_samples)
        estimated_total = rule_score + estimated_agent_score

        logger.info(f"[Smart Decision] Rule={rule_score}/60, Est_Agent={estimated_agent_score}/40, Est_Total={estimated_total}/100")

        # 4. 概率跳过逻辑
        if estimated_total >= 50:
            # 50%概率跳过
            import random
            skip_agent = random.random() < 0.5
            if skip_agent:
                logger.info(f"[Smart Decision] Est_Total={estimated_total}>=50, Skip Agent (prob=0.5)")
                return False, f"预估总分{estimated_total}分达标，概率跳过Agent评估"
            else:
                logger.info(f"[Smart Decision] Est_Total={estimated_total}>=50, Still evaluate (prob=0.5)")
                return True, f"预估总分{estimated_total}分，随机决策需要Agent评估"
        else:
            logger.info(f"[Smart Decision] Est_Total={estimated_total}<50, MUST evaluate")
            return True, f"预估总分{estimated_total}分不达标，必须Agent评估"

    def _count_samples(self, similar_samples: Optional[List[Dict]]) -> int:
        """统计有效样本数量"""
        if not similar_samples:
            return 0
        # 只统计有完整评分数据的样本
        return len([s for s in similar_samples if 'rule_score' in s and 'agent_score' in s])

    def _calculate_variance(self, scores: List[float]) -> float:
        """计算分数方差"""
        if not scores or len(scores) < 2:
            return 999.0  # 样本太少，返回高方差

        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance

    def _estimate_agent_score(
        self,
        rule_score: float,
        similar_samples: Optional[List[Dict]]
    ) -> float:
        """
        基于规则分估算Agent分（2026-02-15调整为40分制）

        策略：
        1. 如果有相似样本，使用平均Agent分
        2. 如果无样本，使用启发式规则：
           - rule_score >= 50: agent_score ≈ 30
           - rule_score >= 40: agent_score ≈ 24
           - rule_score >= 25: agent_score ≈ 16
           - rule_score < 25: agent_score ≈ 10
        """
        if similar_samples:
            agent_scores = [s.get('agent_score', 0) for s in similar_samples if 'agent_score' in s]
            if agent_scores:
                avg_agent = sum(agent_scores) / len(agent_scores)
                logger.info(f"[Estimate] Using avg agent score from {len(agent_scores)} samples: {avg_agent:.1f}")
                return avg_agent

        # 启发式规则（调整为40分制）
        if rule_score >= 50:
            return 30.0
        elif rule_score >= 40:
            return 24.0
        elif rule_score >= 25:
            return 16.0
        else:
            return 10.0


class GeneratorPromptBuilder:
    """生成器提示词构建器"""

    @staticmethod
    def build_system_prompt(processor_id: str) -> str:
        """构建系统提示词"""
        base_prompt = """你是一位专业的课程内容生成专家。你的任务是根据监督者的指令生成高质量的章节内容。

【你的职责】
1. 严格按照指令生成章节内容
2. 确保模拟器代码完整、可运行、美观
3. 确保内容深度足够、逻辑清晰
4. 不要生成与已有内容重复的模拟器

【模拟器代码规范】
- 必须有 setup(ctx) 和 update(ctx) 函数
- 必须使用 ctx.getVar() 读取变量
- 必须有动画效果和文字标签
- 代码至少80行，逻辑完整

【美学设计要求 - 重要】
1. 配色：使用监督者推荐的学科配色方案
   - 主色、次色、强调色协调搭配
   - 文字使用亮色（#ffffff, #e2e8f0），确保高对比度
   - 禁止使用深色（#000000, #111111等），会与背景融合

2. 构图：遵循视觉层次原则
   - 必须有标题（大字号，居中）
   - 必须有图例或状态面板（显示数值）
   - 至少6个文字标签（说明关键元素）
   - 主要元素突出，次要元素辅助

3. 动画：使用缓动函数实现自然流畅
   - 推荐使用 ctx.math.lerp() 实现平滑过渡
   - 推荐使用 easeOutBack 实现弹性效果
   - 避免突兀的跳变

4. 精致度：注重细节品质
   - 矩形使用圆角（cornerRadius: 4-8）
   - 重点元素添加发光效果（setGlow）
   - 代码有清晰注释和分段
   - 变量命名语义化

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
