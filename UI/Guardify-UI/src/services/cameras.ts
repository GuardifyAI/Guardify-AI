import { apiService, type ApiResponse } from './api';
import type { ShopCamerasResponse } from '../types/api';

// Service class for camera-related operations
class CameraService {
  /**
   * Get all cameras for a specific shop
   */
  async getShopCameras(shopId: string, token: string): Promise<ApiResponse<ShopCamerasResponse>> {
    return apiService.makeRequest<ShopCamerasResponse>(`/shops/${shopId}/cameras`, {
      method: 'GET',
    }, token);
  }

  /**
   * Create a new camera for a shop
   */
  async createCamera(shopId: string, cameraName: string, token: string): Promise<ApiResponse<ShopCamerasResponse[0]>> {
    return apiService.makeRequest<ShopCamerasResponse[0]>(`/shops/${shopId}/cameras`, {
      method: 'POST',
      body: JSON.stringify({
        camera_name: cameraName
      })
    }, token);
  }

  /**
   * Delete a camera from a shop
   */
  async deleteCamera(shopId: string, cameraId: string, token: string): Promise<ApiResponse<string>> {
    return apiService.makeRequest<string>(`/shops/${shopId}/cameras/${cameraId}`, {
      method: 'DELETE',
    }, token);
  }

  /**
   * Start recording for a camera in a shop
   */
  async startRecording(
    shopId: string, 
    cameraName: string, 
    duration: number = 30, 
    detectionThreshold: number = 0.8,
    analysisIterations: number = 1,
    token: string
  ): Promise<ApiResponse<string>> {
    return apiService.makeRequest<string>(`/shops/${shopId}/recording/start`, {
      method: 'POST',
      body: JSON.stringify({
        camera_name: cameraName,
        duration: duration,
        detection_threshold: detectionThreshold,
        analysis_iterations: analysisIterations
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

export const cameraService = new CameraService();
