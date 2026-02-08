/**
 * Editor Store - 课程编辑器状态管理
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type {
  EditorState,
  EditorChapter,
  EditorSection,
  ComponentType,
  AIProvider,
  AITrigger,
  AIGuidanceConfig,
  NodeConfig,
  CourseDifficulty,
} from '@/types/editor';
import {
  DEFAULT_AI_GUIDANCE,
  DEFAULT_NODE_CONFIG,
  createDefaultChapter,
  createDefaultSection,
  createDefaultTrigger,
} from '@/types/editor';
import type { CoursePackageV2, LessonStep, TeachingFormType } from '@/types/studio';

// ============================================
// Helper Functions for Type Conversion
// ============================================

/**
 * Map TeachingFormType to ComponentType
 */
function mapStepTypeToComponentType(type: TeachingFormType): ComponentType {
  const mapping: Record<TeachingFormType, ComponentType> = {
    text_content: 'text_content',
    illustrated_content: 'illustrated_content',
    video: 'video',
    simulator: 'simulator',
    ai_tutor: 'ai_tutor',
    assessment: 'assessment',
    quick_check: 'quick_check',
    practice: 'practice',
  };
  return mapping[type] || 'text_content';
}

/**
 * Convert LessonStep to NodeConfig
 */
function convertStepToNodeConfig(step: LessonStep): NodeConfig {
  const baseConfig: NodeConfig = {
    type: mapStepTypeToComponentType(step.type),
  };

  switch (step.type) {
    case 'text_content':
    case 'practice':
      baseConfig.textConfig = {
        content: typeof step.content === 'object' && 'body' in step.content
          ? step.content.body
          : typeof step.content === 'object' && 'text' in step.content
            ? (step.content as { text: string }).text
            : '',
        format: 'markdown',
        keyPoints: typeof step.content === 'object' && 'key_points' in step.content
          ? step.content.key_points
          : undefined,
      };
      break;

    case 'illustrated_content':
      baseConfig.textConfig = {
        content: typeof step.content === 'object' && 'body' in step.content
          ? step.content.body
          : typeof step.content === 'object' && 'text' in step.content
            ? (step.content as { text: string }).text
            : '',
        format: 'markdown',
        keyPoints: typeof step.content === 'object' && 'key_points' in step.content
          ? step.content.key_points
          : undefined,
      };
      // 转换 diagram_spec 到 illustratedConfig
      if ('diagram_spec' in step && step.diagram_spec) {
        baseConfig.illustratedConfig = {
          imageUrl: step.diagram_spec.image_url || '',
          imageAlt: step.diagram_spec.description || '',
          layout: 'text_left_image_right',
        };
      }
      break;

    case 'video':
      baseConfig.videoConfig = {
        videoUrl: step.video_spec?.video_id || '',
        duration: step.video_spec?.duration ? parseInt(step.video_spec.duration) : undefined,
      };
      break;

    case 'simulator':
      baseConfig.simulatorConfig = step.simulator_spec ? {
        type: step.simulator_spec.type || 'preset',
        presetId: step.simulator_spec.preset_id,
        name: step.simulator_spec.name || step.title || '',
        description: step.simulator_spec.description || step.simulator_spec.scenario?.description || '',
        // 自定义代码模式
        mode: step.simulator_spec.mode,
        custom_code: step.simulator_spec.custom_code,
        variables: step.simulator_spec.variables,
        inputs: step.simulator_spec.inputs?.map(input => ({
          id: input.id,
          name: input.name,
          label: input.label,
          type: input.type === 'boolean' ? 'slider' : input.type,
          defaultValue: typeof input.defaultValue === 'number' ? input.defaultValue : 0,
          min: input.min,
          max: input.max,
          step: input.step,
          unit: input.unit,
        })) || [],
        outputs: step.simulator_spec.outputs?.map(output => ({
          id: output.id,
          name: output.name,
          label: output.label,
          type: output.type === 'chart' || output.type === 'animation' ? 'number' : output.type,
          unit: output.unit,
          formula: output.formula,
        })) || [],
        iframeUrl: step.simulator_spec.iframe_url,
        instructions: step.simulator_spec.instructions || [],
        scenario: step.simulator_spec.scenario,
        sdl: step.simulator_spec.sdl,
      } : undefined;
      break;

    case 'ai_tutor':
      baseConfig.aiTutorConfig = step.ai_spec ? {
        openingMessage: step.ai_spec.opening_message,
        conversationGoals: step.ai_spec.conversation_goals?.map(g => g.goal) || [],
        maxTurns: step.ai_spec.max_turns,
      } : undefined;
      break;

    case 'assessment':
    case 'quick_check':
      baseConfig.quizConfig = step.assessment_spec ? {
        questions: step.assessment_spec.questions?.map((q, idx) => ({
          id: `q-${idx}`,
          question: q.question,
          options: q.options || [],
          correctIndex: q.correct && q.options ? q.options.indexOf(q.correct) : 0,
          explanation: q.explanation,
        })) || [],
        passingScore: step.assessment_spec.pass_required ? 70 : 0,
        showExplanation: true,
      } : undefined;
      break;
  }

  // Handle diagram if present
  if (step.diagram_spec) {
    baseConfig.diagramConfig = {
      type: step.diagram_spec.type === 'flowchart' ? 'flowchart' : 'static',
      data: {
        description: step.diagram_spec.description,
        annotations: step.diagram_spec.annotations,
        designNotes: step.diagram_spec.design_notes,
      },
      title: step.diagram_spec.diagram_id,
    };
  }

  return baseConfig;
}

interface EditorActions {
  // Course operations
  loadCourse: (courseId: string, data: { title: string; coverImage?: string; difficulty?: CourseDifficulty; tags?: string[]; chapters: EditorChapter[]; aiGuidance: AIGuidanceConfig }) => void;
  loadFromPackage: (pkg: CoursePackageV2) => void;
  setCourseTitle: (title: string) => void;
  setCourseCoverImage: (coverImage: string | null) => void;
  setCourseDifficulty: (difficulty: CourseDifficulty) => void;
  setCourseTags: (tags: string[]) => void;
  addCourseTag: (tag: string) => void;
  removeCourseTag: (tag: string) => void;
  setIsSaving: (isSaving: boolean) => void;
  setIsLoading: (isLoading: boolean) => void;
  markDirty: () => void;
  markClean: () => void;

  // Chapter operations
  addChapter: (title?: string) => void;
  updateChapter: (id: string, updates: Partial<EditorChapter>) => void;
  deleteChapter: (id: string) => void;
  reorderChapters: (fromIndex: number, toIndex: number) => void;
  toggleChapterExpanded: (id: string) => void;

  // Section operations
  addSection: (chapterId: string, title?: string, type?: ComponentType) => void;
  updateSection: (id: string, updates: Partial<EditorSection>) => void;
  updateSectionConfig: (id: string, config: Partial<NodeConfig>) => void;
  deleteSection: (id: string) => void;
  reorderSections: (chapterId: string, fromIndex: number, toIndex: number) => void;

  // Selection operations
  selectChapter: (id: string | null) => void;
  selectSection: (id: string | null) => void;

  // AI Guidance operations
  setAIProvider: (provider: AIProvider) => void;
  setAIApiKey: (apiKey: string) => void;
  updatePersona: (persona: string) => void;
  setMaxTurns: (maxTurns: number) => void;
  setTemperature: (temperature: number) => void;
  updateAIGuidance: (updates: Partial<AIGuidanceConfig>) => void;
  addTrigger: (trigger?: Partial<AITrigger>) => void;
  updateTrigger: (id: string, updates: Partial<AITrigger>) => void;
  deleteTrigger: (id: string) => void;

  // Reset
  reset: () => void;
}

type EditorStore = EditorState & EditorActions;

const initialState: EditorState = {
  courseId: null,
  courseTitle: '',
  courseCoverImage: null,
  courseDifficulty: 'intermediate',
  courseTags: [],
  chapters: [],
  selectedChapterId: null,
  selectedSectionId: null,
  aiGuidance: { ...DEFAULT_AI_GUIDANCE },
  isDirty: false,
  isSaving: false,
  isLoading: false,
};

export const useEditorStore = create<EditorStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      // Course operations
      loadCourse: (courseId, data) =>
        set({
          courseId,
          courseTitle: data.title,
          courseCoverImage: data.coverImage || null,
          courseDifficulty: data.difficulty || 'intermediate',
          courseTags: (Array.isArray(data.tags) ? data.tags : (() => { try { const t = typeof data.tags === 'string' ? JSON.parse(data.tags) : []; return Array.isArray(t) ? t : []; } catch { return []; } })()).sort(),
          chapters: data.chapters,
          aiGuidance: data.aiGuidance,
          selectedChapterId: null,
          selectedSectionId: null,
          isDirty: false,
          isLoading: false,
        }),

      loadFromPackage: (pkg) => {
        // 将 CoursePackageV2 转换为编辑器格式
        const chapters: EditorChapter[] = pkg.lessons.map((lesson, lessonIndex) => {
          const sections: EditorSection[] = lesson.script.map((step, stepIndex) => {
            // 将 TeachingFormType 映射到 ComponentType
            const componentType = mapStepTypeToComponentType(step.type);
            const config = convertStepToNodeConfig(step);

            return {
              id: step.step_id || `section-${Date.now()}-${stepIndex}`,
              chapterId: lesson.lesson_id,
              title: step.title || `步骤 ${stepIndex + 1}`,
              order: stepIndex,
              componentType,
              config,
            };
          });

          return {
            id: lesson.lesson_id,
            title: lesson.title,
            order: lessonIndex,
            sections,
            expanded: lessonIndex === 0,
          };
        });

        const aiGuidance: AIGuidanceConfig = {
          ...DEFAULT_AI_GUIDANCE,
          persona: pkg.global_ai_config?.tutor_persona || DEFAULT_AI_GUIDANCE.persona,
        };

        // 解析难度等级
        const difficulty = (pkg.meta as { difficulty?: string })?.difficulty as CourseDifficulty || 'intermediate';
        // 解析标签
        const rawTags = (pkg.meta as { tags?: string[] | string })?.tags;
        const tags = (Array.isArray(rawTags) ? rawTags : (() => { try { const t = typeof rawTags === 'string' ? JSON.parse(rawTags) : []; return Array.isArray(t) ? t : []; } catch { return []; } })()).sort();

        set({
          courseId: `new-${Date.now()}`,
          courseTitle: pkg.meta.title,
          courseCoverImage: pkg.meta.cover_url || null,
          courseDifficulty: difficulty,
          courseTags: tags,
          chapters,
          aiGuidance,
          selectedChapterId: chapters[0]?.id || null,
          selectedSectionId: chapters[0]?.sections[0]?.id || null,
          isDirty: true,
          isLoading: false,
        });
      },

      setCourseTitle: (title) =>
        set({ courseTitle: title, isDirty: true }),

      setCourseCoverImage: (coverImage) =>
        set({ courseCoverImage: coverImage, isDirty: true }),

      setCourseDifficulty: (difficulty) =>
        set({ courseDifficulty: difficulty, isDirty: true }),

      setCourseTags: (tags) =>
        set({ courseTags: tags.slice(0, 3).sort(), isDirty: true }),

      addCourseTag: (tag) => {
        const { courseTags } = get();
        const trimmedTag = tag.trim();
        if (trimmedTag && courseTags.length < 3 && !courseTags.includes(trimmedTag)) {
          set({ courseTags: [...courseTags, trimmedTag].sort(), isDirty: true });
        }
      },

      removeCourseTag: (tag) => {
        const { courseTags } = get();
        set({ courseTags: courseTags.filter(t => t !== tag), isDirty: true });
      },

      setIsSaving: (isSaving) => set({ isSaving }),

      setIsLoading: (isLoading) => set({ isLoading }),

      markDirty: () => set({ isDirty: true }),

      markClean: () => set({ isDirty: false }),

      // Chapter operations
      addChapter: (title) => {
        const { chapters } = get();
        const newChapter = createDefaultChapter(chapters.length);
        if (title) {
          newChapter.title = title;
        }
        set({
          chapters: [...chapters, newChapter],
          selectedChapterId: newChapter.id,
          selectedSectionId: null,
          isDirty: true,
        });
      },

      updateChapter: (id, updates) =>
        set((state) => ({
          chapters: state.chapters.map((ch) =>
            ch.id === id ? { ...ch, ...updates } : ch
          ),
          isDirty: true,
        })),

      deleteChapter: (id) =>
        set((state) => {
          const newChapters = state.chapters
            .filter((ch) => ch.id !== id)
            .map((ch, index) => ({ ...ch, order: index }));
          return {
            chapters: newChapters,
            selectedChapterId:
              state.selectedChapterId === id ? null : state.selectedChapterId,
            selectedSectionId:
              state.chapters.find((ch) => ch.id === id)?.sections.some(
                (s) => s.id === state.selectedSectionId
              )
                ? null
                : state.selectedSectionId,
            isDirty: true,
          };
        }),

      reorderChapters: (fromIndex, toIndex) =>
        set((state) => {
          const newChapters = [...state.chapters];
          const [removed] = newChapters.splice(fromIndex, 1);
          newChapters.splice(toIndex, 0, removed);
          return {
            chapters: newChapters.map((ch, index) => ({ ...ch, order: index })),
            isDirty: true,
          };
        }),

      toggleChapterExpanded: (id) =>
        set((state) => ({
          chapters: state.chapters.map((ch) =>
            ch.id === id ? { ...ch, expanded: !ch.expanded } : ch
          ),
        })),

      // Section operations
      addSection: (chapterId, title, type) => {
        const { chapters } = get();
        const chapter = chapters.find((ch) => ch.id === chapterId);
        if (!chapter) return;

        const newSection = createDefaultSection(chapterId, chapter.sections.length);
        if (title) {
          newSection.title = title;
        }
        if (type) {
          newSection.componentType = type;
          newSection.config = { ...DEFAULT_NODE_CONFIG, type };
        }

        set((state) => ({
          chapters: state.chapters.map((ch) =>
            ch.id === chapterId
              ? { ...ch, sections: [...ch.sections, newSection], expanded: true }
              : ch
          ),
          selectedSectionId: newSection.id,
          isDirty: true,
        }));
      },

      updateSection: (id, updates) =>
        set((state) => ({
          chapters: state.chapters.map((ch) => ({
            ...ch,
            sections: ch.sections.map((s) =>
              s.id === id ? { ...s, ...updates } : s
            ),
          })),
          isDirty: true,
        })),

      updateSectionConfig: (id, configUpdates) =>
        set((state) => ({
          chapters: state.chapters.map((ch) => ({
            ...ch,
            sections: ch.sections.map((s) =>
              s.id === id
                ? { ...s, config: { ...s.config, ...configUpdates } }
                : s
            ),
          })),
          isDirty: true,
        })),

      deleteSection: (id) =>
        set((state) => ({
          chapters: state.chapters.map((ch) => ({
            ...ch,
            sections: ch.sections
              .filter((s) => s.id !== id)
              .map((s, index) => ({ ...s, order: index })),
          })),
          selectedSectionId:
            state.selectedSectionId === id ? null : state.selectedSectionId,
          isDirty: true,
        })),

      reorderSections: (chapterId, fromIndex, toIndex) =>
        set((state) => ({
          chapters: state.chapters.map((ch) => {
            if (ch.id !== chapterId) return ch;
            const newSections = [...ch.sections];
            const [removed] = newSections.splice(fromIndex, 1);
            newSections.splice(toIndex, 0, removed);
            return {
              ...ch,
              sections: newSections.map((s, index) => ({ ...s, order: index })),
            };
          }),
          isDirty: true,
        })),

      // Selection operations
      selectChapter: (id) =>
        set({ selectedChapterId: id, selectedSectionId: null }),

      selectSection: (id) => {
        const { chapters } = get();
        let chapterId: string | null = null;
        for (const ch of chapters) {
          if (ch.sections.some((s) => s.id === id)) {
            chapterId = ch.id;
            break;
          }
        }
        set({ selectedSectionId: id, selectedChapterId: chapterId });
      },

      // AI Guidance operations
      setAIProvider: (provider) =>
        set((state) => ({
          aiGuidance: { ...state.aiGuidance, provider },
          isDirty: true,
        })),

      setAIApiKey: (apiKey) =>
        set((state) => ({
          aiGuidance: { ...state.aiGuidance, apiKey },
          isDirty: true,
        })),

      updatePersona: (persona) =>
        set((state) => ({
          aiGuidance: { ...state.aiGuidance, persona },
          isDirty: true,
        })),

      setMaxTurns: (maxTurns) =>
        set((state) => ({
          aiGuidance: { ...state.aiGuidance, maxTurns },
          isDirty: true,
        })),

      setTemperature: (temperature) =>
        set((state) => ({
          aiGuidance: { ...state.aiGuidance, temperature },
          isDirty: true,
        })),

      updateAIGuidance: (updates) =>
        set((state) => ({
          aiGuidance: { ...state.aiGuidance, ...updates },
          isDirty: true,
        })),

      addTrigger: (trigger) => {
        const newTrigger = { ...createDefaultTrigger(), ...trigger };
        set((state) => ({
          aiGuidance: {
            ...state.aiGuidance,
            triggers: [...state.aiGuidance.triggers, newTrigger],
          },
          isDirty: true,
        }));
      },

      updateTrigger: (id, updates) =>
        set((state) => ({
          aiGuidance: {
            ...state.aiGuidance,
            triggers: state.aiGuidance.triggers.map((t) =>
              t.id === id ? { ...t, ...updates } : t
            ),
          },
          isDirty: true,
        })),

      deleteTrigger: (id) =>
        set((state) => ({
          aiGuidance: {
            ...state.aiGuidance,
            triggers: state.aiGuidance.triggers.filter((t) => t.id !== id),
          },
          isDirty: true,
        })),

      // Reset
      reset: () => set({ ...initialState }),
    }),
    {
      name: 'hercu-editor',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        courseId: state.courseId,
        courseTitle: state.courseTitle,
        courseCoverImage: state.courseCoverImage,
        chapters: state.chapters,
        aiGuidance: state.aiGuidance,
        selectedChapterId: state.selectedChapterId,
        selectedSectionId: state.selectedSectionId,
      }),
    }
  )
);

// ============================================
// Selectors
// ============================================

export const selectCourseId = (state: EditorStore) => state.courseId;
export const selectCourseTitle = (state: EditorStore) => state.courseTitle;
export const selectCourseCoverImage = (state: EditorStore) => state.courseCoverImage;
export const selectChapters = (state: EditorStore) => state.chapters;
export const selectSelectedChapterId = (state: EditorStore) => state.selectedChapterId;
export const selectSelectedSectionId = (state: EditorStore) => state.selectedSectionId;
export const selectAIGuidance = (state: EditorStore) => state.aiGuidance;
export const selectIsDirty = (state: EditorStore) => state.isDirty;
export const selectIsSaving = (state: EditorStore) => state.isSaving;
export const selectIsLoading = (state: EditorStore) => state.isLoading;

// ============================================
// Derived Selectors
// ============================================

export const getSelectedChapter = (state: EditorStore): EditorChapter | null => {
  if (!state.selectedChapterId) return null;
  return state.chapters.find((ch) => ch.id === state.selectedChapterId) || null;
};

export const getSelectedSection = (state: EditorStore): EditorSection | null => {
  if (!state.selectedSectionId) return null;
  for (const ch of state.chapters) {
    const section = ch.sections.find((s) => s.id === state.selectedSectionId);
    if (section) return section;
  }
  return null;
};

export const getTotalSections = (state: EditorStore): number => {
  return state.chapters.reduce((sum, ch) => sum + ch.sections.length, 0);
};

export const getChapterById = (state: EditorStore, id: string): EditorChapter | null => {
  return state.chapters.find((ch) => ch.id === id) || null;
};

export const getSectionById = (state: EditorStore, id: string): EditorSection | null => {
  for (const ch of state.chapters) {
    const section = ch.sections.find((s) => s.id === id);
    if (section) return section;
  }
  return null;
};
