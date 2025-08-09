import { useState, useEffect } from 'react';
import { shopsService } from '../services/shops';
import { useAuth } from '../context/AuthContext';
import type { GlobalStatsResponse } from '../types';

export function useGlobalStats(includeCategory: boolean = true) {
  const [stats, setStats] = useState<GlobalStatsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { token, isAuthenticated } = useAuth();

  const fetchGlobalStats = async () => {
    if (!token || !isAuthenticated) {
      setStats(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await shopsService.getGlobalStats(token, includeCategory);
      
      if (response.result && !response.errorMessage) {
        setStats(response.result);
      } else {
        setError(response.errorMessage || 'Failed to fetch global stats');
        setStats(null);
      }
    } catch (error) {
      console.error('Error fetching global stats:', error);
      setError('Failed to connect to server');
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && token) {
      fetchGlobalStats();
    } else {
      setStats(null);
    }
  }, [isAuthenticated, token, includeCategory]);

  return {
    stats,
    loading,
    error,
    refetch: fetchGlobalStats
  };
}
