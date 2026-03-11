/**
 * Agent Dashboard 类型定义
 */

// Agent 状态枚举
export type AgentStatus = 'online' | 'offline' | 'busy' | 'error';

// Agent 接口
export interface Agent {
  id: string;
  name: string | null;
  status: AgentStatus;
  current_task: string | null;
  last_seen: string;
  created_at: string;
  updated_at: string;
}

// Session 状态枚举
export type SessionStatus = 'online' | 'offline' | 'busy';

// Thinking level 类型
export type ThinkingLevel = 'off' | 'minimal' | 'low' | 'medium' | 'high' | 'xhigh';

// Session 接口（扩展）
export interface Session {
  id: string;
  agent_id: string | null;
  label: string | null;
  kind: string | null;
  created_at: string;
  last_activity: string;
  message_count: number;
  request_count: number;
}

// Session 详情接口（用于卡片展示）
export interface SessionInfo {
  id: string;
  agent_id: string;
  agent_name: string;
  channel: string;
  status: SessionStatus;
  model: string;
  thinking_level: ThinkingLevel;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  context_limit: number;
  context_usage_percent: number;
  last_activity: string;
  created_at: string;
}

// Tool Call 接口
export interface ToolCall {
  id: number;
  session_id: string | null;
  tool_name: string;
  tool_args: Record<string, any> | null;
  result_summary: string | null;
  timestamp: string;
  duration_ms: number | null;
}

// Metrics 接口
export interface Metrics {
  agent_id: string | null;
  date: string;
  token_count: number;
  request_count: number;
  avg_response_time_ms: number;
  estimated_cost: number;
}

// Metrics Summary 接口
export interface MetricsSummary {
  today: {
    token_count: number;
    request_count: number;
    estimated_cost: number;
  } | null;
  this_week: {
    token_count: number;
    request_count: number;
    estimated_cost: number;
  } | null;
  this_month: {
    token_count: number;
    request_count: number;
    estimated_cost: number;
  } | null;
  total_agents: number;
  active_agents: number;
}

// Trend Data 接口
export interface TrendDataPoint {
  date: string;
  token_count: number;
  request_count: number;
  estimated_cost: number;
}

// API 响应类型
export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export interface ListResponse<T> {
  sessions?: T[];
  messages?: T[];
  tool_calls?: T[];
  [key: string]: T[] | number | undefined;
  total: number;
}

// Message 接口
export interface Message {
  id: number;
  session_id: string;
  role: string;
  content: string | null;
  tool_call_id: string | null;
  tool_name: string | null;
  tool_args: Record<string, any> | null;
  tool_result: string | null;
  is_tool_call: boolean;
  is_tool_result: boolean;
  timestamp: string;
}
