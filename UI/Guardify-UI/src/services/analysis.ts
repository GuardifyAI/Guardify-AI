// src/services/analysis.ts
import { apiService, type ApiResponse } from './api';
import type { ApiEventAnalysis } from '../types/api';

export async function getEventAnalysis(
  eventId: string,
  token: string
): Promise<ApiResponse<ApiEventAnalysis >> {
  return apiService.makeRequest<ApiEventAnalysis >(`/analysis/${eventId}`, { method: 'GET' }, token);
}


export const analysisService = { getEventAnalysis };
export default analysisService;
