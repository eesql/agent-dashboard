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
  Code
} from 'lucide-react';
import type { Session, ToolCall } from '@/types';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';

export const SessionDetail: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<Session | null>(null);
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    
    const fetchSessionDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        // TODO: 调用 API 获取会话详情和消息历史
        // const result = await sessionApi.get(sessionId);
        // setSession(result);
        
        // 模拟数据
        setSession({
          id: sessionId,
          agent_id: 'agent-123',
          label: 'Demo Session',
          kind: 'subagent',
          created_at: new Date(Date.now() - 86400000).toISOString(),
          last_activity: new Date().toISOString(),
          message_count: 15,
        });
        
        setToolCalls([
          {
            id: 1,
            session_id: sessionId,
            tool_name: 'read',
            tool_args: { path: './src/App.tsx' },
            result_summary: 'Read 150 lines',
            timestamp: new Date().toISOString(),
            duration_ms: 45,
          },
          {
            id: 2,
            session_id: sessionId,
            tool_name: 'exec',
            tool_args: { command: 'npm install' },
            result_summary: 'Installed packages',
            timestamp: new Date(Date.now() - 300000).toISOString(),
            duration_ms: 15230,
          },
        ]);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch session details');
      } finally {
        setLoading(false);
      }
    };

    fetchSessionDetail();
  }, [sessionId]);

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
      <Card>
        <div className="flex items-center gap-2 mb-4">
          <Code size={18} className="text-primary-500" />
          <h2 className="text-lg font-semibold text-text-primary">
            消息历史
          </h2>
        </div>
        <MessageList sessionId={sessionId} />
      </Card>
    </div>
  );
};

export default SessionDetail;
