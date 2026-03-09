/**
 * Agent 状态管理
 */
import { create } from 'zustand';
import { agentApi } from '@/services/api';
import type { Agent } from '@/types';

interface AgentState {
  agents: Agent[];
  loading: boolean;
  error: string | null;
  lastSync: Date | null;
  syncMessage: string | null;
  
  // Actions
  fetchAgents: () => Promise<void>;
  syncAgents: () => Promise<void>;
  getAgent: (agentId: string) => Agent | undefined;
  getOnlineAgents: () => Agent[];
  clearError: () => void;
  clearSyncMessage: () => void;
}

export const useAgentStore = create<AgentState>((set, get) => ({
  agents: [],
  loading: false,
  error: null,
  lastSync: null,
  syncMessage: null,
  
  fetchAgents: async () => {
    set({ loading: true, error: null });
    try {
      const agents = await agentApi.list() as unknown as Agent[];
      set({ agents, loading: false, lastSync: new Date() });
    } catch (error: any) {
      set({ 
        loading: false, 
        error: error.message || 'Failed to fetch agents' 
      });
    }
  },
  
  syncAgents: async () => {
    set({ loading: true, error: null });
    try {
      const result = await agentApi.sync() as unknown as { success: boolean; synced: number; agents?: Agent[]; synced_agents?: number; error?: string };
      if (result.success) {
        set({ 
          agents: result.agents || get().agents, 
          loading: false, 
          lastSync: new Date(),
          syncMessage: `同步成功：${result.synced || result.synced_agents || 0} 个 Agent`
        });
      } else {
        throw new Error(result.error || 'Sync failed');
      }
    } catch (error: any) {
      set({ 
        loading: false, 
        error: error.message || 'Failed to sync agents' 
      });
    }
  },
  

  
  getAgent: (agentId: string) => {
    return get().agents.find(a => a.id === agentId);
  },
  
  getOnlineAgents: () => {
    return get().agents.filter(a => a.status === 'online' || a.status === 'busy');
  },
  
  clearError: () => {
    set({ error: null });
  },
  
  clearSyncMessage: () => {
    set({ syncMessage: null });
  },
}));
