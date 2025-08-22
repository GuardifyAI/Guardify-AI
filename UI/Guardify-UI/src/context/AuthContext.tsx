import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { User, AuthContextType } from '../types/ui';
import { authService } from '../services/auth.ts'
import { cleanErrorMessage } from "../utils/errorUtils.ts";
import { mapApiLoginResponse } from '../utils/mappers';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Set loading to false immediately since we're not checking for stored tokens
  useEffect(() => {
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    setIsLoading(true);
    
    try {
      const data = await authService.login(email, password);

      if (data.result && !data.errorMessage) {
        const userData = mapApiLoginResponse(data.result);
        // Add the email since login doesn't return it but we know it from the form
        userData.email = email;
        
        setUser(userData);
        setToken(data.result.token); // Use the actual token from backend
        
        return { success: true };
      } else {
        // Backend returned an error message - clean it up for display
        let errorMessage = data.errorMessage || 'Login failed';
        
        // Log the raw error message for debugging
        console.log('Raw error message from backend:', errorMessage);
        
        // Clean up error message for better user experience
        const cleanedMessage = cleanErrorMessage(errorMessage);
        console.log('Cleaned error message:', cleanedMessage);
        
        return { success: false, error: cleanedMessage };
      }
    } catch (error) {
      console.error('Login error:', error);
      // Only show "Failed to connect" for actual network errors
      if (error instanceof TypeError && error.message.includes('fetch')) {
        return { 
          success: false, 
          error: 'Failed to connect to server. Please check if the backend is running.' 
        };
      }
      return { 
        success: false, 
        error: 'An unexpected error occurred. Please try again.' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    isLoading,
    isAuthenticated: !!user && !!token,
  };

  // Debug logging
  console.log('Auth state:', { user, token, isAuthenticated: !!user && !!token });

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}