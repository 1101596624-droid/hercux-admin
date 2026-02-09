interface LineChartProps {
  data: Array<{
    label: string;
    value: number;
  }>;
  color?: string;
  height?: number;
}

export function LineChart({ data, color = '#3b82f6', height = 200 }: LineChartProps) {
  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <p className="text-gray-400 text-sm">暂无数据</p>
      </div>
    );
  }

  const maxValue = Math.max(...data.map(d => d.value), 0.1);
  const minValue = Math.min(...data.map(d => d.value), 0);
  const range = maxValue - minValue || 1;

  const points = data.map((d, i) => {
    const x = (i / (data.length - 1 || 1)) * 100;
    const y = ((maxValue - d.value) / range) * 80 + 10;
    return { x, y, ...d };
  });

  const pathData = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
    .join(' ');

  return (
    <div className="relative" style={{ height }}>
      <svg
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        className="w-full h-full"
      >
        {/* Grid lines */}
        {[0, 25, 50, 75, 100].map(y => (
          <line
            key={y}
            x1="0"
            y1={y}
            x2="100"
            y2={y}
            stroke="#e5e7eb"
            strokeWidth="0.2"
          />
        ))}

        {/* Area fill */}
        <path
          d={`${pathData} L 100 100 L 0 100 Z`}
          fill={color}
          fillOpacity="0.1"
        />

        {/* Line */}
        <path
          d={pathData}
          fill="none"
          stroke={color}
          strokeWidth="0.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points */}
        {points.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r="1"
            fill={color}
            className="hover:r-2 transition-all"
          />
        ))}
      </svg>

      {/* Labels */}
      <div className="flex justify-between mt-2 text-xs text-gray-500">
        {data.map((d, i) => (
          <span key={i} className="truncate" style={{ maxWidth: '60px' }}>
            {d.label}
          </span>
        ))}
      </div>

      {/* Value labels */}
      <div className="absolute top-0 right-0 text-xs text-gray-400">
        {maxValue.toFixed(2)}
      </div>
      <div className="absolute bottom-8 right-0 text-xs text-gray-400">
        {minValue.toFixed(2)}
      </div>
    </div>
  );
}
