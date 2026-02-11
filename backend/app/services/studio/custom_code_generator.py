# -*- coding: utf-8 -*-
"""
自定义代码生成器
为高级模拟器生成HTML代码
"""

from typing import Dict, Any, Optional


# 代码生成的系统提示
CUSTOM_CODE_SYSTEM_PROMPT = """你是一个专业的教育模拟器代码生成器。你需要生成用于物理/生物/化学等学科的交互式模拟器HTML页面。

## 画布规格
- 宽度: 800px
- 高度: 500px
- 背景色: #1e293b (深蓝灰色)

## 代码结构要求

你必须生成一个完整的HTML文档，包含以下结构：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>模拟器标题</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #1e293b;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        canvas {
            display: block;
        }
        .controls {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(15, 23, 42, 0.95);
            padding: 20px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        /* 其他样式 */
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>
    <div class="controls">
        <!-- 控制面板：滑块、按钮等 -->
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        // 设置画布尺寸
        canvas.width = 800;
        canvas.height = 500;

        // 变量定义
        let variables = {
            speed: 2,
            amplitude: 30
        };

        // 初始化函数
        function init() {
            // 初始化代码
        }

        // 动画循环
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 绘制代码

            requestAnimationFrame(animate);
        }

        // 启动
        init();
        animate();
    </script>
</body>
</html>
```

## Canvas 2D API 使用指南

### 基础绘制
- `ctx.fillStyle = color` - 设置填充颜色
- `ctx.strokeStyle = color` - 设置描边颜色
- `ctx.lineWidth = width` - 设置线宽
- `ctx.fillRect(x, y, w, h)` - 绘制填充矩形
- `ctx.strokeRect(x, y, w, h)` - 绘制描边矩形
- `ctx.clearRect(x, y, w, h)` - 清除矩形区域

### 路径绘制
- `ctx.beginPath()` - 开始新路径
- `ctx.moveTo(x, y)` - 移动到点
- `ctx.lineTo(x, y)` - 画线到点
- `ctx.arc(x, y, radius, startAngle, endAngle)` - 画圆弧
- `ctx.fill()` - 填充路径
- `ctx.stroke()` - 描边路径

### 文本绘制
- `ctx.font = '16px Arial'` - 设置字体
- `ctx.fillText(text, x, y)` - 绘制填充文本
- `ctx.strokeText(text, x, y)` - 绘制描边文本
- `ctx.textAlign = 'center'` - 文本对齐

### 变换
- `ctx.save()` - 保存状态
- `ctx.restore()` - 恢复状态
- `ctx.translate(x, y)` - 平移
- `ctx.rotate(angle)` - 旋转（弧度）
- `ctx.scale(sx, sy)` - 缩放

## 代码规范

1. 【重要】必须是完整的HTML文档，包含 <!DOCTYPE html>
2. 【重要】Canvas尺寸固定为 800x500
3. 使用 requestAnimationFrame 实现动画循环
4. 控制面板使用 HTML input 元素（滑块、按钮等）
5. 颜色使用十六进制格式如 '#3b82f6' 或 rgba()
6. 坐标系：左上角为(0,0)，x向右增加，y向下增加
7. 不使用外部依赖库，纯原生 JavaScript + Canvas API
8. 确保所有交互元素都有清晰的标签和视觉反馈

## 示例：波浪传导模拟器

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>波浪传导模拟器</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #1e293b;
            font-family: sans-serif;
        }
        canvas {
            display: block;
        }
        .controls {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(15, 23, 42, 0.95);
            padding: 20px;
            border-radius: 12px;
            min-width: 300px;
        }
        .control-item {
            margin: 10px 0;
            color: #e2e8f0;
        }
        .control-item label {
            display: block;
            margin-bottom: 5px;
            font-size: 14px;
        }
        input[type="range"] {
            width: 100%;
        }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>
    <div class="controls">
        <div class="control-item">
            <label>速度: <span id="speedValue">2.0</span></label>
            <input type="range" id="speed" min="0.5" max="5" step="0.1" value="2">
        </div>
        <div class="control-item">
            <label>振幅: <span id="amplitudeValue">30</span></label>
            <input type="range" id="amplitude" min="10" max="80" step="1" value="30">
        </div>
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = 800;
        canvas.height = 500;

        let speed = 2.0;
        let amplitude = 30;
        let time = 0;

        // 节点配置
        const nodeCount = 20;
        const startY = 80;
        const endY = 400;
        const spacing = (endY - startY) / (nodeCount - 1);
        const centerX = canvas.width / 2;

        // 控制面板事件
        document.getElementById('speed').addEventListener('input', (e) => {
            speed = parseFloat(e.target.value);
            document.getElementById('speedValue').textContent = speed.toFixed(1);
        });

        document.getElementById('amplitude').addEventListener('input', (e) => {
            amplitude = parseFloat(e.target.value);
            document.getElementById('amplitudeValue').textContent = amplitude;
        });

        function animate() {
            ctx.fillStyle = '#1e293b';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 绘制标题
            ctx.font = 'bold 24px sans-serif';
            ctx.fillStyle = '#ffffff';
            ctx.textAlign = 'center';
            ctx.fillText('波浪传导模拟', centerX, 30);

            // 绘制节点
            for (let i = 0; i < nodeCount; i++) {
                const y = startY + i * spacing;
                const phase = i * 0.3;
                const offset = Math.sin(time * speed - phase) * amplitude;
                const x = centerX + offset;

                // 透明度随偏移量变化
                const alpha = 0.5 + Math.abs(offset) / amplitude * 0.5;

                ctx.beginPath();
                ctx.arc(x, y, 8, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(251, 191, 36, ${alpha})`;
                ctx.fill();
            }

            // 绘制阶段标签
            const stages = ['颈椎', '胸椎', '腰椎'];
            ctx.font = '14px sans-serif';
            ctx.fillStyle = '#94a3b8';
            stages.forEach((name, i) => {
                ctx.fillText(name, 100 + i * 200, 460);
            });

            time += 0.016; // ~60fps
            requestAnimationFrame(animate);
        }

        animate();
    </script>
</body>
</html>
```

## 输出要求

只输出完整的HTML代码，不要包含markdown代码块标记。代码必须可以直接在浏览器中运行。
"""


def get_custom_code_prompt(topic: str, description: str, variables: list = None) -> str:
    """
    生成自定义代码的用户提示

    Args:
        topic: 模拟器主题
        description: 详细描述
        variables: 可选的变量列表 [{"name": "speed", "min": 0, "max": 10, "default": 2}, ...]

    Returns:
        用户提示字符串
    """
    var_desc = ""
    if variables:
        var_desc = "\n\n## 需要支持的变量（用户可通过滑块调节）\n"
        for var in variables:
            var_desc += f"- {var['name']}: 范围 {var.get('min', 0)} - {var.get('max', 100)}，默认值 {var.get('default', 50)}\n"

    return f"""请为以下主题创建一个交互式模拟器：

## 主题
{topic}

## 描述
{description}
{var_desc}

请生成完整的模拟器代码，包含 setup() 和 update() 函数。确保：
1. 视觉效果清晰美观
2. 动画流畅自然
3. 正确使用变量控制参数
4. 代码结构清晰
"""


def validate_custom_code(code: str) -> tuple[bool, str]:
    """
    验证生成的代码是否符合规范

    Args:
        code: 生成的HTML代码字符串

    Returns:
        (是否有效, 错误信息)
    """
    if not code or not code.strip():
        return False, "代码为空"

    # 检查必要的HTML结构
    if '<!DOCTYPE html>' not in code and '<!doctype html>' not in code:
        return False, "缺少 DOCTYPE 声明"

    if '<canvas' not in code:
        return False, "缺少 canvas 元素"

    if '<script>' not in code and '<script ' not in code:
        return False, "缺少 script 标签"

    # 检查危险代码（允许 document 和 window，因为是完整HTML）
    dangerous_patterns = [
        'eval(',
        'Function(',
        'localStorage',
        'sessionStorage',
        'XMLHttpRequest',
        'import(',
        'require(',
        '__proto__',
        'constructor[',
    ]

    for pattern in dangerous_patterns:
        if pattern in code:
            return False, f"代码包含不允许的模式: {pattern}"

    return True, ""


def extract_variables_from_code(code: str) -> list:
    """
    从HTML代码中提取使用的变量（从input元素的id中提取）

    Args:
        code: HTML代码字符串

    Returns:
        变量名列表
    """
    import re

    # 匹配 <input ... id="variableName" ...> 或类似模式
    # HTML模拟器自带控制面板，不需要外部变量定义
    # 返回空列表
    return []


class CustomCodeGenerator:
    """自定义代码生成器"""

    def __init__(self, ai_client):
        """
        初始化生成器

        Args:
            ai_client: AI客户端实例
        """
        self.ai_client = ai_client

    async def generate(
        self,
        topic: str,
        description: str,
        variables: list = None,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        生成模拟器代码

        Args:
            topic: 主题
            description: 描述
            variables: 变量列表
            max_retries: 最大重试次数

        Returns:
            {
                "success": bool,
                "code": str,
                "variables": list,
                "error": str | None
            }
        """
        user_prompt = get_custom_code_prompt(topic, description, variables)

        for attempt in range(max_retries + 1):
            try:
                # 调用AI生成代码
                response = await self.ai_client.chat(
                    messages=[
                        {"role": "system", "content": CUSTOM_CODE_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )

                code = response.get("content", "").strip()

                # 移除可能的markdown代码块标记
                if code.startswith("```"):
                    lines = code.split("\n")
                    code = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

                # 验证代码
                is_valid, error_msg = validate_custom_code(code)
                if not is_valid:
                    if attempt < max_retries:
                        user_prompt += f"\n\n上次生成的代码有问题：{error_msg}，请修正。"
                        continue
                    return {
                        "success": False,
                        "code": "",
                        "variables": [],
                        "error": error_msg
                    }

                # 提取变量
                used_variables = extract_variables_from_code(code)

                return {
                    "success": True,
                    "code": code,
                    "variables": used_variables,
                    "error": None
                }

            except Exception as e:
                if attempt < max_retries:
                    continue
                return {
                    "success": False,
                    "code": "",
                    "variables": [],
                    "error": str(e)
                }

        return {
            "success": False,
            "code": "",
            "variables": [],
            "error": "生成失败"
        }
