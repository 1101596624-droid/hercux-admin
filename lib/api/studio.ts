/**
 * Studio API - 课程生成工具 API 服务
 */

import type {
  Processor,
  ProcessorWithConfig,
  ProcessorConfigUpdate,
  CreateProcessorRequest,
  PackageListItem,
  CoursePackageV2,
  GenerateRequestV2,
  V2StreamCallbacks,
  UploadResponse,
} from '@/types/studio';
import { apiClient } from './admin/client';

// Studio API 使用独立的 base URL
const STUDIO_API_BASE_URL = process.env.NEXT_PUBLIC_STUDIO_API_URL || 'http://localhost:8001';

/**
 * Studio API Client
 */
class StudioApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    config: RequestInit & { params?: Record<string, string | number | boolean> } = {}
  ): Promise<T> {
    const { params, ...fetchConfig } = config;

    let url = `${this.baseURL}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        searchParams.append(key, String(value));
      });
      url += `?${searchParams.toString()}`;
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(fetchConfig.headers as Record<string, string>),
    };

    const response = await fetch(url, {
      ...fetchConfig,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: response.statusText,
      }));
      throw new Error(error.detail || error.message || `HTTP Error: ${response.status}`);
    }

    return response.json();
  }

  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET', params });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  async postFormData<T>(endpoint: string, formData: FormData): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: response.statusText,
      }));
      throw new Error(error.detail || error.message || `HTTP Error: ${response.status}`);
    }

    return response.json();
  }

  getBaseURL(): string {
    return this.baseURL;
  }
}

// Studio API 客户端实例
export const studioApiClient = new StudioApiClient(STUDIO_API_BASE_URL);

// ============================================
// Packages API
// ============================================

export const studioPackagesApi = {
  /**
   * 获取课程包列表
   */
  list: async (status?: string, limit: number = 50): Promise<{ packages: PackageListItem[]; total: number }> => {
    const params: Record<string, any> = { limit };
    if (status) params.status = status;
    return studioApiClient.get('/api/v1/studio/packages', params);
  },

  /**
   * 保存课程包到数据库 (调用主后端 API)
   */
  saveToDatabase: async (pkg: CoursePackageV2): Promise<{ success: boolean; course_id: number; message: string }> => {
    const response = await apiClient.post<{ success: boolean; course_id: number; nodes_created: number; edges_created: number; message: string }>(
      '/internal/import-package',
      { package: pkg }
    );
    return response.data;
  },

  /**
   * 获取单个课程包
   */
  get: async (id: string): Promise<CoursePackageV2> => {
    return studioApiClient.get(`/api/v1/studio/packages/${id}`);
  },

  /**
   * 删除课程包
   */
  delete: async (id: string): Promise<{ success: boolean }> => {
    return studioApiClient.delete(`/api/v1/studio/packages/${id}`);
  },

  /**
   * 导出课程包 JSON
   */
  export: async (id: string): Promise<{ json: string }> => {
    return studioApiClient.get(`/api/v1/studio/packages/${id}/export`);
  },

  /**
   * 发布课程包
   */
  publish: async (id: string): Promise<{ success: boolean }> => {
    return studioApiClient.post(`/api/v1/studio/packages/${id}/publish`);
  },

  /**
   * 归档课程包
   */
  archive: async (id: string): Promise<{ success: boolean }> => {
    return studioApiClient.post(`/api/v1/studio/packages/${id}/archive`);
  },

  /**
   * 复制课程包
   */
  duplicate: async (id: string, newTitle?: string): Promise<{ success: boolean; package: CoursePackageV2 }> => {
    return studioApiClient.post(`/api/v1/studio/packages/${id}/duplicate`, { new_title: newTitle });
  },
};

// ============================================
// V2 Generation API (Lesson-based with Processors)
// ============================================

export const studioGenerateApi = {
  /**
   * V2 流式生成课程 (基于 Lesson 结构)
   */
  generateStream: (data: GenerateRequestV2, callbacks: V2StreamCallbacks): (() => void) => {
    const controller = new AbortController();

    fetch(`${STUDIO_API_BASE_URL}/api/v1/studio/packages/generate-v2`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let receivedComplete = false;

        const processEvent = (eventType: string, dataStr: string) => {
          if (!eventType || !dataStr) {
            console.warn('[SSE] Empty event or data, skipping');
            return;
          }
          try {
            const eventData = JSON.parse(dataStr);

            switch (eventType) {
              case 'phase':
                callbacks.onPhase(eventData.phase, eventData.message, eventData.processor);
                break;
              case 'structure':
                callbacks.onStructure(
                  eventData.meta,
                  eventData.lessons_count,
                  eventData.lessons_outline,
                  eventData.processor
                );
                break;
              case 'lesson_start':
                callbacks.onLessonStart(
                  eventData.index,
                  eventData.total,
                  eventData.title,
                  eventData.recommended_forms,
                  eventData.complexity_level
                );
                break;
              case 'chunk':
                callbacks.onChunk(eventData.content, eventData.phase, eventData.lesson_index);
                break;
              case 'step_complete':
                if (callbacks.onStepComplete) {
                  callbacks.onStepComplete(
                    eventData.lesson_index,
                    eventData.step_index,
                    eventData.step,
                    eventData.total_steps
                  );
                }
                break;
              case 'lesson_complete':
                console.log('[SSE] lesson_complete received:', {
                  index: eventData.index,
                  total: eventData.total,
                  hasLesson: !!eventData.lesson,
                  lessonTitle: eventData.lesson?.title,
                  scriptLength: eventData.lesson?.script?.length,
                  scriptSteps: eventData.lesson?.script?.map((s: any) => s.title)
                });
                callbacks.onLessonComplete(
                  eventData.index,
                  eventData.total,
                  eventData.lesson,
                  eventData.warning
                );
                break;
              case 'complete':
                receivedComplete = true;
                callbacks.onComplete(eventData.package);
                break;
              case 'error':
                callbacks.onError(eventData.message);
                break;
            }
          } catch (e) {
            console.error(`[SSE] Failed to parse ${eventType} event:`, e, 'Data length:', dataStr.length, 'Data preview:', dataStr.substring(0, 500));
          }
        };

        // 改进的 SSE 解析：正确处理多行 data 和事件边界
        const processBuffer = (buf: string): string => {
          // SSE 事件以双换行符分隔
          const events = buf.split('\n\n');
          // 最后一个可能是不完整的事件，保留到下次处理
          const remaining = events.pop() || '';

          for (const eventBlock of events) {
            if (!eventBlock.trim()) continue;

            const lines = eventBlock.split('\n');
            let currentEvent = '';
            let dataLines: string[] = [];

            for (const line of lines) {
              if (line.startsWith('event: ')) {
                currentEvent = line.slice(7).trim();
              } else if (line.startsWith('data: ')) {
                dataLines.push(line.slice(6));
              } else if (line.startsWith('data:')) {
                // 处理 "data:" 后面没有空格的情况
                dataLines.push(line.slice(5));
              }
            }

            // 合并所有 data 行
            if (currentEvent && dataLines.length > 0) {
              const fullData = dataLines.join('');
              processEvent(currentEvent, fullData);
            }
          }

          return remaining;
        };

        while (reader) {
          const { done, value } = await reader.read();

          if (value) {
            buffer += decoder.decode(value, { stream: !done });
            buffer = processBuffer(buffer);
          }

          if (done) {
            // 处理剩余的缓冲区
            if (buffer.trim()) {
              processBuffer(buffer + '\n\n');
            }
            if (!receivedComplete) {
              console.error('[SSE] Stream ended without complete event');
              callbacks.onError('生成流意外中断，请重试');
            }
            break;
          }
        }
      })
      .catch((error) => {
        if (error.name !== 'AbortError') {
          callbacks.onError(error.message || 'V2 流式生成失败');
        }
      });

    return () => controller.abort();
  },

  /**
   * V3 流式生成课程 (监督者+生成者架构)
   * 新架构特点：
   * - 监督者AI生成大纲并审核每个章节
   * - 生成者AI根据指令生成章节
   * - 自动重试不合格的章节（最多3次）
   * - 高质量模拟器标准
   */
  generateStreamV3: (data: GenerateRequestV2, callbacks: V3StreamCallbacks): (() => void) => {
    const controller = new AbortController();

    fetch(`${STUDIO_API_BASE_URL}/api/v1/studio/packages/generate-v3`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let receivedComplete = false;

        const processEvent = (eventType: string, dataStr: string) => {
          if (!eventType || !dataStr) {
            console.warn('[SSE V3] Empty event or data, skipping');
            return;
          }
          try {
            const eventData = JSON.parse(dataStr);

            switch (eventType) {
              case 'phase':
                callbacks.onPhase(eventData.phase, eventData.message, eventData.processor);
                break;
              case 'outline':
                // V3 新事件：大纲生成完成
                callbacks.onOutline(eventData.outline);
                break;
              case 'chapter_start':
                callbacks.onChapterStart(
                  eventData.index,
                  eventData.total,
                  eventData.title,
                  eventData.attempt
                );
                break;
              case 'chunk':
                callbacks.onChunk(eventData.content, eventData.chapter_index, eventData.attempt);
                break;
              case 'chapter_review':
                // V3 新事件：章节审核结果
                callbacks.onChapterReview(
                  eventData.index,
                  eventData.status,
                  eventData.score,
                  eventData.issues,
                  eventData.simulator_issues,
                  eventData.comment
                );
                break;
              case 'chapter_retry':
                // V3 新事件：章节重试
                callbacks.onChapterRetry(
                  eventData.index,
                  eventData.attempt,
                  eventData.reason
                );
                break;
              case 'chapter_complete':
                callbacks.onChapterComplete(
                  eventData.index,
                  eventData.total,
                  eventData.chapter,
                  eventData.attempts
                );
                break;
              case 'complete':
                receivedComplete = true;
                callbacks.onComplete(eventData.package, eventData.stats);
                break;
              case 'error':
                callbacks.onError(eventData.message);
                break;
            }
          } catch (e) {
            console.error(`[SSE V3] Failed to parse ${eventType} event:`, e, 'Data preview:', dataStr.substring(0, 500));
          }
        };

        const processBuffer = (buf: string): string => {
          const events = buf.split('\n\n');
          const remaining = events.pop() || '';

          for (const eventBlock of events) {
            if (!eventBlock.trim()) continue;

            const lines = eventBlock.split('\n');
            let currentEvent = '';
            let dataLines: string[] = [];

            for (const line of lines) {
              if (line.startsWith('event: ')) {
                currentEvent = line.slice(7).trim();
              } else if (line.startsWith('data: ')) {
                dataLines.push(line.slice(6));
              } else if (line.startsWith('data:')) {
                dataLines.push(line.slice(5));
              }
            }

            if (currentEvent && dataLines.length > 0) {
              const fullData = dataLines.join('');
              processEvent(currentEvent, fullData);
            }
          }

          return remaining;
        };

        while (reader) {
          const { done, value } = await reader.read();

          if (value) {
            buffer += decoder.decode(value, { stream: !done });
            buffer = processBuffer(buffer);
          }

          if (done) {
            if (buffer.trim()) {
              processBuffer(buffer + '\n\n');
            }
            if (!receivedComplete) {
              console.error('[SSE V3] Stream ended without complete event');
              callbacks.onError('生成流意外中断，请重试');
            }
            break;
          }
        }
      })
      .catch((error) => {
        if (error.name !== 'AbortError') {
          callbacks.onError(error.message || 'V3 流式生成失败');
        }
      });

    return () => controller.abort();
  },
};

/**
 * V3 流式生成回调接口
 */
export interface V3StreamCallbacks {
  onPhase: (phase: number, message: string, processor?: any) => void;
  onOutline: (outline: V3CourseOutline) => void;
  onChapterStart: (index: number, total: number, title: string, attempt: number) => void;
  onChunk: (content: string, chapterIndex: number, attempt: number) => void;
  onChapterReview: (
    index: number,
    status: 'approved' | 'rejected' | 'needs_revision',
    score: number,
    issues: string[],
    simulatorIssues: string[],
    comment: string
  ) => void;
  onChapterRetry: (index: number, attempt: number, reason: string) => void;
  onChapterComplete: (index: number, total: number, chapter: any, attempts: number) => void;
  onComplete: (pkg: CoursePackageV2, stats: V3GenerationStats) => void;
  onError: (message: string) => void;
}

export interface V3CourseOutline {
  title: string;
  description: string;
  total_chapters: number;
  estimated_hours: number;
  difficulty: string;
  chapters: Array<{
    index: number;
    title: string;
    chapter_type: string;
    suggested_simulator: string | null;
  }>;
}

export interface V3GenerationStats {
  total_chapters: number;
  total_simulators: number;
  generation_time: number;
}

// ============================================
// Processors API (Plugin System)
// ============================================

export const studioProcessorsApi = {
  /**
   * 获取所有处理器列表
   */
  list: async (includeDisabled: boolean = false): Promise<{ processors: ProcessorWithConfig[] }> => {
    return studioApiClient.get('/api/v1/studio/processors', { include_disabled: includeDisabled });
  },

  /**
   * 获取单个处理器信息
   */
  get: async (id: string): Promise<ProcessorWithConfig> => {
    return studioApiClient.get(`/api/v1/studio/processors/${id}`);
  },

  /**
   * 更新处理器配置
   */
  updateConfig: async (id: string, config: ProcessorConfigUpdate): Promise<{ message: string; config: ProcessorConfigUpdate }> => {
    return studioApiClient.put(`/api/v1/studio/processors/${id}/config`, config);
  },

  /**
   * 启用处理器
   */
  enable: async (id: string): Promise<{ message: string }> => {
    return studioApiClient.post(`/api/v1/studio/processors/${id}/enable`);
  },

  /**
   * 禁用处理器
   */
  disable: async (id: string): Promise<{ message: string }> => {
    return studioApiClient.post(`/api/v1/studio/processors/${id}/disable`);
  },

  /**
   * 创建自定义处理器
   */
  create: async (data: CreateProcessorRequest): Promise<{ message: string; processor: ProcessorWithConfig }> => {
    return studioApiClient.post('/api/v1/studio/processors', data);
  },

  /**
   * 更新自定义处理器
   */
  update: async (id: string, data: CreateProcessorRequest): Promise<{ message: string; processor: ProcessorWithConfig }> => {
    return studioApiClient.put(`/api/v1/studio/processors/${id}`, data);
  },

  /**
   * 删除自定义处理器
   */
  delete: async (id: string): Promise<{ message: string }> => {
    return studioApiClient.delete(`/api/v1/studio/processors/${id}`);
  },
};

// ============================================
// Upload API
// ============================================

export const studioUploadApi = {
  /**
   * 上传文件并提取文本
   */
  uploadFile: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    return studioApiClient.postFormData('/api/v1/studio/upload', formData);
  },
};

// ============================================
// Health API
// ============================================

export const studioHealthApi = {
  /**
   * 检查 Studio API 健康状态
   */
  check: async (): Promise<{ status: string; version: string }> => {
    return studioApiClient.get('/api/v1/studio/health');
  },
};

// ============================================
// Error Handling
// ============================================

export const getStudioErrorMessage = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  return '未知错误';
};
