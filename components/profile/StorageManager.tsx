'use client';

import { Card, CardHeader, CardContent, Button } from '@/components/ui';
import { useState } from 'react';

export function StorageManager() {
  const [storageUsed] = useState(2.4); // GB
  const storageTotal = 10; // GB
  const storagePercent = (storageUsed / storageTotal) * 100;

  const storageItems = [
    { type: '视频缓存', size: 1.2, color: 'bg-blue-500' },
    { type: '课件文档', size: 0.8, color: 'bg-green-500' },
    { type: '模拟器数据', size: 0.3, color: 'bg-yellow-500' },
    { type: '其他', size: 0.1, color: 'bg-gray-500' },
  ];

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-dark-900">存储管理</h3>
      </CardHeader>
      <CardContent className="p-6">
        {/* Storage Overview */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-dark-600">已使用</span>
            <span className="text-sm font-semibold text-dark-900">
              {storageUsed} GB / {storageTotal} GB
            </span>
          </div>
          <div className="h-3 bg-dark-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary-500 to-blue-600 rounded-full"
              style={{ width: `${storagePercent}%` }}
            />
          </div>
        </div>

        {/* Storage Breakdown */}
        <div className="space-y-2 mb-4">
          {storageItems.map((item) => (
            <div key={item.type} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${item.color}`} />
                <span className="text-dark-700">{item.type}</span>
              </div>
              <span className="text-dark-600">{item.size} GB</span>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="pt-4 border-t border-dark-200 space-y-2">
          <Button variant="outline" size="sm" className="w-full">
            <span className="mr-2">🗑️</span>
            清理缓存
          </Button>
          <Button variant="ghost" size="sm" className="w-full">
            <span className="mr-2">📊</span>
            查看详情
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
