'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  StatCard,
  GrowthChart,
  HeatmapChart,
  PieChartComponent,
  BarChartComponent,
} from '@/components/admin';
import {
  analyticsAPI,
  OverviewData,
  GrowthDataPoint,
  HeatmapData,
  UserSourceData,
  LearningTimeData,
  mockOverviewData,
  mockGrowthData,
  mockUserSourceData,
  mockLearningTimeData,
  mockHeatmapData,
} from '@/lib/api/admin/analytics';

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<OverviewData>(mockOverviewData);
  const [growthData, setGrowthData] = useState<GrowthDataPoint[]>(mockGrowthData);
  const [growthPeriod, setGrowthPeriod] = useState<'7d' | '30d' | '90d'>('30d');
  const [heatmapData, setHeatmapData] = useState<HeatmapData>(mockHeatmapData);
  const [userSources, setUserSources] = useState<UserSourceData[]>(mockUserSourceData);
  const [learningTime, setLearningTime] = useState<LearningTimeData[]>(mockLearningTimeData);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    loadGrowthData();
  }, [growthPeriod]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [overviewRes, heatmapRes, sourcesRes, learningTimeRes] = await Promise.all([
        analyticsAPI.getOverview(),
        analyticsAPI.getHeatmap(),
        analyticsAPI.getUserSources(),
        analyticsAPI.getLearningTime(),
      ]);
      setOverview(overviewRes);
      setHeatmapData(heatmapRes);
      setUserSources(sourcesRes);
      setLearningTime(learningTimeRes);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadGrowthData = async () => {
    try {
      const data = await analyticsAPI.getGrowth(growthPeriod);
      setGrowthData(data);
    } catch (error) {
      console.error('Failed to load growth data:', error);
    }
  };

  const calculateChange = (current: number, previous: number): string => {
    if (previous === 0) return '+0%';
    const change = ((current - previous) / previous) * 100;
    return change >= 0 ? `+${change.toFixed(1)}%` : `${change.toFixed(1)}%`;
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
          <h1 className="text-3xl font-bold text-slate-900">数据分析</h1>
          <p className="text-slate-500 mt-1">用户行为与学习数据总览</p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/admin/analytics/learning"
            className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors"
          >
            学习分析
          </Link>
          <Link
            href="/admin/analytics/retention"
            className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors"
          >
            留存分析
          </Link>
          <button className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700 transition-colors">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            导出报告
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="总用户数"
          value={overview.totalUsers.toLocaleString()}
          change={calculateChange(overview.newUsersToday, overview.newUsersYesterday)}
          changeType={overview.newUsersToday >= overview.newUsersYesterday ? 'up' : 'down'}
          subtitle={`今日新增 ${overview.newUsersToday}`}
          icon={
            <svg className="w-6 h-6 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          }
        />
        <StatCard
          title="活跃用户"
          value={overview.activeUsers.toLocaleString()}
          subtitle={`占总用户 ${((overview.activeUsers / overview.totalUsers) * 100).toFixed(1)}%`}
          icon={
            <svg className="w-6 h-6 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
          }
        />
        <StatCard
          title="今日学习时长"
          value={`${overview.todayLearningHours.toLocaleString()}h`}
          subtitle={`人均 ${overview.activeUsers > 0 ? Math.round(overview.todayLearningHours / overview.activeUsers * 60) : 0} 分钟`}
          icon={
            <svg className="w-6 h-6 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
          }
        />
        <StatCard
          title="AI 对话次数"
          value={overview.aiConversations.toLocaleString()}
          subtitle="今日累计"
          icon={
            <svg className="w-6 h-6 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          }
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Growth Chart */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-slate-900">用户增长趋势</h3>
            <select
              value={growthPeriod}
              onChange={(e) => setGrowthPeriod(e.target.value as '7d' | '30d' | '90d')}
              className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 text-slate-600 focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <option value="7d">近 7 天</option>
              <option value="30d">近 30 天</option>
              <option value="90d">近 90 天</option>
            </select>
          </div>
          <GrowthChart data={growthData} />
        </div>

        {/* User Source Distribution */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <h3 className="text-lg font-semibold text-slate-900 mb-6">用户来源分布</h3>
          <PieChartComponent data={userSources} />
        </div>
      </div>

      {/* Heatmap */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-slate-900">学习活跃度热力图</h3>
          <span className="text-sm text-slate-500">按小时统计的活跃用户分布</span>
        </div>
        <HeatmapChart data={heatmapData.data} />
      </div>

      {/* Learning Time Distribution */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-slate-900">每日学习时长分布</h3>
        </div>
        <BarChartComponent data={learningTime} />
      </div>
    </div>
  );
}
