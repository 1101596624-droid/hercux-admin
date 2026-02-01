'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { LearningTimeData } from '@/lib/api/admin/analytics';

interface BarChartComponentProps {
  data: LearningTimeData[];
}

export function BarChartComponent({ data }: BarChartComponentProps) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
        <XAxis
          dataKey="range"
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#64748B', fontSize: 12 }}
        />
        <YAxis
          axisLine={false}
          tickLine={false}
          tick={{ fill: '#64748B', fontSize: 12 }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
          }}
          formatter={(value) => [`${Number(value).toLocaleString()} 人`, '用户数']}
        />
        <Bar
          dataKey="count"
          fill="#DC2626"
          radius={[6, 6, 0, 0]}
          name="count"
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
