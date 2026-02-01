'use client';

import { Card, CardHeader, CardContent, Button } from '@/components/ui';
import { useState } from 'react';

interface GoalSelectorProps {
  sport: string;
  phase: string;
  onSelect: (goal: string) => void;
}

export function GoalSelector({ sport, phase, onSelect }: GoalSelectorProps) {
  const [selectedGoal, setSelectedGoal] = useState<string>('');
  const [customGoal, setCustomGoal] = useState('');

  const goals = [
    {
      id: 'weight-loss',
      name: '减重塑形',
      icon: '⚖️',
      description: '科学减脂,保持肌肉',
      metrics: ['体脂率', '体重', '围度'],
    },
    {
      id: 'muscle-gain',
      name: '增肌增重',
      icon: '💪',
      description: '增加肌肉量和力量',
      metrics: ['肌肉量', '力量水平', '蛋白摄入'],
    },
    {
      id: 'endurance',
      name: '提升耐力',
      icon: '🏃',
      description: '增强心肺功能和持久力',
      metrics: ['VO2 Max', '心率', '跑量'],
    },
    {
      id: 'strength',
      name: '增强力量',
      icon: '🏋️',
      description: '提高最大力量和爆发力',
      metrics: ['最大力量', '1RM', '功率'],
    },
    {
      id: 'flexibility',
      name: '改善柔韧',
      icon: '🤸',
      description: '提高关节活动度和灵活性',
      metrics: ['柔韧度', '活动范围', '平衡性'],
    },
    {
      id: 'health',
      name: '健康维护',
      icon: '❤️',
      description: '改善整体健康状况',
      metrics: ['血压', '血糖', '睡眠质量'],
    },
  ];

  const handleConfirm = () => {
    if (selectedGoal) {
      onSelect(selectedGoal === 'custom' ? customGoal : selectedGoal);
    }
  };

  return (
    <div>
      <Card>
        <CardHeader>
          <h2 className="text-2xl font-bold text-dark-900">
            设定训练目标
          </h2>
          <p className="text-dark-600">
            明确的目标能帮助您更好地坚持训练
          </p>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            {goals.map((goal) => (
              <button
                key={goal.id}
                onClick={() => setSelectedGoal(goal.id)}
                className={`text-left p-5 rounded-xl border-2 transition-all duration-200 ${
                  selectedGoal === goal.id
                    ? 'border-primary-500 bg-primary-50 shadow-md'
                    : 'border-dark-200 bg-white hover:border-primary-300'
                }`}
              >
                <div className="text-3xl mb-3">{goal.icon}</div>
                <h3 className="text-lg font-bold text-dark-900 mb-2">
                  {goal.name}
                </h3>
                <p className="text-sm text-dark-600 mb-3">
                  {goal.description}
                </p>
                <div className="space-y-1">
                  {goal.metrics.map((metric) => (
                    <div key={metric} className="flex items-center gap-2 text-xs text-dark-500">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                      <span>{metric}</span>
                    </div>
                  ))}
                </div>
              </button>
            ))}
          </div>

          {/* Custom Goal */}
          <div className="mb-6">
            <button
              onClick={() => setSelectedGoal('custom')}
              className={`w-full text-left p-5 rounded-xl border-2 transition-all duration-200 ${
                selectedGoal === 'custom'
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-dark-200 bg-white hover:border-primary-300'
              }`}
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="text-3xl">🎯</span>
                <span className="text-lg font-bold text-dark-900">
                  自定义目标
                </span>
              </div>
              {selectedGoal === 'custom' && (
                <input
                  type="text"
                  value={customGoal}
                  onChange={(e) => setCustomGoal(e.target.value)}
                  placeholder="输入您的训练目标..."
                  className="w-full px-4 py-2 border border-dark-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  autoFocus
                />
              )}
            </button>
          </div>

          {/* Confirm Button */}
          <Button
            variant="primary"
            size="lg"
            className="w-full"
            onClick={handleConfirm}
            disabled={!selectedGoal || (selectedGoal === 'custom' && !customGoal)}
          >
            确认并生成计划
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
