'use client';

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { GrowthDataPoint } from '@/lib/api/admin/analytics';

interface GrowthChartProps {
  data: GrowthDataPoint[];
}

export function GrowthChart({ data }: GrowthChartProps) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorTotalUsers" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#DC2626" stopOpacity={0.15}/>
            <stop offset="95%" stopColor="#DC2626" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="colorActiveUsers" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.15}/>
            <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
        <XAxis
          dataKey="date"
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
          formatter={(value, name) => {
            const labels: Record<string, string> = {
              totalUsers: '总用户',
              activeUsers: '活跃用户',
              newUsers: '新增用户'
            };
            return [Number(value).toLocaleString(), labels[String(name)] || String(name)];
          }}
        />
        <Legend
          formatter={(value: string) => {
            const labels: Record<string, string> = {
              totalUsers: '总用户',
              activeUsers: '活跃用户'
            };
            return labels[value] || value;
          }}
        />
        <Area
          type="monotone"
          dataKey="totalUsers"
          stroke="#DC2626"
          strokeWidth={2}
          fillOpacity={1}
          fill="url(#colorTotalUsers)"
          name="totalUsers"
        />
        <Area
          type="monotone"
          dataKey="activeUsers"
          stroke="#3B82F6"
          strokeWidth={2}
          fillOpacity={1}
          fill="url(#colorActiveUsers)"
          name="activeUsers"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
