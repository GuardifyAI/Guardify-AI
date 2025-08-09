import { useState, useEffect } from 'react';
import { shopsService } from '../services/shops';
import { useAuth } from '../context/AuthContext';
import type { StatsResponse } from '../types';

export function useStats(shopId?: string, includeCategory: boolean = true) {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { token, isAuthenticated } = useAuth();

  const fetchStats = async () => {
    if (!token || !isAuthenticated) {
      setStats(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // If shopId provided, get shop stats; otherwise get global stats
      const response = shopId 
        ? await shopsService.getShopStats(shopId, token, includeCategory)
        : await shopsService.getGlobalStats(token, includeCategory);
      
      if (response.result && !response.errorMessage) {
        setStats(response.result);
      } else {
        setError(response.errorMessage || 'Failed to fetch stats');
        setStats(null);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
      setError('Failed to connect to server');
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [shopId, token, isAuthenticated, includeCategory]);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats
  };
}
