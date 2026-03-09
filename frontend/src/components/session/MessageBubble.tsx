/**
 * 消息气泡组件
 */
import React from 'react';
import { User, Cpu, Tool, Code, FileText } from 'lucide-react';
import type { Message } from '@/stores/messageStore';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isTool = message.role === 'tool' || message.is_tool_call || message.is_tool_result;
  const isAssistant = message.role === 'assistant';

  // 渲染工具调用
  if (message.is_tool_call) {
    return (
      <div className="flex items-start gap-3 p-4 bg-code-bg rounded-lg border border-border-default">
        <div className="p-2 bg-primary-500/10 rounded">
          <Tool size={18} className="text-primary-500" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-semibold text-text-primary">
              工具调用：{message.tool_name}
            </span>
            <span className="text-xs text-text-muted">
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          </div>
          {message.tool_args && (
            <pre className="text-xs text-text-secondary bg-code-bg p-3 rounded overflow-x-auto font-mono">
              {JSON.stringify(message.tool_args, null, 2)}
            </pre>
          )}
        </div>
      </div>
    );
  }

  // 渲染工具结果
  if (message.is_tool_result) {
    return (
      <div className="flex items-start gap-3 p-4 bg-success-bg rounded-lg border border-border-default">
        <div className="p-2 bg-success-500/10 rounded">
          <FileText size={18} className="text-success-500" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-semibold text-text-primary">
              工具结果：{message.tool_name}
            </span>
            <span className="text-xs text-text-muted">
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          </div>
          {message.tool_result && (
            <pre className="text-xs text-text-secondary bg-code-bg p-3 rounded overflow-x-auto font-mono">
              {message.tool_result.slice(0, 500)}
              {message.tool_result.length > 500 && '...'}
            </pre>
          )}
        </div>
      </div>
    );
  }

  // 渲染普通消息
  return (
    <div
      className={`flex items-start gap-3 ${
        isUser ? 'flex-row-reverse' : 'flex-row'
      }`}
    >
      {/* 头像 */}
      <div
        className={`p-2 rounded ${
          isUser
            ? 'bg-primary-500/10'
            : isAssistant
            ? 'bg-secondary-500/10'
            : 'bg-code-bg'
        }`}
      >
        {isUser ? (
          <User size={18} className="text-primary-500" />
        ) : isAssistant ? (
          <Cpu size={18} className="text-secondary-500" />
        ) : (
          <Code size={18} className="text-text-muted" />
        )}
      </div>

      {/* 消息内容 */}
      <div
        className={`flex-1 max-w-[80%] ${
          isUser ? 'text-right' : 'text-left'
        }`}
      >
        <div
          className={`inline-block p-4 rounded-lg ${
            isUser
              ? 'bg-primary-500/10 text-text-primary'
              : isAssistant
              ? 'bg-bg-tertiary text-text-primary'
              : 'bg-code-bg text-text-secondary'
          }`}
        >
          {message.content ? (
            <div className="text-sm whitespace-pre-wrap">{message.content}</div>
          ) : (
            <span className="text-sm text-text-muted">[无文本内容]</span>
          )}
        </div>
        <div className="text-xs text-text-muted mt-1">
          {new Date(message.timestamp).toLocaleString()}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
