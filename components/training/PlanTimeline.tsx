'use client';

import { Card, CardHeader, CardContent, Badge } from '@/components/ui';

import type { TrainingPlan } from '@/lib/api/training';

interface PlanTimelineProps {
  plan: TrainingPlan;
}

export function PlanTimeline({ plan }: PlanTimelineProps) {
  const phases = [
    {
      id: 1,
      name: '基础适应期',
      weeks: '第 1-2 周',
      focus: '建立基础,适应训练',
      color: 'bg-green-500',
      items: [
        '低强度有氧训练',
        '基本动作模式学习',
        '建立训练习惯',
        '评估身体状况',
      ],
      status: 'completed',
    },
    {
      id: 2,
      name: '强度提升期',
      weeks: '第 3-6 周',
      focus: '逐步增加训练强度',
      color: 'bg-blue-500',
      items: [
        '中等强度训练',
        '动作质量提升',
        '引入负重训练',
        '营养计划调整',
      ],
      status: 'current',
    },
    {
      id: 3,
      name: '专项训练期',
      weeks: '第 7-10 周',
      focus: '针对性强化训练',
      color: 'bg-purple-500',
      items: [
        '高强度间歇训练',
        '专项技术训练',
        '力量突破',
        '恢复优化',
      ],
      status: 'upcoming',
    },
    {
      id: 4,
      name: '巩固维持期',
      weeks: '第 11-12 周',
      focus: '巩固成果,防止退步',
      color: 'bg-yellow-500',
      items: [
        '适度降低强度',
        '维持训练频率',
        '测试评估',
        '制定长期计划',
      ],
      status: 'upcoming',
    },
  ];

  return (
    <Card>
      <CardHeader>
        <h3 className="text-xl font-bold text-dark-900">训练时间线</h3>
        <p className="text-dark-600">12 周系统化训练计划</p>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-8">
          {phases.map((phase, index) => (
            <div key={phase.id} className="relative">
              {/* Timeline Line */}
              {index < phases.length - 1 && (
                <div className="absolute left-6 top-14 w-0.5 h-full bg-dark-200" />
              )}

              <div className="flex gap-6">
                {/* Phase Indicator */}
                <div className="relative flex-shrink-0">
                  <div className={`w-12 h-12 rounded-full ${phase.color} flex items-center justify-center text-white font-bold text-lg`}>
                    {phase.id}
                  </div>
                  {phase.status === 'current' && (
                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full animate-pulse" />
                  )}
                </div>

                {/* Phase Content */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="text-lg font-bold text-dark-900">
                        {phase.name}
                      </h4>
                      <p className="text-sm text-dark-600">{phase.weeks}</p>
                    </div>
                    <Badge
                      variant={
                        phase.status === 'completed'
                          ? 'success'
                          : phase.status === 'current'
                          ? 'info'
                          : 'default'
                      }
                    >
                      {phase.status === 'completed'
                        ? '已完成'
                        : phase.status === 'current'
                        ? '进行中'
                        : '未开始'}
                    </Badge>
                  </div>

                  <p className="text-dark-700 mb-3 font-medium">
                    {phase.focus}
                  </p>

                  <div className="grid grid-cols-2 gap-2">
                    {phase.items.map((item) => (
                      <div
                        key={item}
                        className={`flex items-center gap-2 p-2 rounded-lg text-sm ${
                          phase.status === 'completed'
                            ? 'bg-green-50 text-green-900'
                            : phase.status === 'current'
                            ? 'bg-blue-50 text-blue-900'
                            : 'bg-dark-50 text-dark-700'
                        }`}
                      >
                        <span>
                          {phase.status === 'completed' ? '✓' : '•'}
                        </span>
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
