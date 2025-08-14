import { apiService, type ApiResponse } from './api';
import type { ApiShop, StatsResponse } from '../types/api';

// Service class
class ShopsService {
  /**
   * Get all shops for the authenticated user
   */
  async getUserShops(token: string): Promise<ApiResponse<ApiShop[]>> {
    return apiService.makeRequest<ApiShop[]>('/shops', {
      method: 'GET',
    }, token);
  }

  /**
   * Get statistics for a specific shop
   */
  async getShopStats(shopId: string, token: string, includeCategory: boolean = true): Promise<ApiResponse<StatsResponse>> {
    const queryParams = new URLSearchParams({
      include_category: includeCategory.toString()
    });
    
    return apiService.makeRequest<StatsResponse>(`/shops/${shopId}/stats?${queryParams}`, {
      method: 'GET',
    }, token);
  }

  /**
   * Get global statistics across all shops
   */
  async getGlobalStats(token: string, includeCategory: boolean = true): Promise<ApiResponse<StatsResponse>> {
    const queryParams = new URLSearchParams({
      include_category: includeCategory.toString()
    });
    
    return apiService.makeRequest<StatsResponse>(`/stats?${queryParams}`, {
      method: 'GET',
    }, token);
  }


}

export const shopsService = new ShopsService();
