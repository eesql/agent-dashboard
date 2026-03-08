/**
 * API 服务封装
 */
import { request } from '@/utils/request';
import type { Agent, Session, ToolCall, MetricsSummary, ListResponse } from '@/types';

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
};
