import { useState, useEffect } from 'react';
import { shopsService } from '../services/shops';
import { useAuth } from '../context/AuthContext';
import type { Shop } from '../types/ui';
import { mapApiShops } from '../utils/mappers';

export function useShops() {
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { token, isAuthenticated } = useAuth();

  const fetchShops = async () => {
    if (!token || !isAuthenticated) {
      setShops([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await shopsService.getUserShops(token);
      
      if (response.result && !response.errorMessage) {
        setShops(mapApiShops(response.result));
      } else {
        setError(response.errorMessage || 'Failed to fetch shops');
        setShops([]);
      }
    } catch (error) {
      console.error('Error fetching shops:', error);
      setError('Failed to connect to server');
      setShops([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && token) {
      fetchShops();
    } else {
      setShops([]);
    }
  }, [isAuthenticated, token]);

  return {
    shops,
    loading,
    error,
    refetch: fetchShops
  };
}
