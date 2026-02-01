'use client';

import { Card } from '@/components/ui';
import { Progress, CircularProgress } from '@/components/ui';

interface StatsCardsProps {
  totalHours: number;
  weeklyChange: number;
  currentStreak: number;
  weeklyProgress: number;
  weeklyGoal: number;
  intensity: number;
}

export function StatsCards({
  totalHours,
  weeklyChange,
  currentStreak,
  weeklyProgress,
  weeklyGoal,
  intensity
}: StatsCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* 学习时长 */}
      <Card className="p-6 hover:shadow-elevated transition-shadow">
        <div className="text-sm text-dark-500 mb-2">学习时长</div>
        <div className="text-3xl font-bold text-dark-900">
          {totalHours}
          <span className="text-lg text-dark-400 ml-1">小时</span>
        </div>
        <div className={`text-xs mt-2 ${weeklyChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {weeklyChange >= 0 ? '↑' : '↓'} 本周 {weeklyChange >= 0 ? '+' : ''}{weeklyChange}h
        </div>
      </Card>

      {/* 连续天数 */}
      <Card className="p-6 hover:shadow-elevated transition-shadow">
        <div className="text-sm text-dark-500 mb-2">连续天数</div>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-dark-900">{currentStreak}</span>
          <span className="text-lg text-dark-400">天</span>
        </div>
        <div className="text-xs text-dark-400 mt-2 flex items-center gap-1">
          🔥 继续保持！
        </div>
      </Card>

      {/* 周目标进度 */}
      <Card className="p-6 hover:shadow-elevated transition-shadow">
        <div className="text-sm text-dark-500 mb-3">周目标进度</div>
        <div className="flex items-center justify-center">
          <CircularProgress
            value={weeklyProgress}
            max={weeklyGoal}
            size={100}
            strokeWidth={8}
            variant="default"
            showLabel
          />
        </div>
        <div className="text-xs text-dark-600 text-center mt-2">
          {weeklyProgress} / {weeklyGoal} 小时
        </div>
      </Card>

      {/* 训练强度 */}
      <Card className="p-6 hover:shadow-elevated transition-shadow">
        <div className="text-sm text-dark-500 mb-2">训练强度</div>
        <div className="text-3xl font-bold text-primary-600">{intensity}</div>
        <div className="text-xs text-dark-400 mt-2">
          {intensity <= 3 && 'RPE 1-3 (轻度)'}
          {intensity > 3 && intensity <= 5 && 'RPE 4-5 (适中)'}
          {intensity > 5 && intensity <= 7 && 'RPE 6-7 (较高)'}
          {intensity > 7 && 'RPE 8-10 (高强度)'}
        </div>
      </Card>
    </div>
  );
}
