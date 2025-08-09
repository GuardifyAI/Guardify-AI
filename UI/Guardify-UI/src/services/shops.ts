import { apiService, type ApiResponse } from './api';
import type { ApiShop, ShopEventsResponse, GlobalStatsResponse } from '../types';

// Service class
class ShopsService {
  /**
   * Get all shops for the authenticated user
   * @param token - The authentication token (should include "Bearer " prefix)
   * @returns Promise resolving to API response containing user's shops
   */
  async getUserShops(token: string): Promise<ApiResponse<ApiShop[]>> {
    return apiService.makeRequest<ApiShop[]>('/shops', {
      method: 'GET',
    }, token);
  }

  /**
   * Get all events for a specific shop
   * @param shopId - The shop ID to get events for
   * @param token - The authentication token
   */
  async getShopEvents(shopId: string, token: string): Promise<ApiResponse<ShopEventsResponse>> {
    return apiService.makeRequest<ShopEventsResponse>(`/shops/${shopId}/events`, {
      method: 'GET',
    }, token);
  }

  /**
   * Get global statistics across all shops for the authenticated user
   * @param token - The authentication token
   * @param includeCategory - Whether to include events_by_category (default: true)
   */
  async getGlobalStats(token: string, includeCategory: boolean = true): Promise<ApiResponse<GlobalStatsResponse>> {
    const queryParams = new URLSearchParams({
      include_category: includeCategory.toString()
    });
    
    return apiService.makeRequest<GlobalStatsResponse>(`/stats?${queryParams}`, {
      method: 'GET',
    }, token);
  }
}

// Export singleton instance
export const shopsService = new ShopsService();
