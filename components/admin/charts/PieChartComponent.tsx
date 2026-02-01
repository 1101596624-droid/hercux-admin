'use client';

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { UserSourceData } from '@/lib/api/admin/analytics';

interface PieChartComponentProps {
  data: UserSourceData[];
}

export function PieChartComponent({ data }: PieChartComponentProps) {
  return (
    <div className="flex items-center gap-8">
      <ResponsiveContainer width="50%" height={200}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={80}
            paddingAngle={4}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => [`${value}%`, '占比']}
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #E2E8F0',
              borderRadius: '12px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex-1 space-y-3">
        {data.map(item => (
          <div key={item.name} className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
            <span className="text-sm text-slate-600 flex-1">{item.name}</span>
            <span className="text-sm font-semibold text-slate-900">{item.value}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
