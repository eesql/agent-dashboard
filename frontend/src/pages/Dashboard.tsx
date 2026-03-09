/**
 * Dashboard 主页面
 */
import React, { useEffect } from 'react';
import { useAgentStore } from '@/stores/agentStore';
import { useMetricsStore } from '@/stores/metricsStore';
import { useToolCallStore } from '@/stores/toolCallStore';
import { useWebSocket } from '@/hooks/useWebSocket';
import { AgentCard } from '@/components/dashboard/AgentCard';
import { MetricsCard } from '@/components/dashboard/MetricsCard';
import { ToolCallTimeline } from '@/components/dashboard/ToolCallTimeline';
import { StatsChart } from '@/components/dashboard/StatsChart';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { RefreshCw, Box, Wifi, WifiOff, MessageSquare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { 
    agents, 
    loading: agentsLoading, 
    error: agentsError,
    syncMessage,
    fetchAgents, 
    syncAgents,
    getOnlineAgents,
    clearError,
    clearSyncMessage
  } = useAgentStore();
  
  const { 
    summary, 
    trendData,
    fetchSummary,
    fetchTrendData,
  } = useMetricsStore();
  
  const { 
    toolCalls, 
    fetchToolCalls,
  } = useToolCallStore();

  // WebSocket 连接
  const { isConnected } = useWebSocket({
    url: 'ws://localhost:8000/ws',
    onConnect: () => {
      console.log('[Dashboard] WebSocket connected');
    },
    onDisconnect: () => {
      console.log('[Dashboard] WebSocket disconnected');
    },
  });

  useEffect(() => {
    // 初始加载
    fetchAgents();
    fetchSummary();
    fetchTrendData(7); // 获取过去 7 天的趋势数据
    fetchToolCalls({ limit: 20, hours: 24 }); // 获取最近 20 条工具调用记录
    
    // 定时刷新（每 30 秒）
    const interval = setInterval(() => {
      fetchAgents();
      fetchSummary();
      fetchTrendData(7);
      fetchToolCalls({ limit: 20, hours: 24 });
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const handleSync = async () => {
    await syncAgents();
  };

  const onlineAgents = getOnlineAgents();

  return (
    <div className="p-6 space-y-6">
      {/* 页面头部 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Dashboard</h1>
          <p className="text-sm text-text-secondary mt-1">
            OpenClaw Agent 状态监控
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* WebSocket 状态指示器 */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-bg-secondary border border-border-default rounded-md">
            {isConnected ? (
              <>
                <Wifi size={16} className="text-success-500" />
                <span className="text-xs text-text-secondary">Live</span>
              </>
            ) : (
              <>
                <WifiOff size={16} className="text-text-muted" />
                <span className="text-xs text-text-muted">Offline</span>
              </>
            )}
          </div>
          
          <Button 
            onClick={handleSync} 
            loading={agentsLoading}
            variant="secondary"
          >
            <RefreshCw size={16} />
            同步状态
          </Button>
        </div>
      </div>

      {/* 错误提示 */}
      {agentsError && (
        <div className="p-4 bg-error-500/10 border border-error-500/20 rounded-lg flex items-center justify-between">
          <p className="text-sm text-error-500">{agentsError}</p>
          <button onClick={clearError} className="text-error-500 hover:text-error-400">×</button>
        </div>
      )}
      
      {/* 同步成功提示 */}
      {syncMessage && (
        <div className="p-4 bg-success-500/10 border border-success-500/20 rounded-lg flex items-center justify-between">
          <p className="text-sm text-success-500">{syncMessage}</p>
          <button onClick={clearSyncMessage} className="text-success-500 hover:text-success-400">×</button>
        </div>
      )}

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricsCard
          title="Total Agents"
          value={summary?.total_agents || 0}
          icon="agents"
        />
        <MetricsCard
          title="Active Agents"
          value={onlineAgents.length}
          icon="agents"
          subtitle={`${summary?.active_agents || 0} online`}
        />
        <MetricsCard
          title="Requests Today"
          value={summary?.today?.request_count || 0}
          icon="requests"
        />
        <MetricsCard
          title="Tokens Today"
          value={summary?.today?.token_count || 0}
          icon="tokens"
          subtitle={`$${(summary?.today?.estimated_cost || 0).toFixed(4)}`}
        />
      </div>

      {/* Agent 列表 */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-text-primary">
            Agents ({agents.length})
          </h2>
          <span className="text-sm text-text-secondary">
            Last sync: {agentsLoading ? 'Syncing...' : 'Just now'}
          </span>
        </div>

        {agents.length === 0 ? (
          <div className="text-center py-12">
            <Box size={48} className="mx-auto text-text-muted mb-4" />
            <p className="text-text-secondary">No agents found</p>
            <p className="text-sm text-text-muted mt-2">
              Click "同步状态" to fetch agents from OpenClaw
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent) => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>
        )}
      </div>

      {/* 统计图表 + 工具调用时间线 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 统计图表 */}
        <StatsChart 
          data={trendData || undefined} 
          type="tokens" 
          period="week" 
        />
        
        {/* 工具调用时间线 */}
        <ToolCallTimeline 
          toolCalls={toolCalls} 
          limit={5} 
        />
      </div>

      {/* Sessions 快捷入口 */}
      <Card hover className="cursor-pointer" onClick={() => navigate('/sessions')}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary-500/10 rounded-lg">
              <MessageSquare size={24} className="text-primary-500" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-text-primary">
                查看会话历史
              </h3>
              <p className="text-sm text-text-secondary mt-1">
                管理所有会话记录和消息历史
              </p>
            </div>
          </div>
          <Button variant="secondary">
            前往 Sessions →
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default Dashboard;
