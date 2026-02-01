'use client';

import { Card, CardHeader, CardContent, Button } from '@/components/ui';
import Link from 'next/link';

export function SettingsPanel() {
  const settingGroups = [
    {
      title: '账户设置',
      items: [
        { icon: '👤', label: '个人资料', href: '/profile/edit' },
        { icon: '🔒', label: '密码安全', href: '/profile/security' },
        { icon: '📧', label: '邮箱设置', href: '/profile/email' },
      ],
    },
    {
      title: '学习偏好',
      items: [
        { icon: '🎯', label: '学习目标', href: '/profile/goals' },
        { icon: '🔔', label: '通知设置', href: '/profile/notifications' },
        { icon: '🌙', label: '主题设置', href: '/profile/theme' },
      ],
    },
    {
      title: '数据与隐私',
      items: [
        { icon: '📊', label: '数据导出', href: '/profile/export' },
        { icon: '🔐', label: '隐私设置', href: '/profile/privacy' },
        { icon: '🗑️', label: '删除账户', href: '/profile/delete' },
      ],
    },
  ];

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-dark-900">设置</h3>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-4">
          {settingGroups.map((group) => (
            <div key={group.title}>
              <h4 className="text-xs font-semibold text-dark-500 uppercase tracking-wider mb-2">
                {group.title}
              </h4>
              <div className="space-y-1">
                {group.items.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="flex items-center gap-3 p-2 rounded-lg hover:bg-dark-50 transition-colors group"
                  >
                    <span className="text-lg">{item.icon}</span>
                    <span className="text-sm text-dark-700 group-hover:text-dark-900">
                      {item.label}
                    </span>
                    <span className="ml-auto text-dark-400 group-hover:text-dark-600">
                      →
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 pt-6 border-t border-dark-200">
          <Button variant="ghost" size="sm" className="w-full text-red-600 hover:bg-red-50">
            <span className="mr-2">🚪</span>
            退出登录
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
