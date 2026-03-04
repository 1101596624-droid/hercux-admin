/**
 * Studio Generation Service V3 - 监督者+生成者架构
 * 确保页面切换时生成不会中断
 */

import { useStudioStore, getAllSourceMaterial, getUploadSourceIds } from '@/stores/studio/useStudioStore';
import { studioGenerateApi, studioAsyncApi, V3StreamCallbacks, V3CourseOutline, V3GenerationStats } from '@/lib/api/studio';
import type { ProcessorWithConfig, LessonOutline, GenerateRequestV2 } from '@/types/studio';

class StudioGenerationService {
  private cancelFn: (() => void) | null = null;
  private isRunning = false;
  private isPaused = false;
  private isPausingOrCancelling = false;
  private activeTaskId: string | null = null;
  private currentRequest: GenerateRequestV2 | null = null;

  private createClientRequestId(): string {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID();
    }
    return `studio-v3-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  /**
   * 开始生成课程 (V3 架构)
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
    this.isPaused = false;
    this.activeTaskId = null;

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

    const requestPayload: GenerateRequestV2 = {
      course_title: courseTitle,
      source_material: getAllSourceMaterial(sources),
      source_upload_ids: getUploadSourceIds(sources),
      source_info: sourceInfo || '',
      processor_id: selectedProcessorId,
      client_request_id: this.createClientRequestId(),
    };
    this.currentRequest = requestPayload;
    this.startStream(requestPayload);
  }

  private startStream(requestPayload: GenerateRequestV2) {
    const store = useStudioStore.getState();
    this.cancelFn = studioGenerateApi.generateStreamV3(requestPayload, this.createV3Callbacks());
    // 仅中断订阅，不自动取消后台任务
    store.setCancelGeneration(() => this.cancel());
  }

  /**
   * 创建 V3 回调
   */
  private createV3Callbacks(): V3StreamCallbacks {
    return {
      onTaskCreated: (taskId) => {
        this.activeTaskId = taskId;
      },
      onPhase: (phase, message, processorInfo) => {
        const s = useStudioStore.getState();
        s.setStreamStatus(message);
        s.setGenerationPhase(phase);
      },

      onOutline: (outline: V3CourseOutline) => {
        const s = useStudioStore.getState();
        s.setTotalLessons(outline.total_chapters);
        // 转换为 lessonsOutline 格式
        const lessonsOutline: LessonOutline[] = outline.chapters.map(ch => ({
          title: ch.title,
          recommended_forms: ['text_content', 'simulator', 'assessment'],
          complexity_level: 'standard' as const,
          suggested_simulator: ch.suggested_simulator,
        }));
        s.setLessonsOutline(lessonsOutline);
        s.setGenerationMeta({
          title: outline.title,
          description: outline.description,
          total_lessons: outline.total_chapters,
          estimated_hours: outline.estimated_hours,
          style: 'v3',
          created_at: new Date().toISOString(),
          difficulty: outline.difficulty,
        });
        // 保存完整大纲
        useStudioStore.setState({ v3Outline: outline });
      },

      onChapterStart: (index, total, title, attempt) => {
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
        const s = useStudioStore.getState();
        s.setStreamStatus(`第 ${index + 1} 章需要重做 (第${attempt}次尝试)...`);
        s.setStreamedContent('');
        useStudioStore.setState({ v3CurrentAttempt: attempt });
      },

      onSimulatorProgress: (simulatorName, _stepIndex, round, maxRounds, stage, message) => {
        const s = useStudioStore.getState();
        s.setStreamStatus(`模拟器 "${simulatorName}": ${message}`);
      },

      onChapterComplete: (index, total, chapter, attempts) => {
        const s = useStudioStore.getState();

        // 修复：使用all_completed_chapters恢复完整章节列表（Bug #3修复）
        if (chapter.all_completed_chapters && Array.isArray(chapter.all_completed_chapters)) {
          s.setCompletedLessonsData(chapter.all_completed_chapters);
        } else {
          // 兼容旧版本：如果没有all_completed_chapters，则append
          s.addCompletedLesson(index, chapter);
        }

        s.clearStreamingSteps();

        const attemptText = attempts > 1 ? ` (${attempts}次尝试后通过)` : '';
        s.setStreamStatus(`第 ${index + 1}/${total} 章完成${attemptText}`);
      },

      onComplete: (pkg, stats: V3GenerationStats) => {
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
        this.activeTaskId = null;
        this.currentRequest = null;
      },

      onError: (message) => {
        if (this.isPausingOrCancelling) {
          return;
        }
        const s = useStudioStore.getState();
        s.setStreamStatus(`错误: ${message}`);
        s.setGenerationError(message);
        s.setIsGenerating(false);
        this.isRunning = false;
        this.cancelFn = null;
        if (message.includes('任务已取消')) {
          this.activeTaskId = null;
          this.currentRequest = null;
        }
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
   * 显式取消后台任务（用于“取消生成”按钮）
   */
  async cancelWithServer(adminId: number = 1) {
    const taskId = this.activeTaskId;
    this.cancel();
    if (taskId) {
      try {
        await studioAsyncApi.cancelTask(taskId, adminId);
      } catch (error) {
        console.error('[GenerationService V3] cancel server task failed:', error);
      }
    }
    this.activeTaskId = null;
    this.currentRequest = null;
    const store = useStudioStore.getState();
    store.setStreamStatus('任务已取消');
    store.setGenerationError('任务已取消');
  }

  /**
   * 重试生成（V3 不支持断点续传，从头开始）
   */
  retry(processor: ProcessorWithConfig | null) {
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
    }
  }

  /**
   * 继续订阅（后台任务持续执行，使用同一 request_id 复连）
   */
  resume() {
    if (this.isPaused) {
      this.isPaused = false;
      useStudioStore.setState({ isPaused: false });
      if (this.currentRequest) {
        this.isRunning = true;
        useStudioStore.setState({ isGenerating: true, generationError: null });
        this.startStream(this.currentRequest);
      }
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
