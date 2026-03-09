/**
 * API 服务封装
 */
import { request } from '@/utils/request';
import type { Agent, Session, ToolCall, MetricsSummary, ListResponse, TrendDataPoint, Message } from '@/types';

// Agent API
export const agentApi = {
  // 获取所有 Agent
  list: () => {
    return request.get<Agent[]>('/agents');
  },
  
  // 获取单个 Agent
  get: (agentId: string) => {
    return request.get<Agent>(`/agents/${agentId}`);
  },
  
  // 同步 Agent 状态
  sync: () => {
    return request.post<{ synced: number; agents: Agent[] }>('/agents/sync');
  },
};

// Session API
export const sessionApi = {
  // 获取会话列表
  list: (params?: { limit?: number; agent_id?: string }) => {
    return request.get<ListResponse<Session>>('/sessions', { params });
  },
  
  // 获取会话详情
  get: (sessionId: string) => {
    return request.get<Session>(`/sessions/${sessionId}`);
  },
};

// Tool Call API
export const toolCallApi = {
  // 获取工具调用列表
  list: (params?: { session_id?: string; limit?: number; hours?: number }) => {
    return request.get<ListResponse<ToolCall>>('/tool-calls', { params });
  },
  
  // 获取单个工具调用
  get: (toolCallId: number) => {
    return request.get<ToolCall>(`/tool-calls/${toolCallId}`);
  },
};

// Metrics API
export const metricsApi = {
  // 获取统计汇总
  getSummary: () => {
    return request.get<MetricsSummary>('/metrics/summary');
  },
  
  // 获取今日统计
  getToday: () => {
    return request.get<MetricsSummary>('/metrics/today');
  },
  
  // 获取趋势数据
  getTrend: (days: number = 7, agentId?: string) => {
    const params: any = { days };
    if (agentId) {
      params.agent_id = agentId;
    }
    return request.get<TrendDataPoint[]>('/metrics/trend', { params });
  },
};

// Message API
export const messageApi = {
  // 获取消息列表
  list: (sessionId: string, params?: { limit?: number; offset?: number }) => {
    return request.get<{ messages: Message[]; total: number; has_more: boolean }>(
      `/sessions/${sessionId}/messages`,
      { params }
    );
  },
  
  // 同步消息
  sync: (sessionId: string) => {
    return request.post<{ status: string; count: number }>(
      `/sessions/${sessionId}/messages/sync`
    );
  },
};
