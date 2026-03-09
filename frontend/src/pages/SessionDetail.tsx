/**
 * 会话详情页面
 */
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ToolCallTimeline } from '@/components/dashboard/ToolCallTimeline';
import { MessageList } from '@/components/session/MessageList';
import { 
  ArrowLeft, 
  MessageSquare, 
  Clock, 
  Calendar,
  User,
  Cpu,
  Code,
  RefreshCw
} from 'lucide-react';
import type { Session, ToolCall, Message } from '@/types';
import { sessionApi, messageApi } from '@/services/api';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';

export const SessionDetail: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<Session | null>(null);
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [messageOffset, setMessageOffset] = useState(0);
  const MESSAGE_LIMIT = 50;

  useEffect(() => {
    if (!sessionId) return;
    
    const fetchSessionDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        // 获取会话详情
        const sessionRes = await sessionApi.get(sessionId);
        setSession(sessionRes.data);
        
        // 获取工具调用
        const toolCallsRes = await sessionApi.list({ limit: 20 });
        setToolCalls(toolCallsRes.data.sessions || []);
        
        // 获取消息历史
        await fetchMessages(0);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch session details');
      } finally {
        setLoading(false);
      }
    };

    fetchSessionDetail();
  }, [sessionId]);

  const fetchMessages = async (offset: number) => {
    if (!sessionId) return;
    
    try {
      const res = await messageApi.list(sessionId, { limit: MESSAGE_LIMIT, offset });
      const data = res.data;
      setMessages(prev => offset === 0 ? data.messages : [...prev, ...data.messages]);
      setMessageOffset(offset + data.messages.length);
    } catch (err: any) {
      console.error('Failed to fetch messages:', err);
    }
  };

  const handleSync = async () => {
    if (!sessionId) return;
    
    setSyncing(true);
    try {
      await messageApi.sync(sessionId);
      await fetchMessages(0);
    } catch (err: any) {
      console.error('Sync failed:', err);
    } finally {
      setSyncing(false);
    }
  };

  const handleLoadMore = () => {
    fetchMessages(messageOffset);
  };

  if (loading) {
    return (
      <div className="p-6">
        <Card>
          <div className="text-center py-12">
            <p className="text-text-secondary">加载中...</p>
          </div>
        </Card>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="p-6">
        <Card>
          <div className="text-center py-12">
            <p className="text-error-500">{error || 'Session not found'}</p>
            <Button 
              className="mt-4" 
              onClick={() => navigate('/sessions')}
            >
              返回列表
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 页面头部 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => navigate('/sessions')}
          >
            <ArrowLeft size={16} />
            返回
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-text-primary">
              会话详情
            </h1>
            <p className="text-sm text-text-secondary mt-1 font-mono">
              {session.id}
            </p>
          </div>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={handleSync}
          disabled={syncing}
        >
          <RefreshCw size={16} className={syncing ? 'animate-spin' : ''} />
          {syncing ? '同步中...' : '同步消息'}
        </Button>
      </div>

      {/* 会话信息 */}
      <Card>
        <h2 className="text-lg font-semibold text-text-primary mb-4">
          会话信息
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-text-secondary text-sm">
              <MessageSquare size={14} />
              <span>标签</span>
            </div>
            <p className="text-text-primary font-medium">
              {session.label || '-'}
            </p>
          </div>
          
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-text-secondary text-sm">
              <Cpu size={14} />
              <span>类型</span>
            </div>
            <Badge 
              status={session.kind === 'subagent' ? 'online' : session.kind === 'acp' ? 'busy' : 'offline'}
              label={session.kind || 'unknown'}
            />
          </div>
          
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-text-secondary text-sm">
              <User size={14} />
              <span>Agent</span>
            </div>
            <p className="text-text-primary font-mono text-sm">
              {session.agent_id ? session.agent_id.slice(0, 12) + '...' : '-'}
            </p>
          </div>
          
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-text-secondary text-sm">
              <MessageSquare size={14} />
              <span>消息数</span>
            </div>
            <p className="text-text-primary font-tabular font-medium">
              {session.message_count}
            </p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t border-border-default">
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <Calendar size={14} />
            <span>创建时间：</span>
            <span className="font-mono">
              {format(new Date(session.created_at), 'yyyy-MM-dd HH:mm:ss', { locale: zhCN })}
            </span>
          </div>
          
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <Clock size={14} />
            <span>最后活动：</span>
            <span className="font-mono">
              {format(new Date(session.last_activity), 'yyyy-MM-dd HH:mm:ss', { locale: zhCN })}
            </span>
          </div>
        </div>
      </Card>

      {/* 工具调用时间线 */}
      <ToolCallTimeline toolCalls={toolCalls} limit={10} />

      {/* 消息历史 */}
      <Card className="flex flex-col" style={{ height: '500px' }}>
        <div className="flex items-center gap-2 mb-4 p-4 border-b border-border-default">
          <Code size={18} className="text-primary-500" />
          <h2 className="text-lg font-semibold text-text-primary">
            消息历史
          </h2>
          <span className="text-sm text-text-muted ml-auto">
            {messages.length} 条消息
          </span>
        </div>
        <MessageList 
          messages={messages}
          loading={syncing}
          onLoadMore={handleLoadMore}
          hasMore={messageOffset < (session.message_count || 0)}
        />
      </Card>
    </div>
  );
};

export default SessionDetail;
