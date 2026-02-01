'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  aiMonitorAPI,
  AIAlert,
  mockAIAlerts,
} from '@/lib/api/admin/ai-monitor';

const severityConfig: Record<string, { label: string; color: string; bg: string }> = {
  critical: { label: '严重', color: 'text-red-700', bg: 'bg-red-100' },
  warning: { label: '警告', color: 'text-orange-700', bg: 'bg-orange-100' },
  info: { label: '提示', color: 'text-blue-700', bg: 'bg-blue-100' },
};

const statusConfig: Record<string, { label: string; color: string }> = {
  open: { label: '待处理', color: 'bg-red-500' },
  acknowledged: { label: '已确认', color: 'bg-orange-500' },
  resolved: { label: '已解决', color: 'bg-green-500' },
};

export default function AIAlertsPage() {
  const [alerts, setAlerts] = useState<AIAlert[]>(mockAIAlerts);
  const [stats, setStats] = useState({ open: 1, acknowledged: 1, resolved: 1 });
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');

  useEffect(() => {
    loadAlerts();
  }, [statusFilter]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const result = await aiMonitorAPI.getAlerts(statusFilter || undefined);
      setAlerts(result.data);
      setStats(result.stats);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (id: number, newStatus: string) => {
    try {
      await aiMonitorAPI.updateAlert(id, { status: newStatus });
      loadAlerts();
    } catch (error) {
      console.error('Failed to update alert:', error);
    }
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
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
            <span className="text-slate-900">告警管理</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900">告警管理</h1>
          <p className="text-slate-500 mt-1">监控和处理 AI 服务告警</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <button
          onClick={() => setStatusFilter('open')}
          className={`p-4 rounded-xl border transition-all ${
            statusFilter === 'open' ? 'border-red-500 bg-red-50' : 'border-slate-200 bg-white hover:bg-slate-50'
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-sm text-slate-600">待处理</span>
          </div>
          <p className="text-3xl font-bold text-slate-900 mt-2">{stats.open}</p>
        </button>
        <button
          onClick={() => setStatusFilter('acknowledged')}
          className={`p-4 rounded-xl border transition-all ${
            statusFilter === 'acknowledged' ? 'border-orange-500 bg-orange-50' : 'border-slate-200 bg-white hover:bg-slate-50'
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-orange-500" />
            <span className="text-sm text-slate-600">已确认</span>
          </div>
          <p className="text-3xl font-bold text-slate-900 mt-2">{stats.acknowledged}</p>
        </button>
        <button
          onClick={() => setStatusFilter('resolved')}
          className={`p-4 rounded-xl border transition-all ${
            statusFilter === 'resolved' ? 'border-green-500 bg-green-50' : 'border-slate-200 bg-white hover:bg-slate-50'
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-sm text-slate-600">已解决</span>
          </div>
          <p className="text-3xl font-bold text-slate-900 mt-2">{stats.resolved}</p>
        </button>
      </div>

      {/* Clear Filter */}
      {statusFilter && (
        <button
          onClick={() => setStatusFilter('')}
          className="text-sm text-red-500 hover:text-red-600"
        >
          清除筛选
        </button>
      )}

      {/* Alerts List */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-red-200 border-t-red-500 rounded-full animate-spin"></div>
          </div>
        ) : alerts.length === 0 ? (
          <div className="bg-white rounded-2xl p-12 shadow-sm border border-slate-100 text-center">
            <svg className="w-16 h-16 text-slate-300 mx-auto mb-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
            <p className="text-slate-500">暂无告警</p>
          </div>
        ) : (
          alerts.map((alert) => {
            const severity = severityConfig[alert.severity] || severityConfig.info;
            const status = statusConfig[alert.status] || statusConfig.open;
            return (
              <div key={alert.id} className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className={`w-10 h-10 rounded-xl ${severity.bg} flex items-center justify-center`}>
                      {alert.severity === 'critical' ? (
                        <svg className="w-5 h-5 text-red-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="10" />
                          <line x1="12" y1="8" x2="12" y2="12" />
                          <line x1="12" y1="16" x2="12.01" y2="16" />
                        </svg>
                      ) : alert.severity === 'warning' ? (
                        <svg className="w-5 h-5 text-orange-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                          <line x1="12" y1="9" x2="12" y2="13" />
                          <line x1="12" y1="17" x2="12.01" y2="17" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="10" />
                          <line x1="12" y1="16" x2="12" y2="12" />
                          <line x1="12" y1="8" x2="12.01" y2="8" />
                        </svg>
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-slate-900">{alert.title}</h3>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${severity.bg} ${severity.color}`}>
                          {severity.label}
                        </span>
                      </div>
                      <p className="text-sm text-slate-600 mb-2">{alert.message}</p>
                      <div className="flex items-center gap-4 text-xs text-slate-400">
                        <span>触发值: {alert.metric_value}</span>
                        <span>阈值: {alert.threshold_value}</span>
                        <span>{formatTime(alert.created_at)}</span>
                      </div>
                      {alert.resolution_note && (
                        <p className="text-sm text-green-600 mt-2">
                          处理备注: {alert.resolution_note}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${status.color}`} />
                    <span className="text-sm text-slate-500">{status.label}</span>
                    {alert.status === 'open' && (
                      <button
                        onClick={() => handleUpdateStatus(alert.id, 'acknowledged')}
                        className="ml-4 px-3 py-1.5 text-sm text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors"
                      >
                        确认
                      </button>
                    )}
                    {alert.status === 'acknowledged' && (
                      <button
                        onClick={() => handleUpdateStatus(alert.id, 'resolved')}
                        className="ml-4 px-3 py-1.5 text-sm text-white bg-green-500 rounded-lg hover:bg-green-600 transition-colors"
                      >
                        解决
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
