/**
 * 缓动函数库 - 提供各种动画缓动效果
 */

import type { EasingType, PresetEasing, BezierEasing, SpringEasing } from '@/types/simulator-engine';

// ==================== 基础缓动函数 ====================

/** 线性 */
export const linear = (t: number): number => t;

/** 二次方缓入 */
export const easeInQuad = (t: number): number => t * t;

/** 二次方缓出 */
export const easeOutQuad = (t: number): number => t * (2 - t);

/** 二次方缓入缓出 */
export const easeInOutQuad = (t: number): number =>
  t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;

/** 三次方缓入 */
export const easeInCubic = (t: number): number => t * t * t;

/** 三次方缓出 */
export const easeOutCubic = (t: number): number => {
  const t1 = t - 1;
  return t1 * t1 * t1 + 1;
};

/** 三次方缓入缓出 */
export const easeInOutCubic = (t: number): number =>
  t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;

/** 四次方缓入 */
export const easeInQuart = (t: number): number => t * t * t * t;

/** 四次方缓出 */
export const easeOutQuart = (t: number): number => {
  const t1 = t - 1;
  return 1 - t1 * t1 * t1 * t1;
};

/** 四次方缓入缓出 */
export const easeInOutQuart = (t: number): number => {
  const t1 = t - 1;
  return t < 0.5 ? 8 * t * t * t * t : 1 - 8 * t1 * t1 * t1 * t1;
};

/** 五次方缓入 */
export const easeInQuint = (t: number): number => t * t * t * t * t;

/** 五次方缓出 */
export const easeOutQuint = (t: number): number => {
  const t1 = t - 1;
  return 1 + t1 * t1 * t1 * t1 * t1;
};

/** 五次方缓入缓出 */
export const easeInOutQuint = (t: number): number => {
  const t1 = t - 1;
  return t < 0.5 ? 16 * t * t * t * t * t : 1 + 16 * t1 * t1 * t1 * t1 * t1;
};

// ==================== 正弦缓动 ====================

/** 正弦缓入 */
export const easeInSine = (t: number): number =>
  1 - Math.cos((t * Math.PI) / 2);

/** 正弦缓出 */
export const easeOutSine = (t: number): number =>
  Math.sin((t * Math.PI) / 2);

/** 正弦缓入缓出 */
export const easeInOutSine = (t: number): number =>
  -(Math.cos(Math.PI * t) - 1) / 2;

// ==================== 指数缓动 ====================

/** 指数缓入 */
export const easeInExpo = (t: number): number =>
  t === 0 ? 0 : Math.pow(2, 10 * t - 10);

/** 指数缓出 */
export const easeOutExpo = (t: number): number =>
  t === 1 ? 1 : 1 - Math.pow(2, -10 * t);

/** 指数缓入缓出 */
export const easeInOutExpo = (t: number): number => {
  if (t === 0) return 0;
  if (t === 1) return 1;
  return t < 0.5
    ? Math.pow(2, 20 * t - 10) / 2
    : (2 - Math.pow(2, -20 * t + 10)) / 2;
};

// ==================== 圆形缓动 ====================

/** 圆形缓入 */
export const easeInCirc = (t: number): number =>
  1 - Math.sqrt(1 - t * t);

/** 圆形缓出 */
export const easeOutCirc = (t: number): number => {
  const t1 = t - 1;
  return Math.sqrt(1 - t1 * t1);
};

/** 圆形缓入缓出 */
export const easeInOutCirc = (t: number): number =>
  t < 0.5
    ? (1 - Math.sqrt(1 - Math.pow(2 * t, 2))) / 2
    : (Math.sqrt(1 - Math.pow(-2 * t + 2, 2)) + 1) / 2;

// ==================== 弹性缓动 ====================

/** 弹性缓入 */
export const easeInElastic = (t: number): number => {
  if (t === 0) return 0;
  if (t === 1) return 1;
  const c4 = (2 * Math.PI) / 3;
  return -Math.pow(2, 10 * t - 10) * Math.sin((t * 10 - 10.75) * c4);
};

/** 弹性缓出 */
export const easeOutElastic = (t: number): number => {
  if (t === 0) return 0;
  if (t === 1) return 1;
  const c4 = (2 * Math.PI) / 3;
  return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
};

/** 弹性缓入缓出 */
export const easeInOutElastic = (t: number): number => {
  if (t === 0) return 0;
  if (t === 1) return 1;
  const c5 = (2 * Math.PI) / 4.5;
  return t < 0.5
    ? -(Math.pow(2, 20 * t - 10) * Math.sin((20 * t - 11.125) * c5)) / 2
    : (Math.pow(2, -20 * t + 10) * Math.sin((20 * t - 11.125) * c5)) / 2 + 1;
};

// ==================== 回弹缓动 ====================

/** 回弹缓入 */
export const easeInBack = (t: number): number => {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return c3 * t * t * t - c1 * t * t;
};

/** 回弹缓出 */
export const easeOutBack = (t: number): number => {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  const t1 = t - 1;
  return 1 + c3 * t1 * t1 * t1 + c1 * t1 * t1;
};

/** 回弹缓入缓出 */
export const easeInOutBack = (t: number): number => {
  const c1 = 1.70158;
  const c2 = c1 * 1.525;
  return t < 0.5
    ? (Math.pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
    : (Math.pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2;
};

// ==================== 弹跳缓动 ====================

/** 弹跳缓出 */
export const easeOutBounce = (t: number): number => {
  const n1 = 7.5625;
  const d1 = 2.75;

  if (t < 1 / d1) {
    return n1 * t * t;
  } else if (t < 2 / d1) {
    const t1 = t - 1.5 / d1;
    return n1 * t1 * t1 + 0.75;
  } else if (t < 2.5 / d1) {
    const t1 = t - 2.25 / d1;
    return n1 * t1 * t1 + 0.9375;
  } else {
    const t1 = t - 2.625 / d1;
    return n1 * t1 * t1 + 0.984375;
  }
};

/** 弹跳缓入 */
export const easeInBounce = (t: number): number =>
  1 - easeOutBounce(1 - t);

/** 弹跳缓入缓出 */
export const easeInOutBounce = (t: number): number =>
  t < 0.5
    ? (1 - easeOutBounce(1 - 2 * t)) / 2
    : (1 + easeOutBounce(2 * t - 1)) / 2;

// ==================== 弹簧缓动 ====================

/**
 * 弹簧缓动 - 模拟弹簧物理效果
 * @param tension 张力 (默认 300)
 * @param friction 摩擦力 (默认 20)
 */
export const createSpringEasing = (tension = 300, friction = 20) => {
  return (t: number): number => {
    const omega = Math.sqrt(tension);
    const zeta = friction / (2 * Math.sqrt(tension));

    if (zeta < 1) {
      // 欠阻尼
      const omegaD = omega * Math.sqrt(1 - zeta * zeta);
      return 1 - Math.exp(-zeta * omega * t) * (
        Math.cos(omegaD * t) + (zeta * omega / omegaD) * Math.sin(omegaD * t)
      );
    } else if (zeta === 1) {
      // 临界阻尼
      return 1 - (1 + omega * t) * Math.exp(-omega * t);
    } else {
      // 过阻尼
      const s1 = -omega * (zeta + Math.sqrt(zeta * zeta - 1));
      const s2 = -omega * (zeta - Math.sqrt(zeta * zeta - 1));
      return 1 - (s2 * Math.exp(s1 * t) - s1 * Math.exp(s2 * t)) / (s2 - s1);
    }
  };
};

/** 默认弹簧缓动 */
export const spring = createSpringEasing();

// ==================== 贝塞尔曲线 ====================

/**
 * 创建三次贝塞尔缓动函数
 * @param x1 控制点1 x
 * @param y1 控制点1 y
 * @param x2 控制点2 x
 * @param y2 控制点2 y
 */
export const createBezierEasing = (x1: number, y1: number, x2: number, y2: number) => {
  // 牛顿迭代法求解贝塞尔曲线
  const NEWTON_ITERATIONS = 4;
  const NEWTON_MIN_SLOPE = 0.001;
  const SUBDIVISION_PRECISION = 0.0000001;
  const SUBDIVISION_MAX_ITERATIONS = 10;

  const kSplineTableSize = 11;
  const kSampleStepSize = 1.0 / (kSplineTableSize - 1.0);

  const sampleValues = new Float32Array(kSplineTableSize);

  const A = (a1: number, a2: number) => 1.0 - 3.0 * a2 + 3.0 * a1;
  const B = (a1: number, a2: number) => 3.0 * a2 - 6.0 * a1;
  const C = (a1: number) => 3.0 * a1;

  const calcBezier = (t: number, a1: number, a2: number) =>
    ((A(a1, a2) * t + B(a1, a2)) * t + C(a1)) * t;

  const getSlope = (t: number, a1: number, a2: number) =>
    3.0 * A(a1, a2) * t * t + 2.0 * B(a1, a2) * t + C(a1);

  const binarySubdivide = (x: number, a: number, b: number, mX1: number, mX2: number) => {
    let currentX: number;
    let currentT: number;
    let i = 0;
    do {
      currentT = a + (b - a) / 2.0;
      currentX = calcBezier(currentT, mX1, mX2) - x;
      if (currentX > 0.0) {
        b = currentT;
      } else {
        a = currentT;
      }
    } while (Math.abs(currentX) > SUBDIVISION_PRECISION && ++i < SUBDIVISION_MAX_ITERATIONS);
    return currentT;
  };

  const newtonRaphsonIterate = (x: number, guessT: number, mX1: number, mX2: number) => {
    for (let i = 0; i < NEWTON_ITERATIONS; ++i) {
      const currentSlope = getSlope(guessT, mX1, mX2);
      if (currentSlope === 0.0) {
        return guessT;
      }
      const currentX = calcBezier(guessT, mX1, mX2) - x;
      guessT -= currentX / currentSlope;
    }
    return guessT;
  };

  // 预计算样本值
  for (let i = 0; i < kSplineTableSize; ++i) {
    sampleValues[i] = calcBezier(i * kSampleStepSize, x1, x2);
  }

  const getTForX = (x: number) => {
    let intervalStart = 0.0;
    let currentSample = 1;
    const lastSample = kSplineTableSize - 1;

    for (; currentSample !== lastSample && sampleValues[currentSample] <= x; ++currentSample) {
      intervalStart += kSampleStepSize;
    }
    --currentSample;

    const dist = (x - sampleValues[currentSample]) / (sampleValues[currentSample + 1] - sampleValues[currentSample]);
    const guessForT = intervalStart + dist * kSampleStepSize;

    const initialSlope = getSlope(guessForT, x1, x2);
    if (initialSlope >= NEWTON_MIN_SLOPE) {
      return newtonRaphsonIterate(x, guessForT, x1, x2);
    } else if (initialSlope === 0.0) {
      return guessForT;
    } else {
      return binarySubdivide(x, intervalStart, intervalStart + kSampleStepSize, x1, x2);
    }
  };

  return (t: number): number => {
    if (t === 0 || t === 1) return t;
    return calcBezier(getTForX(t), y1, y2);
  };
};

// ==================== 预设贝塞尔曲线 ====================

/** CSS ease */
export const ease = createBezierEasing(0.25, 0.1, 0.25, 1);

/** CSS ease-in */
export const easeIn = createBezierEasing(0.42, 0, 1, 1);

/** CSS ease-out */
export const easeOut = createBezierEasing(0, 0, 0.58, 1);

/** CSS ease-in-out */
export const easeInOut = createBezierEasing(0.42, 0, 0.58, 1);

// ==================== 缓动函数映射 ====================

/** 缓动函数类型 */
export type EasingFunction = (t: number) => number;

/** 预设缓动函数映射表 */
export const easingFunctions: Record<PresetEasing, EasingFunction> = {
  linear,
  easeIn,
  easeOut,
  easeInOut,
  easeInQuad,
  easeOutQuad,
  easeInOutQuad,
  easeInCubic,
  easeOutCubic,
  easeInOutCubic,
  easeInQuart,
  easeOutQuart,
  easeInOutQuart,
  easeInQuint,
  easeOutQuint,
  easeInOutQuint,
  easeInSine,
  easeOutSine,
  easeInOutSine,
  easeInExpo,
  easeOutExpo,
  easeInOutExpo,
  easeInCirc,
  easeOutCirc,
  easeInOutCirc,
  easeInElastic,
  easeOutElastic,
  easeInOutElastic,
  easeInBack,
  easeOutBack,
  easeInOutBack,
  easeInBounce,
  easeOutBounce,
  easeInOutBounce,
};

/**
 * 检查是否为贝塞尔缓动
 */
function isBezierEasing(easing: EasingType): easing is BezierEasing {
  return typeof easing === 'object' && easing !== null && easing.type === 'bezier';
}

/**
 * 检查是否为弹簧缓动
 */
function isSpringEasing(easing: EasingType): easing is SpringEasing {
  return typeof easing === 'object' && easing !== null && easing.type === 'spring';
}

/**
 * 获取缓动函数
 * @param easing 缓动类型
 */
export function getEasingFunction(easing: EasingType): EasingFunction {
  // 处理贝塞尔缓动
  if (isBezierEasing(easing)) {
    return createBezierEasing(...easing.controlPoints);
  }

  // 处理弹簧缓动
  if (isSpringEasing(easing)) {
    return createSpringEasing(easing.stiffness, easing.damping);
  }

  // 预设缓动
  return easingFunctions[easing] || linear;
}

/**
 * 应用缓动函数进行插值
 * @param start 起始值
 * @param end 结束值
 * @param progress 进度 (0-1)
 * @param easing 缓动类型
 */
export function interpolate(
  start: number,
  end: number,
  progress: number,
  easing: EasingType = 'linear'
): number {
  const easingFn = getEasingFunction(easing);
  const easedProgress = easingFn(Math.max(0, Math.min(1, progress)));
  return start + (end - start) * easedProgress;
}
