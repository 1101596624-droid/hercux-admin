'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { RetentionChart } from '@/components/admin';
import {
  analyticsAPI,
  RetentionData,
  UserCluster,
  mockRetentionData,
  mockUserClusters,
} from '@/lib/api/admin/analytics';

export default function RetentionAnalyticsPage() {
  const [retentionData, setRetentionData] = useState<RetentionData>(mockRetentionData);
  const [clusters, setClusters] = useState<UserCluster[]>(mockUserClusters);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [retentionRes, clustersRes] = await Promise.all([
        analyticsAPI.getRetention(),
        analyticsAPI.getClusters(),
      ]);
      setRetentionData(retentionRes);
      setClusters(clustersRes);
    } catch (error) {
      console.error('Failed to load retention data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Filter for churn risk users
  const churnRiskCluster = clusters.find(c => c.name === '流失风险用户');

  // Calculate lifecycle distribution from clusters
  const totalUsers = clusters.reduce((sum, c) => sum + c.count, 0);
  const lifecycleData = clusters.map(cluster => ({
    stage: cluster.name,
    desc: cluster.description,
    count: cluster.count,
    percent: totalUsers > 0 ? Math.round((cluster.count / totalUsers) * 100 * 10) / 10 : 0,
    color: cluster.color,
  }));

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
            <span className="text-slate-900">留存分析</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900">留存与活跃分析</h1>
          <p className="text-slate-500 mt-1">追踪用户留存率与生命周期状态</p>
        </div>
      </div>

      {/* Retention Curve */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">用户留存曲线</h3>
            <p className="text-sm text-slate-500 mt-1">
              新用户在不同时间节点的留存情况 (样本: {retentionData.cohortSize.toLocaleString()} 用户)
            </p>
          </div>
          <select className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 text-slate-600 focus:outline-none focus:ring-2 focus:ring-red-500">
            <option>近 30 天新用户</option>
            <option>近 60 天新用户</option>
            <option>近 90 天新用户</option>
          </select>
        </div>
        <RetentionChart data={retentionData} />

        {/* Key Retention Metrics */}
        <div className="grid grid-cols-5 gap-4 mt-6 pt-6 border-t border-slate-100">
          {[
            { day: 'D1', rate: retentionData.d1 },
            { day: 'D3', rate: retentionData.d3 },
            { day: 'D7', rate: retentionData.d7 },
            { day: 'D14', rate: retentionData.d14 },
            { day: 'D30', rate: retentionData.d30 },
          ].map(item => (
            <div key={item.day} className="text-center">
              <p className="text-2xl font-bold text-slate-900">{item.rate}%</p>
              <p className="text-sm text-slate-500">{item.day} 留存</p>
            </div>
          ))}
        </div>
      </div>

      {/* Churn Warning */}
      {churnRiskCluster && churnRiskCluster.count > 0 && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-red-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                  <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-900">流失预警</h3>
                <p className="text-sm text-slate-500">
                  {churnRiskCluster.count.toLocaleString()} 位用户 7天以上未活跃
                </p>
              </div>
            </div>
            <button className="px-4 py-2 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700 transition-colors">
              批量发送召回通知
            </button>
          </div>

          <div className="bg-red-50 rounded-xl p-4">
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <p className="text-sm text-red-700">
                  这些用户可能即将流失，建议通过推送通知、邮件或短信进行召回。
                </p>
              </div>
              <Link
                href="/admin/users?status=inactive"
                className="px-4 py-2 bg-white border border-red-200 rounded-lg text-sm text-red-600 hover:bg-red-50 transition-colors whitespace-nowrap"
              >
                查看用户列表
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* User Lifecycle Distribution */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <h3 className="text-lg font-semibold text-slate-900 mb-6">用户生命周期分布</h3>
        <div className="grid grid-cols-4 gap-4">
          {lifecycleData.map(item => (
            <div key={item.stage} className="relative">
              <div className="text-center mb-4">
                <p className="text-sm text-slate-500">{item.stage}</p>
                <p className="text-xs text-slate-400">{item.desc}</p>
              </div>
              <div className="h-32 flex items-end justify-center">
                <div
                  className="w-16 rounded-t-lg transition-all"
                  style={{
                    height: `${Math.max(item.percent * 1.5, 10)}%`,
                    backgroundColor: item.color,
                  }}
                />
              </div>
              <div className="text-center mt-3">
                <p className="text-xl font-bold text-slate-900">{item.count.toLocaleString()}</p>
                <p className="text-sm text-slate-500">{item.percent}%</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Retention Insights */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">留存洞察</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-green-50 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-5 h-5 text-green-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              <span className="text-sm font-medium text-green-700">优势</span>
            </div>
            <p className="text-sm text-green-600">
              D1 留存率 {retentionData.d1}% 表现良好，新用户首日体验较佳
            </p>
          </div>
          <div className="bg-orange-50 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-5 h-5 text-orange-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <span className="text-sm font-medium text-orange-700">关注点</span>
            </div>
            <p className="text-sm text-orange-600">
              D3 到 D7 留存下降 {retentionData.d3 - retentionData.d7}%，需优化首周学习体验
            </p>
          </div>
          <div className="bg-blue-50 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-5 h-5 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 16v-4" />
                <path d="M12 8h.01" />
              </svg>
              <span className="text-sm font-medium text-blue-700">建议</span>
            </div>
            <p className="text-sm text-blue-600">
              建议在 D3 发送学习提醒，D7 推送个性化课程推荐
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
