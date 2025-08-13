// src/services/events.ts
import { apiService, type ApiResponse } from './api';
import type { ApiEvent, ApiEventWithAnalysis } from '../types/api';

export async function getAllEvents(token: string, includeAnalysis: boolean = false )
:Promise<ApiResponse<ApiEvent[] | ApiEventWithAnalysis[]>> {
  const qs = includeAnalysis ? '?include_analysis=1' : '';
  return apiService.makeRequest<ApiEvent[] | ApiEventWithAnalysis[]>(
    `/events${qs}`, { method: 'GET' }, token);
}
  
export async function getShopEvents( shopId: string, token: string, includeAnalysis: boolean = false )
:Promise<ApiResponse<ApiEvent[] | ApiEventWithAnalysis[]>> {
  const qs = includeAnalysis ? '?include_analysis=1' : '';
  return apiService.makeRequest<ApiEvent[] | ApiEventWithAnalysis[]>(
  `/shops/${shopId}/events${qs}`, { method: 'GET' }, token );
}

export async function getEventDetails(
  shopId: string,
  eventId: string,
  token: string
  ): Promise<ApiResponse<ApiEventWithAnalysis>> {
    // Details always include analysis
    return apiService.makeRequest<ApiEventWithAnalysis>(
    `/shops/${shopId}/events/${eventId}?include_analysis=1`, { method: 'GET' }, token);
}       
        
class EventsService {
  async getGlobalEvents(token: string, includeAnalysis: boolean = false): Promise<ApiResponse<ApiEvent[] | ApiEventWithAnalysis[]>> {
    return getAllEvents(token, includeAnalysis);
  }

  async getShopEvents(shopId: string, token: string, includeAnalysis: boolean = false): Promise<ApiResponse<ApiEvent[] | ApiEventWithAnalysis[]>> {
    return getShopEvents(shopId, token, includeAnalysis);
  }

  async getEventDetails(shopId: string, eventId: string, token: string): Promise<ApiResponse<ApiEventWithAnalysis>> {
    return getEventDetails(shopId, eventId, token);
  }
}

export const eventsService = new EventsService();
export const eventsApi = { getAllEvents, getShopEvents, getEventDetails };
