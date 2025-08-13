// src/services/analysis.ts
import { apiService, type ApiResponse } from './api';
import type { ApiEventAnalysis } from '../types/api';

export async function getEventAnalysis(
  eventId: string,
  token: string
): Promise<ApiResponse<ApiEventAnalysis >> {
  return apiService.makeRequest<ApiEventAnalysis >(`/analysis/${eventId}`, { method: 'GET' }, token);
}

export async function upsertEventAnalysis(
  eventId: string,
  body: { final_detection: boolean; final_confidence: number; decision_reasoning: string },
  token: string
): Promise<ApiResponse<ApiEventAnalysis >> {
  return apiService.makeRequest<ApiEventAnalysis >(
    `/analysis/${eventId}`,
    { method: 'POST', body: JSON.stringify(body) },
    token
  );
}

export const analysisService = { getEventAnalysis, upsertEventAnalysis };
export default analysisService;
