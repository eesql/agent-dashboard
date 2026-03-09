/**
 * 消息列表组件（支持虚拟滚动）
 */
import React, { useEffect, useRef, useState } from 'react';
import { MessageBubble } from './MessageBubble';
import type { Message } from '@/types';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';

interface MessageListProps {
  messages: Message[];
  loading?: boolean;
  onLoadMore?: () => void;
  hasMore?: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  loading = false,
  onLoadMore,
  hasMore = false,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [visibleCount, setVisibleCount] = useState(50);

  // 初始加载显示最近 50 条
  useEffect(() => {
    setVisibleCount(50);
  }, [messages]);

  // 滚动到底部时加载更多
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      
      // 距离底部 200px 时加载更多
      if (scrollHeight - scrollTop - clientHeight < 200 && hasMore && onLoadMore) {
        onLoadMore();
      }
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [hasMore, onLoadMore]);

  // 只显示最近的 visibleCount 条消息
  const visibleMessages = messages.slice(-visibleCount);

  if (loading && messages.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center text-text-secondary">
          <div className="animate-spin w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-2"></div>
          <p>加载消息中...</p>
        </div>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center text-text-muted">
          <p>暂无消息</p>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto space-y-3 p-4"
      style={{ maxHeight: 'calc(100vh - 400px)' }}
    >
      {messages.length > visibleCount && (
        <div className="text-center text-xs text-text-muted py-2">
          还有 {messages.length - visibleCount} 条更早的消息，滚动加载更多
        </div>
      )}
      
      {visibleMessages.map((message) => (
        <div key={message.id}>
          <MessageBubble message={message} />
          <div className="text-xs text-text-muted mt-1 ml-12">
            {format(new Date(message.timestamp), 'HH:mm:ss', { locale: zhCN })}
          </div>
        </div>
      ))}

      {loading && (
        <div className="text-center text-text-secondary py-4">
          加载中...
        </div>
      )}
    </div>
  );
};

export default MessageList;
