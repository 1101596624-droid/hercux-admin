'use client';

import { Card, CardHeader, CardContent } from '@/components/ui';

interface PhaseSelectorProps {
  sport: string;
  onSelect: (phase: string) => void;
}

export function PhaseSelector({ sport, onSelect }: PhaseSelectorProps) {
  const phases = [
    {
      id: 'beginner',
      name: '入门阶段',
      icon: '🌱',
      description: '适合刚开始训练的新手',
      features: ['基础动作学习', '循序渐进', '建立习惯'],
      duration: '4-8周',
      color: 'border-green-500',
    },
    {
      id: 'intermediate',
      name: '进阶阶段',
      icon: '📈',
      description: '有一定基础,想要提升',
      features: ['强度提升', '技术优化', '系统训练'],
      duration: '8-12周',
      color: 'border-blue-500',
    },
    {
      id: 'advanced',
      name: '高级阶段',
      icon: '🏆',
      description: '经验丰富,追求卓越',
      features: ['专项突破', '竞技水平', '精细调整'],
      duration: '12-16周',
      color: 'border-purple-500',
    },
    {
      id: 'maintenance',
      name: '维持阶段',
      icon: '⚖️',
      description: '保持当前水平和状态',
      features: ['稳定训练', '防止退步', '长期坚持'],
      duration: '持续',
      color: 'border-yellow-500',
    },
  ];

  return (
    <div>
      <Card>
        <CardHeader>
          <h2 className="text-2xl font-bold text-dark-900">
            选择训练阶段
          </h2>
          <p className="text-dark-600">
            根据您的当前水平选择合适的训练阶段
          </p>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {phases.map((phase) => (
              <button
                key={phase.id}
                onClick={() => onSelect(phase.id)}
                className={`group text-left p-6 rounded-xl border-2 ${phase.color} bg-white hover:shadow-xl transition-all duration-200`}
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className="text-4xl transform group-hover:scale-110 transition-transform">
                    {phase.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-dark-900 mb-1">
                      {phase.name}
                    </h3>
                    <p className="text-sm text-dark-600">
                      {phase.description}
                    </p>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  {phase.features.map((feature) => (
                    <div key={feature} className="flex items-center gap-2 text-sm text-dark-700">
                      <span className="text-primary-600">✓</span>
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-dark-500">建议周期</span>
                  <span className="font-semibold text-dark-900">{phase.duration}</span>
                </div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
