'use client';

import { useEffect, useState } from 'react';
import { StatCard } from '@/components/admin';
import { LineChart, BarChart, PieChart } from '@/components/admin/charts';

interface AgentStats {
  templates: {
    total: number;
    avgQuality: number;
  };
  patterns: {
    total: number;
    strategies: number;
    antiPatterns: number;
    avgConfidence: number;
  };
  trajectories: {
    total: number;
    successRate: number;
    avgQuality: number;
    last7Days: number;
  };
  health: {
    status: string;
    version: string;
    uptime?: number;
  };
  recentGenerations: Array<{
    date: string;
    count: number;
    avgQuality: number;
  }>;
  topPatterns: Array<{
    description: string;
    useCount: number;
    successRate: number;
  }>;
}

export default function AgentMonitorPage() {
  const [stats, setStats] = useState<AgentStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDistilling, setIsDistilling] = useState(false);
  const [isDecaying, setIsDecaying] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  const fetchStats = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';
      const response = await fetch(`${API_URL}/agent/stats`);

      if (!response.ok) {
        throw new Error('获取统计数据失败');
      }

      const data = await response.json();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // 每30秒刷新
    return () => clearInterval(interval);
  }, []);

  const handleDistill = async () => {
    setIsDistilling(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';
      const response = await fetch(`${API_URL}/agent/distill`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain: 'simulator' }),
      });

      if (!response.ok) throw new Error('蒸馏失败');

      const result = await response.json();
      alert(`成功！新提取了 ${result.new_patterns} 个策略模式`);
      fetchStats();
    } catch (err) {
      alert(err instanceof Error ? err.message : '蒸馏失败');
    } finally {
      setIsDistilling(false);
    }
  };

  const handleDecay = async () => {
    setIsDecaying(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';
      const response = await fetch(`${API_URL}/agent/decay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain: 'simulator', decay_factor: 0.95 }),
      });

      if (!response.ok) throw new Error('衰减失败');

      const result = await response.json();
      alert(`成功！影响了 ${result.affected_patterns} 个低表现模式`);
      fetchStats();
    } catch (err) {
      alert(err instanceof Error ? err.message : '衰减失败');
    } finally {
      setIsDecaying(false);
    }
  };

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';
      const response = await fetch(`${API_URL}/agent/sync`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('同步失败');

      const result = await response.json();
      alert(`成功！新增 ${result.new_templates} 个模板，${result.new_patterns} 个模式`);
      fetchStats();
    } catch (err) {
      alert(err instanceof Error ? err.message : '同步失败');
    } finally {
      setIsSyncing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          <p className="font-medium">错误</p>
          <p className="text-sm">{error}</p>
          <button
            onClick={fetchStats}
            className="mt-2 text-sm underline hover:no-underline"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="p-6 space-y-6">
      {/* 标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agent 监控</h1>
          <p className="text-gray-600 mt-1">HERCU Agent 经验晶化智能体系统</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            stats.health.status === 'ok'
              ? 'bg-green-100 text-green-700'
              : 'bg-red-100 text-red-700'
          }`}>
            {stats.health.status === 'ok' ? '● 运行中' : '● 离线'}
          </span>
          <span className="text-sm text-gray-500">v{stats.health.version}</span>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="模板库"
          value={stats.templates.total}
          change={`平均质量 ${stats.templates.avgQuality.toFixed(2)}`}
          icon="📚"
          trend="neutral"
        />
        <StatCard
          title="经验模式"
          value={stats.patterns.total}
          change={`${stats.patterns.strategies} 策略 + ${stats.patterns.antiPatterns} 反模式`}
          icon="🧠"
          trend="neutral"
        />
        <StatCard
          title="生成轨迹"
          value={stats.trajectories.total}
          change={`成功率 ${(stats.trajectories.successRate * 100).toFixed(1)}%`}
          icon="📈"
          trend={stats.trajectories.successRate > 0.8 ? 'up' : 'neutral'}
        />
        <StatCard
          title="近7天生成"
          value={stats.trajectories.last7Days}
          change={`平均质量 ${stats.trajectories.avgQuality.toFixed(2)}`}
          icon="⚡"
          trend="neutral"
        />
      </div>

      {/* 操作按钮 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">训练操作</h2>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleDistill}
            disabled={isDistilling}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isDistilling ? '蒸馏中...' : '🔬 经验蒸馏'}
          </button>
          <button
            onClick={handleDecay}
            disabled={isDecaying}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isDecaying ? '处理中...' : '📉 置信度衰减'}
          </button>
          <button
            onClick={handleSync}
            disabled={isSyncing}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSyncing ? '同步中...' : '🔄 数据同步'}
          </button>
          <button
            onClick={fetchStats}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            🔃 刷新数据
          </button>
        </div>
        <p className="text-sm text-gray-500 mt-3">
          提示：经验蒸馏需要 ≥3 条成功和失败轨迹。置信度衰减会降低低表现模式的权重。
        </p>
      </div>

      {/* 图表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 生成趋势 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">近期生成趋势</h2>
          {stats.recentGenerations.length > 0 ? (
            <LineChart
              data={stats.recentGenerations.map(g => ({
                label: g.date,
                value: g.avgQuality,
              }))}
              color="#3b82f6"
              height={250}
            />
          ) : (
            <p className="text-gray-500 text-center py-12">暂无数据</p>
          )}
        </div>

        {/* 热门策略 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">热门策略模式</h2>
          {stats.topPatterns.length > 0 ? (
            <div className="space-y-3">
              {stats.topPatterns.slice(0, 5).map((pattern, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {pattern.description}
                    </p>
                    <p className="text-xs text-gray-500">
                      使用 {pattern.useCount} 次 · 成功率 {(pattern.successRate * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div className={`ml-3 px-2 py-1 rounded text-xs font-medium ${
                    pattern.successRate > 0.8
                      ? 'bg-green-100 text-green-700'
                      : pattern.successRate > 0.5
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {pattern.successRate > 0.8 ? '优秀' : pattern.successRate > 0.5 ? '良好' : '待优化'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-12">暂无数据</p>
          )}
        </div>
      </div>

      {/* 模式分布 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">模式类型分布</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600">
              {stats.patterns.strategies}
            </div>
            <p className="text-sm text-gray-600 mt-1">策略模式</p>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-orange-600">
              {stats.patterns.antiPatterns}
            </div>
            <p className="text-sm text-gray-600 mt-1">反模式</p>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-green-600">
              {(stats.patterns.avgConfidence * 100).toFixed(0)}%
            </div>
            <p className="text-sm text-gray-600 mt-1">平均置信度</p>
          </div>
        </div>
      </div>
    </div>
  );
}
