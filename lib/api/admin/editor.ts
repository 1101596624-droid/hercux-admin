/**
 * Editor API - 课程编辑器 API
 */

import { apiClient } from './client';
import type {
  EditorCourseData,
  SaveCourseRequest,
  SaveCourseResponse,
  PublishCourseResponse,
  EditorChapter,
  AIGuidanceConfig,
} from '@/types/editor';
import { DEFAULT_AI_GUIDANCE } from '@/types/editor';

// ============================================
// Course Editor API
// ============================================

export const editorAPI = {
  /**
   * 获取课程编辑数据
   */
  async getCourse(courseId: string): Promise<EditorCourseData> {
    const { data } = await apiClient.get<EditorCourseData>(`/admin/editor/courses/${courseId}`);
    return data;
  },

  /**
   * 保存课程
   */
  async saveCourse(courseId: string, request: SaveCourseRequest): Promise<SaveCourseResponse> {
    const { data } = await apiClient.put<SaveCourseResponse>(
      `/admin/editor/courses/${courseId}`,
      request
    );
    return data;
  },

  /**
   * 创建新课程
   */
  async createCourse(request: SaveCourseRequest): Promise<{ courseId: string }> {
    const { data } = await apiClient.post<{ courseId: string }>(
      '/admin/editor/courses',
      request
    );
    return data;
  },

  /**
   * 发布课程
   */
  async publishCourse(courseId: string): Promise<PublishCourseResponse> {
    const { data } = await apiClient.post<PublishCourseResponse>(
      `/admin/editor/courses/${courseId}/publish`
    );
    return data;
  },

  /**
   * 获取课程预览数据
   */
  async getPreview(courseId: string): Promise<{ previewUrl: string }> {
    const { data } = await apiClient.get<{ previewUrl: string }>(
      `/admin/editor/courses/${courseId}/preview`
    );
    return data;
  },

  /**
   * 验证课程配置
   */
  async validateCourse(courseId: string): Promise<{ valid: boolean; errors: string[] }> {
    const { data } = await apiClient.post<{ valid: boolean; errors: string[] }>(
      `/admin/editor/courses/${courseId}/validate`
    );
    return data;
  },

  /**
   * 复制课程
   */
  async duplicateCourse(courseId: string): Promise<{ newCourseId: string }> {
    const { data } = await apiClient.post<{ newCourseId: string }>(
      `/admin/editor/courses/${courseId}/duplicate`
    );
    return data;
  },
};

// ============================================
// Real API that fetches from admin/courses
// ============================================

export const realEditorAPI = {
  async getCourse(courseId: string): Promise<EditorCourseData> {
    // 获取课程详情
    const { data: courseDetail } = await apiClient.get(`/admin/courses/${courseId}`);

    // 获取课程节点
    const { data: nodesData } = await apiClient.get(`/admin/courses/${courseId}/nodes`);

    // 将节点数据转换为编辑器格式
    const chapters: EditorChapter[] = [];

    // 按节点创建章节（每个 lesson 节点作为一个章节）
    if (nodesData.nodes && nodesData.nodes.length > 0) {
      nodesData.nodes.forEach((node: any, index: number) => {
        // 解析节点内容（数据库已统一为jsonb类型，不再需要双重解析）
        let content = {};
        try {
          if (typeof node.content === 'string') {
            content = JSON.parse(node.content);
          } else if (node.content) {
            content = node.content;
          }
        } catch (e) {
          console.error('Failed to parse node content:', e);
        }

        // 解析节点配置（数据库已统一为jsonb类型，不再需要双重解析）
        let config = {};
        try {
          if (typeof node.config === 'string') {
            config = JSON.parse(node.config);
          } else if (node.config) {
            config = node.config;
          }
        } catch (e) {
          console.error('Failed to parse node config:', e);
        }

        const chapter: EditorChapter = {
          id: `chapter-${node.id}`,
          title: node.title || `第${index + 1}课`,
          order: node.sequence || index,
          expanded: index === 0,
          sections: [],
        };

        // 如果有 steps，将每个 step 作为一个 section
        const steps = (content as any).steps || [];
        steps.forEach((step: any, stepIndex: number) => {
          const sectionConfig: any = {
            type: step.type || 'text_content',
          };

          // 根据 step 类型设置对应的配置
          if (step.content) {
            sectionConfig.textConfig = {
              content: step.content.body || '',
              format: 'markdown',
              keyPoints: step.content.key_points || [],
            };
          }

          // 转换 diagram_spec 到 illustratedConfig
          if (step.diagram_spec) {
            sectionConfig.illustratedConfig = {
              imageUrl: step.diagram_spec.image_url || '',
              imageAlt: step.diagram_spec.description || '',
              layout: 'text_left_image_right',
            };
          }

          if (step.simulator_spec) {
            sectionConfig.simulatorConfig = {
              id: step.step_id || `sim-${stepIndex}`,
              // 如果有 custom_code 则使用 custom 模式，如果有 sdl 则使用 interactive 类型
              type: step.simulator_spec.mode === 'custom' ? 'custom' :
                    step.simulator_spec.sdl ? 'interactive' : (step.simulator_spec.type || 'preset'),
              mode: step.simulator_spec.mode,
              custom_code: step.simulator_spec.custom_code,
              variables: step.simulator_spec.variables,
              name: step.simulator_spec.name || step.title || '',
              description: step.simulator_spec.description || step.simulator_spec.scenario?.description || '',
              thumbnail: '',
              parameters: step.simulator_spec.parameters || [],
              inputs: step.simulator_spec.inputs || [],
              outputs: step.simulator_spec.outputs || [],
              initialState: step.simulator_spec.initialState || {},
              scenario: step.simulator_spec.scenario,
              interfaceSpec: step.simulator_spec.interface_spec,
              evaluationLogic: step.simulator_spec.evaluation_logic,
              pixi_config: step.simulator_spec.pixi_config,
              sdl: step.simulator_spec.sdl,
              instructions: step.simulator_spec.instructions || [],
              presetId: step.simulator_spec.preset_id,
            };
          }

          if (step.video_spec) {
            sectionConfig.videoConfig = {
              videoUrl: step.video_spec.video_url || '',
              duration: step.video_spec.duration ? parseInt(step.video_spec.duration) : undefined,
            };
          }

          if (step.assessment_spec) {
            sectionConfig.quizConfig = {
              questions: (step.assessment_spec.questions || []).map((q: any, idx: number) => ({
                id: `q-${idx}`,
                question: q.question,
                options: q.options || [],
                correctIndex: q.options?.indexOf(q.correct) ?? 0,
                explanation: q.explanation,
              })),
              passingScore: 60,
              showExplanation: true,
            };
          }

          if (step.ai_spec) {
            sectionConfig.aiTutorConfig = {
              openingMessage: step.ai_spec.opening_message,
              conversationGoals: step.ai_spec.conversation_goals?.map((g: any) => g.goal) || [],
              maxTurns: step.ai_spec.max_turns,
            };
          }

          chapter.sections.push({
            id: `section-${node.id}-${stepIndex}`,
            chapterId: chapter.id,
            title: step.title || `步骤 ${stepIndex + 1}`,
            order: stepIndex,
            componentType: step.type || 'text_content',
            config: sectionConfig,
          });
        });

        // 如果没有 steps，创建一个默认 section
        if (chapter.sections.length === 0) {
          chapter.sections.push({
            id: `section-${node.id}-0`,
            chapterId: chapter.id,
            title: node.title || '内容',
            order: 0,
            componentType: 'text_content',
            config: {
              type: 'text_content',
              textConfig: {
                content: node.description || '',
                format: 'markdown',
                keyPoints: [],
              },
            },
          });
        }

        chapters.push(chapter);
      });
    }

    return {
      id: courseId,
      title: courseDetail.name || '未命名课程',
      description: courseDetail.description || '',
      difficulty: courseDetail.difficulty || 'intermediate',
      tags: courseDetail.tags || [],
      coverImage: courseDetail.thumbnail_url || '',
      chapters,
      aiGuidance: DEFAULT_AI_GUIDANCE,
      createdAt: courseDetail.created_at,
      updatedAt: courseDetail.updated_at || courseDetail.created_at,
    };
  },

  async saveCourse(courseId: string, request: SaveCourseRequest): Promise<SaveCourseResponse> {
    // 更新课程基本信息
    await apiClient.put(`/admin/courses/${courseId}`, {
      name: request.title,
      difficulty: request.difficulty || 'intermediate',
      tags: request.tags || [],
      thumbnail_url: request.coverImage || null,
    });

    // 获取现有节点
    const { data: existingNodesData } = await apiClient.get(`/admin/courses/${courseId}/nodes`);
    const existingNodes = existingNodesData.nodes || [];

    // 更新每个章节对应的节点
    if (request.chapters && request.chapters.length > 0) {
      for (let i = 0; i < request.chapters.length; i++) {
        const chapter = request.chapters[i];

        // 将章节的 sections 转换为 steps 格式
        const steps = chapter.sections.map((section, stepIndex) => {
          const step: any = {
            step_id: section.id,
            type: section.componentType || 'text_content',
            title: section.title,
          };

          // 根据组件类型添加对应的配置
          if (section.config) {
            if (section.config.textConfig) {
              step.content = {
                body: section.config.textConfig.content || '',
                key_points: section.config.textConfig.keyPoints || [],
              };
            }
            if (section.config.illustratedConfig) {
              step.diagram_spec = {
                type: 'static',
                image_url: section.config.illustratedConfig.imageUrl || '',
                description: section.config.illustratedConfig.imageAlt || '',
                image_generated: true,
              };
            }
            if (section.config.videoConfig) {
              step.video_spec = section.config.videoConfig;
            }
            if (section.config.quizConfig) {
              step.assessment_spec = {
                type: 'multiple_choice',
                questions: section.config.quizConfig.questions || [],
                pass_required: false,
              };
            }
            if (section.config.simulatorConfig) {
              step.simulator_spec = section.config.simulatorConfig;
            }
            if (section.config.aiTutorConfig) {
              step.ai_spec = section.config.aiTutorConfig;
            }
          }

          return step;
        });

        // 构建节点内容
        const nodeContent = {
          version: '2.0',
          lesson_id: chapter.id,
          title: chapter.title,
          rationale: '',
          estimated_minutes: 30,
          learning_objectives: [],
          complexity_level: 'standard',
          steps: steps,
        };

        // 查找对应的现有节点
        const existingNode = existingNodes.find((n: any) =>
          n.node_id === `${courseId}_${chapter.id}` ||
          n.component_id === chapter.id ||
          n.sequence === i + 1
        );

        if (existingNode) {
          // 更新现有节点
          await apiClient.put(`/admin/courses/${courseId}/nodes/${existingNode.id}`, {
            title: chapter.title,
            content: nodeContent,
            sequence: i + 1,
          });
        } else {
          // 创建新节点
          await apiClient.post(`/admin/courses/${courseId}/nodes`, {
            node_id: `${courseId}_${chapter.id}`,
            type: 'lesson',
            component_id: chapter.id,
            title: chapter.title,
            description: '',
            sequence: i + 1,
            content: nodeContent,
            config: {
              estimated_minutes: 30,
              learning_objectives: [],
              complexity_level: 'standard',
            },
            timeline_config: {
              estimated_minutes: 30,
            },
            unlock_condition: i === 0 ? { strategy: 'none' } : { strategy: 'previous_complete' },
          });
        }
      }
    }

    return {
      success: true,
      courseId,
      updatedAt: new Date().toISOString(),
    };
  },

  async createCourse(request: SaveCourseRequest): Promise<{ courseId: string }> {
    // 1. 创建课程记录
    const { data: courseData } = await apiClient.post('/admin/courses', {
      name: request.title,
      description: '',
      difficulty: request.difficulty || 'intermediate',
      tags: request.tags || [],
      thumbnail_url: request.coverImage || null,
    });

    const courseId = courseData.id;

    // 2. 为每个章节创建节点
    if (request.chapters && request.chapters.length > 0) {
      for (let i = 0; i < request.chapters.length; i++) {
        const chapter = request.chapters[i];

        // 将章节的 sections 转换为 steps 格式
        const steps = chapter.sections.map((section, stepIndex) => {
          const step: any = {
            step_id: section.id,
            type: section.componentType || 'text_content',
            title: section.title,
          };

          // 根据组件类型添加对应的配置
          if (section.config) {
            if (section.config.textConfig) {
              step.content = {
                body: section.config.textConfig.content || '',
                key_points: section.config.textConfig.keyPoints || [],
              };
            }
            if (section.config.illustratedConfig) {
              // 转换 illustratedConfig 到 diagram_spec
              step.diagram_spec = {
                type: 'static',
                image_url: section.config.illustratedConfig.imageUrl || '',
                description: section.config.illustratedConfig.imageAlt || '',
                image_generated: true,
              };
            }
            if (section.config.videoConfig) {
              step.video_spec = section.config.videoConfig;
            }
            if (section.config.quizConfig) {
              step.assessment_spec = {
                type: 'multiple_choice',
                questions: section.config.quizConfig.questions || [],
                pass_required: false,
              };
            }
            if (section.config.simulatorConfig) {
              step.simulator_spec = section.config.simulatorConfig;
            }
            if (section.config.aiTutorConfig) {
              step.ai_spec = section.config.aiTutorConfig;
            }
          }

          return step;
        });

        // 构建节点内容
        const nodeContent = {
          version: '2.0',
          lesson_id: chapter.id,
          title: chapter.title,
          rationale: '',
          estimated_minutes: 30,
          learning_objectives: [],
          complexity_level: 'standard',
          steps: steps,
        };

        // 创建节点（包含 content）
        await apiClient.post(`/admin/courses/${courseId}/nodes`, {
          node_id: `${courseId}_${chapter.id}`,
          type: 'lesson',
          component_id: chapter.id,
          title: chapter.title,
          description: '',
          sequence: i + 1,
          content: nodeContent,
          config: {
            estimated_minutes: 30,
            learning_objectives: [],
            complexity_level: 'standard',
          },
          timeline_config: {
            estimated_minutes: 30,
          },
          unlock_condition: i === 0 ? { strategy: 'none' } : { strategy: 'previous_complete' },
        });
      }
    }

    return {
      courseId: courseId.toString(),
    };
  },

  async publishCourse(courseId: string): Promise<PublishCourseResponse> {
    await apiClient.post(`/admin/courses/${courseId}/publish`, null, {
      params: { publish: true }
    });

    return {
      success: true,
      publishedAt: new Date().toISOString(),
      publishedVersion: '1.0.0',
    };
  },

  async validateCourse(courseId: string): Promise<{ valid: boolean; errors: string[] }> {
    return { valid: true, errors: [] };
  },

  async duplicateCourse(courseId: string): Promise<{ newCourseId: string }> {
    return { newCourseId: `course-${Date.now()}` };
  },
};

// ============================================
// Mock Data (for development fallback)
// ============================================

const MOCK_DELAY = 500;

const mockCourseData: EditorCourseData = {
  id: 'course-1',
  title: '示例课程',
  chapters: [
    {
      id: 'chapter-1',
      title: '第一章：入门',
      order: 0,
      expanded: true,
      sections: [
        {
          id: 'section-1-1',
          chapterId: 'chapter-1',
          title: '1.1 课程介绍',
          order: 0,
          componentType: 'video',
          config: {
            type: 'video',
            videoConfig: {
              videoUrl: 'https://example.com/video1.mp4',
              duration: 300,
            },
          },
        },
        {
          id: 'section-1-2',
          chapterId: 'chapter-1',
          title: '1.2 基础概念',
          order: 1,
          componentType: 'text_content',
          config: {
            type: 'text_content',
            textConfig: {
              content: '# 基础概念\n\n这是课程的基础概念介绍...',
              format: 'markdown',
              keyPoints: ['概念1', '概念2', '概念3'],
            },
          },
        },
      ],
    },
    {
      id: 'chapter-2',
      title: '第二章：进阶',
      order: 1,
      expanded: false,
      sections: [
        {
          id: 'section-2-1',
          chapterId: 'chapter-2',
          title: '2.1 模拟练习',
          order: 0,
          componentType: 'simulator',
          config: {
            type: 'simulator',
          },
        },
        {
          id: 'section-2-2',
          chapterId: 'chapter-2',
          title: '2.2 测验',
          order: 1,
          componentType: 'assessment',
          config: {
            type: 'assessment',
            quizConfig: {
              questions: [
                {
                  id: 'q1',
                  question: '以下哪个是正确的？',
                  options: ['选项A', '选项B', '选项C', '选项D'],
                  correctIndex: 0,
                  explanation: '选项A是正确的，因为...',
                },
              ],
              passingScore: 60,
              showExplanation: true,
            },
          },
        },
      ],
    },
  ],
  aiGuidance: {
    ...DEFAULT_AI_GUIDANCE,
    persona: '你是一位专业的课程导师，帮助学生理解和掌握课程内容。',
    triggers: [
      {
        id: 'trigger-1',
        name: '进入节点时问候',
        condition: { type: 'on_enter' },
        prompt: '欢迎来到这个章节！有什么我可以帮助你的吗？',
        enabled: true,
      },
    ],
  },
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-15T12:00:00Z',
};

/**
 * Mock API for development
 */
export const mockEditorAPI = {
  async getCourse(courseId: string): Promise<EditorCourseData> {
    await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
    return { ...mockCourseData, id: courseId };
  },

  async saveCourse(courseId: string, request: SaveCourseRequest): Promise<SaveCourseResponse> {
    await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
    console.log('Mock save course:', courseId, request);
    return {
      success: true,
      courseId,
      updatedAt: new Date().toISOString(),
    };
  },

  async createCourse(request: SaveCourseRequest): Promise<{ courseId: string }> {
    await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
    console.log('Mock create course:', request);
    return {
      courseId: `course-${Date.now()}`,
    };
  },

  async publishCourse(courseId: string): Promise<PublishCourseResponse> {
    await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
    console.log('Mock publish course:', courseId);
    return {
      success: true,
      publishedAt: new Date().toISOString(),
      publishedVersion: '1.0.0',
    };
  },

  async validateCourse(courseId: string): Promise<{ valid: boolean; errors: string[] }> {
    await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
    return { valid: true, errors: [] };
  },

  async duplicateCourse(courseId: string): Promise<{ newCourseId: string }> {
    await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
    return { newCourseId: `course-${Date.now()}` };
  },
};

// Use real API to fetch course data from backend
export const courseEditorAPI = realEditorAPI;
