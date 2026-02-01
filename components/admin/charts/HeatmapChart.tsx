'use client';

interface HeatmapChartProps {
  data: number[][];
}

const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`);

function getColor(value: number): string {
  if (value < 15) return 'bg-slate-100';
  if (value < 30) return 'bg-red-100';
  if (value < 45) return 'bg-red-200';
  if (value < 60) return 'bg-red-400';
  return 'bg-red-600';
}

export function HeatmapChart({ data }: HeatmapChartProps) {
  return (
    <div className="overflow-x-auto">
      <div className="min-w-[600px]">
        {/* Hour labels */}
        <div className="flex gap-1 mb-2 pl-12">
          {[0, 6, 12, 18, 23].map((h, idx) => (
            <div
              key={h}
              className="text-xs text-slate-400"
              style={{ marginLeft: idx === 0 ? 0 : `${(h - [0, 6, 12, 18][idx - 1]) * 16 - 8}px` }}
            >
              {h}:00
            </div>
          ))}
        </div>

        {/* Heatmap grid */}
        {data.map((row, dayIndex) => (
          <div key={dayIndex} className="flex items-center gap-1 mb-1">
            <span className="text-xs text-slate-500 w-10">{days[dayIndex]}</span>
            {row.map((value, hourIndex) => (
              <div
                key={hourIndex}
                className={`w-4 h-4 rounded-sm ${getColor(value)} transition-colors hover:ring-2 hover:ring-red-300 cursor-pointer`}
                title={`${days[dayIndex]} ${hours[hourIndex]}: ${value} 活跃用户`}
              />
            ))}
          </div>
        ))}

        {/* Legend */}
        <div className="flex items-center gap-2 mt-4 pl-12">
          <span className="text-xs text-slate-400">低</span>
          <div className="flex gap-1">
            {['bg-slate-100', 'bg-red-100', 'bg-red-200', 'bg-red-400', 'bg-red-600'].map((color, i) => (
              <div key={i} className={`w-4 h-4 rounded-sm ${color}`} />
            ))}
          </div>
          <span className="text-xs text-slate-400">高</span>
        </div>
      </div>
    </div>
  );
}
