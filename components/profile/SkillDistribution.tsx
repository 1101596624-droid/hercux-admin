'use client';

import { Card, CardHeader, CardContent, CircularProgress } from '@/components/ui';
import type { UserStats } from '@/types/user';

interface SkillDistributionProps {
  stats: UserStats | null;
}

export function SkillDistribution({ stats }: SkillDistributionProps) {
  const skills = [
    { name: '运动生理学', level: 75, color: 'text-blue-600', bgColor: 'bg-blue-100' },
    { name: '运动训练学', level: 60, color: 'text-green-600', bgColor: 'bg-green-100' },
    { name: '运动生物力学', level: 45, color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { name: '运动营养学', level: 30, color: 'text-purple-600', bgColor: 'bg-purple-100' },
  ];

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-dark-900">技能分布</h3>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-4">
          {skills.map((skill) => (
            <div key={skill.name}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-dark-700">
                  {skill.name}
                </span>
                <span className={`text-sm font-semibold ${skill.color}`}>
                  {skill.level}%
                </span>
              </div>
              <div className="h-2 bg-dark-100 rounded-full overflow-hidden">
                <div
                  className={`h-full ${skill.bgColor} rounded-full transition-all duration-500`}
                  style={{ width: `${skill.level}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Overall Progress */}
        <div className="mt-6 pt-6 border-t border-dark-200">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-dark-900 mb-1">综合掌握度</h4>
              <p className="text-sm text-dark-600">
                已掌握 {stats?.completedNodes || 0} 个知识节点
              </p>
            </div>
            <CircularProgress
              value={stats?.averageScore || 0}
              max={100}
              size={80}
              strokeWidth={8}
              variant="success"
              showLabel
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
