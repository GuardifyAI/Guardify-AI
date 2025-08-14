import type { ApiLoginResponse } from '../types/api';
import { apiService, type ApiResponse } from './api';

class AuthService {
  /**
   * Login user with email and password
   * @param email - The user's email address
   * @param password - The user's password
   * @returns Promise resolving to API response containing login data and token
   */
  async login(email: string, password: string): Promise<ApiResponse<ApiLoginResponse>> {
    return apiService.makeRequest<ApiLoginResponse>('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  /**
   * Logout user
   * @param userId - The unique identifier of the user to logout
   * @param token - The authentication token for the user session
   * @returns Promise resolving to API response containing the logged-out user ID
   */
  async logout(userId: string, token: string): Promise<ApiResponse<{ userId: string }>> {
    return apiService.makeRequest<{ userId: string }>('/logout', {
      method: 'GET',
      body: JSON.stringify({ userId }),
    }, token);
  }
}

// Export singleton instance
export const authService = new AuthService();
export default authService;
