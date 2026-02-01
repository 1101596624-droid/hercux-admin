'use client';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { Badge as UIBadge } from '@/components/ui';

interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  unlockedAt?: Date;
  progress?: number;
  requirement?: number;
}

interface BadgesPanelProps {
  badges: Badge[];
}

const rarityColors = {
  common: 'bg-gray-100 border-gray-300',
  rare: 'bg-blue-50 border-blue-300',
  epic: 'bg-purple-50 border-purple-300',
  legendary: 'bg-yellow-50 border-yellow-300',
};

const rarityLabels = {
  common: '普通',
  rare: '稀有',
  epic: '史诗',
  legendary: '传说',
};

export function BadgesPanel({ badges }: BadgesPanelProps) {
  const unlockedBadges = badges.filter(b => b.unlockedAt);
  const lockedBadges = badges.filter(b => !b.unlockedAt);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>成就徽章</CardTitle>
          <UIBadge variant="primary">
            {unlockedBadges.length} / {badges.length}
          </UIBadge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {/* Unlocked badges first */}
          {unlockedBadges.map((badge) => (
            <div
              key={badge.id}
              className={`relative p-4 rounded-xl border-2 ${rarityColors[badge.rarity]}
                         hover:scale-105 transition-transform cursor-pointer group`}
            >
              <div className="text-center">
                <div className="text-4xl mb-2">{badge.icon}</div>
                <h4 className="text-sm font-semibold text-dark-900 mb-1">
                  {badge.name}
                </h4>
                <p className="text-xs text-dark-500 mb-2 line-clamp-2">
                  {badge.description}
                </p>
                <UIBadge size="sm" variant="default">
                  {rarityLabels[badge.rarity]}
                </UIBadge>
              </div>

              {/* Tooltip on hover */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2
                            opacity-0 group-hover:opacity-100 transition-opacity
                            bg-dark-900 text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap
                            pointer-events-none z-10">
                解锁于 {badge.unlockedAt?.toLocaleDateString('zh-CN')}
                <div className="absolute top-full left-1/2 -translate-x-1/2
                              border-4 border-transparent border-t-dark-900" />
              </div>
            </div>
          ))}

          {/* Locked badges */}
          {lockedBadges.map((badge) => (
            <div
              key={badge.id}
              className="relative p-4 rounded-xl border-2 border-dark-200 bg-dark-50
                         opacity-60 hover:opacity-80 transition-opacity cursor-pointer group"
            >
              <div className="text-center">
                <div className="text-4xl mb-2 grayscale">{badge.icon}</div>
                <h4 className="text-sm font-semibold text-dark-700 mb-1">
                  {badge.name}
                </h4>
                <p className="text-xs text-dark-500 mb-2 line-clamp-2">
                  {badge.description}
                </p>
                {badge.progress !== undefined && badge.requirement !== undefined && (
                  <div className="text-xs text-dark-600">
                    {badge.progress} / {badge.requirement}
                  </div>
                )}
              </div>

              {/* Lock icon */}
              <div className="absolute top-2 right-2 text-dark-400">
                🔒
              </div>
            </div>
          ))}
        </div>

        {badges.length === 0 && (
          <div className="text-center py-12">
            <div className="text-4xl mb-3">🏆</div>
            <p className="text-dark-500">暂无成就徽章</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
