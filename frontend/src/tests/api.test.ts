/**
 * API 服务测试用例
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { agentApi, sessionApi, toolCallApi, metricsApi, messageApi } from '@/services/api';

// Mock axios
const mockGet = vi.fn();
const mockPost = vi.fn();

vi.mock('@/utils/request', () => ({
  request: {
    get: (url: string, config?: any) => mockGet(url, config),
    post: (url: string, data?: any, config?: any) => mockPost(url, data, config),
  },
}));

describe('API Services', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('agentApi', () => {
    it('should list agents', async () => {
      const mockData = [
        { id: 'agent:1', name: 'model-1', status: 'online' },
        { id: 'agent:2', name: 'model-2', status: 'offline' },
      ];
      mockGet.mockResolvedValue(mockData);

      const result = await agentApi.list();

      expect(mockGet).toHaveBeenCalledWith('/agents', undefined);
      expect(result).toEqual(mockData);
    });

    it('should get single agent', async () => {
      const mockData = { id: 'agent:1', name: 'model-1', status: 'online' };
      mockGet.mockResolvedValue(mockData);

      const result = await agentApi.get('agent:1');

      expect(mockGet).toHaveBeenCalledWith('/agents/agent:1', undefined);
      expect(result).toEqual(mockData);
    });

    it('should sync agents', async () => {
      const mockData = { synced: 4, agents: [] };
      mockPost.mockResolvedValue(mockData);

      const result = await agentApi.sync();

      expect(mockPost).toHaveBeenCalledWith('/agents/sync', undefined, undefined);
      expect(result).toEqual(mockData);
    });
  });

  describe('sessionApi', () => {
    it('should list sessions', async () => {
      const mockData = {
        sessions: [
          { id: 'session:1', label: 'test', kind: 'direct' },
          { id: 'session:2', label: 'test2', kind: 'subagent' },
        ],
        total: 2,
      };
      mockGet.mockResolvedValue(mockData);

      const result = await sessionApi.list({ limit: 100 });

      expect(mockGet).toHaveBeenCalledWith('/sessions', { params: { limit: 100 } });
      expect(result).toEqual(mockData);
      expect(result.sessions).toBeDefined();
    });

    it('should list sessions with default params', async () => {
      const mockData = { sessions: [], total: 0 };
      mockGet.mockResolvedValue(mockData);

      await sessionApi.list();

      expect(mockGet).toHaveBeenCalledWith('/sessions', { params: undefined });
    });

    it('should get session detail', async () => {
      const mockData = {
        id: 'session:1',
        label: 'test',
        kind: 'direct',
        agent_id: 'agent:1',
        message_count: 100,
      };
      mockGet.mockResolvedValue(mockData);

      const result = await sessionApi.get('session:1');

      expect(mockGet).toHaveBeenCalledWith('/sessions/session:1', undefined);
      expect(result).toEqual(mockData);
      expect(result.id).toBe('session:1');
    });
  });

  describe('toolCallApi', () => {
    it('should list tool calls', async () => {
      const mockData = {
        tool_calls: [
          { id: 1, tool_name: 'web_search', session_id: 'session:1' },
        ],
        total: 1,
      };
      mockGet.mockResolvedValue(mockData);

      const result = await toolCallApi.list({ session_id: 'session:1', limit: 20 });

      expect(mockGet).toHaveBeenCalledWith('/tool-calls', {
        params: { session_id: 'session:1', limit: 20 },
      });
      expect(result).toEqual(mockData);
      expect(result.tool_calls).toBeDefined();
    });

    it('should get single tool call', async () => {
      const mockData = { id: 1, tool_name: 'web_search' };
      mockGet.mockResolvedValue(mockData);

      const result = await toolCallApi.get(1);

      expect(mockGet).toHaveBeenCalledWith('/tool-calls/1', undefined);
      expect(result).toEqual(mockData);
    });
  });

  describe('metricsApi', () => {
    it('should get metrics summary', async () => {
      const mockData = {
        today: { token_count: 1000, request_count: 10 },
        this_week: { token_count: 5000, request_count: 50 },
        this_month: { token_count: 20000, request_count: 200 },
      };
      mockGet.mockResolvedValue(mockData);

      const result = await metricsApi.getSummary();

      expect(mockGet).toHaveBeenCalledWith('/metrics/summary', undefined);
      expect(result).toEqual(mockData);
    });

    it('should get today metrics', async () => {
      const mockData = { date: '2026-03-10', token_count: 1000 };
      mockGet.mockResolvedValue(mockData);

      const result = await metricsApi.getToday();

      expect(mockGet).toHaveBeenCalledWith('/metrics/today', undefined);
      expect(result).toEqual(mockData);
    });

    it('should get trend data', async () => {
      const mockData = [
        { date: '2026-03-04', token_count: 100 },
        { date: '2026-03-05', token_count: 200 },
      ];
      mockGet.mockResolvedValue(mockData);

      const result = await metricsApi.getTrend(7, 'agent:1');

      expect(mockGet).toHaveBeenCalledWith('/metrics/trend', {
        params: { days: 7, agent_id: 'agent:1' },
      });
      expect(result).toEqual(mockData);
    });
  });

  describe('messageApi', () => {
    it('should list messages', async () => {
      const mockData = {
        messages: [{ id: 1, content: 'Hello' }],
        total: 1,
        has_more: false,
      };
      mockGet.mockResolvedValue(mockData);

      const result = await messageApi.list('session:1', { limit: 50, offset: 0 });

      expect(mockGet).toHaveBeenCalledWith('/sessions/session:1/messages', {
        params: { limit: 50, offset: 0 },
      });
      expect(result).toEqual(mockData);
      expect(result.messages).toBeDefined();
    });

    it('should sync messages', async () => {
      const mockData = { status: 'success', count: 10 };
      mockPost.mockResolvedValue(mockData);

      const result = await messageApi.sync('session:1');

      expect(mockPost).toHaveBeenCalledWith('/sessions/session:1/messages/sync', undefined, undefined);
      expect(result).toEqual(mockData);
    });
  });
});
