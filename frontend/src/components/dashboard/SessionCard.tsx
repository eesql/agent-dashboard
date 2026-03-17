/**
 * Session 信息卡片组件
 */
import React from 'react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { 
  Clock, 
  Cpu, 
  MessageSquare,
  Brain,
  TrendingUp
} from 'lucide-react';
import type { SessionInfo } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

interface SessionCardProps {
  session: SessionInfo;
  onClick?: () => void;
}

const getStatusBorder = (status: string) => {
  switch (status) {
    case 'online': return 'border-l-status-online';
    case 'busy': return 'border-l-status-busy';
    default: return 'border-l-status-offline';
  }
};

const getThinkingLabel = (level: string) => {
  const labels: Record<string, string> = {
    'off': '关闭',
    'minimal': '最小',
    'low': '低',
    'medium': '中',
    'high': '高',
    'xhigh': '极高',
  };
  return labels[level] || level;
};

const getThinkingColor = (level: string) => {
  switch (level) {
    case 'high':
    case 'xhigh':
      return 'text-purple-400';
    case 'medium':
      return 'text-blue-400';
    case 'low':
    case 'minimal':
      return 'text-text-secondary';
    default:
      return 'text-text-muted';
  }
};

const getUsageColor = (percent: number) => {
  if (percent >= 80) return 'bg-error-500';
  if (percent >= 50) return 'bg-warning-500';
  return 'bg-success-500';
};

/**
 * 截断会话 ID 显示
 */
const truncateSessionId = (id: string) => {
  if (id.length <= 40) return id;
  const parts = id.split(':');
  if (parts.length >= 4) {
    return `${parts[0]}:${parts[1]}:${parts[2]}:...${parts[parts.length - 1].slice(-8)}`;
  }
  return id.slice(0, 20) + '...' + id.slice(-10);
};

/**
 * 从 session ID 提取有意义的名称
 */
const extractSessionName = (id: string): string => {
  const parts = id.split(':');
  if (parts.length < 3) return id;
  
  const agentName = parts[1] || 'unknown';
  const channel = parts[2] || '';
  
  const channelNames: Record<string, string> = {
    'qqbot': 'QQ Bot',
    'feishu': '飞书',
    'telegram': 'Telegram',
    'discord': 'Discord',
    'wecom': '企业微信',
    'slack': 'Slack',
    'direct': '私信',
  };
  
  const channelName = channelNames[channel] || channel;
  
  if (channelName) {
    return `${agentName} / ${channelName}`;
  }
  return agentName;
};

export const SessionCard: React.FC<SessionCardProps> = ({ session, onClick }) => {
  const formatLastActivity = (dateString: string) => {
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

  const sessionName = extractSessionName(session.id);
  const usagePercent = Math.min(session.context_usage_percent, 100);

  return (
    <Card 
      hover={!!onClick}
      onClick={onClick}
      className={`border-l-4 ${getStatusBorder(session.status)}`}
    >
      {/* 标题行 */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-semibold text-text-primary mb-1 truncate" title={session.id}>
            {sessionName}
          </h3>
          <p className="text-xs text-text-muted font-mono truncate" title={session.id}>
            {truncateSessionId(session.id)}
          </p>
        </div>
        <Badge status={session.status} />
      </div>

      {/* 模型和思考模式 */}
      <div className="flex items-center gap-4 mb-3">
        <div className="flex items-center gap-1.5">
          <Cpu size={12} className="text-text-muted" />
          <span className="text-sm text-text-secondary">{session.model}</span>
        </div>
        {session.thinking_level && session.thinking_level !== 'off' && (
          <div className="flex items-center gap-1.5">
            <Brain size={12} className={getThinkingColor(session.thinking_level)} />
            <span className={`text-sm ${getThinkingColor(session.thinking_level)}`}>
              思考: {getThinkingLabel(session.thinking_level)}
            </span>
          </div>
        )}
      </div>

      {/* 上下文使用进度条 */}
      <div className="mb-3">
        <div className="flex items-center justify-between text-xs text-text-secondary mb-1">
          <span className="flex items-center gap-1">
            <TrendingUp size={12} />
            上下文使用
          </span>
          <span>{session.total_tokens.toLocaleString()} / {session.context_limit.toLocaleString()}</span>
        </div>
        <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
          <div 
            className={`h-full ${getUsageColor(usagePercent)} transition-all duration-300`}
            style={{ width: `${usagePercent}%` }}
          />
        </div>
        <div className="text-xs text-text-muted mt-1 text-right">
          {usagePercent}%
        </div>
      </div>

      {/* Token 统计 */}
      <div className="grid grid-cols-2 gap-2 mb-3 p-2 bg-bg-tertiary rounded-md">
        <div>
          <p className="text-xs text-text-muted">Input</p>
          <p className="text-sm font-medium text-text-primary">{session.input_tokens.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs text-text-muted">Output</p>
          <p className="text-sm font-medium text-text-primary">{session.output_tokens.toLocaleString()}</p>
        </div>
      </div>

      {/* 底部信息 */}
      <div className="flex items-center gap-4 text-xs text-text-secondary">
        <div className="flex items-center gap-1">
          <Clock size={14} />
          <span>{formatLastActivity(session.last_activity)}</span>
        </div>
        <div className="flex items-center gap-1">
          <MessageSquare size={14} />
          <span>{session.channel}</span>
        </div>
      </div>
    </Card>
  );
};

export default SessionCard;
