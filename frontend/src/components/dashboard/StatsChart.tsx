/**
 * 统计图表组件
 */
import React from 'react';
import { Card } from '@/components/ui/Card';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import { Activity, TrendingUp } from 'lucide-react';
import type { TrendDataPoint } from '@/types';

interface ChartData {
  date: string;
  tokens: number;
  requests: number;
  cost: number;
}

interface StatsChartProps {
  data?: TrendDataPoint[];
  type?: 'tokens' | 'requests' | 'cost';
  period?: 'day' | 'week' | 'month';
}

// 将 API 数据转换为图表数据格式
const convertToChartData = (trendData: TrendDataPoint[]): ChartData[] => {
  return trendData.map(item => ({
    date: item.date.slice(5), // 截取 MM-DD 部分
    tokens: item.token_count,
    requests: item.request_count,
    cost: item.estimated_cost,
  }));
};

// 模拟数据（仅用于调试，实际应从 API 获取）
const generateMockData = (period: string): ChartData[] => {
  const data: ChartData[] = [];
  const now = new Date();
  
  const days = period === 'day' ? 24 : period === 'week' ? 7 : 30;
  
  for (let i = days; i >= 0; i--) {
    const date = new Date(now);
    date.setHours(date.getHours() - i);
    
    data.push({
      date: period === 'day' 
        ? `${date.getHours()}:00` 
        : `${date.getMonth() + 1}/${date.getDate()}`,
      tokens: Math.floor(Math.random() * 5000) + 1000,
      requests: Math.floor(Math.random() * 100) + 20,
      cost: Number((Math.random() * 0.1).toFixed(4)),
    });
  }
  
  return data;
};

export const StatsChart: React.FC<StatsChartProps> = ({
  data,
  type = 'tokens',
  period = 'week',
}) => {
  // 优先使用 API 数据，如果没有则使用模拟数据
  const chartData = data ? convertToChartData(data) : generateMockData(period);

  const getTitle = () => {
    switch (type) {
      case 'tokens':
        return { title: 'Token 消耗趋势', icon: Activity, color: '#6366F1' };
      case 'requests':
        return { title: '请求数量趋势', icon: TrendingUp, color: '#10B981' };
      case 'cost':
        return { title: '成本趋势', icon: Activity, color: '#F59E0B' };
      default:
        return { title: '统计趋势', icon: Activity, color: '#6366F1' };
    }
  };

  const config = getTitle();
  const Icon = config.icon;

  const formatYAxis = (value: number) => {
    if (type === 'tokens') {
      if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
      if (value >= 1000) return `${(value / 1000).toFixed(0)}K`;
      return value.toString();
    }
    if (type === 'cost') {
      return `$${value.toFixed(3)}`;
    }
    return value.toString();
  };

  const dataKey = type === 'tokens' ? 'tokens' : type === 'requests' ? 'requests' : 'cost';

  return (
    <Card>
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-1">
          <Icon size={18} className={type === 'tokens' ? 'text-primary-500' : type === 'requests' ? 'text-success-500' : 'text-warning-500'} />
          <h3 className="text-lg font-semibold text-text-primary">{config.title}</h3>
        </div>
        <p className="text-sm text-text-secondary">
          过去 {period === 'day' ? '24 小时' : period === 'week' ? '7 天' : '30 天'}
        </p>
      </div>

      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id={`color${type}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={config.color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={config.color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
            <XAxis 
              dataKey="date" 
              stroke="#64748B"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              stroke="#64748B"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              tickFormatter={formatYAxis}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1E293B',
                border: '1px solid #334155',
                borderRadius: '6px',
                color: '#F1F5F9',
              }}
              labelStyle={{ color: '#94A3B8' }}
              formatter={(value: number) => {
                if (type === 'tokens') {
                  if (value >= 1000000) return [`${(value / 1000000).toFixed(2)}M`, 'Tokens'];
                  if (value >= 1000) return [`${(value / 1000).toFixed(0)}K`, 'Tokens'];
                  return [value.toString(), 'Tokens'];
                }
                if (type === 'cost') {
                  return [`$${(value as number).toFixed(4)}`, 'Cost'];
                }
                return [value.toString(), 'Requests'];
              }}
            />
            <Area
              type="monotone"
              dataKey={dataKey}
              stroke={config.color}
              strokeWidth={2}
              fill={`url(#color${type})`}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};

export default StatsChart;
