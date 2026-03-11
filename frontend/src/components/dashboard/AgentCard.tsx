/**
 * Agent 状态卡片组件
 */
import React from 'react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Activity, Clock, Cpu, Bot } from 'lucide-react';
import type { Agent } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

interface AgentCardProps {
  agent: Agent;
  onClick?: () => void;
}

/**
 * 从 session key 提取 agent 名称
 * agent:main:qqbot:direct:xxx → "main / QQ Bot"
 * agent:agent-feishu-pd:feishu:direct:xxx → "agent-feishu-pd / 飞书"
 */
const extractAgentName = (id: string): string => {
  const parts = id.split(':');
  if (parts.length < 3) return id;
  
  const agentName = parts[1] || 'unknown';
  const channel = parts[2] || '';
  
  // 渠道名称映射
  const channelNames: Record<string, string> = {
    'qqbot': 'QQ Bot',
    'feishu': '飞书',
    'telegram': 'Telegram',
    'discord': 'Discord',
    'wecom': '企业微信',
    'slack': 'Slack',
    'direct': '',
  };
  
  const channelName = channelNames[channel] || channel;
  
  if (channelName) {
    return `${agentName} / ${channelName}`;
  }
  return agentName;
};

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

  const agentName = extractAgentName(agent.id);
  const modelName = agent.name || 'Unknown';

  return (
    <Card 
      hover={!!onClick}
      onClick={onClick}
      className={`border-l-4 ${getStatusBorder(agent.status)}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-text-primary mb-1 truncate" title={agentName}>
            {agentName}
          </h3>
          <div className="flex items-center gap-2">
            <Cpu size={12} className="text-text-muted" />
            <span className="text-sm text-text-secondary">{modelName}</span>
          </div>
        </div>
        <Badge status={agent.status} />
      </div>

      {agent.current_task && (
        <div className="mb-4 p-3 bg-bg-tertiary rounded-md">
          <div className="flex items-center gap-2 mb-1">
            <Bot size={14} className="text-text-secondary" />
            <span className="text-xs text-text-secondary font-medium">当前任务</span>
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
