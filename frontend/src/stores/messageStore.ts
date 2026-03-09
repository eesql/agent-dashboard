/**
 * 消息 Store
 */
import { create } from 'zustand';
import { api } from '@/services/api';

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

interface MessageState {
  messages: Message[];
  loading: boolean;
  error: string | null;
  total: number;
  hasMore: boolean;
  
  fetchMessages: (sessionId: string, params?: { limit?: number; offset?: number }) => Promise<void>;
  syncMessages: (sessionId: string) => Promise<void>;
  clearMessages: () => void;
}

export const useMessageStore = create<MessageState>((set, get) => ({
  messages: [],
  loading: false,
  error: null,
  total: 0,
  hasMore: false,

  fetchMessages: async (sessionId: string, params?: { limit?: number; offset?: number }) => {
    set({ loading: true, error: null });
    try {
      const queryParams = new URLSearchParams();
      if (params?.limit) queryParams.append('limit', params.limit.toString());
      if (params?.offset) queryParams.append('offset', params.offset.toString());
      
      const response = await api.get(`/api/sessions/${sessionId}/messages?${queryParams}`);
      const data = await response.json();
      
      set({
        messages: data.messages || [],
        total: data.total || 0,
        hasMore: data.has_more || false,
        loading: false,
      });
    } catch (error: any) {
      set({
        error: error.message || 'Failed to fetch messages',
        loading: false,
      });
    }
  },

  syncMessages: async (sessionId: string) => {
    try {
      const response = await api.post(`/api/sessions/${sessionId}/messages/sync`);
      const data = await response.json();
      console.log('Messages synced:', data);
      
      // 同步后重新获取消息
      await get().fetchMessages(sessionId);
    } catch (error: any) {
      console.error('Failed to sync messages:', error);
    }
  },

  clearMessages: () => {
    set({
      messages: [],
      total: 0,
      hasMore: false,
      error: null,
    });
  },
}));
