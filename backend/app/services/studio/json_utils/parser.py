# ============================================
# json_utils/parser.py - JSON 解析和修复工具
# ============================================

import json
import re
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def escape_unescaped_quotes_in_strings(text: str) -> str:
    """修复 JSON 字符串值中未转义的双引号

    AI 有时会生成类似这样的 JSON:
    "rationale": "学生常误解"肌丝本身缩短"，需要..."

    这里的内部双引号应该被转义为 \"
    """
    result = []
    i = 0
    in_string = False
    string_start = -1

    while i < len(text):
        char = text[i]

        # 处理转义字符
        if char == '\\' and i + 1 < len(text):
            result.append(char)
            result.append(text[i + 1])
            i += 2
            continue

        if char == '"':
            if not in_string:
                # 开始一个字符串
                in_string = True
                string_start = i
                result.append(char)
            else:
                # 可能是字符串结束，也可能是未转义的内部引号
                # 检查后面的字符来判断
                next_non_space = i + 1
                while next_non_space < len(text) and text[next_non_space] in ' \t\n\r':
                    next_non_space += 1

                # 如果后面是 JSON 结构字符，说明这是字符串结束
                if next_non_space >= len(text) or text[next_non_space] in ':,}]':
                    in_string = False
                    result.append(char)
                else:
                    # 这是一个未转义的内部引号，需要转义
                    # 但要检查是否是新键值对的开始（前面有逗号或开括号）
                    # 回溯检查前面的非空白字符
                    prev_non_space = len(result) - 1
                    while prev_non_space >= 0 and result[prev_non_space] in ' \t\n\r':
                        prev_non_space -= 1

                    if prev_non_space >= 0 and result[prev_non_space] in '{[,':
                        # 这是新键值对的开始，当前字符串被截断了
                        # 先闭合当前字符串
                        in_string = False
                        result.append('"')
                        # 然后开始新字符串
                        in_string = True
                        result.append(',')
                        result.append(char)
                    else:
                        # 这是内部引号，需要转义
                        result.append('\\')
                        result.append(char)
        else:
            result.append(char)

        i += 1

    return ''.join(result)


def safe_parse_json(text: str) -> Optional[dict]:
    """安全解析 JSON，支持修复被截断的 JSON"""
    text = text.strip()

    # 1. 直接尝试解析
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        pass

    # 1.5. 尝试修复未转义的引号后解析
    try:
        fixed = escape_unescaped_quotes_in_strings(text)
        return json.loads(fixed)
    except (json.JSONDecodeError, ValueError):
        pass

    # 2. 尝试从 markdown 代码块提取
    if "```" in text:
        # 尝试匹配完整的代码块
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            content = match.group(1)
            try:
                return json.loads(content)
            except (json.JSONDecodeError, ValueError):
                pass
            # 尝试修复未转义引号
            try:
                fixed = escape_unescaped_quotes_in_strings(content)
                return json.loads(fixed)
            except (json.JSONDecodeError, ValueError):
                pass
            # 代码块内容也可能被截断，尝试修复
            repaired = repair_truncated_json(content)
            if repaired:
                try:
                    return json.loads(repaired)
                except (json.JSONDecodeError, ValueError):
                    # 修复后再尝试转义引号
                    try:
                        fixed = escape_unescaped_quotes_in_strings(repaired)
                        return json.loads(fixed)
                    except (json.JSONDecodeError, ValueError):
                        pass

        # 尝试匹配只有开头标记的代码块（结尾被截断）
        match_start = re.search(r'```(?:json)?\s*([\s\S]+)', text)
        if match_start:
            content = match_start.group(1)
            # 移除可能的尾部 ``` 标记
            content = re.sub(r'\s*```\s*$', '', content)
            try:
                return json.loads(content)
            except (json.JSONDecodeError, ValueError):
                pass
            # 尝试修复未转义引号
            try:
                fixed = escape_unescaped_quotes_in_strings(content)
                return json.loads(fixed)
            except (json.JSONDecodeError, ValueError):
                pass
            repaired = repair_truncated_json(content)
            if repaired:
                try:
                    return json.loads(repaired)
                except (json.JSONDecodeError, ValueError):
                    # 修复后再尝试转义引号
                    try:
                        fixed = escape_unescaped_quotes_in_strings(repaired)
                        return json.loads(fixed)
                    except (json.JSONDecodeError, ValueError):
                        pass

    # 3. 提取 JSON 部分（从第一个 { 开始）
    start = text.find('{')
    if start != -1:
        json_text = text[start:]

        # 移除尾部的 markdown 代码块标记
        json_text = re.sub(r'\s*```\s*$', '', json_text)

        # 先尝试直接解析
        try:
            return json.loads(json_text)
        except (json.JSONDecodeError, ValueError):
            pass

        # 尝试修复未转义引号
        try:
            fixed = escape_unescaped_quotes_in_strings(json_text)
            return json.loads(fixed)
        except (json.JSONDecodeError, ValueError):
            pass

        # 4. 尝试修复被截断的 JSON
        repaired = repair_truncated_json(json_text)
        if repaired:
            try:
                result = json.loads(repaired)
                return result
            except (json.JSONDecodeError, ValueError):
                # 修复后再尝试转义引号
                try:
                    fixed = escape_unescaped_quotes_in_strings(repaired)
                    result = json.loads(fixed)
                    return result
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"JSON parse failed after all repair attempts: {e}, text length: {len(text)}")

    logger.debug(f"safe_parse_json: all strategies failed, text length: {len(text)}")
    return None


def repair_truncated_json(text: str) -> Optional[str]:
    """尝试修复被截断的 JSON - 更健壮的版本"""
    if not text:
        return None

    # 追踪状态
    in_string = False
    escape_next = False
    bracket_stack = []  # 记录括号类型和位置

    for i, char in enumerate(text):
        if escape_next:
            escape_next = False
            continue
        if char == '\\' and in_string:
            escape_next = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == '{':
            bracket_stack.append('}')
        elif char == '[':
            bracket_stack.append(']')
        elif char == '}':
            if bracket_stack and bracket_stack[-1] == '}':
                bracket_stack.pop()
        elif char == ']':
            if bracket_stack and bracket_stack[-1] == ']':
                bracket_stack.pop()

    # 如果在字符串中间截断，需要找到最后一个完整的 JSON 元素
    if in_string:
        safe_positions = []
        temp_in_string = False
        temp_escape = False
        temp_bracket_depth = 0

        for i, char in enumerate(text):
            if temp_escape:
                temp_escape = False
                continue
            if char == '\\' and temp_in_string:
                temp_escape = True
                continue
            if char == '"':
                temp_in_string = not temp_in_string
                continue
            if temp_in_string:
                continue

            if char in '{[':
                temp_bracket_depth += 1
            elif char in '}]':
                temp_bracket_depth -= 1
                safe_positions.append(i + 1)
            elif char == ',':
                safe_positions.append(i)

        if safe_positions:
            last_safe = safe_positions[-1]
            text = text[:last_safe]
            text = text.rstrip()
            if text.endswith(','):
                text = text[:-1]
        else:
            last_quote = -1
            temp_in_string = False
            temp_escape = False
            for i, char in enumerate(text):
                if temp_escape:
                    temp_escape = False
                    continue
                if char == '\\' and temp_in_string:
                    temp_escape = True
                    continue
                if char == '"':
                    temp_in_string = not temp_in_string
                    if not temp_in_string:
                        last_quote = i

            if last_quote > 0:
                text = text[:last_quote + 1]
            else:
                text = text + '"'

    # 重新计算需要闭合的括号
    in_string = False
    escape_next = False
    bracket_stack = []

    for char in text:
        if escape_next:
            escape_next = False
            continue
        if char == '\\' and in_string:
            escape_next = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == '{':
            bracket_stack.append('}')
        elif char == '[':
            bracket_stack.append(']')
        elif char == '}':
            if bracket_stack and bracket_stack[-1] == '}':
                bracket_stack.pop()
        elif char == ']':
            if bracket_stack and bracket_stack[-1] == ']':
                bracket_stack.pop()

    # 如果仍然在字符串中，闭合它
    if in_string:
        text += '"'

    # 闭合所有未闭合的括号（按正确顺序）
    while bracket_stack:
        text += bracket_stack.pop()

    return text
