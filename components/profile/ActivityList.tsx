'use client';

import { Card, CardHeader, CardContent } from '@/components/ui';
import type { Activity } from '@/types/user';

interface ActivityListProps {
  activities: Activity[];
}

export function ActivityList({ activities }: ActivityListProps) {
  const activityIcons: Record<Activity['type'], string> = {
    course_completed: '🎓',
    node_completed: '✓',
    badge_earned: '🏆',
    plan_generated: '📋',
    quiz_passed: '📝',
  };

  const activityColors: Record<Activity['type'], string> = {
    course_completed: 'bg-green-50 border-green-200 text-green-900',
    node_completed: 'bg-blue-50 border-blue-200 text-blue-900',
    badge_earned: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    plan_generated: 'bg-purple-50 border-purple-200 text-purple-900',
    quiz_passed: 'bg-orange-50 border-orange-200 text-orange-900',
  };

  // Mock activities if empty
  const displayActivities = activities.length > 0 ? activities : [
    {
      id: '1',
      type: 'course_completed' as const,
      action: '完成了课程',
      detail: '运动生理学基础',
      timestamp: new Date().toISOString(),
    },
    {
      id: '2',
      type: 'badge_earned' as const,
      action: '获得徽章',
      detail: '学习达人',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: '3',
      type: 'quiz_passed' as const,
      action: '通过测验',
      detail: '第一章测验 - 95分',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
    },
  ];

  const formatTime = (timestamp: string | Date) => {
    const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}天前`;
    if (hours > 0) return `${hours}小时前`;
    return '刚刚';
  };

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-dark-900">最近活动</h3>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-3">
          {displayActivities.map((activity) => (
            <div
              key={activity.id}
              className={`flex items-start gap-3 p-3 rounded-lg border ${activityColors[activity.type]}`}
            >
              <div className="text-2xl flex-shrink-0">
                {activityIcons[activity.type]}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium mb-1">
                  {activity.action}
                </p>
                <p className="text-sm opacity-80 truncate">
                  {activity.detail}
                </p>
              </div>
              <div className="text-xs opacity-60 flex-shrink-0">
                {formatTime(activity.timestamp)}
              </div>
            </div>
          ))}
        </div>

        {displayActivities.length === 0 && (
          <div className="text-center py-8 text-dark-500">
            <div className="text-4xl mb-2">📭</div>
            <p>暂无活动记录</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
