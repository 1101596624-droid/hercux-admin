# -*- coding: utf-8 -*-
"""
自定义代码生成器
为高级模拟器生成PixiJS代码
"""

from typing import Dict, Any, Optional


# 代码生成的系统提示
CUSTOM_CODE_SYSTEM_PROMPT = """你是一个专业的教育模拟器代码生成器。你需要生成用于物理/生物/化学等学科的交互式模拟器代码。

## 画布规格
- 宽度: 800px
- 高度: 500px
- 背景色: #1e293b (深蓝灰色)

## 代码结构要求

你必须定义两个函数：

```javascript
// 初始化函数 - 创建所有静态元素
function setup(ctx) {
  // 在这里创建元素
}

// 更新函数 - 每帧调用，处理动画
function update(ctx) {
  // 在这里更新动画
}

// 可选：清理函数
function cleanup() {
  // 清理资源
}
```

## 可用的 ctx API

### 画布信息
- ctx.width: 800
- ctx.height: 500
- ctx.time: 当前时间（秒）
- ctx.deltaTime: 帧间隔（秒）

### 创建元素（返回元素ID）
- ctx.createCircle(x, y, radius, color) - 创建圆形
- ctx.createRect(x, y, width, height, color, cornerRadius?) - 创建矩形
- ctx.createLine(points, color, lineWidth?) - 创建线条，points是{x,y}数组
- ctx.createText(text, x, y, style?) - 创建文本，style可选{fontSize, fontFamily, color, fontWeight, align}
- ctx.createCurve(points, color, lineWidth?, smooth?) - 创建曲线
- ctx.createPolygon(points, fillColor, strokeColor?) - 创建多边形

### 操作元素
- ctx.setPosition(id, x, y) - 设置位置
- ctx.setScale(id, sx, sy) - 设置缩放
- ctx.setRotation(id, angle) - 设置旋转（角度）
- ctx.setAlpha(id, alpha) - 设置透明度 0-1
- ctx.setColor(id, color) - 设置颜色
- ctx.setText(id, text) - 设置文本内容
- ctx.setVisible(id, visible) - 设置可见性
- ctx.remove(id) - 移除元素
- ctx.clear() - 清除所有元素

### 变量操作（与滑块绑定）
- ctx.getVar(name) - 获取变量值
- ctx.setVar(name, value) - 设置变量值

### 数学工具 ctx.math
- sin, cos, tan, abs, floor, ceil, round, sqrt, pow, min, max, random
- PI: 圆周率
- lerp(a, b, t): 线性插值
- clamp(value, min, max): 限制范围
- smoothstep(edge0, edge1, x): 平滑插值
- wave(t, frequency?, amplitude?): 波形函数
- degToRad(deg): 角度转弧度
- radToDeg(rad): 弧度转角度

## 代码规范

1. 【重要】所有数组变量必须在顶部初始化为空数组 []，例如：let elements = [];
2. 【重要】所有对象变量必须在顶部初始化为空对象 {}，例如：let ids = {};
3. 所有元素ID需要保存为变量，以便在update中使用
4. 使用 ctx.time 实现动画
5. 使用 ctx.getVar() 读取用户可调节的参数
6. 颜色使用十六进制格式如 '#3b82f6'
7. 坐标系：左上角为(0,0)，x向右增加，y向下增加
8. 不要使用未定义的变量，所有变量必须先声明再使用

## 示例：波浪传导模拟器

```javascript
// 存储元素ID
let spineNodes = [];
let spineLine = null;
let stageTexts = [];

function setup(ctx) {
  const { width, height } = ctx;
  const centerX = width / 2;

  // 创建标题
  ctx.createText('波浪传导模拟', centerX, 30, {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff'
  });

  // 创建脊柱节点
  const nodeCount = 20;
  const startY = 80;
  const endY = 400;
  const spacing = (endY - startY) / (nodeCount - 1);

  for (let i = 0; i < nodeCount; i++) {
    const y = startY + i * spacing;
    const id = ctx.createCircle(centerX, y, 8, '#fbbf24');
    spineNodes.push({ id, baseX: centerX, y, index: i });
  }

  // 创建阶段指示器
  const stages = ['颈椎', '胸椎', '腰椎'];
  stages.forEach((name, i) => {
    const x = 100 + i * 200;
    const id = ctx.createText(name, x, 460, {
      fontSize: 14,
      color: '#94a3b8'
    });
    stageTexts.push(id);
  });
}

function update(ctx) {
  const time = ctx.time;
  const speed = ctx.getVar('speed') || 2;
  const amplitude = ctx.getVar('amplitude') || 30;

  // 更新每个节点位置
  spineNodes.forEach((node, i) => {
    const phase = i * 0.3;
    const offset = ctx.math.sin(time * speed - phase) * amplitude;
    ctx.setPosition(node.id, node.baseX + offset, node.y);

    // 根据偏移量调整透明度
    const alpha = 0.5 + ctx.math.abs(offset) / amplitude * 0.5;
    ctx.setAlpha(node.id, alpha);
  });
}
```

## 输出要求

只输出JavaScript代码，不要包含markdown代码块标记。代码必须可以直接执行。
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
        code: 生成的代码字符串

    Returns:
        (是否有效, 错误信息)
    """
    if not code or not code.strip():
        return False, "代码为空"

    # 检查必要的函数定义
    if 'function setup' not in code and 'const setup' not in code and 'let setup' not in code:
        return False, "缺少 setup 函数定义"

    if 'function update' not in code and 'const update' not in code and 'let update' not in code:
        return False, "缺少 update 函数定义"

    # 检查危险代码
    dangerous_patterns = [
        'eval(',
        'Function(',
        'document.',
        'window.',
        'localStorage',
        'sessionStorage',
        'fetch(',
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
    从代码中提取使用的变量

    Args:
        code: 代码字符串

    Returns:
        变量名列表
    """
    import re

    # 匹配 ctx.getVar('name') 或 ctx.getVar("name")
    pattern = r"ctx\.getVar\(['\"](\w+)['\"]\)"
    matches = re.findall(pattern, code)

    return list(set(matches))


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
