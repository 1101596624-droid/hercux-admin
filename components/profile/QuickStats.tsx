'use client';

import { Card, CardHeader, CardContent } from '@/components/ui';
import type { UserStats } from '@/types/user';

interface QuickStatsProps {
  stats: UserStats | null;
}

export function QuickStats({ stats }: QuickStatsProps) {
  const statItems = [
    {
      label: '学习时长',
      value: `${stats?.studyTime || 0}h`,
      icon: '⏱️',
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      label: '平均分数',
      value: `${stats?.averageScore || 0}%`,
      icon: '📊',
      color: 'text-green-600',
      bg: 'bg-green-50',
    },
    {
      label: '连续学习',
      value: `${stats?.currentStreak || 0}天`,
      icon: '🔥',
      color: 'text-orange-600',
      bg: 'bg-orange-50',
    },
    {
      label: '最高连续',
      value: `${stats?.longestStreak || 0}天`,
      icon: '🏆',
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
    },
  ];

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-dark-900">快速统计</h3>
      </CardHeader>
      <CardContent className="p-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {statItems.map((item) => (
            <div
              key={item.label}
              className={`${item.bg} rounded-lg p-4 text-center`}
            >
              <div className="text-3xl mb-2">{item.icon}</div>
              <div className={`text-2xl font-bold ${item.color} mb-1`}>
                {item.value}
              </div>
              <div className="text-sm text-dark-600">{item.label}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
