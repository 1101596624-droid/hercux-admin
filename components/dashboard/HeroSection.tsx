'use client';

import { Card } from '@/components/ui';
import { Progress } from '@/components/ui';
import { Button } from '@/components/ui';
import Link from 'next/link';

interface HeroSectionProps {
  currentCourse?: {
    id: string;
    title: string;
    subtitle: string;
    progress: number;
    currentNode: string;
    totalNodes: number;
    completedNodes: number;
  };
}

export function HeroSection({ currentCourse }: HeroSectionProps) {
  if (!currentCourse) {
    return (
      <Card className="p-12 text-center">
        <div className="max-w-md mx-auto">
          <div className="text-6xl mb-6">🎯</div>
          <h2 className="text-2xl font-bold text-dark-900 mb-3">
            开始你的学习之旅
          </h2>
          <p className="text-dark-500 mb-6">
            选择一门课程,开启深度认知学习体验
          </p>
          <Link href="/courses">
            <Button size="lg">浏览课程</Button>
          </Link>
        </div>
      </Card>
    );
  }

  return (
    <Card variant="elevated" className="bg-gradient-to-br from-primary-50 to-white overflow-hidden">
      <div className="p-8">
        <div className="flex items-start justify-between mb-6">
          <div className="flex-1">
            <div className="text-sm text-primary-600 font-medium mb-2">
              当前正在学习
            </div>
            <h2 className="text-2xl font-bold text-dark-900 mb-2">
              {currentCourse.title}
            </h2>
            <p className="text-dark-600">{currentCourse.subtitle}</p>
          </div>

          <Link href={`/courses/${currentCourse.id}/learn`}>
            <Button variant="primary" size="lg">
              继续学习
            </Button>
          </Link>
        </div>

        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-dark-600">整体进度</span>
              <span className="text-sm font-semibold text-dark-900">
                {currentCourse.progress}%
              </span>
            </div>
            <Progress value={currentCourse.progress} size="lg" />
          </div>

          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-dark-600">
                已完成 <span className="font-semibold text-dark-900">{currentCourse.completedNodes}</span> 个节点
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-500" />
              <span className="text-dark-600">
                当前节点: <span className="font-semibold text-dark-900">{currentCourse.currentNode}</span>
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-dark-300" />
              <span className="text-dark-600">
                共 <span className="font-semibold text-dark-900">{currentCourse.totalNodes}</span> 个节点
              </span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
