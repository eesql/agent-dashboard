/**
 * Session Info Store - 管理会话信息状态
 */
import { create } from 'zustand';
import type { SessionInfo } from '@/types';
import { api } from '@/lib/api';

interface SessionInfoState {
  sessions: SessionInfo[];
  summary: {
    total: number;
    online: number;
    busy: number;
    offline: number;
    total_tokens: number;
    by_channel: Record<string, number>;
    by_agent: Record<string, number>;
  } | null;
  loading: boolean;
  error: string | null;
  
  fetchSessions: (filters?: { agent_id?: string; status?: string }) => Promise<void>;
  fetchSummary: () => Promise<void>;
  clearError: () => void;
}

export const useSessionInfoStore = create<SessionInfoState>((set) => ({
  sessions: [],
  summary: null,
  loading: false,
  error: null,
  
  fetchSessions: async (filters = {}) => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams();
      if (filters.agent_id) params.append('agent_id', filters.agent_id);
      if (filters.status) params.append('status', filters.status);
      
      const data = await api.get<SessionInfo[]>(`/api/session-info?${params.toString()}`);
      set({ sessions: data, loading: false });
    } catch (error: any) {
      set({ error: error.message || 'Failed to fetch sessions', loading: false });
    }
  },
  
  fetchSummary: async () => {
    try {
      const data = await api.get<any>('/api/session-info/summary');
      set({ summary: data });
    } catch (error: any) {
      console.error('Failed to fetch session summary:', error);
    }
  },
  
  clearError: () => set({ error: null }),
}));
