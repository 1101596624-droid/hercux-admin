'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  aiMonitorAPI,
  AILogEntry,
  mockAILogs,
} from '@/lib/api/admin/ai-monitor';

const sceneLabels: Record<string, { label: string; color: string }> = {
  tutor: { label: 'AI 导师', color: 'bg-blue-100 text-blue-700' },
  planner: { label: '计划生成', color: 'bg-purple-100 text-purple-700' },
  voice: { label: '语音交互', color: 'bg-green-100 text-green-700' },
  summary: { label: '内容摘要', color: 'bg-orange-100 text-orange-700' },
};

const statusLabels: Record<string, { label: string; color: string }> = {
  success: { label: '成功', color: 'bg-green-100 text-green-700' },
  error: { label: '失败', color: 'bg-red-100 text-red-700' },
  timeout: { label: '超时', color: 'bg-orange-100 text-orange-700' },
};

export default function AILogsPage() {
  const [logs, setLogs] = useState<AILogEntry[]>(mockAILogs);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    scene: '',
    status: '',
  });
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    loadLogs();
  }, [page, filters]);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const result = await aiMonitorAPI.getLogs({
        page,
        limit: 20,
        scene: filters.scene || undefined,
        status: filters.status || undefined,
      });
      setLogs(result.data);
      setTotal(result.total);
    } catch (error) {
      console.error('Failed to load logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm text-slate-500 mb-2">
            <Link href="/admin/ai-monitor" className="hover:text-red-500 transition-colors">
              AI API 监控
            </Link>
            <span>/</span>
            <span className="text-slate-900">调用日志</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900">调用日志</h1>
          <p className="text-slate-500 mt-1">查看 AI API 调用详情</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl p-4 shadow-sm border border-slate-100">
        <div className="flex items-center gap-4 flex-wrap">
          <div>
            <label className="text-xs text-slate-500 mb-1 block">场景</label>
            <select
              value={filters.scene}
              onChange={(e) => setFilters({ ...filters, scene: e.target.value })}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <option value="">全部场景</option>
              <option value="tutor">AI 导师</option>
              <option value="planner">计划生成</option>
              <option value="voice">语音交互</option>
              <option value="summary">内容摘要</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-slate-500 mb-1 block">状态</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <option value="">全部状态</option>
              <option value="success">成功</option>
              <option value="error">失败</option>
              <option value="timeout">超时</option>
            </select>
          </div>
          <div className="flex-1" />
          <button
            onClick={() => loadLogs()}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700 transition-colors"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
            </svg>
            刷新
          </button>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-red-200 border-t-red-500 rounded-full animate-spin"></div>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-100">
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase">时间</th>
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase">用户</th>
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase">场景</th>
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase">模型</th>
                    <th className="text-right px-4 py-3 text-xs font-medium text-slate-500 uppercase">Input</th>
                    <th className="text-right px-4 py-3 text-xs font-medium text-slate-500 uppercase">Output</th>
                    <th className="text-right px-4 py-3 text-xs font-medium text-slate-500 uppercase">延迟</th>
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase">状态</th>
                    <th className="text-right px-4 py-3 text-xs font-medium text-slate-500 uppercase">成本</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => {
                    const scene = sceneLabels[log.scene] || { label: log.scene, color: 'bg-slate-100 text-slate-700' };
                    const status = statusLabels[log.status] || { label: log.status, color: 'bg-slate-100 text-slate-700' };
                    return (
                      <tr key={log.id} className="border-b border-slate-50 hover:bg-slate-50">
                        <td className="px-4 py-3 text-sm text-slate-600">{formatTime(log.created_at)}</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="w-7 h-7 rounded-full bg-slate-200 flex items-center justify-center text-xs font-medium text-slate-600">
                              {log.user_name.charAt(0)}
                            </div>
                            <span className="text-sm text-slate-900">{log.user_name}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${scene.color}`}>
                            {scene.label}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-slate-600 font-mono">{log.model}</td>
                        <td className="px-4 py-3 text-sm text-slate-600 text-right">{log.input_tokens.toLocaleString()}</td>
                        <td className="px-4 py-3 text-sm text-slate-600 text-right">{log.output_tokens.toLocaleString()}</td>
                        <td className="px-4 py-3 text-sm text-slate-600 text-right">{log.latency_ms}ms</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.color}`}>
                            {status.label}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm font-medium text-slate-900 text-right">${log.cost.toFixed(4)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-4 py-3 border-t border-slate-100 flex items-center justify-between">
              <p className="text-sm text-slate-500">
                显示 {(page - 1) * 20 + 1}-{Math.min(page * 20, total)} 共 {total} 条
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition-colors disabled:opacity-50"
                >
                  上一页
                </button>
                <span className="px-3 py-1.5 text-sm bg-red-600 text-white rounded-lg">{page}</span>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page * 20 >= total}
                  className="px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition-colors disabled:opacity-50"
                >
                  下一页
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
