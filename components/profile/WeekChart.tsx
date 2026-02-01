'use client';

import { Card, CardHeader, CardContent } from '@/components/ui';

interface WeekChartProps {
  weeklyProgress?: number;
  weeklyGoal?: number;
}

export function WeekChart({ weeklyProgress = 0, weeklyGoal = 100 }: WeekChartProps) {
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  const mockData = [40, 65, 30, 80, 55, 20, 45]; // Mock weekly data

  const maxValue = Math.max(...mockData);
  const progressPercent = Math.min((weeklyProgress / weeklyGoal) * 100, 100);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-dark-900">本周学习</h3>
          <div className="text-sm text-dark-600">
            {weeklyProgress} / {weeklyGoal} 分钟
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-dark-600">周目标进度</span>
            <span className="text-sm font-semibold text-primary-600">
              {progressPercent.toFixed(0)}%
            </span>
          </div>
          <div className="h-2 bg-dark-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary-500 to-blue-600 rounded-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Bar Chart */}
        <div className="flex items-end justify-between gap-2 h-40">
          {days.map((day, index) => {
            const height = (mockData[index] / maxValue) * 100;
            const isToday = index === new Date().getDay() - 1;

            return (
              <div key={day} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full flex items-end justify-center h-32">
                  <div
                    className={`w-full rounded-t-lg transition-all duration-300 ${
                      isToday
                        ? 'bg-gradient-to-t from-primary-500 to-primary-400'
                        : 'bg-dark-200 hover:bg-primary-200'
                    }`}
                    style={{ height: `${height}%` }}
                    title={`${mockData[index]}分钟`}
                  />
                </div>
                <span className={`text-xs ${isToday ? 'font-bold text-primary-600' : 'text-dark-600'}`}>
                  {day}
                </span>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
