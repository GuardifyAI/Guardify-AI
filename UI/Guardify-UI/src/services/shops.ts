import { apiService, type ApiResponse } from './api';
import type { ApiShop, StatsResponse, ShopCamerasResponse } from '../types/api';

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

  /**
   * Get all cameras for a specific shop
   */
  async getShopCameras(shopId: string, token: string): Promise<ApiResponse<ShopCamerasResponse>> {
    return apiService.makeRequest<ShopCamerasResponse>(`/shops/${shopId}/cameras`, {
      method: 'GET',
    }, token);
  }

  /**
   * Start recording for a camera in a shop
   */
  async startRecording(shopId: string, cameraName: string, duration: number = 30, token: string): Promise<ApiResponse<string>> {
    return apiService.makeRequest<string>(`/shops/${shopId}/recording/start`, {
      method: 'POST',
      body: JSON.stringify({
        camera_name: cameraName,
        duration: duration
      })
    }, token);
  }

  /**
   * Stop recording for a camera in a shop
   */
  async stopRecording(shopId: string, cameraName: string, token: string): Promise<ApiResponse<string>> {
    return apiService.makeRequest<string>(`/shops/${shopId}/recording/stop`, {
      method: 'POST',
      body: JSON.stringify({
        camera_name: cameraName
      })
    }, token);
  }

  /**
   * Get active recording status for a shop
   */
  async getRecordingStatus(shopId: string, token: string): Promise<ApiResponse<Array<{camera_name: string, started_at: number, duration: number}>>> {
    return apiService.makeRequest<Array<{camera_name: string, started_at: number, duration: number}>>(`/shops/${shopId}/recording/status`, {
      method: 'GET',
    }, token);
  }
}

export const shopsService = new ShopsService();
