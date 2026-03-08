/**
 * Agent 状态卡片组件
 */
import React from 'react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Activity, Clock, Cpu } from 'lucide-react';
import type { Agent } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

interface AgentCardProps {
  agent: Agent;
  onClick?: () => void;
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent, onClick }) => {
  const formatLastSeen = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return formatDistanceToNow(date, { 
        addSuffix: true,
        locale: zhCN 
      });
    } catch {
      return 'Unknown';
    }
  };

  const getStatusBorder = (status: string) => {
    switch (status) {
      case 'online': return 'border-l-status-online';
      case 'busy': return 'border-l-status-busy';
      case 'error': return 'border-l-status-error';
      default: return 'border-l-status-offline';
    }
  };

  return (
    <Card 
      hover={!!onClick}
      onClick={onClick}
      className={`border-l-4 ${getStatusBorder(agent.status)}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-text-primary mb-1">
            {agent.name || agent.id}
          </h3>
          <p className="text-xs text-text-muted font-mono">
            {agent.id.slice(0, 20)}...
          </p>
        </div>
        <Badge status={agent.status} />
      </div>

      {agent.current_task && (
        <div className="mb-4 p-3 bg-bg-tertiary rounded-md">
          <div className="flex items-center gap-2 mb-1">
            <Cpu size={14} className="text-text-secondary" />
            <span className="text-xs text-text-secondary font-medium">Current Task</span>
          </div>
          <p className="text-sm text-text-primary font-mono truncate">
            {agent.current_task}
          </p>
        </div>
      )}

      <div className="flex items-center gap-4 text-xs text-text-secondary">
        <div className="flex items-center gap-1">
          <Clock size={14} />
          <span>{formatLastSeen(agent.last_seen)}</span>
        </div>
        <div className="flex items-center gap-1">
          <Activity size={14} />
          <span className="capitalize">{agent.status}</span>
        </div>
      </div>
    </Card>
  );
};

export default AgentCard;
