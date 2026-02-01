'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { RetentionData } from '@/lib/api/admin/analytics';

interface RetentionChartProps {
  data: RetentionData;
}

export function RetentionChart({ data }: RetentionChartProps) {
  const chartData = [
    { day: 'D1', rate: data.d1 },
    { day: 'D3', rate: data.d3 },
    { day: 'D7', rate: data.d7 },
    { day: 'D14', rate: data.d14 },
    { day: 'D30', rate: data.d30 },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
        <XAxis
          dataKey="day"
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#64748B', fontSize: 12 }}
        />
        <YAxis
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#64748B', fontSize: 12 }}
          domain={[0, 100]}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
          }}
          formatter={(value) => [`${value}%`, '留存率']}
        />
        <Line
          type="monotone"
          dataKey="rate"
          stroke="#DC2626"
          strokeWidth={3}
          dot={{ fill: '#DC2626', strokeWidth: 2, r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
