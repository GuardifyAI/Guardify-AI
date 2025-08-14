// src/hooks/useEvents.ts
import { useEffect, useState } from 'react';
import { eventsApi } from '../services/events';
import { useAuth } from '../context/AuthContext';
import type { Event } from '../types/ui';
import { mapApiEvent } from '../utils/mappers';

export function useEvents(shopId?: string) {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { token, isAuthenticated } = useAuth();

  const fetchEvents = async () => {
    if (!token || !isAuthenticated) {
      setEvents([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = shopId
        ? await eventsApi.getShopEvents(shopId, token)
        : await eventsApi.getAllEvents(token);

      if (res.result && !res.errorMessage) {
        setEvents(res.result.map(mapApiEvent));
      } else {
        setError(res.errorMessage || 'Failed to fetch events');
        setEvents([]);
      }
    } catch {
      setError('Failed to connect to server');
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchEvents(); }, [shopId, token, isAuthenticated]);

  return { events, loading, error, refetch: fetchEvents };
}
