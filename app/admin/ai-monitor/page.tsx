'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { StatCard } from '@/components/admin';
import {
  aiMonitorAPI,
  AIOverviewData,
  AITrendPoint,
  AICostBreakdown,
  mockAIOverview,
  mockAITrends,
  mockAICostBreakdown,
} from '@/lib/api/admin/ai-monitor';

export default function AIMonitorPage() {
  const [overview, setOverview] = useState<AIOverviewData>(mockAIOverview);
  const [trends, setTrends] = useState<AITrendPoint[]>(mockAITrends);
  const [costs, setCosts] = useState<AICostBreakdown>(mockAICostBreakdown);
  const [trendPeriod, setTrendPeriod] = useState<'24h' | '7d' | '30d'>('24h');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    loadTrends();
  }, [trendPeriod]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [overviewRes, costsRes] = await Promise.all([
        aiMonitorAPI.getOverview(),
        aiMonitorAPI.getCosts(),
      ]);
      setOverview(overviewRes);
      setCosts(costsRes);
    } catch (error) {
      console.error('Failed to load AI monitor data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTrends = async () => {
    try {
      const data = await aiMonitorAPI.getTrends(trendPeriod);
      setTrends(data);
    } catch (error) {
      console.error('Failed to load trends:', error);
    }
  };

  const formatChange = (value: number): string => {
    const percent = (value * 100).toFixed(1);
    return value >= 0 ? `+${percent}%` : `${percent}%`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-10 h-10 border-4 border-red-200 border-t-red-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">AI API 监控</h1>
          <p className="text-slate-500 mt-1">实时监控 AI 服务使用量与成本</p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/admin/ai-monitor/logs"
            className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors"
          >
            调用日志
          </Link>
          <Link
            href="/admin/ai-monitor/alerts"
            className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors"
          >
            告警管理
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          title="今日调用次数"
          value={overview.today.call_count.toLocaleString()}
          change={formatChange(overview.comparisons.calls_vs_yesterday)}
          changeType={overview.comparisons.calls_vs_yesterday >= 0 ? 'up' : 'down'}
          icon={
            <svg className="w-6 h-6 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          }
        />
        <StatCard
          title="Token 消耗"
          value={`${(overview.today.total_tokens / 1000000).toFixed(1)}M`}
          icon={
            <svg className="w-6 h-6 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v6l4 2" />
            </svg>
          }
        />
        <StatCard
          title="今日成本"
          value={`$${overview.today.total_cost.toFixed(2)}`}
          change={formatChange(overview.comparisons.cost_vs_yesterday)}
          changeType={overview.comparisons.cost_vs_yesterday >= 0 ? 'up' : 'down'}
          icon={
            <svg className="w-6 h-6 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="1" x2="12" y2="23" />
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          }
        />
        <StatCard
          title="平均延迟"
          value={`${overview.today.avg_latency_ms}ms`}
          icon={
            <svg className="w-6 h-6 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
          }
        />
        <StatCard
          title="错误率"
          value={`${(overview.today.error_rate * 100).toFixed(2)}%`}
          icon={
            <svg className="w-6 h-6 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          }
        />
      </div>

      {/* Budget Progress */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">本月预算使用</h3>
            <p className="text-sm text-slate-500">
              已使用 ${costs.total_cost.toFixed(2)} / ${costs.budget.toFixed(2)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-slate-900">{(costs.budget_usage * 100).toFixed(1)}%</p>
            {costs.forecast.will_exceed_budget && (
              <p className="text-sm text-red-500">预计月底超支</p>
            )}
          </div>
        </div>
        <div className="h-4 bg-slate-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              costs.budget_usage > 0.9 ? 'bg-red-500' : costs.budget_usage > 0.7 ? 'bg-orange-500' : 'bg-green-500'
            }`}
            style={{ width: `${Math.min(costs.budget_usage * 100, 100)}%` }}
          />
        </div>
        <div className="flex items-center justify-between mt-2 text-sm text-slate-500">
          <span>月底预估: ${costs.forecast.month_end_cost.toFixed(2)}</span>
          <span>剩余预算: ${(costs.budget - costs.total_cost).toFixed(2)}</span>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Usage Trends */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-slate-900">调用量趋势</h3>
            <select
              value={trendPeriod}
              onChange={(e) => setTrendPeriod(e.target.value as '24h' | '7d' | '30d')}
              className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 text-slate-600 focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <option value="24h">今日</option>
              <option value="7d">近 7 天</option>
              <option value="30d">近 30 天</option>
            </select>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: '#64748B', fontSize: 12 }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748B', fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #E2E8F0',
                  borderRadius: '12px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              />
              <Line type="monotone" dataKey="call_count" stroke="#DC2626" strokeWidth={2} dot={false} name="调用次数" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Model Usage Distribution */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <h3 className="text-lg font-semibold text-slate-900 mb-6">模型使用分布</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={costs.breakdown} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: '#64748B', fontSize: 12 }} />
              <YAxis dataKey="model" type="category" axisLine={false} tickLine={false} tick={{ fill: '#64748B', fontSize: 12 }} width={100} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #E2E8F0',
                  borderRadius: '12px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
                formatter={(value) => [`$${Number(value).toFixed(2)}`, '成本']}
              />
              <Bar dataKey="cost" fill="#DC2626" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Cost Breakdown Table */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <h3 className="text-lg font-semibold text-slate-900 mb-6">成本明细</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">模型</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-slate-500">调用次数</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-slate-500">Token 消耗</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-slate-500">成本</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-slate-500">占比</th>
              </tr>
            </thead>
            <tbody>
              {costs.breakdown.map((item) => (
                <tr key={item.model} className="border-b border-slate-50 hover:bg-slate-50">
                  <td className="py-3 px-4">
                    <span className="font-medium text-slate-900">{item.model}</span>
                  </td>
                  <td className="py-3 px-4 text-right text-slate-600">{item.call_count.toLocaleString()}</td>
                  <td className="py-3 px-4 text-right text-slate-600">
                    {item.tokens > 0 ? `${(item.tokens / 1000000).toFixed(1)}M` : '-'}
                  </td>
                  <td className="py-3 px-4 text-right font-medium text-slate-900">${item.cost.toFixed(2)}</td>
                  <td className="py-3 px-4 text-right">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-50 text-red-600">
                      {(item.percentage * 100).toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="bg-slate-50">
                <td className="py-3 px-4 font-semibold text-slate-900">合计</td>
                <td className="py-3 px-4 text-right font-semibold text-slate-900">
                  {costs.breakdown.reduce((sum, item) => sum + item.call_count, 0).toLocaleString()}
                </td>
                <td className="py-3 px-4 text-right font-semibold text-slate-900">
                  {(costs.breakdown.reduce((sum, item) => sum + item.tokens, 0) / 1000000).toFixed(1)}M
                </td>
                <td className="py-3 px-4 text-right font-semibold text-slate-900">${costs.total_cost.toFixed(2)}</td>
                <td className="py-3 px-4 text-right font-semibold text-slate-900">100%</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  );
}
