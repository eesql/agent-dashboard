/**
 * Tool Call 状态管理
 */
import { create } from 'zustand';
import { toolCallApi } from '@/services/api';
import type { ToolCall } from '@/types';

interface ToolCallState {
  toolCalls: ToolCall[];
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchToolCalls: (params?: { limit?: number; hours?: number }) => Promise<void>;
  clearError: () => void;
}

export const useToolCallStore = create<ToolCallState>((set) => ({
  toolCalls: [],
  loading: false,
  error: null,
  
  fetchToolCalls: async (params?: { limit?: number; hours?: number }) => {
    set({ loading: true, error: null });
    try {
      const response = await toolCallApi.list(params);
      const data = response as unknown as { tool_calls: ToolCall[]; total: number };
      set({ toolCalls: data.tool_calls || [], loading: false });
    } catch (error: any) {
      set({ 
        loading: false, 
        error: error.message || 'Failed to fetch tool calls' 
      });
    }
  },
  
  clearError: () => {
    set({ error: null });
  },
}));
