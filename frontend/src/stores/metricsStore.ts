/**
 * Metrics 状态管理
 */
import { create } from 'zustand';
import { metricsApi } from '@/services/api';
import type { MetricsSummary, TrendDataPoint } from '@/types';

interface MetricsState {
  summary: MetricsSummary | null;
  trendData: TrendDataPoint[] | null;
  loading: boolean;
  loadingTrend: boolean;
  error: string | null;
  errorTrend: string | null;
  
  // Actions
  fetchSummary: () => Promise<void>;
  fetchTrendData: (days?: number, agentId?: string) => Promise<void>;
  clearError: () => void;
}

export const useMetricsStore = create<MetricsState>((set) => ({
  summary: null,
  trendData: null,
  loading: false,
  loadingTrend: false,
  error: null,
  errorTrend: null,
  
  fetchSummary: async () => {
    set({ loading: true, error: null });
    try {
      const summary = await metricsApi.getSummary() as unknown as MetricsSummary;
      set({ summary, loading: false });
    } catch (error: any) {
      set({ 
        loading: false, 
        error: error.message || 'Failed to fetch metrics' 
      });
    }
  },
  
  fetchTrendData: async (days: number = 7, agentId?: string) => {
    set({ loadingTrend: true, errorTrend: null });
    try {
      const trendData = await metricsApi.getTrend(days, agentId) as unknown as TrendDataPoint[];
      set({ trendData, loadingTrend: false });
    } catch (error: any) {
      set({ 
        loadingTrend: false, 
        errorTrend: error.message || 'Failed to fetch trend data' 
      });
    }
  },
  
  clearError: () => {
    set({ error: null });
  },
}));
