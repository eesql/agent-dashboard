/**
 * 会话列表页面
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { sessionApi } from '@/services/api';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { 
  MessageSquare, 
  Clock, 
  Search, 
  Filter,
  RefreshCw,
  Calendar,
  User
} from 'lucide-react';
import type { Session } from '@/types';
import { formatDistanceToNow, format } from 'date-fns';
import { zhCN } from 'date-fns/locale';

export const Sessions: React.FC = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterKind, setFilterKind] = useState<string>('all');
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await sessionApi.list({ limit: 100 });
      setSessions(result.sessions || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch sessions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const formatTime = (dateString: string) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      
      // 24 小时内显示相对时间，否则显示日期
      if (diff < 24 * 60 * 60 * 1000) {
        return formatDistanceToNow(date, { 
          addSuffix: true,
          locale: zhCN 
        });
      }
      return format(date, 'MM-dd HH:mm', { locale: zhCN });
    } catch {
      return 'Unknown';
    }
  };

  const getKindBadge = (kind: string | null) => {
    if (!kind) return <span className="text-xs text-text-muted">-</span>;
    
    const colors: Record<string, string> = {
      subagent: 'badge-online',
      acp: 'badge-busy',
      default: 'badge-offline',
    };
    
    return (
      <span className={`badge ${colors[kind] || colors.default}`}>
        {kind}
      </span>
    );
  };

  // 过滤会话
  const filteredSessions = sessions.filter(session => {
    const matchSearch = !searchTerm || 
      session.label?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      session.id.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchKind = filterKind === 'all' || session.kind === filterKind;
    
    return matchSearch && matchKind;
  });

  const uniqueKinds = Array.from(new Set(sessions.map(s => s.kind).filter(Boolean)));

  return (
    <div className="p-6 space-y-6">
      {/* 页面头部 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Sessions</h1>
          <p className="text-sm text-text-secondary mt-1">
            会话历史管理
          </p>
        </div>
        <Button onClick={fetchSessions} loading={loading} variant="secondary">
          <RefreshCw size={16} />
          刷新
        </Button>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="p-4 bg-error-500/10 border border-error-500/20 rounded-lg">
          <p className="text-sm text-error-500">{error}</p>
        </div>
      )}

      {/* 搜索和筛选 */}
      <Card>
        <div className="flex flex-col md:flex-row gap-4">
          {/* 搜索框 */}
          <div className="flex-1 relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
            <input
              type="text"
              placeholder="搜索会话 ID 或标签..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
          
          {/* 类型筛选 */}
          <div className="flex items-center gap-2">
            <Filter size={18} className="text-text-muted" />
            <select
              value={filterKind}
              onChange={(e) => setFilterKind(e.target.value)}
              className="input w-auto"
            >
              <option value="all">全部类型</option>
              {uniqueKinds.map(kind => (
                <option key={kind} value={kind}>{kind}</option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {/* 统计信息 */}
      <div className="flex items-center gap-4 text-sm text-text-secondary">
        <span>共 {filteredSessions.length} 个会话</span>
        <span>（总计 {sessions.length} 个）</span>
      </div>

      {/* 会话列表 */}
      {filteredSessions.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <MessageSquare size={48} className="mx-auto text-text-muted mb-4" />
            <p className="text-text-secondary">
              {sessions.length === 0 ? '暂无会话数据' : '没有匹配的会话'}
            </p>
          </div>
        </Card>
      ) : (
        <Card className="overflow-hidden p-0">
          <div className="overflow-x-auto">
            <table className="table w-full">
              <thead>
                <tr className="border-b border-border-default">
                  <th className="font-medium">会话 ID</th>
                  <th className="font-medium">标签</th>
                  <th className="font-medium">类型</th>
                  <th className="font-medium">Agent</th>
                  <th className="font-medium">消息数</th>
                  <th className="font-medium">最后活动</th>
                  <th className="font-medium">操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredSessions.map((session) => (
                  <tr 
                    key={session.id}
                    className="border-b border-divider hover:bg-bg-tertiary transition-colors"
                  >
                    <td className="font-mono text-sm text-text-primary">
                      {session.id.slice(0, 12)}...
                    </td>
                    <td className="text-sm text-text-primary">
                      {session.label || '-'}
                    </td>
                    <td>
                      {getKindBadge(session.kind)}
                    </td>
                    <td className="text-sm text-text-secondary">
                      <div className="flex items-center gap-1">
                        <User size={14} />
                        {session.agent_id ? session.agent_id.slice(0, 8) + '...' : '-'}
                      </div>
                    </td>
                    <td className="text-sm text-text-secondary font-tabular">
                      {session.message_count}
                    </td>
                    <td className="text-sm text-text-secondary">
                      <div className="flex items-center gap-1">
                        <Clock size={14} />
                        {formatTime(session.last_activity)}
                      </div>
                    </td>
                    <td>
                      <Button 
                        size="sm" 
                        variant="ghost"
                        onClick={() => navigate(`/sessions/${session.id}`)}
                      >
                        详情
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Sessions;
