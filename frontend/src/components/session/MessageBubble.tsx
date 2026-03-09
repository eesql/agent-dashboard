/**
 * 消息气泡组件
 */
import React from 'react';
import { MessageSquare, Tool, Code, FileText, Image } from 'lucide-react';
import type { Message } from '@/types';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isTool = message.role === 'tool' || message.is_tool_call || message.is_tool_result;
  const isToolCall = message.is_tool_call;
  const isToolResult = message.is_tool_result;

  // 工具调用样式
  if (isToolCall) {
    return (
      <div className="flex items-start gap-3 p-4 bg-primary-500/10 rounded-lg border border-primary-500/20">
        <div className="p-2 bg-primary-500/20 rounded-lg">
          <Tool size={16} className="text-primary-500" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-semibold text-primary-500">
              工具调用
            </span>
            <span className="text-xs text-text-secondary font-mono">
              {message.tool_name}
            </span>
          </div>
          {message.tool_args && (
            <pre className="text-xs text-text-secondary bg-bg-tertiary p-2 rounded overflow-x-auto">
              {JSON.stringify(message.tool_args, null, 2)}
            </pre>
          )}
        </div>
      </div>
    );
  }

  // 工具结果样式
  if (isToolResult) {
    return (
      <div className="flex items-start gap-3 p-4 bg-success-500/10 rounded-lg border border-success-500/20">
        <div className="p-2 bg-success-500/20 rounded-lg">
          <FileText size={16} className="text-success-500" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-semibold text-success-500">
              工具结果
            </span>
            <span className="text-xs text-text-secondary font-mono">
              {message.tool_name}
            </span>
          </div>
          {message.tool_result && (
            <pre className="text-xs text-text-secondary bg-bg-tertiary p-2 rounded overflow-x-auto max-h-40 overflow-y-auto">
              {message.tool_result.slice(0, 500)}
              {message.tool_result.length > 500 && '...'}
            </pre>
          )}
        </div>
      </div>
    );
  }

  // 普通工具消息
  if (isTool) {
    return (
      <div className="flex items-start gap-3 p-4 bg-bg-tertiary rounded-lg border border-border-default">
        <div className="p-2 bg-bg-tertiary rounded-lg">
          <Tool size={16} className="text-text-muted" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-text-primary whitespace-pre-wrap">
            {message.content || '工具执行'}
          </p>
        </div>
      </div>
    );
  }

  // 用户消息
  if (isUser) {
    return (
      <div className="flex items-start gap-3 p-4 bg-primary-500/20 rounded-lg border border-primary-500/30">
        <div className="p-2 bg-primary-500/30 rounded-lg">
          <MessageSquare size={16} className="text-primary-500" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-text-primary whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
      </div>
    );
  }

  // Assistant 消息（默认）
  return (
    <div className="flex items-start gap-3 p-4 bg-bg-secondary rounded-lg border border-border-default">
      <div className="p-2 bg-bg-tertiary rounded-lg">
        <MessageSquare size={16} className="text-text-muted" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-text-primary whitespace-pre-wrap">
          {message.content}
        </p>
      </div>
    </div>
  );
};

export default MessageBubble;
