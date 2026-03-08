/**
 * 状态徽章组件
 */
import React from 'react';
import { Circle } from 'lucide-react';
import type { AgentStatus } from '@/types';

interface BadgeProps {
  status: AgentStatus;
  label?: string;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ status, label, className = '' }) => {
  const getStatusConfig = (status: AgentStatus) => {
    switch (status) {
      case 'online':
        return { class: 'badge-online', label: label || 'Online' };
      case 'offline':
        return { class: 'badge-offline', label: label || 'Offline' };
      case 'busy':
        return { class: 'badge-busy', label: label || 'Busy' };
      case 'error':
        return { class: 'badge-error', label: label || 'Error' };
      default:
        return { class: 'badge-offline', label: label || 'Unknown' };
    }
  };

  const config = getStatusConfig(status);

  return (
    <span className={`badge ${config.class} ${className}`}>
      <Circle size={8} fill="currentColor" />
      {config.label}
    </span>
  );
};

export default Badge;
