/**
 * Metrics 状态管理
 */
import { create } from 'zustand';
import { metricsApi } from '@/services/api';
import type { MetricsSummary } from '@/types';

interface MetricsState {
  summary: MetricsSummary | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchSummary: () => Promise<void>;
  clearError: () => void;
}

export const useMetricsStore = create<MetricsState>((set) => ({
  summary: null,
  loading: false,
  error: null,
  
  fetchSummary: async () => {
    set({ loading: true, error: null });
    try {
      const summary = await metricsApi.getSummary();
      set({ summary, loading: false });
    } catch (error: any) {
      set({ 
        loading: false, 
        error: error.message || 'Failed to fetch metrics' 
      });
    }
  },
  
  clearError: () => {
    set({ error: null });
  },
}));
