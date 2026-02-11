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

# 旧的ctx API白名单 (已废弃，仅用于检测和警告)
DEPRECATED_CTX_APIS = [
    'createCircle', 'createRect', 'createText', 'createLine',
    'createCurve', 'createPolygon', 'setPosition', 'setScale',
    'setRotation', 'setAlpha', 'setColor', 'setText', 'setVisible',
    'remove', 'clear', 'setGlow', 'setCurvePoints', 'setRadius',
    'setSize', 'getVar', 'setVar'
]

# 所有有效的API（新的Canvas 2D API）
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
        self.claude_service = ClaudeService()
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
            score, issues = self._supervisor_review(code)
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

            if score >= 74:
                logger.info(f"[Simulator Gen] Passed with score {score}/100")
                yield {"type": "result", "code": self._auto_fix_colors(code), "score": score, "source": "generated"}
                return

            logger.warning(f"[Round {round_num}] Score {score}/100 < 74, issues: {issues}")

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
                history_hint += f"- 第{h['round']}轮 ({h['score']}分): {', '.join(h['issues'][:3])}\n"

        prompt = f"""生成完整HTML模拟器。只输出完整的HTML代码，不要任何markdown标记或解释。

【模拟器】{simulator_name}
【描述】{simulator_description}
【画布尺寸】800×500（管理端预览），运行时CSS自适应
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
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            overflow: hidden;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        #canvas {{
            display: block;
            background: #0F172A;
            border-radius: 8px;
        }}
        .controls {{
            margin-top: 20px;
            background: rgba(30, 41, 59, 0.95);
            padding: 15px 25px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(100, 116, 139, 0.3);
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
            color: #CBD5E1;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
        }}
        .value-display {{
            color: #60A5FA;
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
            width: 16px;
            height: 16px;
            background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
            border-radius: 50%%;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <canvas id="canvas" width="800" height="500"></canvas>
    <div class="controls">
        <!-- 变量控制HTML将在这里生成 -->
    </div>
    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        let variables = {{/* 变量初始值 */}};

        // 变量监听器将在这里生成

        function animate() {{
            ctx.fillStyle = '#0F172A';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

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

【推荐配色方案】
主色调: '#3B82F6', '#60A5FA', '#93C5FD'
次色调: '#8B5CF6', '#A78BFA', '#C4B5FD'
强调色: '#F59E0B', '#FBBF24', '#FCD34D'
成功色: '#10B981', '#34D399', '#6EE7B7'
警告色: '#EF4444', '#F87171', '#FCA5A5'
文本色: '#F1F5F9', '#E2E8F0', '#CBD5E1', '#94A3B8'
背景色: '#0F172A', '#1E293B', '#334155'

【核心要求】
1. 完整HTML文档（DOCTYPE + head + body）
2. 所有代码在单个文件中（self-contained）
3. 使用Canvas 2D API绘制（不使用外部库）
4. 使用requestAnimationFrame动画循环
5. 至少2个input range控件
6. 实时显示数值变化
7. 画布尺寸：width="800" height="500"
8. 配色协调美观
9. 代码清晰注释适当

【禁止项】
❌ 外部库（Three.js, D3.js等）
❌ eval(), Function(), setTimeout
❌ fetch(), XMLHttpRequest, localStorage
❌ 不要markdown代码块标记（```html等）
❌ 不要任何解释文字

【质量标准】
- 视觉吸引力：发光效果、渐变、阴影
- 交互性：至少2个可调参数实时响应
- 教育性：清晰展示概念计算准确
- 代码质量：结构清晰注释适当

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
        if last['score'] < 50:
            return 'regenerate'

        # 连续两轮但分数没有提升 → 重做
        if len(history) >= 2:
            prev = history[-2]
            if last['score'] <= prev['score']:
                return 'regenerate'

        # 表面问题（颜色、文本显示不足）→ 修改
        return 'fix'
        return 'fix'

    async def _producer_fix_code(
        self,
        code: str,
        issues: List[str],
        simulator_name: str,
        system_prompt: str
    ) -> Optional[str]:
        """生产者：修复现有代码"""
        if not code:
            return None

        prompt = f"""修复以下HTML代码的问题。只输出修复后的完整HTML代码。

【原代码】
{code}

【需要修复的问题】
{chr(10).join([f"- {issue}" for issue in issues])}

【模拟器】{simulator_name}

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
- 如果有"中文标点"错误，将代码中的中文标点替换为英文标点（字符串和注释中的中文可以保留）

【严格要求】
- 直接输出完整HTML代码
- 不要 ``` 标记
- 不要解释
- 必须以 <!DOCTYPE html> 开头"""

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

    def _supervisor_review(self, code: str) -> tuple:
        """
        监督者：审核代码并打分

        评分标准（满分100）：
        - 可运行性: 30分（HTML结构、脚本正确）
        - 内容完整: 30分（视觉元素、交互功能）
        - 表达深度: 20分（代码行数、元素丰富度）
        - 渲染质量: 20分（颜色正确、动画效果）

        Returns:
            (score, issues)
        """
        score = 100
        issues = []

        # === 可运行性 (30分) ===
        # 检查HTML结构
        has_html_tag = '<!DOCTYPE html>' in code and '<html' in code
        has_canvas = '<canvas' in code
        has_script = '<script>' in code or '<script ' in code

        if not has_html_tag:
            score -= 20
            issues.append("缺少完整HTML结构(<!DOCTYPE html>)")
        if not has_canvas:
            score -= 10
            issues.append("缺少canvas元素")
        if not has_script:
            score -= 10
            issues.append("缺少script脚本")

        # 对于HTML格式，不检查ctx API，因为使用的是Canvas 2D原生API
        # api_valid, _, invalid_apis = self._validate_api_usage(code)
        # if not api_valid:
        #     score -= 15
        #     issues.append(f"无效API: {', '.join(invalid_apis[:3])}")

        # 语法验证（重复声明、中文标点等致命问题）
        syntax_valid, syntax_error = self._validate_js_syntax_detailed(code)
        if not syntax_valid and syntax_error:
            if syntax_error.error_type in (SyntaxErrorType.DUPLICATE_DECLARATION, SyntaxErrorType.CHINESE_PUNCTUATION):
                score -= 25
                issues.append(f"致命语法错误: {syntax_error.message}")
            elif syntax_error.error_type in (SyntaxErrorType.UNCLOSED_BRACKET, SyntaxErrorType.MISMATCHED_BRACKET):
                score -= 20
                issues.append(f"括号错误: {syntax_error.message}")

        # 检查 API 参数格式是否正确
        import re
        # HTML Canvas 2D API使用原生方法，不需要检查ctx.create*参数
        param_issues = []

        # HTML使用原生Math对象，不需要检查
        # global_math_calls = re.findall(r'(?<!\w)Math\.(floor|ceil|round|sin|cos|tan|abs|sqrt|pow|min|max|random|PI)\b', code)
        # if global_math_calls:
        #     unique_calls = list(set(global_math_calls))[:3]
        #     param_issues.append(f"使用了全局Math而非math: Math.{', Math.'.join(unique_calls)}")

        if param_issues:
            score -= 10
            issues.extend(param_issues)

        # HTML Canvas 2D API不需要检查ctx.create*的参数数量
        # 因为使用的是原生Canvas API (fillRect, arc, etc.)

        # === 内容完整 (30分) ===
        # HTML模拟器不需要检查变量读取，因为交互控件直接在HTML中实现

        # 检查是否有文本显示元素
        has_text_display = bool(re.search(r'<(span|div|p)[^>]*id=["\'][^"\']+["\'][^>]*>', code))
        if not has_text_display:
            score -= 10
            issues.append("缺少文本显示元素")


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

        # 代码过长扣分
        if code_lines > 200:
            score -= 10
            issues.append(f"代码过长: {code_lines}行(建议200行以内)")

        # 检查元素丰富度 (HTML中的Canvas绘图调用)
        canvas_draw_count = len(re.findall(r'\b(fillRect|strokeRect|arc|fillText|beginPath|lineTo|moveTo)\b', code))
        if canvas_draw_count < 5:
            score -= 10
            issues.append(f"Canvas绘图元素太少: {canvas_draw_count}个(建议5+)")

        # === 提取 script 代码段 ===
        script_section = ''
        if '<script>' in code:
            script_matches = re.findall(r'<script[^>]*>(.*?)</script>', code, re.DOTALL)
            if script_matches:
                script_section = script_matches[0]

        # === 渲染质量 (20分) ===
        color_valid, _, dark_colors = self._validate_color_contrast(code)
        if not color_valid:
            score -= 5
            issues.append(f"深色: {', '.join(dark_colors[:3])}")

        # 检查动画逻辑 (requestAnimationFrame)
        has_animation = 'requestAnimationFrame' in code
        has_math = bool(re.search(r'Math\.(sin|cos|PI|abs|sqrt|pow)', code))

        if not has_animation:
            score -= 5
            issues.append("缺少动画循环(requestAnimationFrame)")
        if not has_math:
            score -= 3
            issues.append("缺少数学运算(Math.sin/cos等)")

        # 检查交互控件
        has_controls = bool(re.search(r'<input[^>]*type=["\']range["\']', code))
        if not has_controls:
            score -= 5
            issues.append("缺少交互控件(range input)")

        # 检查是否使用了 emoji 或 Unicode 特殊字符代替图形
        emoji_pattern = re.findall(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FA6F]', code)
        if emoji_pattern:
            score -= 10
            issues.append("使用了emoji/Unicode特殊字符，应使用Canvas 2D API绘制")

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
        清理AI响应，提取HTML代码（2026-02-11: 适配HTML格式）

        支持的格式：
        1. 直接的HTML代码（以<!DOCTYPE开头）
        2. Markdown代码块包裹的HTML（```html ... ```）
        3. JSON包裹的HTML（{"code": "..."}）
        """
        import re
        import json as _json

        code = response.strip()
        original_response = response

        # 1. 检测JSON包裹格式：{"code": "<!DOCTYPE html>..."}
        try:
            json_str = code
            # 移除markdown代码块标记
            if json_str.startswith('```'):
                first_newline = json_str.index('\n')
                json_str = json_str[first_newline + 1:]
            if json_str.rstrip().endswith('```'):
                json_str = json_str.rstrip()[:-3].rstrip()

            # 尝试解析JSON
            parsed = _json.loads(json_str)
            if isinstance(parsed, dict) and 'code' in parsed:
                extracted = parsed['code']
                if isinstance(extracted, str) and len(extracted) > 100:
                    # 检查是否是HTML
                    if '<!DOCTYPE' in extracted.upper() or '<HTML' in extracted.upper():
                        logger.info(f"[_clean_simulator_code] Extracted HTML from JSON 'code' field: {len(extracted.splitlines())} lines")
                        return extracted.strip()
        except (ValueError, _json.JSONDecodeError, IndexError):
            pass

        # 2. 提取HTML代码块：```html ... ```
        html_blocks = re.findall(r'```html\s*\n(.*?)```', code, re.DOTALL | re.IGNORECASE)
        if html_blocks:
            # 选择最长的HTML块
            best_block = max(html_blocks, key=len)
            logger.info(f"[_clean_simulator_code] Extracted from ```html block: {len(best_block.splitlines())} lines")
            return best_block.strip()

        # 3. 提取任意代码块：``` ... ```
        code_blocks = re.findall(r'```[a-z]*\s*\n(.*?)```', code, re.DOTALL | re.IGNORECASE)
        if code_blocks:
            # 优先选择包含DOCTYPE或<html>的块
            for block in code_blocks:
                if '<!DOCTYPE' in block.upper() or '<HTML' in block.upper():
                    logger.info(f"[_clean_simulator_code] Extracted HTML from generic code block: {len(block.splitlines())} lines")
                    return block.strip()
            # 如果没有找到HTML特征，选择最长的块
            best_block = max(code_blocks, key=len)
            if len(best_block) > 100:
                logger.info(f"[_clean_simulator_code] Extracted longest code block: {len(best_block.splitlines())} lines")
                return best_block.strip()

        # 4. 直接的HTML代码（没有markdown包裹）
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
                extracted = code[start_pos:end_pos]
                logger.info(f"[_clean_simulator_code] Extracted raw HTML: {len(extracted.splitlines())} lines")
                return extracted.strip()
            else:
                # 没有找到</html>，取到末尾
                extracted = code[start_pos:]
                logger.info(f"[_clean_simulator_code] Extracted HTML (no closing tag): {len(extracted.splitlines())} lines")
                return extracted.strip()

        # 5. 最后尝试：移除明显的解释文字，返回剩余内容
        lines = code.split('\n')
        # 移除开头的纯文字解释行（不包含<或{的行）
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if '<' in stripped or '{' in stripped or stripped.startswith('//') or stripped == '':
                start_idx = i
                break

        # 移除结尾的纯文字解释行
        end_idx = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            stripped = lines[i].strip()
            if '>' in stripped or '}' in stripped or stripped.startswith('//') or stripped == '':
                end_idx = i + 1
                break

        if start_idx < end_idx:
            result = '\n'.join(lines[start_idx:end_idx]).strip()
            if len(result) > 100:
                logger.info(f"[_clean_simulator_code] Extracted after removing explanations: {len(result.splitlines())} lines")
                return result

        # 6. 完全失败，返回原始响应
        logger.warning(f"[_clean_simulator_code] Failed to extract HTML, returning original response: {len(original_response)} chars")
        return original_response.strip()

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
            script = []
            for step_data in data.get('script', []):
                step = ChapterStep(
                    step_id=step_data.get('step_id', f'step_{len(script)+1}'),
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
