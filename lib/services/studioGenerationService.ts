/**
 * Studio Generation Service - 独立于组件生命周期的课程生成服务
 * 确保页面切换时生成不会中断
 */

import { useStudioStore, getAllSourceMaterial } from '@/stores/studio/useStudioStore';
import { studioGenerateApi } from '@/lib/api/studio';
import type { ProcessorWithConfig } from '@/types/studio';

class StudioGenerationService {
  private cancelFn: (() => void) | null = null;
  private isRunning = false;
  private isPaused = false;

  /**
   * 开始生成课程
   */
  startGeneration(processor: ProcessorWithConfig | null) {
    const store = useStudioStore.getState();
    const { sources, courseTitle, sourceInfo, selectedProcessorId } = store;

    if (this.isRunning) {
      console.warn('[GenerationService] Generation already in progress');
      return;
    }

    if (sources.length === 0 || !courseTitle.trim()) {
      console.error('[GenerationService] Missing sources or course title');
      return;
    }

    this.isRunning = true;

    // Reset generation state
    store.setCurrentView('generating');
    store.setStreamedContent('');
    store.setStreamStatus('正在初始化...');
    store.setGenerationPhase(0);
    store.setCurrentLessonIndex(-1);
    store.setTotalLessons(0);
    store.setLessonsOutline([]);
    store.setIsGenerating(true);
    store.setGenerationError(null);
    store.setCurrentProcessor(processor);
    // Clear completed lessons
    useStudioStore.setState({ completedLessons: [], completedLessonsData: [], generationMeta: null });

    // Start streaming generation
    this.cancelFn = studioGenerateApi.generateStream(
      {
        course_title: courseTitle,
        source_material: getAllSourceMaterial(sources),
        source_info: sourceInfo || '',
        processor_id: selectedProcessorId,
      },
      {
        onPhase: (phase, message, processorInfo) => {
          console.log('[GenerationService] onPhase:', { phase, message, processorInfo });
          const s = useStudioStore.getState();
          s.setStreamStatus(message);
          if (phase === 1) s.setGenerationPhase(1);
          else if (phase === 2) s.setGenerationPhase(2);
        },
        onStructure: (meta, lessonsCount, outline, processorInfo) => {
          console.log('[GenerationService] onStructure:', { meta, lessonsCount, outline, processorInfo });
          const s = useStudioStore.getState();
          s.setTotalLessons(lessonsCount);
          s.setLessonsOutline(outline || []);
          s.setGenerationMeta(meta);
          console.log('[GenerationService] Store after setLessonsOutline:', useStudioStore.getState().lessonsOutline);
        },
        onLessonStart: (index, total, title, recommendedForms, complexityLevel) => {
          console.log('[GenerationService] onLessonStart:', { index, total, title });
          const s = useStudioStore.getState();
          s.setCurrentLessonIndex(index);
          s.setTotalLessons(total);
          s.setStreamStatus(`正在生成课时 ${index + 1}/${total}: ${title || ''}...`);
          s.setStreamedContent('');
          // 清空流式步骤，准备接收新课时
          s.clearStreamingSteps();
          s.setStreamingLessonInfo({ title: title || `课时 ${index + 1}` });
        },
        onChunk: (content, phase, lessonIndex) => {
          console.log('[GenerationService] onChunk:', { contentLength: content?.length, phase, lessonIndex });
          const s = useStudioStore.getState();
          s.appendStreamedContent(content);
        },
        onStepComplete: (lessonIndex, stepIndex, step, totalSteps) => {
          console.log('[GenerationService] onStepComplete:', { lessonIndex, stepIndex, stepTitle: step?.title, totalSteps });
          const s = useStudioStore.getState();
          s.addStreamingStep(step);
          s.setStreamStatus(`正在生成步骤 ${stepIndex + 1}/${totalSteps}...`);
        },
        onLessonComplete: (index, total, lesson, warning) => {
          console.log('[GenerationService] onLessonComplete:', {
            index,
            total,
            lessonTitle: lesson?.title,
            scriptLength: lesson?.script?.length,
            scriptSteps: lesson?.script?.map((s: any) => s.title)
          });
          const s = useStudioStore.getState();
          s.addCompletedLesson(index, lesson);
          s.clearStreamingSteps();
          // 验证存储后的数据
          const afterState = useStudioStore.getState();
          console.log('[GenerationService] After addCompletedLesson:', {
            completedLessonsCount: afterState.completedLessonsData?.length,
            lastLessonScriptLength: afterState.completedLessonsData?.[afterState.completedLessonsData.length - 1]?.script?.length
          });
        },
        onComplete: (pkg) => {
          const s = useStudioStore.getState();
          s.setGeneratedPackage(pkg);
          s.setSelectedLessonId(pkg.lessons[0]?.lesson_id || null);
          s.setCurrentView('result');
          s.setIsGenerating(false);
          s.clearStreamingSteps();
          this.isRunning = false;
          this.cancelFn = null;
        },
        onError: (message) => {
          const s = useStudioStore.getState();
          s.setStreamStatus(`错误: ${message}`);
          s.setGenerationError(message);
          s.setIsGenerating(false);
          this.isRunning = false;
          this.cancelFn = null;
          console.error('[GenerationService] Error:', message);
        },
      }
    );

    // Store cancel function in store
    store.setCancelGeneration(() => this.cancel());
  }

  /**
   * 取消生成
   */
  cancel() {
    if (this.cancelFn) {
      this.cancelFn();
      this.cancelFn = null;
    }
    this.isRunning = false;

    const store = useStudioStore.getState();
    store.setIsGenerating(false);
    store.setCancelGeneration(null);
  }

  /**
   * 重试生成（出错后从断点继续）
   */
  retry(processor: ProcessorWithConfig | null) {
    const store = useStudioStore.getState();
    const {
      sources,
      courseTitle,
      sourceInfo,
      selectedProcessorId,
      completedLessons,
      completedLessonsData,
      lessonsOutline,
      generationMeta,
      currentLessonIndex,
    } = store;

    console.log('[GenerationService] Retry called', {
      isRunning: this.isRunning,
      completedLessonsData: completedLessonsData?.length,
      lessonsOutline: lessonsOutline?.length,
      sources: sources?.length,
      courseTitle,
    });

    // Cancel any existing generation
    this.cancel();

    // 强制重置 isRunning 状态
    this.isRunning = false;

    // 检查是否有已完成的课时可以续传
    const hasCompletedLessons = completedLessonsData && completedLessonsData.length > 0 && lessonsOutline && lessonsOutline.length > 0;

    console.log('[GenerationService] hasCompletedLessons:', hasCompletedLessons);

    if (hasCompletedLessons) {
      // 断点续传模式
      console.log('[GenerationService] Resuming from lesson', completedLessonsData.length);

      this.isRunning = true;

      // 保持已有状态，只清除错误
      store.setCurrentView('generating');
      store.setStreamedContent('');
      store.setStreamStatus(`从课时 ${completedLessonsData.length + 1} 继续生成...`);
      store.setIsGenerating(true);
      store.setGenerationError(null);
      store.setCurrentProcessor(processor);

      // 从断点继续
      this.cancelFn = studioGenerateApi.generateStream(
        {
          course_title: courseTitle,
          source_material: getAllSourceMaterial(sources),
          source_info: sourceInfo || '',
          processor_id: selectedProcessorId,
          // 断点续传参数
          resume_from_lesson: completedLessonsData.length,
          completed_lessons: completedLessonsData,
          lessons_outline: lessonsOutline,
          meta: generationMeta,
        },
        {
          onPhase: (phase, message, processorInfo) => {
            const s = useStudioStore.getState();
            s.setStreamStatus(message);
            s.setGenerationPhase(phase);
          },
          onStructure: (meta, lessonsCount, outline, processorInfo) => {
            // 续传时结构已经有了，不需要更新
          },
          onLessonStart: (index, total, title, recommendedForms, complexityLevel) => {
            const s = useStudioStore.getState();
            s.setCurrentLessonIndex(index);
            s.setStreamStatus(`正在生成课时 ${index + 1}/${total}: ${title || ''}...`);
          },
          onChunk: (content, phase, lessonIndex) => {
            const s = useStudioStore.getState();
            s.appendStreamedContent(content);
          },
          onLessonComplete: (index, total, lesson, warning) => {
            const s = useStudioStore.getState();
            s.addCompletedLesson(index, lesson);
          },
          onComplete: (pkg) => {
            const s = useStudioStore.getState();
            s.setGeneratedPackage(pkg);
            s.setSelectedLessonId(pkg.lessons[0]?.lesson_id || null);
            s.setCurrentView('result');
            s.setIsGenerating(false);
            this.isRunning = false;
            this.cancelFn = null;
          },
          onError: (message) => {
            const s = useStudioStore.getState();
            s.setStreamStatus(`错误: ${message}`);
            s.setGenerationError(message);
            s.setIsGenerating(false);
            this.isRunning = false;
            this.cancelFn = null;
            console.error('[GenerationService] Resume Error:', message);
          },
        }
      );

      store.setCancelGeneration(() => this.cancel());
    } else {
      // 没有已完成的课时，从头开始
      console.log('[GenerationService] No completed lessons, starting fresh');
      store.setGeneratedPackage(null);
      store.setGenerationError(null);
      store.setStreamedContent('');
      useStudioStore.setState({ completedLessons: [], completedLessonsData: [], generationMeta: null });
      this.startGeneration(processor);
    }
  }

  /**
   * 检查是否正在生成
   */
  isGenerating() {
    return this.isRunning;
  }

  /**
   * 暂停生成 - 取消当前请求，保留已完成的课时
   */
  pause() {
    if (this.isRunning && !this.isPaused) {
      this.isPaused = true;
      this.isRunning = false;
      // 取消当前流式请求
      if (this.cancelFn) {
        this.cancelFn();
        this.cancelFn = null;
      }
      useStudioStore.setState({ isPaused: true, isGenerating: false });
      console.log('[GenerationService] Paused - request cancelled, progress saved');
    }
  }

  /**
   * 继续生成 - 从断点恢复
   */
  resume() {
    if (this.isPaused) {
      this.isPaused = false;
      useStudioStore.setState({ isPaused: false });
      console.log('[GenerationService] Resuming from checkpoint...');

      const store = useStudioStore.getState();
      const processor = store.currentProcessor;

      // 使用 retry 方法从断点继续
      this.retry(processor);
    }
  }

  /**
   * 检查是否暂停
   */
  getIsPaused() {
    return this.isPaused;
  }
}

// 单例实例
export const studioGenerationService = new StudioGenerationService();
