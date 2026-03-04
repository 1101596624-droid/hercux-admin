'use client';

import { Card, CardHeader, CardContent, Badge } from '@/components/ui';
import { useState } from 'react';

import type { TrainingPlan } from '@/lib/api/training';

interface WeeklyViewProps {
  plan: TrainingPlan;
}

export function WeeklyView({ plan }: WeeklyViewProps) {
  const [selectedWeek, setSelectedWeek] = useState(1);

  const weeks = Array.from({ length: 12 }, (_, i) => i + 1);

  const weekSchedule = [
    {
      day: '周一',
      sessions: [
        { type: 'strength', name: '力量训练 - 上肢', duration: '45min', intensity: 'high' },
      ],
    },
    {
      day: '周二',
      sessions: [
        { type: 'cardio', name: '有氧训练', duration: '30min', intensity: 'medium' },
      ],
    },
    {
      day: '周三',
      sessions: [
        { type: 'strength', name: '力量训练 - 下肢', duration: '50min', intensity: 'high' },
      ],
    },
    {
      day: '周四',
      sessions: [
        { type: 'rest', name: '积极恢复', duration: '20min', intensity: 'low' },
      ],
    },
    {
      day: '周五',
      sessions: [
        { type: 'strength', name: '力量训练 - 核心', duration: '40min', intensity: 'medium' },
      ],
    },
    {
      day: '周六',
      sessions: [
        { type: 'cardio', name: '长时间有氧', duration: '60min', intensity: 'medium' },
        { type: 'flexibility', name: '拉伸放松', duration: '15min', intensity: 'low' },
      ],
    },
    {
      day: '周日',
      sessions: [
        { type: 'rest', name: '完全休息', duration: '-', intensity: 'rest' },
      ],
    },
  ];

  const typeColors: Record<string, string> = {
    strength: 'bg-red-100 text-red-900 border-red-200',
    cardio: 'bg-blue-100 text-blue-900 border-blue-200',
    flexibility: 'bg-purple-100 text-purple-900 border-purple-200',
    rest: 'bg-green-100 text-green-900 border-green-200',
  };

  const intensityLabels: Record<string, string> = {
    high: '高强度',
    medium: '中强度',
    low: '低强度',
    rest: '休息',
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-dark-900">周视图</h3>
            <p className="text-dark-600">查看每周详细训练安排</p>
          </div>
          <select
            value={selectedWeek}
            onChange={(e) => setSelectedWeek(Number(e.target.value))}
            className="px-4 py-2 border border-dark-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {weeks.map((week) => (
              <option key={week} value={week}>
                第 {week} 周
              </option>
            ))}
          </select>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-3">
          {weekSchedule.map((day) => (
            <div
              key={day.day}
              className="p-4 bg-white border border-dark-200 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-16 text-center">
                  <div className="text-sm font-bold text-dark-900">{day.day}</div>
                </div>
                <div className="flex-1 space-y-2">
                  {day.sessions.map((session, idx) => (
                    <div
                      key={idx}
                      className={`flex items-center justify-between p-3 border rounded-lg ${
                        typeColors[session.type] || 'bg-dark-50'
                      }`}
                    >
                      <div className="flex-1">
                        <div className="font-semibold mb-1">{session.name}</div>
                        <div className="flex items-center gap-3 text-xs opacity-80">
                          <span>⏱️ {session.duration}</span>
                          <span>• {intensityLabels[session.intensity]}</span>
                        </div>
                      </div>
                      {session.type !== 'rest' && (
                        <button className="px-3 py-1 text-xs font-medium bg-white rounded-md hover:bg-opacity-80 transition-colors">
                          查看详情
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Week Summary */}
        <div className="mt-6 p-4 bg-primary-50 border border-primary-200 rounded-lg">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-primary-600">5</div>
              <div className="text-sm text-dark-600">训练天数</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary-600">280</div>
              <div className="text-sm text-dark-600">总时长(分钟)</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary-600">1600</div>
              <div className="text-sm text-dark-600">预估消耗(卡)</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
