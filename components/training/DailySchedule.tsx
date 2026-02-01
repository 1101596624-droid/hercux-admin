'use client';

import { Card, CardHeader, CardContent, Button } from '@/components/ui';
import { useState } from 'react';

interface DailyScheduleProps {
  plan: any;
}

export function DailySchedule({ plan }: DailyScheduleProps) {
  const [selectedDate] = useState(new Date());

  const exercises = [
    {
      id: 1,
      name: '杠铃卧推',
      sets: 4,
      reps: '8-10',
      rest: '90秒',
      weight: '60kg',
      notes: '保持肩胛骨后缩',
      completed: true,
    },
    {
      id: 2,
      name: '哑铃飞鸟',
      sets: 3,
      reps: '12-15',
      rest: '60秒',
      weight: '15kg',
      notes: '控制动作幅度',
      completed: true,
    },
    {
      id: 3,
      name: '双杠臂屈伸',
      sets: 3,
      reps: '10-12',
      rest: '60秒',
      weight: '自重',
      notes: '身体保持垂直',
      completed: false,
    },
    {
      id: 4,
      name: '绳索下压',
      sets: 3,
      reps: '15-20',
      rest: '45秒',
      weight: '25kg',
      notes: '肘关节固定',
      completed: false,
    },
  ];

  const completedExercises = exercises.filter((e) => e.completed).length;
  const totalExercises = exercises.length;
  const progress = (completedExercises / totalExercises) * 100;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-dark-900">今日训练</h3>
            <p className="text-dark-600">
              {selectedDate.toLocaleDateString('zh-CN', {
                month: 'long',
                day: 'numeric',
                weekday: 'long',
              })}
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-primary-600">
              {completedExercises}/{totalExercises}
            </div>
            <div className="text-sm text-dark-600">完成度</div>
          </div>
        </div>
        {/* Progress Bar */}
        <div className="mt-4">
          <div className="h-2 bg-dark-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary-500 to-blue-600 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        {/* Exercise List */}
        <div className="space-y-4">
          {exercises.map((exercise) => (
            <div
              key={exercise.id}
              className={`p-4 border-2 rounded-lg transition-all ${
                exercise.completed
                  ? 'bg-green-50 border-green-200'
                  : 'bg-white border-dark-200 hover:border-primary-300'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="text-lg font-bold text-dark-900 mb-1">
                    {exercise.name}
                  </h4>
                  <div className="flex items-center gap-4 text-sm text-dark-600">
                    <span>🔢 {exercise.sets} 组</span>
                    <span>🔁 {exercise.reps} 次</span>
                    <span>⏱️ 休息 {exercise.rest}</span>
                  </div>
                </div>
                <button
                  className={`flex-shrink-0 w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all ${
                    exercise.completed
                      ? 'bg-green-500 border-green-500 text-white'
                      : 'border-dark-300 hover:border-primary-500'
                  }`}
                >
                  {exercise.completed && '✓'}
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="p-2 bg-white rounded-lg border border-dark-200">
                  <span className="text-dark-600">重量: </span>
                  <span className="font-semibold text-dark-900">
                    {exercise.weight}
                  </span>
                </div>
                <div className="p-2 bg-white rounded-lg border border-dark-200">
                  <span className="text-dark-600">备注: </span>
                  <span className="font-semibold text-dark-900">
                    {exercise.notes}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="mt-6 grid grid-cols-2 gap-3">
          <Button variant="outline" size="md" className="w-full">
            修改计划
          </Button>
          <Button variant="primary" size="md" className="w-full">
            完成训练
          </Button>
        </div>

        {/* Post-workout Note */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start gap-3">
            <span className="text-2xl">💡</span>
            <div className="flex-1 text-sm">
              <div className="font-semibold text-blue-900 mb-1">
                训练后建议
              </div>
              <p className="text-blue-800">
                完成训练后进行10-15分钟拉伸,补充20-30g蛋白质,充分休息让肌肉恢复生长。
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
