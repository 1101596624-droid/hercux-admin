/**
 * GeneratingView - 生成中视图组件 (三栏布局)
 * 支持实时预览已生成的课时内容
 */

'use client';

import { useState, useEffect, useMemo, useRef } from 'react';
import { Loader2, CheckCircle2, XCircle, RefreshCw, AlertTriangle, Pause, Play, ChevronRight, FileText, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { getTotalCharCount, useStudioStore } from '@/stores/studio/useStudioStore';
import { StepRenderer } from '@/components/studio/steps/StepRenderer';
import type { ProcessorWithConfig, UploadedSource, LessonOutline, Lesson } from '@/types/studio';
import { RefObject } from 'react';

interface GeneratingViewProps {
  // Generation state
  generationPhase: number;
  currentLessonIndex: number;
  totalLessons: number;
  lessonsOutline: LessonOutline[];
  completedLessons: number[];
  currentProcessor: ProcessorWithConfig | null;

  // Streaming
  streamStatus: string;
  streamedContent: string;
  streamContainerRef: RefObject<HTMLDivElement>;

  // Course info
  courseTitle: string;
  sources: UploadedSource[];

  // Error state
  generationError: string | null;

  // Actions
  handleCancelGenerate: () => void;
  handleRetry: () => void;

  // 新增：已完成的课时数据
  completedLessonsData?: Lesson[];
  // 新增：暂停/继续
  isPaused?: boolean;
  handlePause?: () => void;
  handleResume?: () => void;
  // 新增：重新生成步骤
  onRegenerateStep?: (lessonIndex: number, stepIndex: number, additionalPrompt?: string) => void;
}

// 打字机效果配置
const TYPEWRITER_DELAY_MS = 5000; // 显示比生成晚5秒
const TYPEWRITER_CHARS_PER_TICK = 3; // 每次显示字符数
const TYPEWRITER_INTERVAL = 20; // 更新间隔(ms)

/**
 * 打字机内容组件 - 实时逐字显示生成内容
 */
function TypewriterContent({
  streamedContent,
  currentLessonIndex,
  totalLessons,
  lessonsOutline,
  streamingLessonInfo,
  isPaused,
}: {
  streamedContent: string;
  currentLessonIndex: number;
  totalLessons: number;
  lessonsOutline: LessonOutline[];
  streamingLessonInfo: { title: string; rationale?: string; learning_objectives?: string[] } | null;
  isPaused?: boolean;
}) {
  // 显示的字符数
  const [displayedLength, setDisplayedLength] = useState(0);
  // 用 ref 存储 streamedContent 以避免 useEffect 依赖问题
  const streamedContentRef = useRef(streamedContent);
  streamedContentRef.current = streamedContent;

  // 打字机效果：逐字显示
  useEffect(() => {
    if (isPaused) return;

    const timer = setInterval(() => {
      setDisplayedLength(prev => {
        const target = streamedContentRef.current.length;
        if (prev >= target) {
          return prev; // 已经显示完了
        }
        // 每次增加几个字符
        return Math.min(target, prev + TYPEWRITER_CHARS_PER_TICK);
      });
    }, TYPEWRITER_INTERVAL);

    return () => clearInterval(timer);
  }, [isPaused]);

  // 当课时切换时重置
  useEffect(() => {
    setDisplayedLength(0);
  }, [currentLessonIndex]);

  // 尝试从流式JSON中提取已完成的步骤
  const extractCompletedSteps = (content: string): any[] => {
    const steps: any[] = [];

    // 查找 script 数组
    const scriptMatch = content.match(/"script"\s*:\s*\[/);
    if (!scriptMatch) return steps;

    const scriptStart = scriptMatch.index! + scriptMatch[0].length;
    let depth = 1;
    let stepStart = scriptStart;
    let inString = false;
    let escape = false;

    for (let i = scriptStart; i < content.length && depth > 0; i++) {
      const char = content[i];

      if (escape) {
        escape = false;
        continue;
      }

      if (char === '\\') {
        escape = true;
        continue;
      }

      if (char === '"') {
        inString = !inString;
        continue;
      }

      if (inString) continue;

      if (char === '{') {
        if (depth === 1) stepStart = i;
        depth++;
      } else if (char === '}') {
        depth--;
        if (depth === 1) {
          // 找到一个完整的步骤对象
          const stepStr = content.slice(stepStart, i + 1);
          try {
            const step = JSON.parse(stepStr);
            if (step.step_id && step.type) {
              steps.push(step);
            }
          } catch (e) {
            // 解析失败，跳过
          }
        }
      } else if (char === '[') {
        depth++;
      } else if (char === ']') {
        depth--;
      }
    }

    return steps;
  };

  // 提取课时基本信息
  const extractLessonInfo = (content: string) => {
    const titleMatch = content.match(/"title"\s*:\s*"([^"]+)"/);
    const rationaleMatch = content.match(/"rationale"\s*:\s*"([^"]+)"/);
    return {
      title: titleMatch ? titleMatch[1] : null,
      rationale: rationaleMatch ? rationaleMatch[1].replace(/\\n/g, '\n') : null
    };
  };

  const completedSteps = extractCompletedSteps(streamedContent);
  const lessonInfo = extractLessonInfo(streamedContent);
  const isTyping = displayedLength < streamedContent.length;

  // 控制显示的步骤数量（带5秒延迟效果）
  const [visibleStepCount, setVisibleStepCount] = useState(0);
  const stepTimestampsRef = useRef<number[]>([]);

  useEffect(() => {
    // 记录每个新步骤的到达时间
    if (completedSteps.length > stepTimestampsRef.current.length) {
      for (let i = stepTimestampsRef.current.length; i < completedSteps.length; i++) {
        stepTimestampsRef.current.push(Date.now());
      }
    }

    // 检查是否有步骤可以显示（延迟5秒）
    const checkAndShowSteps = () => {
      const now = Date.now();
      let newVisibleCount = 0;
      for (let i = 0; i < stepTimestampsRef.current.length; i++) {
        if (now - stepTimestampsRef.current[i] >= TYPEWRITER_DELAY_MS) {
          newVisibleCount = i + 1;
        }
      }
      if (newVisibleCount > visibleStepCount) {
        setVisibleStepCount(newVisibleCount);
      }
    };

    const timer = setInterval(checkAndShowSteps, 200);
    return () => clearInterval(timer);
  }, [completedSteps.length, visibleStepCount]);

  useEffect(() => {
    setVisibleStepCount(0);
    stepTimestampsRef.current = [];
  }, [currentLessonIndex]);

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      {/* 课时头部 */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
        {/* 三个呼吸闪烁的圆点 */}
        <div className="flex items-center gap-3 mb-4">
          <div className="flex gap-1.5">
            <motion.div
              animate={{ opacity: [1, 0.4, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0 }}
              className="w-3 h-3 rounded-full bg-red-500"
            />
            <motion.div
              animate={{ opacity: [1, 0.4, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
              className="w-3 h-3 rounded-full bg-yellow-500"
            />
            <motion.div
              animate={{ opacity: [1, 0.4, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.6 }}
              className="w-3 h-3 rounded-full bg-green-500"
            />
          </div>
        </div>

        {currentLessonIndex >= 0 && (
          <>
            <p className="text-xs text-red-600 uppercase tracking-wider mb-2">
              正在生成课时 {currentLessonIndex + 1}/{totalLessons}
            </p>
            <h3 className="text-xl font-bold text-slate-900">
              {lessonInfo.title || streamingLessonInfo?.title || lessonsOutline[currentLessonIndex]?.title || '课时内容'}
            </h3>
            {lessonInfo.rationale && (
              <p className="mt-2 text-sm text-slate-600 italic">{lessonInfo.rationale}</p>
            )}
          </>
        )}

        {/* 进度指示 */}
        <div className="mt-4 pt-4 border-t border-slate-100">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>已生成 {completedSteps.length} 个步骤</span>
            <span>{streamedContent.length.toLocaleString()} 字符</span>
          </div>
          <div className="mt-2 h-1 bg-slate-100 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-purple-500 to-violet-500"
              animate={{ width: ['0%', '100%'] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
            />
          </div>
        </div>
      </div>

      {/* 实时渲染的步骤 */}
      <AnimatePresence mode="popLayout">
        {completedSteps.slice(0, visibleStepCount).map((step, index) => (
          <motion.div
            key={step.step_id || index}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
          >
            <StepRenderer step={step} stepIndex={index} showRegenerate={true} />
          </motion.div>
        ))}
      </AnimatePresence>

      {/* 正在生成下一步的指示器 */}
      {isTyping && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 border-dashed"
        >
          <div className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
              className="w-6 h-6 border-2 border-slate-200 border-t-purple-500 rounded-full"
            />
            <span className="text-sm text-slate-500">正在生成下一个步骤...</span>
            {/* 闪烁光标 */}
            <motion.span
              animate={{
                opacity: [1, 0],
                boxShadow: [
                  '0 0 8px rgba(168, 85, 247, 0.8)',
                  '0 0 2px rgba(168, 85, 247, 0.3)'
                ]
              }}
              transition={{ duration: 0.5, repeat: Infinity }}
              className="inline-block w-0.5 h-5 bg-purple-500 rounded-sm"
            />
          </div>
        </motion.div>
      )}
    </div>
  );
}

export function GeneratingView({
  generationPhase,
  currentLessonIndex,
  totalLessons,
  lessonsOutline,
  completedLessons,
  currentProcessor,
  streamStatus,
  streamedContent,
  streamContainerRef,
  courseTitle,
  sources,
  generationError,
  handleCancelGenerate,
  handleRetry,
  completedLessonsData = [],
  isPaused = false,
  handlePause,
  handleResume,
  onRegenerateStep,
}: GeneratingViewProps) {
  const totalChars = getTotalCharCount(sources);
  const hasError = !!generationError;

  // 从 store 获取流式步骤
  const { streamingLessonInfo } = useStudioStore();

  // 当前选中查看的课时索引（-1 表示查看实时生成内容）
  const [selectedPreviewIndex, setSelectedPreviewIndex] = useState<number>(-1);

  // 获取当前选中预览的课时
  const previewLesson = useMemo(() => {
    if (selectedPreviewIndex >= 0 && completedLessonsData[selectedPreviewIndex]) {
      return completedLessonsData[selectedPreviewIndex];
    }
    return null;
  }, [selectedPreviewIndex, completedLessonsData]);

  return (
    <div className="flex-1 flex min-h-[150vh]">
      {/* Left Panel - Lessons List */}
      <div className="w-80 bg-slate-50 border-r border-slate-200 flex flex-col sticky top-0 h-screen">
        <div className="p-4 border-b border-slate-200">
          <h2 className="text-sm font-bold text-slate-700 uppercase tracking-wider">课时列表</h2>
          <p className="text-xs text-slate-500 mt-1">
            {generationPhase === 1 ? '正在分析课程结构...' :
             generationPhase === 2 ? `已完成 ${completedLessons.length}/${totalLessons} 个课时` :
             '准备中...'}
          </p>
          {currentProcessor && (
            <div className="flex items-center gap-2 mt-2 px-2 py-1 bg-white rounded-lg border border-slate-200">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: currentProcessor.color || '#ef4444' }}
              />
              <span className="text-xs text-slate-600">{currentProcessor.name}</span>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-auto p-3">
          {/* Phase 1 - Analyzing */}
          {generationPhase === 1 && lessonsOutline.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4"
              >
                <Sparkles size={24} className="text-red-600" />
              </motion.div>
              <p className="text-sm font-medium text-slate-700">正在分析课程结构</p>
              <p className="text-xs text-slate-500 mt-1">AI 正在规划课时大纲...</p>
            </div>
          )}

          {/* Lessons Outline */}
          {lessonsOutline.length > 0 && (
            <div className="space-y-2">
              {lessonsOutline.map((lesson, index) => {
                const isCompleted = completedLessons.includes(index);
                const isCurrent = currentLessonIndex === index;
                const isSelected = selectedPreviewIndex === index;
                const canPreview = isCompleted && completedLessonsData[index];

                return (
                  <button
                    key={index}
                    onClick={() => canPreview ? setSelectedPreviewIndex(index) : null}
                    disabled={!canPreview}
                    className={cn(
                      'w-full p-3 rounded-xl text-left transition-all',
                      isSelected ? 'bg-red-50 border-2 border-red-500' :
                      isCurrent ? 'bg-amber-50 border-2 border-amber-400' :
                      isCompleted ? 'bg-green-50 border-2 border-green-400 hover:bg-green-100 cursor-pointer' :
                      'bg-white border-2 border-slate-200'
                    )}
                  >
                    <div className="flex items-start gap-3">
                      {/* Status Icon */}
                      <div className={cn(
                        'w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0',
                        isCompleted ? 'bg-green-500' :
                        isCurrent ? 'bg-amber-400' :
                        'bg-slate-200'
                      )}>
                        {isCurrent ? (
                          <Loader2 size={14} className="text-white animate-spin" />
                        ) : isCompleted ? (
                          <CheckCircle2 size={14} className="text-white" />
                        ) : (
                          <span className="text-xs font-bold text-slate-500">{index + 1}</span>
                        )}
                      </div>

                      {/* Lesson Info */}
                      <div className="flex-1 min-w-0">
                        <p className={cn(
                          'text-sm font-medium truncate',
                          isSelected ? 'text-red-700' :
                          isCurrent ? 'text-amber-700' :
                          isCompleted ? 'text-green-700' :
                          'text-slate-600'
                        )}>
                          {lesson.title}
                        </p>
                        {isCompleted && canPreview && (
                          <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                            <FileText size={10} />
                            点击预览内容
                          </p>
                        )}
                      </div>

                      {/* Arrow for completed */}
                      {canPreview && (
                        <ChevronRight size={16} className={cn(
                          'flex-shrink-0',
                          isSelected ? 'text-red-500' : 'text-green-400'
                        )} />
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Control Buttons */}
        <div className="p-4 border-t border-slate-200 space-y-2">
          {/* Progress Bar */}
          {totalLessons > 0 && (
            <div className="mb-3">
              <div className="flex items-center justify-between text-xs text-slate-600 mb-1">
                <span>生成进度</span>
                <span>{completedLessons.length}/{totalLessons}</span>
              </div>
              <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-red-500 to-orange-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${(completedLessons.length / totalLessons) * 100}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </div>
          )}

          {hasError ? (
            <>
              <button
                onClick={handleRetry}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors font-medium"
              >
                <RefreshCw size={18} />
                重新生成
              </button>
              <button
                onClick={handleCancelGenerate}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm text-slate-600 hover:text-red-600 hover:bg-red-50 border border-slate-200 hover:border-red-200 rounded-lg transition-colors"
              >
                <XCircle size={18} />
                取消
              </button>
            </>
          ) : (
            <>
              {/* Pause/Resume Button */}
              {handlePause && handleResume && (
                <button
                  onClick={isPaused ? handleResume : handlePause}
                  className={cn(
                    'w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm rounded-lg transition-colors font-medium',
                    isPaused
                      ? 'bg-green-600 text-white hover:bg-green-700'
                      : 'bg-amber-500 text-white hover:bg-amber-600'
                  )}
                >
                  {isPaused ? (
                    <>
                      <Play size={18} />
                      继续生成
                    </>
                  ) : (
                    <>
                      <Pause size={18} />
                      暂停生成
                    </>
                  )}
                </button>
              )}

              {/* Cancel Button */}
              <button
                onClick={handleCancelGenerate}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm text-slate-600 hover:text-red-600 hover:bg-red-50 border border-slate-200 hover:border-red-200 rounded-lg transition-colors"
              >
                <XCircle size={18} />
                取消生成
              </button>
            </>
          )}

          {/* View Live Button */}
          {selectedPreviewIndex >= 0 && (
            <button
              onClick={() => setSelectedPreviewIndex(-1)}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <Sparkles size={16} />
              查看实时生成
            </button>
          )}
        </div>
      </div>

      {/* Center Panel - Content Preview */}
      <div className="flex-1 flex flex-col bg-white">
        {/* Header */}
        <div className="p-6 border-b border-slate-200 flex-shrink-0 sticky top-0 bg-white z-10">
          <div className="flex items-center gap-4">
            {hasError ? (
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <AlertTriangle size={20} className="text-red-600" />
              </div>
            ) : selectedPreviewIndex >= 0 ? (
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle2 size={20} className="text-green-600" />
              </div>
            ) : (
              <motion.div
                animate={isPaused ? {} : { rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className={cn(
                  'w-10 h-10 rounded-full flex items-center justify-center',
                  isPaused ? 'bg-amber-100' : 'bg-red-100'
                )}
              >
                {isPaused ? (
                  <Pause size={20} className="text-amber-600" />
                ) : (
                  <Loader2 size={20} className="text-red-600" />
                )}
              </motion.div>
            )}
            <div className="flex-1">
              <h2 className={cn(
                "text-lg font-bold",
                hasError ? "text-red-600" : "text-slate-900"
              )}>
                {hasError ? '生成出错' :
                 selectedPreviewIndex >= 0 ? `预览: ${lessonsOutline[selectedPreviewIndex]?.title || '课时内容'}` :
                 isPaused ? '已暂停' :
                 (streamStatus || '正在生成课程包...')}
              </h2>
              <p className="text-sm text-slate-500">
                {hasError ? '点击左侧"重新生成"按钮重试' :
                 selectedPreviewIndex >= 0 ? '查看已生成的课时内容' :
                 isPaused ? '点击"继续生成"按钮继续' :
                 'AI 正在实时生成内容，可点击左侧已完成课时预览'}
              </p>
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div
          ref={streamContainerRef}
          className="flex-1 p-6 bg-slate-50"
        >
          {hasError ? (
            /* Error State */
            <div className="max-w-3xl mx-auto bg-red-50 rounded-2xl border-2 border-red-200 p-6">
              <div className="flex items-start gap-3">
                <AlertTriangle size={24} className="text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-bold text-red-800 mb-2">生成失败</h3>
                  <p className="text-red-700 text-sm mb-4">{generationError}</p>
                  <p className="text-red-600 text-xs">
                    您可以点击左侧的"重新生成"按钮，使用当前导入的素材重新开始生成课程。
                    {completedLessons.length > 0 && ` 已完成 ${completedLessons.length} 个课时，可以从断点继续。`}
                  </p>
                </div>
              </div>
            </div>
          ) : selectedPreviewIndex >= 0 && previewLesson ? (
            /* Preview Completed Lesson */
            <div className="max-w-3xl mx-auto space-y-6">
              {/* Lesson Header */}
              <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
                <h3 className="text-xl font-bold text-slate-900 mb-2">{previewLesson.title}</h3>
                {previewLesson.description && (
                  <p className="text-slate-600 mb-3">{previewLesson.description}</p>
                )}
                {previewLesson.learning_objectives && previewLesson.learning_objectives.length > 0 && (
                  <div className="bg-blue-50 rounded-xl p-4">
                    <p className="text-sm font-medium text-blue-700 mb-2">学习目标</p>
                    <ul className="text-sm text-blue-600 space-y-1">
                      {previewLesson.learning_objectives.map((obj, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <CheckCircle2 size={14} className="mt-0.5 flex-shrink-0" />
                          {obj}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Lesson Rationale */}
              {previewLesson.rationale && (
                <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-2xl p-4 border border-red-100">
                  <p className="text-sm text-red-700">
                    <span className="font-medium">设计理念：</span>{previewLesson.rationale}
                  </p>
                </div>
              )}

              {/* Steps */}
              {previewLesson.steps && previewLesson.steps.map((step, stepIndex) => (
                <StepRenderer
                  key={step.step_id || stepIndex}
                  step={step}
                  stepIndex={stepIndex}
                  showRegenerate={!!onRegenerateStep}
                  onRegenerate={(idx, prompt) => onRegenerateStep?.(selectedPreviewIndex, idx, prompt)}
                />
              ))}
            </div>
          ) : (
            /* 实时打字机效果 - 冷峻风格 */
            <TypewriterContent
              streamedContent={streamedContent}
              currentLessonIndex={currentLessonIndex}
              totalLessons={totalLessons}
              lessonsOutline={lessonsOutline}
              streamingLessonInfo={streamingLessonInfo}
              isPaused={isPaused}
            />
          )}
        </div>
      </div>

      {/* Right Panel - Info */}
      <div className="w-72 bg-slate-50 border-l border-slate-200 flex flex-col sticky top-0 h-screen">
        <div className="p-4 border-b border-slate-200">
          <h2 className="text-sm font-bold text-slate-700 uppercase tracking-wider">生成信息</h2>
        </div>
        <div className="flex-1 overflow-auto p-4">
          <div className="space-y-4">
            {/* Course Title */}
            <div className="bg-white rounded-xl p-4 border border-slate-200">
              <p className="text-xs font-medium text-slate-500 mb-1">课程标题</p>
              <p className="text-sm font-bold text-slate-900">{courseTitle}</p>
            </div>

            {/* Source Info */}
            <div className="bg-white rounded-xl p-4 border border-slate-200">
              <p className="text-xs font-medium text-slate-500 mb-1">素材来源</p>
              <p className="text-sm text-slate-700">{sources.length} 个文件</p>
              <p className="text-xs text-slate-500 mt-1">{totalChars.toLocaleString()} 字符</p>
            </div>

            {/* Generation Status */}
            <div className="bg-white rounded-xl p-4 border border-slate-200">
              <p className="text-xs font-medium text-slate-500 mb-2">生成状态</p>
              <div className="space-y-2">
                {/* Phase 1 */}
                <div className={cn(
                  'flex items-center gap-2 p-2 rounded-lg text-xs',
                  generationPhase === 1 ? 'bg-amber-50 text-amber-700' :
                  generationPhase > 1 ? 'bg-green-50 text-green-700' :
                  'bg-slate-50 text-slate-500'
                )}>
                  {generationPhase === 1 ? (
                    <Loader2 size={12} className="animate-spin" />
                  ) : generationPhase > 1 ? (
                    <CheckCircle2 size={12} />
                  ) : (
                    <div className="w-3 h-3 rounded-full bg-slate-300" />
                  )}
                  <span>分析课程结构</span>
                </div>

                {/* Phase 2 */}
                <div className={cn(
                  'flex items-center gap-2 p-2 rounded-lg text-xs',
                  generationPhase === 2 ? 'bg-amber-50 text-amber-700' :
                  'bg-slate-50 text-slate-500'
                )}>
                  {generationPhase === 2 ? (
                    <Loader2 size={12} className="animate-spin" />
                  ) : (
                    <div className="w-3 h-3 rounded-full bg-slate-300" />
                  )}
                  <span>生成课时内容</span>
                </div>
              </div>
            </div>

            {/* Completed Lessons Count */}
            {totalLessons > 0 && (
              <div className="bg-white rounded-xl p-4 border border-slate-200">
                <p className="text-xs font-medium text-slate-500 mb-2">完成进度</p>
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-green-500 to-emerald-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${(completedLessons.length / totalLessons) * 100}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                  </div>
                  <span className="text-sm font-bold text-slate-700">
                    {completedLessons.length}/{totalLessons}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  {completedLessons.length === 0 ? '等待生成...' :
                   completedLessons.length === totalLessons ? '全部完成！' :
                   `还剩 ${totalLessons - completedLessons.length} 个课时`}
                </p>
              </div>
            )}

            {/* Tips */}
            <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
              <p className="text-xs font-medium text-blue-700 mb-2">提示</p>
              <ul className="text-xs text-blue-600 space-y-1">
                <li>• 点击左侧已完成课时可预览内容</li>
                <li>• 如内容不满意可取消重新生成</li>
                <li>• 生成过程中请勿关闭页面</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
