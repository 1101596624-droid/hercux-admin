'use client';

import { Card, CardHeader, CardContent } from '@/components/ui';

interface SportSelectorProps {
  onSelect: (sport: string) => void;
}

export function SportSelector({ onSelect }: SportSelectorProps) {
  const sports = [
    {
      id: 'running',
      name: '跑步',
      icon: '🏃',
      description: '提升心肺功能,增强耐力',
      color: 'from-blue-500 to-blue-600',
    },
    {
      id: 'strength',
      name: '力量训练',
      icon: '🏋️',
      description: '增肌塑形,提高基础代谢',
      color: 'from-red-500 to-red-600',
    },
    {
      id: 'swimming',
      name: '游泳',
      icon: '🏊',
      description: '全身协调,低冲击有氧',
      color: 'from-cyan-500 to-cyan-600',
    },
    {
      id: 'cycling',
      name: '骑行',
      icon: '🚴',
      description: '户外有氧,增强腿部力量',
      color: 'from-green-500 to-green-600',
    },
    {
      id: 'yoga',
      name: '瑜伽',
      icon: '🧘',
      description: '柔韧平衡,身心放松',
      color: 'from-purple-500 to-purple-600',
    },
    {
      id: 'basketball',
      name: '篮球',
      icon: '🏀',
      description: '团队协作,爆发力训练',
      color: 'from-orange-500 to-orange-600',
    },
    {
      id: 'soccer',
      name: '足球',
      icon: '⚽',
      description: '全场奔跑,战术配合',
      color: 'from-indigo-500 to-indigo-600',
    },
    {
      id: 'mixed',
      name: '综合训练',
      icon: '💪',
      description: '多项目组合,全面发展',
      color: 'from-pink-500 to-pink-600',
    },
  ];

  return (
    <div>
      <Card>
        <CardHeader>
          <h2 className="text-2xl font-bold text-dark-900">
            选择您的运动项目
          </h2>
          <p className="text-dark-600">
            我们将根据您的选择定制专业的训练计划
          </p>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {sports.map((sport) => (
              <button
                key={sport.id}
                onClick={() => onSelect(sport.id)}
                className="group relative p-6 rounded-xl border-2 border-dark-200 hover:border-primary-500 bg-white hover:shadow-lg transition-all duration-200"
              >
                <div className={`absolute inset-0 rounded-xl bg-gradient-to-br ${sport.color} opacity-0 group-hover:opacity-10 transition-opacity`} />
                <div className="relative">
                  <div className="text-5xl mb-3 transform group-hover:scale-110 transition-transform">
                    {sport.icon}
                  </div>
                  <h3 className="text-lg font-bold text-dark-900 mb-2">
                    {sport.name}
                  </h3>
                  <p className="text-sm text-dark-600">
                    {sport.description}
                  </p>
                </div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
