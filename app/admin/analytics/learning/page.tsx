'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  FunnelChart,
} from '@/components/admin';
import {
  analyticsAPI,
  FunnelStage,
  UserCluster,
  AIUsageData,
  mockFunnelData,
  mockUserClusters,
  mockAIUsageData,
} from '@/lib/api/admin/analytics';

// Video completion data (will be replaced with real API)
const videoCompletionData = [
  { range: '0-25%', count: 1245, percent: 15 },
  { range: '25-50%', count: 2156, percent: 26 },
  { range: '50-75%', count: 2890, percent: 35 },
  { range: '75-100%', count: 1988, percent: 24 },
];

const clusterIcons: Record<string, React.ReactNode> = {
  '高活跃学习者': (
    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  ),
  '稳定学习者': (
    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10" />
      <path d="M12 2a10 10 0 0 1 10 10" />
      <path d="M12 12l4-4" />
    </svg>
  ),
  '间歇学习者': (
    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  ),
  '流失风险用户': (
    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <line x1="23" y1="1" x2="17" y2="7" />
      <line x1="17" y1="1" x2="23" y2="7" />
    </svg>
  ),
};

export default function LearningAnalyticsPage() {
  const [funnelData, setFunnelData] = useState<FunnelStage[]>(mockFunnelData);
  const [clusters, setClusters] = useState<UserCluster[]>(mockUserClusters);
  const [aiUsage, setAIUsage] = useState<AIUsageData>(mockAIUsageData);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [funnelRes, clustersRes, aiUsageRes] = await Promise.all([
        analyticsAPI.getFunnel(),
        analyticsAPI.getClusters(),
        analyticsAPI.getAIUsage('24h'),
      ]);
      setFunnelData(funnelRes);
      setClusters(clustersRes);
      setAIUsage(aiUsageRes);
    } catch (error) {
      console.error('Failed to load learning analytics:', error);
    } finally {
      setLoading(false);
    }
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
          <div className="flex items-center gap-2 text-sm text-slate-500 mb-2">
            <Link href="/admin/analytics" className="hover:text-red-500 transition-colors">
              数据分析
            </Link>
            <span>/</span>
            <span className="text-slate-900">学习行为分析</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900">学习行为分析</h1>
          <p className="text-slate-500 mt-1">深入了解用户学习模式与转化路径</p>
        </div>
      </div>

      {/* Learning Funnel */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">学习转化漏斗</h3>
            <p className="text-sm text-slate-500 mt-1">从注册到完课的完整转化路径</p>
          </div>
          <select className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 text-slate-600 focus:outline-none focus:ring-2 focus:ring-red-500">
            <option>全部课程</option>
            <option>运动生物力学</option>
            <option>CSCS 认证</option>
          </select>
        </div>
        <FunnelChart data={funnelData} />
      </div>

      {/* Learning Depth Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Video Completion Rate */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <h3 className="text-lg font-semibold text-slate-900 mb-6">视频完播率分布</h3>
          <div className="space-y-4">
            {videoCompletionData.map(item => (
              <div key={item.range}>
                <div className="flex items-center justify-between text-sm mb-1.5">
                  <span className="text-slate-600">{item.range}</span>
                  <span className="text-slate-900 font-medium">
                    {item.count.toLocaleString()} 用户 ({item.percent}%)
                  </span>
                </div>
                <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-600 rounded-full transition-all"
                    style={{ width: `${item.percent}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Conversation Stats */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <h3 className="text-lg font-semibold text-slate-900 mb-6">AI 导师对话统计</h3>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-slate-50 rounded-xl p-4 text-center">
              <p className="text-3xl font-bold text-slate-900">{aiUsage.totalConversations.toLocaleString()}</p>
              <p className="text-xs text-slate-500 mt-1">今日对话总数</p>
            </div>
            <div className="bg-slate-50 rounded-xl p-4 text-center">
              <p className="text-3xl font-bold text-slate-900">{aiUsage.uniqueUsers.toLocaleString()}</p>
              <p className="text-xs text-slate-500 mt-1">参与用户数</p>
            </div>
          </div>
          <div className="bg-slate-50 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">人均对话次数</span>
              <span className="text-lg font-bold text-slate-900">{aiUsage.avgMessagesPerUser}</span>
            </div>
          </div>
          <div className="mt-4">
            <p className="text-sm font-medium text-slate-700 mb-3">对话趋势</p>
            <div className="flex items-end gap-1 h-20">
              {aiUsage.trend.map((item, index) => {
                const maxCount = Math.max(...aiUsage.trend.map(t => t.count));
                const height = maxCount > 0 ? (item.count / maxCount) * 100 : 0;
                return (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div
                      className="w-full bg-red-500 rounded-t"
                      style={{ height: `${height}%`, minHeight: '4px' }}
                    />
                    <span className="text-xs text-slate-400 mt-1">{item.time}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* User Learning Clusters */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <h3 className="text-lg font-semibold text-slate-900 mb-6">用户学习模式聚类</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {clusters.map(item => (
            <div key={item.name} className="border border-slate-200 rounded-xl p-5 hover:shadow-md transition-shadow">
              <div
                className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
                style={{ backgroundColor: `${item.color}20`, color: item.color }}
              >
                {clusterIcons[item.name] || (
                  <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                  </svg>
                )}
              </div>
              <h4 className="text-lg font-semibold text-slate-900">{item.name}</h4>
              <p className="text-sm text-slate-500 mt-1">{item.description}</p>
              <p className="text-2xl font-bold text-slate-900 mt-3">{item.count.toLocaleString()}</p>
              <p className="text-xs text-slate-400">用户</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
