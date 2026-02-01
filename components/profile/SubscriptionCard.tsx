'use client';

import { Card, CardHeader, CardContent, Button, Badge } from '@/components/ui';

export function SubscriptionCard() {
  const isPro = false; // Mock subscription status
  const expiryDate = new Date(Date.now() + 30 * 24 * 3600000); // 30 days from now

  const features = {
    free: [
      '基础课程访问',
      '每日 3 次 AI 对话',
      '基础模拟器',
      '社区访问',
    ],
    pro: [
      '全部课程无限访问',
      '无限 AI 对话',
      '高级模拟器',
      '优先技术支持',
      '离线下载',
      '专属徽章',
    ],
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-dark-900">订阅状态</h3>
          <Badge variant={isPro ? 'success' : 'default'}>
            {isPro ? 'PRO' : 'FREE'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        {isPro ? (
          <>
            {/* Pro Subscription Info */}
            <div className="mb-4 p-4 bg-gradient-to-br from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">👑</span>
                <span className="font-semibold text-yellow-900">
                  HERCU Pro
                </span>
              </div>
              <p className="text-sm text-yellow-800">
                有效期至: {expiryDate.toLocaleDateString('zh-CN')}
              </p>
            </div>

            {/* Pro Features */}
            <div className="space-y-2 mb-4">
              {features.pro.map((feature) => (
                <div key={feature} className="flex items-center gap-2 text-sm">
                  <span className="text-green-600">✓</span>
                  <span className="text-dark-700">{feature}</span>
                </div>
              ))}
            </div>

            <Button variant="outline" size="sm" className="w-full">
              续费订阅
            </Button>
          </>
        ) : (
          <>
            {/* Free Plan Info */}
            <div className="mb-4 p-4 bg-dark-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">📚</span>
                <span className="font-semibold text-dark-900">
                  免费计划
                </span>
              </div>
              <p className="text-sm text-dark-600">
                升级到 Pro 解锁全部功能
              </p>
            </div>

            {/* Free Features */}
            <div className="space-y-2 mb-4">
              {features.free.map((feature) => (
                <div key={feature} className="flex items-center gap-2 text-sm">
                  <span className="text-primary-600">✓</span>
                  <span className="text-dark-700">{feature}</span>
                </div>
              ))}
            </div>

            {/* Upgrade CTA */}
            <div className="space-y-2">
              <Button variant="primary" size="sm" className="w-full">
                <span className="mr-2">👑</span>
                升级到 Pro
              </Button>
              <p className="text-xs text-center text-dark-500">
                ¥99/月 或 ¥899/年
              </p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
