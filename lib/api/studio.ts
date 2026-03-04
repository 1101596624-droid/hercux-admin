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
  UploadResponse,
  UploadFileResponse,
  UploadTaskCreateResponse,
  UploadTaskStatusResponse,
  Lesson,
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

  async get<T>(endpoint: string, params?: Record<string, string | number | boolean>): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET', params });
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
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
    const params: Record<string, string | number | boolean> = { limit };
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
// V3 Generation API (Supervisor-Generator Architecture)
// ============================================

export const studioGenerateApi = {
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
    const CONNECT_MAX_ATTEMPTS = 3;
    const CONNECT_RETRY_BASE_DELAY_MS = 800;
    const STREAM_IDLE_TIMEOUT_MS = 120000;
    const CHUNK_FLUSH_INTERVAL_MS = 80;
    const RETRYABLE_HTTP_STATUS = new Set([408, 429, 500, 502, 503, 504]);

    let stopRequested = false;
    let errorEmitted = false;
    let receivedComplete = false;
    let idleTimer: ReturnType<typeof setTimeout> | null = null;
    let chunkFlushTimer: ReturnType<typeof setTimeout> | null = null;
    let chunkBuffer = '';
    let chunkMeta = { chapterIndex: 0, attempt: 1 };
    let idleTimeoutTriggered = false;

    const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

    const clearIdleTimer = () => {
      if (idleTimer) {
        clearTimeout(idleTimer);
        idleTimer = null;
      }
    };

    const flushChunkBuffer = () => {
      if (!chunkBuffer) return;
      const content = chunkBuffer;
      chunkBuffer = '';
      callbacks.onChunk(content, chunkMeta.chapterIndex, chunkMeta.attempt);
    };

    const clearChunkFlushTimer = () => {
      if (chunkFlushTimer) {
        clearTimeout(chunkFlushTimer);
        chunkFlushTimer = null;
      }
    };

    const scheduleChunkFlush = () => {
      if (chunkFlushTimer) return;
      chunkFlushTimer = setTimeout(() => {
        chunkFlushTimer = null;
        flushChunkBuffer();
      }, CHUNK_FLUSH_INTERVAL_MS);
    };

    const resetIdleTimer = () => {
      clearIdleTimer();
      idleTimer = setTimeout(() => {
        if (stopRequested || receivedComplete) return;
        idleTimeoutTriggered = true;
        controller.abort();
      }, STREAM_IDLE_TIMEOUT_MS);
    };

    const cleanupTimers = () => {
      clearIdleTimer();
      clearChunkFlushTimer();
    };

    const emitErrorOnce = (message: string) => {
      if (stopRequested || receivedComplete || errorEmitted) return;
      errorEmitted = true;
      cleanupTimers();
      callbacks.onError(message);
    };

    const normalizeError = (error: unknown, fallback = 'V3 流式生成失败') => {
      if (error instanceof Error) return error;
      return new Error(typeof error === 'string' ? error : fallback);
    };

    const streamOnce = async () => {
      let attemptReceivedAnyEvent = false;
      let buffer = '';
      const decoder = new TextDecoder();
      idleTimeoutTriggered = false;

      const annotateAndThrow = (err: unknown, statusCode?: number) => {
        const normalized = normalizeError(err);
        const extra = normalized as Error & { statusCode?: number; receivedAnyEvent?: boolean };
        extra.receivedAnyEvent = attemptReceivedAnyEvent;
        if (statusCode !== undefined) {
          extra.statusCode = statusCode;
        }
        throw normalized;
      };

      try {
        const response = await fetch(`${STUDIO_API_BASE_URL}/api/v1/studio/packages/generate-v3`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
          signal: controller.signal,
        });

        if (!response.ok) {
          annotateAndThrow(new Error(`HTTP error! status: ${response.status}`), response.status);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('响应流不可用');
        }

        const processEvent = (eventType: string, dataStr: string) => {
          if (!eventType || !dataStr) return;

          let eventData: Record<string, any>;
          try {
            eventData = JSON.parse(dataStr);
          } catch (e) {
            console.error(
              `[SSE V3] Failed to parse ${eventType} event:`,
              e,
              'Data preview:',
              dataStr.substring(0, 500)
            );
            return;
          }

          attemptReceivedAnyEvent = true;
          resetIdleTimer();

          if (eventType !== 'chunk') {
            flushChunkBuffer();
          }

          switch (eventType) {
            case 'phase':
              callbacks.onPhase(eventData.phase, eventData.message, eventData.processor);
              break;
            case 'outline':
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
              if (typeof eventData.content === 'string' && eventData.content.length > 0) {
                chunkBuffer += eventData.content;
                chunkMeta = {
                  chapterIndex: Number(eventData.chapter_index ?? chunkMeta.chapterIndex),
                  attempt: Number(eventData.attempt ?? chunkMeta.attempt),
                };
                scheduleChunkFlush();
              }
              break;
            case 'chapter_review':
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
              annotateAndThrow(new Error(eventData.message || '生成失败'));
              break;
            case 'simulator_progress':
              callbacks.onSimulatorProgress?.(
                eventData.simulator_name,
                eventData.step_index,
                eventData.round,
                eventData.max_rounds,
                eventData.stage,
                eventData.message
              );
              break;
            default:
              break;
          }
        };

        const processBuffer = (buf: string): string => {
          const events = buf.split('\n\n');
          const remaining = events.pop() || '';

          for (const eventBlock of events) {
            if (!eventBlock.trim()) continue;

            const lines = eventBlock.split('\n');
            let currentEvent = '';
            const dataLines: string[] = [];

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
              processEvent(currentEvent, dataLines.join('\n'));
            }
          }

          return remaining;
        };

        resetIdleTimer();
        while (!stopRequested) {
          const { done, value } = await reader.read();

          if (value) {
            resetIdleTimer();
            buffer += decoder.decode(value, { stream: !done });
            buffer = processBuffer(buffer);
          }

          if (done) {
            if (buffer.trim()) {
              processBuffer(buffer + '\n\n');
            }
            flushChunkBuffer();
            if (!receivedComplete) {
              annotateAndThrow(new Error('STREAM_ENDED_WITHOUT_COMPLETE'));
            }
            break;
          }
        }
      } catch (err) {
        const normalized = normalizeError(err);
        const extra = normalized as Error & { statusCode?: number; receivedAnyEvent?: boolean };
        if (extra.receivedAnyEvent === undefined) {
          extra.receivedAnyEvent = attemptReceivedAnyEvent;
        }
        if (idleTimeoutTriggered) {
          normalized.message = 'STREAM_IDLE_TIMEOUT';
        }
        throw normalized;
      } finally {
        cleanupTimers();
      }
    };

    const runWithRetry = async () => {
      for (let attempt = 1; attempt <= CONNECT_MAX_ATTEMPTS; attempt += 1) {
        try {
          await streamOnce();
          return;
        } catch (err) {
          const error = normalizeError(err);
          const extra = error as Error & { statusCode?: number; receivedAnyEvent?: boolean };
          const statusCode = extra.statusCode;
          const hasReceivedEvents = Boolean(extra.receivedAnyEvent);
          const isAbortError = error.name === 'AbortError';
          const errorText = error.message || 'V3 流式生成失败';
          const isNetworkLikeError =
            error instanceof TypeError ||
            /network|fetch|failed to fetch|load failed/i.test(errorText);

          if (stopRequested || (isAbortError && !idleTimeoutTriggered)) {
            return;
          }

          if (errorText === 'STREAM_IDLE_TIMEOUT') {
            emitErrorOnce('生成连接超时，请检查网络后重试');
            return;
          }

          const retryable =
            !hasReceivedEvents &&
            (isNetworkLikeError || (typeof statusCode === 'number' && RETRYABLE_HTTP_STATUS.has(statusCode)));

          if (retryable && attempt < CONNECT_MAX_ATTEMPTS) {
            const waitMs = CONNECT_RETRY_BASE_DELAY_MS * attempt;
            console.warn(
              `[SSE V3] Connect attempt ${attempt} failed, retrying in ${waitMs}ms:`,
              errorText
            );
            await delay(waitMs);
            continue;
          }

          if (errorText === 'STREAM_ENDED_WITHOUT_COMPLETE') {
            emitErrorOnce('生成流意外中断，请重试');
          } else {
            emitErrorOnce(errorText || 'V3 流式生成失败');
          }
          return;
        }
      }
    };

    runWithRetry().catch((err) => {
      const error = normalizeError(err);
      if (error.name !== 'AbortError') {
        emitErrorOnce(error.message || 'V3 流式生成失败');
      }
    });

    return () => {
      stopRequested = true;
      cleanupTimers();
      controller.abort();
    };
  },
};

/**
 * V3 流式生成回调接口
 */
export interface V3StreamCallbacks {
  onPhase: (phase: number, message: string, processor?: ProcessorWithConfig) => void;
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
  onChapterComplete: (index: number, total: number, chapter: Lesson, attempts: number) => void;
  onComplete: (pkg: CoursePackageV2, stats: V3GenerationStats) => void;
  onError: (message: string) => void;
  onSimulatorProgress?: (
    simulatorName: string,
    stepIndex: number,
    round: number,
    maxRounds: number,
    stage: string,
    message: string
  ) => void;
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
   * 纯上传文件（不做解析）
   */
  uploadFileOnly: async (file: File): Promise<UploadFileResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    return studioApiClient.postFormData('/api/v1/studio/upload/files', formData);
  },

  /**
   * 删除已上传文件
   */
  deleteUploadedFile: async (uploadId: string): Promise<{ success: boolean; upload_id: string }> => {
    return studioApiClient.delete(`/api/v1/studio/upload/files/${uploadId}`);
  },

  /**
   * 创建异步上传提取任务
   */
  createUploadTask: async (file: File): Promise<UploadTaskCreateResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    return studioApiClient.postFormData('/api/v1/studio/upload/tasks', formData);
  },

  /**
   * 查询异步上传任务状态
   */
  getUploadTaskStatus: async (taskId: string): Promise<UploadTaskStatusResponse> => {
    return studioApiClient.get(`/api/v1/studio/upload/tasks/${taskId}`);
  },

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
// Async Generation API (任务队列化并发生成)
// ============================================

export interface GenerationTaskInfo {
  task_id: string;
  course_title: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress_pct: number;
  current_phase: string;
  chapters_completed: number;
  chapters_total: number;
  package_id?: string;
  error_message?: string;
  created_at?: string;
  started_at?: string;
  completed_at?: string;
  queue_position?: number;
}

export interface QueueInfo {
  queue_length: number;
  running_count: number;
  max_concurrent: number;
  max_queue_size: number;
}

export const studioAsyncApi = {
  /**
   * 提交异步课程生成任务
   */
  submitGeneration: async (data: GenerateRequestV2, adminId: number = 1): Promise<{ success: boolean; task_id: string; queue_position: number }> => {
    return studioApiClient.post(`/api/v1/studio/packages/generate-async?admin_id=${adminId}`, data);
  },

  /**
   * 获取任务列表
   */
  listTasks: async (adminId?: number, limit: number = 20): Promise<{ tasks: GenerationTaskInfo[] }> => {
    const params: Record<string, string | number | boolean> = { limit };
    if (adminId !== undefined) params.admin_id = adminId;
    return studioApiClient.get('/api/v1/studio/tasks', params);
  },

  /**
   * 获取单个任务状态
   */
  getTaskStatus: async (taskId: string): Promise<GenerationTaskInfo> => {
    return studioApiClient.get(`/api/v1/studio/tasks/${taskId}/status`);
  },

  /**
   * 获取队列概况
   */
  getQueueInfo: async (): Promise<QueueInfo> => {
    return studioApiClient.get('/api/v1/studio/tasks/queue-info');
  },

  /**
   * 取消任务
   */
  cancelTask: async (taskId: string, adminId: number = 1): Promise<{ success: boolean; message: string }> => {
    return studioApiClient.delete(`/api/v1/studio/tasks/${taskId}?admin_id=${adminId}`);
  },

  /**
   * 删除任务记录
   */
  deleteTask: async (taskId: string, adminId: number = 1): Promise<{ success: boolean; message: string }> => {
    return studioApiClient.delete(`/api/v1/studio/tasks/${taskId}/record?admin_id=${adminId}`);
  },

  /**
   * 重试已取消/失败的任务
   */
  retryTask: async (taskId: string, adminId: number = 1): Promise<{ success: boolean; task_id: string; queue_position: number }> => {
    return studioApiClient.post(`/api/v1/studio/tasks/${taskId}/retry?admin_id=${adminId}`);
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
