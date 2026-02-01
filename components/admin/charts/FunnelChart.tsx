'use client';

import { FunnelStage } from '@/lib/api/admin/analytics';

interface FunnelChartProps {
  data: FunnelStage[];
}

export function FunnelChart({ data }: FunnelChartProps) {
  return (
    <div className="space-y-3">
      {data.map((item, index) => (
        <div key={item.stage} className="relative">
          <div className="flex items-center gap-4">
            <div className="w-24 text-sm text-slate-600 text-right">{item.stage}</div>
            <div className="flex-1 relative">
              <div
                className="h-10 bg-red-600 rounded-r-lg flex items-center justify-end pr-4 transition-all duration-500"
                style={{ width: `${item.rate}%`, opacity: 1 - (index * 0.15) }}
              >
                <span className="text-white text-sm font-medium">{item.count.toLocaleString()}</span>
              </div>
            </div>
            <div className="w-16 text-right">
              <span className="text-sm font-semibold text-slate-700">{item.rate}%</span>
            </div>
          </div>
          {index < data.length - 1 && (
            <div className="flex items-center gap-4 my-1">
              <div className="w-24" />
              <div className="text-xs text-slate-400 pl-2">
                ↓ 流失 {data[index].rate - data[index + 1].rate}%
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
