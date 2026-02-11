"""
模拟器预发布检查脚本
在课程发布前运行，检查所有模拟器代码的常见问题。

用法:
  python scripts/check_simulators.py [--course-id ID]

不指定 course-id 则检查所有课程。
"""

import asyncio
import json
import re
import sys
import argparse


# ==================== 检查函数 ====================

def check_duplicate_declarations(code: str) -> list:
    """检查同一作用域内的重复 let/const 声明"""
    issues = []
    lines = code.split('\n')
    current_func = None
    brace_depth = 0
    declarations = {}

    for line_num, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('/*'):
            continue

        if 'function setup' in stripped:
            current_func = 'setup'
            brace_depth = 0
            declarations.setdefault('setup', {})
        elif 'function update' in stripped:
            current_func = 'update'
            brace_depth = 0
            declarations.setdefault('update', {})

        brace_depth += stripped.count('{') - stripped.count('}')

        if current_func and brace_depth == 1:
            if stripped.startswith(('for', 'if', 'while', 'switch', '//')):
                continue
            m = re.match(r'(let|const)\s+(\w+)', stripped)
            if m:
                var_name = m.group(2)
                func_decls = declarations.get(current_func, {})
                if var_name in func_decls:
                    issues.append(f"FATAL: {current_func}() 中重复声明 '{var_name}' (行{line_num+1}, 首次行{func_decls[var_name]+1})")
                func_decls[var_name] = line_num
                declarations[current_func] = func_decls

    return issues


def check_chinese_punctuation(code: str) -> list:
    """检查代码区域（非字符串、非注释）中的中文标点"""
    issues = []
    chinese_punct = re.compile(r'[，。；：（）【】！？]')
    lines = code.split('\n')

    for line_num, line in enumerate(lines):
        clean = re.sub(r'//[^\n]*', '', line)
        clean = re.sub(r'/\*.*?\*/', '', clean, flags=re.DOTALL)
        clean = re.sub(r"'[^']*'|\"[^\"]*\"|`[^`]*`", '', clean, flags=re.DOTALL)
        found = chinese_punct.findall(clean)
        if found:
            issues.append(f"FATAL: 行{line_num+1} 代码中有中文标点: {''.join(found)} | {line.strip()[:80]}")

    return issues


def check_missing_functions(code: str) -> list:
    """检查是否缺少 setup/update 函数"""
    issues = []
    if 'function setup' not in code:
        issues.append("FATAL: 缺少 function setup(ctx)")
    if 'function update' not in code:
        issues.append("FATAL: 缺少 function update(ctx)")
    return issues


def check_bracket_balance(code: str) -> list:
    """检查括号平衡（去除字符串和注释后）"""
    issues = []
    # 去除注释和字符串
    clean = re.sub(r'//[^\n]*', '', code)
    clean = re.sub(r'/\*.*?\*/', '', clean, flags=re.DOTALL)
    clean = re.sub(r"'[^']*'|\"[^\"]*\"|`[^`]*`", '', clean, flags=re.DOTALL)

    o = clean.count('{') - clean.count('}')
    p = clean.count('(') - clean.count(')')
    b = clean.count('[') - clean.count(']')
    if o != 0:
        issues.append(f"FATAL: 大括号不平衡: {'+' if o > 0 else ''}{o}")
    if p != 0:
        issues.append(f"FATAL: 小括号不平衡: {'+' if p > 0 else ''}{p}")
    if b != 0:
        issues.append(f"WARN: 方括号不平衡: {'+' if b > 0 else ''}{b}")
    return issues


def check_unguarded_create_in_update(code: str) -> list:
    """检查 update 中无 if 保护的 ctx.create 调用"""
    issues = []
    if 'function update' not in code:
        return issues

    update_section = code.split('function update')[1] if 'function update' in code else ''
    update_lines = update_section.split('\n')
    in_if_block = False
    if_depth = 0

    for uline in update_lines:
        ustripped = uline.strip()
        if ustripped.startswith('if') or ustripped.startswith('} else'):
            in_if_block = True
            if_depth = 0
        if in_if_block:
            if_depth += ustripped.count('{') - ustripped.count('}')
            if if_depth <= 0:
                in_if_block = False
        if not in_if_block and 'ctx.create' in ustripped and not ustripped.startswith('//'):
            issues.append(f"WARN: update中无条件创建元素(每帧执行会内存泄漏): {ustripped[:80]}")

    return issues


def check_variable_consistency(code: str, variables: list) -> list:
    """检查代码中 getVar 引用的变量名是否与 variables 配置一致"""
    issues = []
    var_names = set()
    for v in variables:
        name = v.get('name') or v.get('id') or ''
        if name:
            var_names.add(name)

    # 代码中引用的变量
    code_vars = set(re.findall(r"ctx\.getVar\(['\"](\w+)['\"]\)", code))

    # 配置中有但代码没读取的
    missing = var_names - code_vars
    if missing:
        issues.append(f"WARN: 滑块变量未被代码读取: {', '.join(missing)}")

    # 代码读取了但配置中没有的
    phantom = code_vars - var_names
    if phantom:
        issues.append(f"WARN: 代码引用了不存在的变量: {', '.join(phantom)}")

    return issues


def check_invalid_apis(code: str) -> list:
    """检查是否使用了无效的 API"""
    issues = []
    valid_apis = {
        'createCircle', 'createRect', 'createText', 'createLine',
        'createCurve', 'createPolygon',
        'setPosition', 'setScale', 'setRotation', 'setAlpha',
        'setColor', 'setText', 'setVisible', 'remove', 'clear',
        'setGlow', 'setCurvePoints', 'setRadius', 'setSize',
        'getVar', 'setVar',
        'width', 'height', 'time', 'deltaTime', 'math',
    }
    api_calls = re.findall(r'ctx\.(\w+)', code)
    invalid = set()
    for api in api_calls:
        if api not in valid_apis and api != 'math':
            invalid.add(api)
    if invalid:
        issues.append(f"WARN: 无效API调用: {', '.join(list(invalid)[:5])}")
    return issues


# ==================== 主逻辑 ====================

async def main():
    parser = argparse.ArgumentParser(description='模拟器预发布检查')
    parser.add_argument('--course-id', type=int, help='指定课程ID，不指定则检查所有')
    parser.add_argument('--db-url', default='postgresql://hercu:Hercu2026Secure@localhost/hercu_db',
                        help='数据库连接URL')
    args = parser.parse_args()

    try:
        import asyncpg
    except ImportError:
        print("需要 asyncpg 库，请运行: pip install asyncpg")
        sys.exit(1)

    conn = await asyncpg.connect(args.db_url)

    query = "SELECT id, title, content FROM course_nodes WHERE content LIKE '%custom_code%'"
    params = []
    if args.course_id:
        query += " AND course_id = $1"
        params.append(args.course_id)
    query += " ORDER BY course_id, sequence"

    rows = await conn.fetch(query, *params)

    total = 0
    fatal_count = 0
    warn_count = 0
    problems = []

    for row in rows:
        node_id = row['id']
        title = row['title']
        content_str = row['content']
        try:
            content = json.loads(content_str) if isinstance(content_str, str) else content_str
            steps = content.get('steps', [])
            for i, step in enumerate(steps):
                spec = step.get('simulator_spec', {})
                if spec and spec.get('custom_code'):
                    code = spec['custom_code']
                    sim_name = spec.get('name', 'unknown')
                    variables = spec.get('variables', [])
                    total += 1
                    all_issues = []

                    all_issues.extend(check_duplicate_declarations(code))
                    all_issues.extend(check_chinese_punctuation(code))
                    all_issues.extend(check_missing_functions(code))
                    all_issues.extend(check_bracket_balance(code))
                    all_issues.extend(check_unguarded_create_in_update(code))
                    all_issues.extend(check_variable_consistency(code, variables))
                    all_issues.extend(check_invalid_apis(code))

                    has_fatal = any('FATAL' in x for x in all_issues)
                    has_warn = any('WARN' in x for x in all_issues)
                    status = 'FAIL' if has_fatal else ('WARN' if has_warn else 'OK')

                    if has_fatal:
                        fatal_count += 1
                    if has_warn and not has_fatal:
                        warn_count += 1

                    print(f"[{status}] NODE {node_id} | {title} | step {i} | {sim_name}")
                    if all_issues:
                        for issue in all_issues:
                            print(f"  {issue}")
                        if has_fatal:
                            problems.append((node_id, title, sim_name, [x for x in all_issues if 'FATAL' in x]))
                    print()

        except Exception as e:
            print(f"ERROR parsing node {node_id}: {e}")

    print(f"{'='*60}")
    print(f"总模拟器数: {total}")
    print(f"FATAL (运行崩溃): {fatal_count}")
    print(f"WARN (潜在问题): {warn_count}")
    print(f"OK: {total - fatal_count - warn_count}")

    if problems:
        print(f"\n致命问题列表:")
        for p in problems:
            print(f"  NODE {p[0]} | {p[1]} | {p[2]}")
            for issue in p[3]:
                print(f"    {issue}")

    await conn.close()

    # 返回退出码：有 FATAL 则返回 1
    sys.exit(1 if fatal_count > 0 else 0)


if __name__ == '__main__':
    asyncio.run(main())
