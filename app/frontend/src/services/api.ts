/**
 * api.ts — API Client for LendFlow FinOps Platform
 * Connects to FastAPI backend (/api/...) with robust fallback data.
 */

import {
  SummaryResponse, ExplorerResponse, OptimisationsResponse,
  StorageResponse, TransferResponse, TagsResponse,
  AnomaliesResponse, SimulatorResponse, WarRoomResponse,
  WarRoomActionResponse
} from '../types/finops';

const API_BASE = '/api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  if (!res.ok) {
    throw new Error(`API Error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const finopsApi = {
  getSummary: async (): Promise<SummaryResponse> => {
    return fetchJson<SummaryResponse>('/summary');
  },

  getExplorer: async (params?: Record<string, string | number>): Promise<ExplorerResponse> => {
    const query = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : '';
    return fetchJson<ExplorerResponse>(`/explorer${query}`);
  },

  getOptimisations: async (params?: Record<string, string>): Promise<OptimisationsResponse> => {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return fetchJson<OptimisationsResponse>(`/optimisations${query}`);
  },

  getStorage: async (): Promise<StorageResponse> => {
    return fetchJson<StorageResponse>('/storage');
  },

  getTransfer: async (): Promise<TransferResponse> => {
    return fetchJson<TransferResponse>('/transfer');
  },

  getTags: async (): Promise<TagsResponse> => {
    return fetchJson<TagsResponse>('/tags');
  },

  getAnomalies: async (params?: Record<string, string | number>): Promise<AnomaliesResponse> => {
    const query = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : '';
    return fetchJson<AnomaliesResponse>(`/anomalies${query}`);
  },

  getSimulator: async (): Promise<SimulatorResponse> => {
    return fetchJson<SimulatorResponse>('/simulator');
  },

  simulate: async (enabledIds: number[]): Promise<SimulatorResponse> => {
    return fetchJson<SimulatorResponse>('/simulator', {
      method: 'POST',
      body: JSON.stringify({ enabled_recommendation_ids: enabledIds })
    });
  },

  getWarRoom: async (): Promise<WarRoomResponse> => {
    return fetchJson<WarRoomResponse>('/war-room');
  },

  simulateWarRoomAction: async (scenarioId: string, actionIds: string[]): Promise<WarRoomActionResponse> => {
    return fetchJson<WarRoomActionResponse>('/war-room/simulate', {
      method: 'POST',
      body: JSON.stringify({ scenario_id: scenarioId, selected_action_ids: actionIds })
    });
  },

  dispatchAnomalyAlert: async (anomalyId: string, channel: string = 'slack'): Promise<{ status: string; message: string; recipient: string }> => {
    return fetchJson<{ status: string; message: string; recipient: string }>(`/anomalies/${anomalyId}/alert?channel=${channel}`, {
      method: 'POST'
    });
  }
};
