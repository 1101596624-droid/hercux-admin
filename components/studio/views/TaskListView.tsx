'use client';

/**
 * 课程生成任务列表视图 (2026-02-23)
 *
 * 显示所有课程生成任务的状态、进度，支持取消和查看结果。
 * 自动轮询活跃任务的进度。
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { Loader2, CheckCircle2, XCircle, Clock, Trash2, RefreshCw, ListOrdered } from 'lucide-react';
import { studioAsyncApi, type GenerationTaskInfo, type QueueInfo } from '@/lib/api/studio';

interface TaskListViewProps {
  onViewPackage?: (packageId: string) => void;
  adminId?: number;
}

export function TaskListView({ onViewPackage, adminId = 1 }: TaskListViewProps) {
  const [tasks, setTasks] = useState<GenerationTaskInfo[]>([]);
  const [queueInfo, setQueueInfo] = useState<QueueInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      const [taskRes, queueRes] = await Promise.all([
        studioAsyncApi.listTasks(adminId),
        studioAsyncApi.getQueueInfo(),
      ]);
      setTasks(taskRes.tasks);
      setQueueInfo(queueRes);
    } catch (e) {
      console.error('获取任务列表失败:', e);
    } finally {
      setLoading(false);
    }
  }, [adminId]);

  useEffect(() => {
    fetchTasks();
    // 有活跃任务时每3秒轮询
    pollRef.current = setInterval(fetchTasks, 3000);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [fetchTasks]);

  const handleCancel = async (taskId: string) => {
    try {
      await studioAsyncApi.cancelTask(taskId, adminId);
      fetchTasks();
    } catch (e) {
      console.error('取消任务失败:', e);
    }
  };

  const handleDelete = async (taskId: string) => {
    if (!confirm('确定删除此任务记录？')) return;
    try {
      await studioAsyncApi.deleteTask(taskId, adminId);
      fetchTasks();
    } catch (e) {
      console.error('删除任务失败:', e);
    }
  };

  const handleRetry = async (taskId: string) => {
    try {
      await studioAsyncApi.retryTask(taskId, adminId);
      fetchTasks();
    } catch (e) {
      console.error('重试任务失败:', e);
    }
  };

  const statusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'running': return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'completed': return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'cancelled': return <XCircle className="w-4 h-4 text-gray-400" />;
      default: return null;
    }
  };

  const statusText = (status: string) => {
    const map: Record<string, string> = {
      pending: '排队中', running: '生成中', completed: '已完成',
      failed: '失败', cancelled: '已取消',
    };
    return map[status] || status;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-500">加载中...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 队列概况 */}
      {queueInfo && (
        <div className="flex items-center gap-4 px-4 py-3 bg-blue-50 rounded-lg text-sm">
          <ListOrdered className="w-4 h-4 text-blue-600" />
          <span>排队: <b>{queueInfo.queue_length}</b></span>
          <span>运行中: <b>{queueInfo.running_count}</b> / {queueInfo.max_concurrent}</span>
          <button onClick={fetchTasks} className="ml-auto p-1 hover:bg-blue-100 rounded">
            <RefreshCw className="w-4 h-4 text-blue-600" />
          </button>
        </div>
      )}

      {/* 任务列表 */}
      {tasks.length === 0 ? (
        <div className="text-center py-12 text-gray-400">暂无生成任务</div>
      ) : (
        <div className="space-y-2">
          {tasks.map((task) => (
            <div key={task.task_id} className="border rounded-lg p-4 bg-white hover:shadow-sm transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {statusIcon(task.status)}
                  <span className="font-medium">{task.course_title}</span>
                  <span className="text-xs text-gray-400">{statusText(task.status)}</span>
                </div>
                <div className="flex items-center gap-2">
                  {task.status === 'completed' && task.package_id && onViewPackage && (
                    <button
                      onClick={() => onViewPackage(task.package_id!)}
                      className="text-xs px-3 py-1 bg-green-50 text-green-700 rounded hover:bg-green-100"
                    >
                      查看课程
                    </button>
                  )}
                  {(task.status === 'pending' || task.status === 'running') && (
                    <button
                      onClick={() => handleCancel(task.task_id)}
                      className="text-xs px-3 py-1 text-red-500 hover:bg-red-50 rounded"
                    >
                      取消
                    </button>
                  )}
                  {(task.status === 'cancelled' || task.status === 'failed') && (
                    <>
                      <button
                        onClick={() => handleRetry(task.task_id)}
                        className="text-xs px-3 py-1 bg-blue-50 text-blue-700 rounded hover:bg-blue-100"
                      >
                        重试
                      </button>
                      <button
                        onClick={() => handleDelete(task.task_id)}
                        className="text-xs px-3 py-1 text-gray-500 hover:bg-gray-100 rounded"
                      >
                        删除
                      </button>
                    </>
                  )}
                </div>
              </div>

              {/* 进度条 */}
              {(task.status === 'running' || task.status === 'pending') && (
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>{task.current_phase}</span>
                    <span>{task.progress_pct}%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${task.progress_pct}%` }}
                    />
                  </div>
                  {task.chapters_total > 0 && (
                    <div className="text-xs text-gray-400 mt-1">
                      章节: {task.chapters_completed} / {task.chapters_total}
                    </div>
                  )}
                </div>
              )}

              {/* 失败信息 */}
              {task.status === 'failed' && task.error_message && (
                <div className="mt-2 text-xs text-red-500 bg-red-50 p-2 rounded">
                  {task.error_message}
                </div>
              )}

              {/* 时间信息 */}
              <div className="mt-2 text-xs text-gray-400">
                {task.created_at && <span>创建: {new Date(task.created_at).toLocaleString('zh-CN')}</span>}
                {task.completed_at && <span className="ml-3">完成: {new Date(task.completed_at).toLocaleString('zh-CN')}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
