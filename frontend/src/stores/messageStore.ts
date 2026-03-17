/**
 * 消息 Store
 */
import { create } from 'zustand';
import { messageApi } from '@/services/api';
import type { Message } from '@/types';

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
      const data = await messageApi.list(sessionId, params);
      
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
      await messageApi.sync(sessionId);
      console.log('Messages synced');
      
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
