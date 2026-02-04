/**
 * Studio Generation Service V3 - 监督者+生成者架构
 * 确保页面切换时生成不会中断
 */

import { useStudioStore, getAllSourceMaterial } from '@/stores/studio/useStudioStore';
import { studioGenerateApi, V3StreamCallbacks, V3CourseOutline, V3GenerationStats } from '@/lib/api/studio';
import type { ProcessorWithConfig } from '@/types/studio';

class StudioGenerationService {
  private cancelFn: (() => void) | null = null;
  private isRunning = false;
  private isPaused = false;
  private isPausingOrCancelling = false;

  /**
   * 开始��成课程 (V3 架构)
   */
  startGeneration(processor: ProcessorWithConfig | null) {
    const store = useStudioStore.getState();
    const { sources, courseTitle, sourceInfo, selectedProcessorId } = store;

    if (this.isRunning) {
      console.warn('[GenerationService V3] Generation already in progress');
      return;
    }

    if (sources.length === 0 || !courseTitle.trim()) {
      console.error('[GenerationService V3] Missing sources or course title');
      return;
    }

    this.isRunning = true;

    // Reset generation state
    store.setCurrentView('generating');
    store.setStreamedContent('');
    store.setStreamStatus('监督者正在分析源材料...');
    store.setGenerationPhase(0);
    store.setCurrentLessonIndex(-1);
    store.setTotalLessons(0);
    store.setLessonsOutline([]);
    store.setIsGenerating(true);
    store.setGenerationError(null);
    store.setCurrentProcessor(processor);
    // Clear completed lessons and V3 specific state
    useStudioStore.setState({
      completedLessons: [],
      completedLessonsData: [],
      generationMeta: null,
      // V3 specific
      v3Outline: null,
      v3CurrentAttempt: 1,
      v3ReviewResults: [],
    });

    // Start V3 streaming generation
    this.cancelFn = studioGenerateApi.generateStreamV3(
      {
        course_title: courseTitle,
        source_material: getAllSourceMaterial(sources),
        source_info: sourceInfo || '',
        processor_id: selectedProcessorId,
      },
      this.createV3Callbacks()
    );

    // Store cancel function in store
    store.setCancelGeneration(() => this.cancel());
  }

  /**
   * 创建 V3 回调
   */
  private createV3Callbacks(): V3StreamCallbacks {
    return {
      onPhase: (phase, message, processorInfo) => {
        console.log('[GenerationService V3] onPhase:', { phase, message });
        const s = useStudioStore.getState();
        s.setStreamStatus(message);
        s.setGenerationPhase(phase);
      },

      onOutline: (outline: V3CourseOutline) => {
        console.log('[GenerationService V3] onOutline:', outline);
        const s = useStudioStore.getState();
        s.setTotalLessons(outline.total_chapters);
        // 转换为 lessonsOutline 格式
        const lessonsOutline = outline.chapters.map(ch => ({
          title: ch.title,
          recommended_forms: ['text_content', 'simulator', 'assessment'],
          complexity_level: 'standard',
          suggested_simulator: ch.suggested_simulator,
        }));
        s.setLessonsOutline(lessonsOutline);
        s.setGenerationMeta({
          description: outline.description,
          estimated_hours: outline.estimated_hours,
          difficulty: outline.difficulty,
        });
        // 保存完整大纲
        useStudioStore.setState({ v3Outline: outline });
      },

      onChapterStart: (index, total, title, attempt) => {
        console.log('[GenerationService V3] onChapterStart:', { index, total, title, attempt });
        const s = useStudioStore.getState();
        s.setCurrentLessonIndex(index);
        s.setTotalLessons(total);
        const attemptText = attempt > 1 ? ` (第${attempt}次尝试)` : '';
        s.setStreamStatus(`正在生成第 ${index + 1}/${total} 章: ${title}${attemptText}...`);
        s.setStreamedContent('');
        s.clearStreamingSteps();
        s.setStreamingLessonInfo({ title: title || `第 ${index + 1} 章` });
        useStudioStore.setState({ v3CurrentAttempt: attempt });
      },

      onChunk: (content, chapterIndex, attempt) => {
        const s = useStudioStore.getState();
        s.appendStreamedContent(content);
      },

      onChapterReview: (index, status, score, issues, simulatorIssues, comment) => {
        console.log('[GenerationService V3] onChapterReview:', { index, status, score, issues, simulatorIssues });
        const s = useStudioStore.getState();

        // 更新状态显示审核结果
        const statusText = status === 'approved' ? '通过' : status === 'rejected' ? '不通过' : '需修改';
        s.setStreamStatus(`第 ${index + 1} 章审核${statusText} (${score}分)`);

        // 保存审核结果
        const currentReviews = useStudioStore.getState().v3ReviewResults || [];
        useStudioStore.setState({
          v3ReviewResults: [...currentReviews, { index, status, score, issues, simulatorIssues, comment }]
        });
      },

      onChapterRetry: (index, attempt, reason) => {
        console.log('[GenerationService V3] onChapterRetry:', { index, attempt, reason });
        const s = useStudioStore.getState();
        s.setStreamStatus(`第 ${index + 1} 章需要重做 (第${attempt}次尝试)...`);
        s.setStreamedContent('');
        useStudioStore.setState({ v3CurrentAttempt: attempt });
      },

      onChapterComplete: (index, total, chapter, attempts) => {
        console.log('[GenerationService V3] onChapterComplete:', {
          index,
          total,
          chapterTitle: chapter?.title,
          scriptLength: chapter?.script?.length,
          attempts
        });
        const s = useStudioStore.getState();
        s.addCompletedLesson(index, chapter);
        s.clearStreamingSteps();

        const attemptText = attempts > 1 ? ` (${attempts}次尝试后通过)` : '';
        s.setStreamStatus(`第 ${index + 1}/${total} 章完成${attemptText}`);
      },

      onComplete: (pkg, stats: V3GenerationStats) => {
        console.log('[GenerationService V3] onComplete:', {
          lessonsCount: pkg.lessons?.length,
          stats
        });
        const s = useStudioStore.getState();
        s.setGeneratedPackage(pkg);
        s.setSelectedLessonId(pkg.lessons[0]?.lesson_id || null);
        s.setCurrentView('result');
        s.setIsGenerating(false);
        s.clearStreamingSteps();

        // 显示生成统计
        const timeMinutes = Math.round(stats.generation_time / 60);
        s.setStreamStatus(`生成完成！共 ${stats.total_chapters} 章，${stats.total_simulators} 个模拟器，耗时 ${timeMinutes} 分钟`);

        this.isRunning = false;
        this.cancelFn = null;
      },

      onError: (message) => {
        if (this.isPausingOrCancelling) {
          console.log('[GenerationService V3] Ignoring error during pause/cancel:', message);
          return;
        }
        const s = useStudioStore.getState();
        s.setStreamStatus(`错误: ${message}`);
        s.setGenerationError(message);
        s.setIsGenerating(false);
        this.isRunning = false;
        this.cancelFn = null;
        console.error('[GenerationService V3] Error:', message);
      },
    };
  }

  /**
   * 取消生成
   */
  cancel() {
    this.isPausingOrCancelling = true;
    if (this.cancelFn) {
      this.cancelFn();
      this.cancelFn = null;
    }
    this.isRunning = false;
    setTimeout(() => { this.isPausingOrCancelling = false; }, 100);

    const store = useStudioStore.getState();
    store.setIsGenerating(false);
    store.setCancelGeneration(null);
  }

  /**
   * 重试生成（V3 不支持断点续传，从头开始）
   */
  retry(processor: ProcessorWithConfig | null) {
    console.log('[GenerationService V3] Retry called - starting fresh');

    // Cancel any existing generation
    this.cancel();
    this.isRunning = false;

    // Clear all state and start fresh
    const store = useStudioStore.getState();
    store.setGeneratedPackage(null);
    store.setGenerationError(null);
    store.setStreamedContent('');
    useStudioStore.setState({
      completedLessons: [],
      completedLessonsData: [],
      generationMeta: null,
      v3Outline: null,
      v3CurrentAttempt: 1,
      v3ReviewResults: [],
    });

    this.startGeneration(processor);
  }

  /**
   * 检查是否正在生成
   */
  isGenerating() {
    return this.isRunning;
  }

  /**
   * 暂停生成
   */
  pause() {
    if (this.isRunning && !this.isPaused) {
      this.isPaused = true;
      this.isRunning = false;
      this.isPausingOrCancelling = true;
      if (this.cancelFn) {
        this.cancelFn();
        this.cancelFn = null;
      }
      setTimeout(() => { this.isPausingOrCancelling = false; }, 100);
      useStudioStore.setState({ isPaused: true, isGenerating: false });
      console.log('[GenerationService V3] Paused');
    }
  }

  /**
   * 继续生成（V3 从头开始，因为监督者需要完整上下文）
   */
  resume() {
    if (this.isPaused) {
      this.isPaused = false;
      useStudioStore.setState({ isPaused: false });
      console.log('[GenerationService V3] Resuming - starting fresh due to supervisor context requirements');

      const store = useStudioStore.getState();
      const processor = store.currentProcessor;
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
