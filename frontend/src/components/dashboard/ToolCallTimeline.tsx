/**
 * 工具调用时间线组件
 */
import React from 'react';
import { Card } from '@/components/ui/Card';
import { 
  Terminal, 
  FileText, 
  Globe, 
  Database, 
  MessageSquare,
  Search,
  Code,
  Play,
  Clock
} from 'lucide-react';
import type { ToolCall } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

interface ToolCallTimelineProps {
  toolCalls: ToolCall[];
  limit?: number;
}

// 工具图标映射
const getToolIcon = (toolName: string) => {
  const name = toolName.toLowerCase();
  
  if (name.includes('exec') || name.includes('shell')) return Terminal;
  if (name.includes('read') || name.includes('write') || name.includes('edit')) return FileText;
  if (name.includes('browser') || name.includes('web') || name.includes('fetch')) return Globe;
  if (name.includes('db') || name.includes('sql') || name.includes('database')) return Database;
  if (name.includes('message') || name.includes('chat') || name.includes('send')) return MessageSquare;
  if (name.includes('search') || name.includes('find')) return Search;
  if (name.includes('code') || name.includes('compile')) return Code;
  if (name.includes('run') || name.includes('execute')) return Play;
  
  return Terminal; // 默认图标
};

// 工具类别颜色
const getToolColor = (toolName: string) => {
  const name = toolName.toLowerCase();
  
  if (name.includes('exec') || name.includes('shell')) return 'text-error-500 bg-error-500/10';
  if (name.includes('read') || name.includes('write')) return 'text-info-500 bg-info-500/10';
  if (name.includes('browser')) return 'text-warning-500 bg-warning-500/10';
  if (name.includes('message')) return 'text-success-500 bg-success-500/10';
  
  return 'text-primary-500 bg-primary-500/10';
};

export const ToolCallTimeline: React.FC<ToolCallTimelineProps> = ({ 
  toolCalls, 
  limit = 20 
}) => {
  const recentCalls = toolCalls.slice(0, limit);

  const formatTime = (dateString: string) => {
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

  const formatDuration = (ms: number | null) => {
    if (ms === null || ms === undefined) return '-';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const truncateArgs = (args: Record<string, any> | null, maxLength = 100) => {
    if (!args) return '-';
    
    const str = JSON.stringify(args);
    if (str.length <= maxLength) return str;
    
    return str.substring(0, maxLength) + '...';
  };

  if (recentCalls.length === 0) {
    return (
      <Card>
        <div className="text-center py-8">
          <Clock size={48} className="mx-auto text-text-muted mb-3" />
          <p className="text-text-secondary">暂无工具调用记录</p>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-text-primary">
          工具调用时间线
        </h3>
        <p className="text-sm text-text-secondary mt-1">
          最近 {recentCalls.length} 次调用
        </p>
      </div>

      <div className="space-y-3">
        {recentCalls.map((call) => {
          const Icon = getToolIcon(call.tool_name);
          const colorClass = getToolColor(call.tool_name);

          return (
            <div key={call.id} className="relative pl-6 pb-3 border-l-2 border-border-default last:pb-0">
              {/* 时间点 */}
              <div className={`absolute left-[-9px] top-0 w-4 h-4 rounded-full border-2 border-bg-secondary ${colorClass}`}>
              </div>

              {/* 内容 */}
              <div className="bg-bg-tertiary rounded-md p-3">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Icon size={16} className={colorClass.split(' ')[0]} />
                    <span className="font-mono text-sm font-medium text-text-primary">
                      {call.tool_name}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-text-secondary">
                    <span>{formatTime(call.timestamp)}</span>
                    <span className="font-tabular">{formatDuration(call.duration_ms)}</span>
                  </div>
                </div>

                {/* 参数预览 */}
                {call.tool_args && Object.keys(call.tool_args).length > 0 && (
                  <div className="mt-2">
                    <div className="text-xs text-text-muted mb-1">Args:</div>
                    <pre className="text-xs font-mono text-text-secondary bg-bg-primary rounded p-2 overflow-x-auto max-h-20">
                      {truncateArgs(call.tool_args)}
                    </pre>
                  </div>
                )}

                {/* 结果摘要 */}
                {call.result_summary && (
                  <div className="mt-2">
                    <div className="text-xs text-text-muted mb-1">Result:</div>
                    <p className="text-xs text-text-secondary line-clamp-2">
                      {call.result_summary}
                    </p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default ToolCallTimeline;
