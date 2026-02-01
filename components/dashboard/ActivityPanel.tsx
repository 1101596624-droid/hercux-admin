'use client';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { Badge } from '@/components/ui';
import { formatDuration } from '@/lib/utils';
import type { Activity } from '@/types/user';

interface ActivityPanelProps {
  activities: Activity[];
}

const activityIcons: Record<Activity['type'], string> = {
  course_completed: '🎓',
  node_completed: '✓',
  badge_earned: '🏆',
  plan_generated: '📋',
  quiz_passed: '📝',
};

const activityColors: Record<Activity['type'], 'primary' | 'info' | 'warning' | 'success'> = {
  course_completed: 'success',
  node_completed: 'primary',
  badge_earned: 'warning',
  plan_generated: 'info',
  quiz_passed: 'primary',
};

export function ActivityPanel({ activities }: ActivityPanelProps) {
  const formatTimeAgo = (timestamp: string | Date): string => {
    const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays < 7) return `${diffDays}天前`;
    return date.toLocaleDateString('zh-CN');
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>最近活动</CardTitle>
      </CardHeader>
      <CardContent>
        {activities.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-3">📋</div>
            <p className="text-dark-500">暂无学习记录</p>
          </div>
        ) : (
          <div className="space-y-4">
            {activities.map((activity) => (
              <div
                key={activity.id}
                className="flex items-start gap-4 p-4 rounded-lg hover:bg-dark-50 transition-colors"
              >
                <div className="text-2xl">{activityIcons[activity.type]}</div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4 mb-1">
                    <h4 className="font-semibold text-dark-900 truncate">
                      {activity.action}
                    </h4>
                    <Badge variant={activityColors[activity.type]} size="sm">
                      {activity.type === 'course_completed' && '课程完成'}
                      {activity.type === 'node_completed' && '节点完成'}
                      {activity.type === 'badge_earned' && '获得徽章'}
                      {activity.type === 'plan_generated' && '计划生成'}
                      {activity.type === 'quiz_passed' && '测验通过'}
                    </Badge>
                  </div>

                  <p className="text-sm text-dark-600 mb-2">
                    {activity.detail}
                  </p>

                  <div className="flex items-center gap-4 text-xs text-dark-500">
                    <span>{formatTimeAgo(activity.timestamp)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
