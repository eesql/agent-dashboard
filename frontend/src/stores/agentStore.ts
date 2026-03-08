/**
 * Agent 状态管理
 */
import { create } from 'zustand';
import { agentApi } from '@/services/api';
import type { Agent } from '@/types';
import type { WebSocketMessage } from '@/hooks/useWebSocket';

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
      const agents = await agentApi.list();
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
      const result = await agentApi.sync();
      if (result.success) {
        set({ 
          agents: result.agents || get().agents, 
          loading: false, 
          lastSync: new Date(),
          syncMessage: `同步成功：${result.synced_agents} 个 Agent`
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
  
  /** 处理 WebSocket 消息 */
  handleWebSocketMessage: (message: WebSocketMessage) => {
    if (message.type === 'agent:status') {
      const updatedAgent = message.data as Agent;
      const agents = get().agents;
      const index = agents.findIndex(a => a.id === updatedAgent.id);
      
      if (index >= 0) {
        // 更新现有 Agent
        const newAgents = [...agents];
        newAgents[index] = updatedAgent;
        set({ agents: newAgents });
      } else {
        // 添加新 Agent
        set({ agents: [...agents, updatedAgent] });
      }
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
