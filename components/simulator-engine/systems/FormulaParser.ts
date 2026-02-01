/**
 * 公式解析器 - 解析并执行数学公式字符串
 * 支持变量、内置函数和基本运算
 */

// 内置数学函数
const BUILT_IN_FUNCTIONS: Record<string, (...args: number[]) => number> = {
  sin: Math.sin,
  cos: Math.cos,
  tan: Math.tan,
  abs: Math.abs,
  floor: Math.floor,
  ceil: Math.ceil,
  round: Math.round,
  sqrt: Math.sqrt,
  pow: Math.pow,
  min: Math.min,
  max: Math.max,
  random: Math.random,
  // 自定义函数
  clamp: (value: number, min: number, max: number) => Math.max(min, Math.min(max, value)),
  lerp: (a: number, b: number, t: number) => a + (b - a) * t,
  smoothstep: (edge0: number, edge1: number, x: number) => {
    const t = Math.max(0, Math.min(1, (x - edge0) / (edge1 - edge0)));
    return t * t * (3 - 2 * t);
  },
  // 波形函数
  wave: (t: number, frequency: number = 1, amplitude: number = 1) =>
    Math.sin(t * frequency * Math.PI * 2) * amplitude,
  sawtooth: (t: number, period: number = 1) =>
    2 * ((t / period) - Math.floor(0.5 + t / period)),
  triangle: (t: number, period: number = 1) =>
    2 * Math.abs(2 * ((t / period) - Math.floor(t / period + 0.5))) - 1,
  pulse: (t: number, period: number = 1, duty: number = 0.5) =>
    ((t % period) / period) < duty ? 1 : 0,
};

// 内置常量
const BUILT_IN_CONSTANTS: Record<string, number> = {
  PI: Math.PI,
  E: Math.E,
  TAU: Math.PI * 2,
};

// Token 类型
type TokenType =
  | 'NUMBER'
  | 'IDENTIFIER'
  | 'OPERATOR'
  | 'LPAREN'
  | 'RPAREN'
  | 'COMMA'
  | 'QUESTION'
  | 'COLON';

interface Token {
  type: TokenType;
  value: string | number;
}

/**
 * 词法分析器 - 将公式字符串转换为 Token 数组
 */
function tokenize(formula: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;

  while (i < formula.length) {
    const char = formula[i];

    // 跳过空白
    if (/\s/.test(char)) {
      i++;
      continue;
    }

    // 数字（包括小数）
    if (/\d/.test(char) || (char === '.' && /\d/.test(formula[i + 1]))) {
      let num = '';
      while (i < formula.length && (/\d/.test(formula[i]) || formula[i] === '.')) {
        num += formula[i];
        i++;
      }
      tokens.push({ type: 'NUMBER', value: parseFloat(num) });
      continue;
    }

    // 标识符（变量名或函数名）
    if (/[a-zA-Z_]/.test(char)) {
      let id = '';
      while (i < formula.length && /[a-zA-Z0-9_]/.test(formula[i])) {
        id += formula[i];
        i++;
      }
      tokens.push({ type: 'IDENTIFIER', value: id });
      continue;
    }

    // 运算符
    if ('+-*/%^'.includes(char)) {
      tokens.push({ type: 'OPERATOR', value: char });
      i++;
      continue;
    }

    // 比较运算符
    if (char === '>' || char === '<' || char === '=' || char === '!') {
      let op = char;
      if (formula[i + 1] === '=') {
        op += '=';
        i++;
      }
      tokens.push({ type: 'OPERATOR', value: op });
      i++;
      continue;
    }

    // 逻辑运算符
    if (char === '&' && formula[i + 1] === '&') {
      tokens.push({ type: 'OPERATOR', value: '&&' });
      i += 2;
      continue;
    }
    if (char === '|' && formula[i + 1] === '|') {
      tokens.push({ type: 'OPERATOR', value: '||' });
      i += 2;
      continue;
    }

    // 括号
    if (char === '(') {
      tokens.push({ type: 'LPAREN', value: '(' });
      i++;
      continue;
    }
    if (char === ')') {
      tokens.push({ type: 'RPAREN', value: ')' });
      i++;
      continue;
    }

    // 逗号
    if (char === ',') {
      tokens.push({ type: 'COMMA', value: ',' });
      i++;
      continue;
    }

    // 三元运算符
    if (char === '?') {
      tokens.push({ type: 'QUESTION', value: '?' });
      i++;
      continue;
    }
    if (char === ':') {
      tokens.push({ type: 'COLON', value: ':' });
      i++;
      continue;
    }

    // 未知字符，跳过
    console.warn(`FormulaParser: Unknown character '${char}' at position ${i}`);
    i++;
  }

  return tokens;
}

/**
 * 运算符优先级
 */
const PRECEDENCE: Record<string, number> = {
  '||': 1,
  '&&': 2,
  '==': 3, '!=': 3, '<': 3, '>': 3, '<=': 3, '>=': 3,
  '+': 4, '-': 4,
  '*': 5, '/': 5, '%': 5,
  '^': 6,
};

/**
 * 解析器类 - 将 Token 数组解析为 AST 并求值
 */
class Parser {
  private tokens: Token[];
  private pos: number = 0;
  private variables: Record<string, number>;

  constructor(tokens: Token[], variables: Record<string, number>) {
    this.tokens = tokens;
    this.variables = variables;
  }

  private current(): Token | null {
    return this.pos < this.tokens.length ? this.tokens[this.pos] : null;
  }

  private consume(): Token | null {
    return this.tokens[this.pos++] || null;
  }

  private peek(offset: number = 0): Token | null {
    return this.tokens[this.pos + offset] || null;
  }

  /**
   * 解析表达式（入口）
   */
  parse(): number {
    return this.parseTernary();
  }

  /**
   * 解析三元运算符
   */
  private parseTernary(): number {
    const condition = this.parseBinaryOp(1);

    if (this.current()?.type === 'QUESTION') {
      this.consume(); // consume '?'
      const trueValue = this.parseTernary();

      if (this.current()?.type !== 'COLON') {
        throw new Error('Expected ":" in ternary expression');
      }
      this.consume(); // consume ':'
      const falseValue = this.parseTernary();

      return condition ? trueValue : falseValue;
    }

    return condition;
  }

  /**
   * 解析二元运算符（按优先级）
   */
  private parseBinaryOp(minPrecedence: number): number {
    let left = this.parseUnary();

    while (true) {
      const token = this.current();
      if (!token || token.type !== 'OPERATOR') break;

      const precedence = PRECEDENCE[token.value as string];
      if (precedence === undefined || precedence < minPrecedence) break;

      this.consume();
      const right = this.parseBinaryOp(precedence + 1);

      switch (token.value) {
        case '+': left = left + right; break;
        case '-': left = left - right; break;
        case '*': left = left * right; break;
        case '/': left = right !== 0 ? left / right : 0; break;
        case '%': left = left % right; break;
        case '^': left = Math.pow(left, right); break;
        case '==': left = left === right ? 1 : 0; break;
        case '!=': left = left !== right ? 1 : 0; break;
        case '<': left = left < right ? 1 : 0; break;
        case '>': left = left > right ? 1 : 0; break;
        case '<=': left = left <= right ? 1 : 0; break;
        case '>=': left = left >= right ? 1 : 0; break;
        case '&&': left = (left && right) ? 1 : 0; break;
        case '||': left = (left || right) ? 1 : 0; break;
      }
    }

    return left;
  }

  /**
   * 解析一元运算符
   */
  private parseUnary(): number {
    const token = this.current();

    if (token?.type === 'OPERATOR' && (token.value === '-' || token.value === '+')) {
      this.consume();
      const value = this.parseUnary();
      return token.value === '-' ? -value : value;
    }

    return this.parsePrimary();
  }

  /**
   * 解析基本表达式（数字、变量、函数调用、括号）
   */
  private parsePrimary(): number {
    const token = this.current();

    if (!token) {
      return 0;
    }

    // 数字
    if (token.type === 'NUMBER') {
      this.consume();
      return token.value as number;
    }

    // 标识符（变量或函数）
    if (token.type === 'IDENTIFIER') {
      const name = token.value as string;
      this.consume();

      // 检查是否是函数调用
      if (this.current()?.type === 'LPAREN') {
        return this.parseFunctionCall(name);
      }

      // 内置常量
      if (name in BUILT_IN_CONSTANTS) {
        return BUILT_IN_CONSTANTS[name];
      }

      // 变量
      if (name in this.variables) {
        return this.variables[name];
      }

      console.warn(`FormulaParser: Unknown variable '${name}'`);
      return 0;
    }

    // 括号表达式
    if (token.type === 'LPAREN') {
      this.consume();
      const value = this.parseTernary();
      if (this.current()?.type === 'RPAREN') {
        this.consume();
      }
      return value;
    }

    return 0;
  }

  /**
   * 解析函数调用
   */
  private parseFunctionCall(name: string): number {
    this.consume(); // consume '('

    const args: number[] = [];

    while (this.current() && this.current()?.type !== 'RPAREN') {
      args.push(this.parseTernary());

      if (this.current()?.type === 'COMMA') {
        this.consume();
      }
    }

    if (this.current()?.type === 'RPAREN') {
      this.consume();
    }

    // 查找内置函数
    if (name in BUILT_IN_FUNCTIONS) {
      return BUILT_IN_FUNCTIONS[name](...args);
    }

    console.warn(`FormulaParser: Unknown function '${name}'`);
    return 0;
  }
}

/**
 * 编译公式为可执行函数（缓存优化）
 */
const formulaCache = new Map<string, (vars: Record<string, number>) => number>();

/**
 * 解析并执行公式
 * @param formula 公式字符串
 * @param variables 变量映射
 * @returns 计算结果
 */
export function evaluateFormula(formula: string, variables: Record<string, number> = {}): number {
  try {
    const tokens = tokenize(formula);
    const parser = new Parser(tokens, variables);
    return parser.parse();
  } catch (error) {
    console.error(`FormulaParser: Error evaluating formula "${formula}":`, error);
    return 0;
  }
}

/**
 * 编译公式为可重复执行的函数
 * @param formula 公式字符串
 * @returns 执行函数
 */
export function compileFormula(formula: string): (variables: Record<string, number>) => number {
  // 检查缓存
  if (formulaCache.has(formula)) {
    return formulaCache.get(formula)!;
  }

  // 预先词法分析
  const tokens = tokenize(formula);

  // 创建执行函数
  const fn = (variables: Record<string, number>): number => {
    try {
      const parser = new Parser(tokens, variables);
      return parser.parse();
    } catch (error) {
      console.error(`FormulaParser: Error executing formula "${formula}":`, error);
      return 0;
    }
  };

  // 缓存
  formulaCache.set(formula, fn);
  return fn;
}

/**
 * 清除公式缓存
 */
export function clearFormulaCache(): void {
  formulaCache.clear();
}

/**
 * 获取公式中使用的变量名
 */
export function getFormulaVariables(formula: string): string[] {
  const tokens = tokenize(formula);
  const variables: string[] = [];

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    if (token.type === 'IDENTIFIER') {
      const name = token.value as string;
      // 排除内置函数和常量
      if (!(name in BUILT_IN_FUNCTIONS) && !(name in BUILT_IN_CONSTANTS)) {
        // 检查下一个 token 是否是左括号（函数调用）
        if (tokens[i + 1]?.type !== 'LPAREN') {
          if (!variables.includes(name)) {
            variables.push(name);
          }
        }
      }
    }
  }

  return variables;
}

export { BUILT_IN_FUNCTIONS, BUILT_IN_CONSTANTS };
