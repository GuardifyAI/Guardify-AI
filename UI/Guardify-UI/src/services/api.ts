import type { User } from '../types';

// API Base URL - Update this if your backend runs on a different port
const API_BASE_URL = 'http://localhost:8574';

// Standard API response format based on backend controller
export interface ApiResponse<T> {
  result: T;
  errorMessage: string | null;
}

// Login request/response types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse extends Omit<User, 'email'> {
  token: string;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Make an authenticated API request
   */
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    token?: string
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Add existing headers if they exist
    if (options.headers) {
      Object.assign(headers, options.headers);
    }

    if (token) {
      headers.Authorization = token;
    }

    const config: RequestInit = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      // Always return the data - let the caller handle success/error based on errorMessage
      return data;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  /**
   * Login user with email and password
   */
  async login(email: string, password: string): Promise<ApiResponse<LoginResponse>> {
    return this.makeRequest<LoginResponse>('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  /**
   * Logout user
   */
  async logout(userId: string, token: string): Promise<ApiResponse<{ userId: string }>> {
    return this.makeRequest<{ userId: string }>('/logout', {
      method: 'GET',
      body: JSON.stringify({ userId }),
    }, token);
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<ApiResponse<string>> {
    return this.makeRequest<string>('/app/health', {
      method: 'GET',
    });
  }

  /**
   * Generic authenticated GET request
   */
  async authenticatedGet<T>(endpoint: string, token: string): Promise<ApiResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      method: 'GET',
    }, token);
  }

  /**
   * Generic authenticated POST request
   */
  async authenticatedPost<T>(
    endpoint: string, 
    data: any, 
    token: string
  ): Promise<ApiResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    }, token);
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;