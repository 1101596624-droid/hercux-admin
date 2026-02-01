'use client';

import { Card } from '@/components/ui';
import { Button } from '@/components/ui';
import Link from 'next/link';

interface AIPlannerProps {
  hasActivePlan?: boolean;
  planSummary?: {
    sport: string;
    phase: string;
    currentWeek: number;
    totalWeeks: number;
    todayWorkout?: string;
  };
}

export function AIPlanner({ hasActivePlan, planSummary }: AIPlannerProps) {
  if (!hasActivePlan || !planSummary) {
    return (
      <Card className="bg-gradient-to-br from-primary-50 via-white to-blue-50 border-2 border-primary-100">
        <div className="p-8 text-center">
          <div className="text-5xl mb-4">🤖</div>
          <h3 className="text-xl font-bold text-dark-900 mb-3">
            AI 训练计划生成器
          </h3>
          <p className="text-dark-600 mb-6 max-w-md mx-auto">
            让 AI 根据你的运动项目、训练阶段和目标,为你量身定制专业的周期化训练计划
          </p>
          <Link href="/training">
            <Button size="lg" variant="primary">
              立即生成训练计划
            </Button>
          </Link>
        </div>
      </Card>
    );
  }

  return (
    <Card className="bg-gradient-to-br from-green-50 via-white to-blue-50 border-2 border-green-100">
      <div className="p-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">🎯</span>
              <h3 className="text-lg font-bold text-dark-900">
                我的训练计划
              </h3>
            </div>
            <div className="flex items-center gap-3 text-sm text-dark-600">
              <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded font-medium">
                {planSummary.sport}
              </span>
              <span>•</span>
              <span>{planSummary.phase}</span>
              <span>•</span>
              <span>第 {planSummary.currentWeek}/{planSummary.totalWeeks} 周</span>
            </div>
          </div>

          <Link href="/training">
            <Button variant="outline" size="sm">
              查看详情
            </Button>
          </Link>
        </div>

        {planSummary.todayWorkout && (
          <div className="bg-white rounded-lg p-4 border border-dark-200">
            <div className="text-sm text-dark-500 mb-2">今日训练</div>
            <p className="text-dark-900 font-medium">{planSummary.todayWorkout}</p>
          </div>
        )}

        <div className="mt-4 pt-4 border-t border-dark-200">
          <div className="flex items-center gap-2 text-sm text-dark-600">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span>AI 训练计划已激活</span>
          </div>
        </div>
      </div>
    </Card>
  );
}
