/**
 * 统计卡片组件
 */
import React from 'react';
import { Card } from '@/components/ui/Card';
import { TrendingUp, Activity, DollarSign, Users } from 'lucide-react';

interface MetricsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: 'tokens' | 'requests' | 'cost' | 'agents';
  trend?: number;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
}) => {
  const getIcon = () => {
    switch (icon) {
      case 'tokens':
        return <Activity size={20} className="text-primary-500" />;
      case 'requests':
        return <TrendingUp size={20} className="text-success-500" />;
      case 'cost':
        return <DollarSign size={20} className="text-warning-500" />;
      case 'agents':
        return <Users size={20} className="text-info-500" />;
    }
  };

  const formatValue = (val: string | number) => {
    if (typeof val === 'number') {
      if (val >= 1000000) return (val / 1000000).toFixed(1) + 'M';
      if (val >= 1000) return (val / 1000).toFixed(1) + 'K';
      return val.toLocaleString();
    }
    return val;
  };

  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-text-secondary mb-1">{title}</p>
          <p className="text-2xl font-bold text-text-primary font-tabular">
            {formatValue(value)}
          </p>
          {subtitle && (
            <p className="text-xs text-text-muted mt-1">{subtitle}</p>
          )}
          {trend !== undefined && (
            <p className={`text-xs mt-2 ${trend >= 0 ? 'text-success-500' : 'text-error-500'}`}>
              {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}% vs last period
            </p>
          )}
        </div>
        <div className="p-2 bg-bg-tertiary rounded-lg">
          {getIcon()}
        </div>
      </div>
    </Card>
  );
};

export default MetricsCard;
