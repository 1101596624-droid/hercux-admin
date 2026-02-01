'use client';

import { Card, CardHeader, CardContent, Badge } from '@/components/ui';
import type { User, UserStats } from '@/types/user';

interface ProfileCardProps {
  user: User;
  stats: UserStats | null;
}

export function ProfileCard({ user, stats }: ProfileCardProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row gap-6">
          {/* Avatar */}
          <div className="flex-shrink-0">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary-500 to-blue-600 flex items-center justify-center text-white font-bold text-3xl">
              {user.name.charAt(0).toUpperCase()}
            </div>
          </div>

          {/* Info */}
          <div className="flex-1">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold text-dark-900 mb-1">
                  {user.name}
                </h2>
                <p className="text-dark-600">{user.email}</p>
              </div>
              <Badge variant="primary">{user.level}</Badge>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 bg-dark-50 rounded-lg">
                <div className="text-2xl font-bold text-primary-600">
                  {stats?.totalCourses || 0}
                </div>
                <div className="text-sm text-dark-600">已学课程</div>
              </div>
              <div className="text-center p-3 bg-dark-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {stats?.completedNodes || 0}
                </div>
                <div className="text-sm text-dark-600">完成节点</div>
              </div>
              <div className="text-center p-3 bg-dark-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {user.badges?.length || 0}
                </div>
                <div className="text-sm text-dark-600">获得徽章</div>
              </div>
            </div>

            {/* Badges Preview */}
            {user.badges && user.badges.length > 0 && (
              <div className="mt-4 pt-4 border-t border-dark-200">
                <h3 className="text-sm font-semibold text-dark-700 mb-2">
                  最新徽章
                </h3>
                <div className="flex gap-2 flex-wrap">
                  {user.badges.slice(0, 5).map((badge) => (
                    <div
                      key={badge.id}
                      className="flex items-center gap-2 px-3 py-1.5 bg-yellow-50 border border-yellow-200 rounded-full"
                      title={badge.description}
                    >
                      <span className="text-lg">{badge.icon}</span>
                      <span className="text-xs font-medium text-yellow-900">
                        {badge.name}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
