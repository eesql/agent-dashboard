/**
 * 消息列表组件（支持虚拟滚动）
 */
import React, { useEffect, useRef, useState } from 'react';
import { useMessageStore } from '@/stores/messageStore';
import { MessageBubble } from './MessageBubble';
import { Button } from '@/components/ui/Button';
import { Loader, RefreshCw } from 'lucide-react';

interface MessageListProps {
  sessionId: string;
}

export const MessageList: React.FC<MessageListProps> = ({ sessionId }) => {
  const { messages, loading, error, total, hasMore, fetchMessages, syncMessages } = useMessageStore();
  const [offset, setOffset] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const limit = 50;

  useEffect(() => {
    // 初始加载
    fetchMessages(sessionId, { limit, offset: 0 });
    setOffset(0);
  }, [sessionId]);

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    // 新消息到达时滚动到底部
    if (messages.length > 0) {
      setTimeout(scrollToBottom, 100);
    }
  }, [messages]);

  // 加载更多
  const loadMore = () => {
    const newOffset = offset + limit;
    setOffset(newOffset);
    fetchMessages(sessionId, { limit, offset: newOffset });
  };

  // 手动同步
  const handleSync = async () => {
    await syncMessages(sessionId);
  };

  if (loading && messages.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader className="animate-spin text-primary-500" size={32} />
      </div>
    );
  }

  if (error && messages.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-error-500 mb-4">{error}</p>
        <Button onClick={handleSync}>
          <RefreshCw size={16} className="mr-2" />
          重新同步
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 同步按钮 */}
      <div className="flex justify-end">
        <Button variant="ghost" size="sm" onClick={handleSync}>
          <RefreshCw size={14} className="mr-2" />
          同步消息
        </Button>
      </div>

      {/* 消息列表 */}
      <div className="space-y-4 max-h-[600px] overflow-y-auto p-4 bg-bg-secondary rounded-lg">
        {messages.length === 0 ? (
          <div className="text-center py-12 text-text-muted">
            <p>暂无消息</p>
            <p className="text-sm mt-2">消息将从 OpenClaw session 文件同步</p>
          </div>
        ) : (
          <>
            {/* 加载更多 */}
            {hasMore && (
              <div className="text-center">
                <Button variant="ghost" size="sm" onClick={loadMore}>
                  加载更多
                </Button>
              </div>
            )}

            {/* 消息 */}
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}

            {/* 列表末尾标记 */}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* 统计信息 */}
      <div className="text-xs text-text-muted text-center">
        共 {total} 条消息 {loading && '（加载中...）'}
      </div>
    </div>
  );
};

export default MessageList;
