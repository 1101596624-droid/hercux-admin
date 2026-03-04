/**
 * Studio Store - 课程生成工具状态管理
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type {
  CoursePackageV2,
  PackageMetaV2,
  Processor,
  ProcessorWithConfig,
  ComplexityLevel,
  ViewMode,
  UploadedSource,
  LessonOutline,
  GenerationProgress,
  Lesson,
  LessonStep,
} from '@/types/studio';
import type { V3CourseOutline } from '@/lib/api/studio';

interface StudioState {
  // View state
  currentView: ViewMode;

  // Sources
  sources: UploadedSource[];

  // Form inputs
  courseTitle: string;
  selectedProcessorId: string;
  sourceInfo: string;

  // Generation state
  streamedContent: string;
  streamStatus: string;
  generationProgress: GenerationProgress | null;
  isGenerating: boolean;
  isPaused: boolean;  // 暂停状态
  generationPhase: number;
  currentLessonIndex: number;
  totalLessons: number;
  lessonsOutline: LessonOutline[];
  completedLessons: number[];
  completedLessonsData: Lesson[];  // 已完成课时的完整数据
  generationMeta: PackageMetaV2 | null;   // 课程元数据
  generationError: string | null;
  currentProcessor: ProcessorWithConfig | null;

  // V3 特有状态
  v3Outline: V3CourseOutline | null;  // V3 大纲
  v3CurrentAttempt: number;  // 当前章节尝试次数
  v3ReviewResults: Array<{
    index: number;
    status: string;
    score: number;
    issues: string[];
    simulatorIssues: string[];
    comment: string;
  }>;  // 审核结果历史

  // 流式步骤状态（用于实时渲染）
  streamingSteps: LessonStep[];  // 当前课时已完成的步骤
  streamingLessonInfo: { title: string; rationale?: string; learning_objectives?: string[] } | null;

  // Generated package
  generatedPackage: CoursePackageV2 | null;

  // Selection state
  selectedLessonId: string | null;
  selectedStepIndex: number;

  // Cancel function for streaming
  cancelGeneration: (() => void) | null;
}

interface StudioActions {
  // View
  setCurrentView: (view: ViewMode) => void;

  // Sources
  setSources: (sources: UploadedSource[]) => void;
  addSource: (source: UploadedSource) => void;
  removeSource: (id: string) => void;

  // Form
  setCourseTitle: (title: string) => void;
  setSelectedProcessorId: (processorId: string) => void;
  setSourceInfo: (info: string) => void;

  // Generation
  setStreamedContent: (content: string) => void;
  appendStreamedContent: (chunk: string) => void;
  setStreamStatus: (status: string) => void;
  setGenerationProgress: (progress: GenerationProgress | null) => void;
  updateGenerationProgress: (updates: Partial<GenerationProgress>) => void;
  setCancelGeneration: (cancel: (() => void) | null) => void;
  setIsGenerating: (isGenerating: boolean) => void;
  setGenerationPhase: (phase: number) => void;
  setCurrentLessonIndex: (index: number) => void;
  setTotalLessons: (total: number) => void;
  setLessonsOutline: (outline: LessonOutline[]) => void;
  addCompletedLesson: (index: number, lessonData?: Lesson) => void;
  setCompletedLessonsData: (lessonsData: Lesson[]) => void; // 修复Bug #3：直接设置完整章节列表
  setGenerationMeta: (meta: PackageMetaV2) => void;
  setGenerationError: (error: string | null) => void;
  setCurrentProcessor: (processor: ProcessorWithConfig | null) => void;
  setIsPaused: (isPaused: boolean) => void;  // 新增：设置暂停状态

  // 流式步骤
  addStreamingStep: (step: LessonStep) => void;
  setStreamingLessonInfo: (info: { title: string; rationale?: string; learning_objectives?: string[] } | null) => void;
  clearStreamingSteps: () => void;

  // Package
  setGeneratedPackage: (pkg: CoursePackageV2 | null) => void;

  // Selection
  setSelectedLessonId: (id: string | null) => void;
  setSelectedStepIndex: (index: number) => void;

  // Reset
  reset: () => void;
  resetGeneration: () => void;
}

type StudioStore = StudioState & StudioActions;

const initialState: StudioState = {
  currentView: 'input',
  sources: [],
  courseTitle: '',
  selectedProcessorId: 'intelligent',
  sourceInfo: '',
  streamedContent: '',
  streamStatus: '',
  generationProgress: null,
  isGenerating: false,
  isPaused: false,
  generationPhase: 0,
  currentLessonIndex: -1,
  totalLessons: 0,
  lessonsOutline: [],
  completedLessons: [],
  completedLessonsData: [],
  generationMeta: null,
  generationError: null,
  currentProcessor: null,
  // V3 特有状态
  v3Outline: null,
  v3CurrentAttempt: 1,
  v3ReviewResults: [],
  streamingSteps: [],
  streamingLessonInfo: null,
  generatedPackage: null,
  selectedLessonId: null,
  selectedStepIndex: 0,
  cancelGeneration: null,
};

export const useStudioStore = create<StudioStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      // View
      setCurrentView: (view) => set({ currentView: view }),

      // Sources
      setSources: (sources) => set({ sources }),
      addSource: (source) =>
        set((state) => ({ sources: [...state.sources, source] })),
      removeSource: (id) =>
        set((state) => ({ sources: state.sources.filter((s) => s.id !== id) })),

      // Form
      setCourseTitle: (title) => set({ courseTitle: title }),
      setSelectedProcessorId: (processorId) => set({ selectedProcessorId: processorId }),
      setSourceInfo: (info) => set({ sourceInfo: info }),

      // Generation
      setStreamedContent: (content) => set({ streamedContent: content }),
      appendStreamedContent: (chunk) =>
        set((state) => ({ streamedContent: state.streamedContent + chunk })),
      setStreamStatus: (status) => set({ streamStatus: status }),
      setGenerationProgress: (progress) => set({ generationProgress: progress }),
      updateGenerationProgress: (updates) =>
        set((state) => ({
          generationProgress: state.generationProgress
            ? { ...state.generationProgress, ...updates }
            : null,
        })),
      setCancelGeneration: (cancel) => set({ cancelGeneration: cancel }),
      setIsGenerating: (isGenerating) => set({ isGenerating }),
      setGenerationPhase: (phase) => set({ generationPhase: phase }),
      setCurrentLessonIndex: (index) => set({ currentLessonIndex: index }),
      setTotalLessons: (total) => set({ totalLessons: total }),
      setLessonsOutline: (outline) => set({ lessonsOutline: outline }),
      addCompletedLesson: (index, lessonData) =>
        set((state) => ({
          completedLessons: [...state.completedLessons, index],
          completedLessonsData: lessonData
            ? [...state.completedLessonsData, lessonData]
            : state.completedLessonsData,
        })),
      setCompletedLessonsData: (lessonsData) =>
        set(() => ({
          completedLessonsData: lessonsData,
          completedLessons: lessonsData.map((_: Lesson, idx: number) => idx),
        })),  // 修复Bug #3：直接设置完整章节列表
      setGenerationMeta: (meta) => set({ generationMeta: meta }),
      setGenerationError: (error) => set({ generationError: error }),
      setCurrentProcessor: (processor) => set({ currentProcessor: processor }),
      setIsPaused: (isPaused) => set({ isPaused }),  // 新增

      // 流式步骤
      addStreamingStep: (step) =>
        set((state) => ({ streamingSteps: [...state.streamingSteps, step] })),
      setStreamingLessonInfo: (info) => set({ streamingLessonInfo: info }),
      clearStreamingSteps: () => set({ streamingSteps: [], streamingLessonInfo: null }),

      // Package
      setGeneratedPackage: (pkg) => set({ generatedPackage: pkg }),

      // Selection
      setSelectedLessonId: (id) => set({ selectedLessonId: id, selectedStepIndex: 0 }),
      setSelectedStepIndex: (index) => set({ selectedStepIndex: index }),

      // Reset
      reset: () => {
        const { cancelGeneration } = get();
        if (cancelGeneration) {
          cancelGeneration();
        }
        set({ ...initialState });
      },
      resetGeneration: () => {
        const { cancelGeneration } = get();
        if (cancelGeneration) {
          cancelGeneration();
        }
        set({
          currentView: 'input',
          streamedContent: '',
          streamStatus: '',
          generationProgress: null,
          isGenerating: false,
          isPaused: false,  // 新增
          generationPhase: 0,
          currentLessonIndex: -1,
          totalLessons: 0,
          lessonsOutline: [],
          completedLessons: [],
          completedLessonsData: [],
          generationMeta: null,
          generationError: null,
          currentProcessor: null,
          streamingSteps: [],
          streamingLessonInfo: null,
          generatedPackage: null,
          selectedLessonId: null,
          selectedStepIndex: 0,
          cancelGeneration: null,
        });
      },
    }),
    {
      name: 'hercu-studio',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        currentView: state.currentView,
        sources: state.sources,
        courseTitle: state.courseTitle,
        selectedProcessorId: state.selectedProcessorId,
        sourceInfo: state.sourceInfo,
        generatedPackage: state.generatedPackage,
        selectedLessonId: state.selectedLessonId,
        selectedStepIndex: state.selectedStepIndex,
        // Persist generation state for page navigation and resume
        isGenerating: state.isGenerating,
        generationPhase: state.generationPhase,
        currentLessonIndex: state.currentLessonIndex,
        totalLessons: state.totalLessons,
        lessonsOutline: state.lessonsOutline,
        completedLessons: state.completedLessons,
        completedLessonsData: state.completedLessonsData,
        generationMeta: state.generationMeta,
        streamedContent: state.streamedContent,
        streamStatus: state.streamStatus,
        generationError: state.generationError,
      }),
    }
  )
);

// ============================================
// Selectors
// ============================================

export const selectCurrentView = (state: StudioStore) => state.currentView;
export const selectSources = (state: StudioStore) => state.sources;
export const selectCourseTitle = (state: StudioStore) => state.courseTitle;
export const selectSelectedProcessorId = (state: StudioStore) => state.selectedProcessorId;
export const selectSourceInfo = (state: StudioStore) => state.sourceInfo;
export const selectGeneratedPackage = (state: StudioStore) => state.generatedPackage;
export const selectGenerationProgress = (state: StudioStore) => state.generationProgress;
export const selectSelectedLessonId = (state: StudioStore) => state.selectedLessonId;
export const selectSelectedStepIndex = (state: StudioStore) => state.selectedStepIndex;

// ============================================
// Helpers
// ============================================

/**
 * 获取当前选中的课时
 */
export const getCurrentLesson = (state: StudioStore): Lesson | null => {
  const pkg = state.generatedPackage;
  if (!pkg) return null;
  return pkg.lessons.find(l => l.lesson_id === state.selectedLessonId) || pkg.lessons[0] || null;
};

/**
 * 获取当前选中的步骤
 */
export const getCurrentStep = (state: StudioStore) => {
  const lesson = getCurrentLesson(state);
  if (!lesson) return null;
  return lesson.steps[state.selectedStepIndex] || lesson.steps[0] || null;
};

/**
 * 获取所有来源的总字符数
 */
export const getTotalCharCount = (sources: UploadedSource[]) => {
  return sources.reduce((sum, s) => sum + s.charCount, 0);
};

/**
 * 合并所有来源材料
 */
export const getAllSourceMaterial = (sources: UploadedSource[]) => {
  return sources
    .filter((source) => source.text && source.text.trim().length > 0)
    .map((source) => `【来源: ${source.name}】\n${source.text}`)
    .join('\n\n---\n\n');
};

/**
 * 获取已上传文件 ID 列表（生成时服务端再解析）
 */
export const getUploadSourceIds = (sources: UploadedSource[]) => {
  return sources
    .filter((source) => source.type === 'file' && source.uploadId)
    .map((source) => source.uploadId as string);
};

/**
 * 检查是否可以开始生成
 */
export const canGenerate = (sources: UploadedSource[], courseTitle: string) => {
  return sources.length > 0 && courseTitle.trim().length > 0;
};

/**
 * 格式化字符数显示
 */
export const formatCharCount = (count: number): string => {
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万`;
  }
  return count.toLocaleString();
};
