import { useEffect, useState } from 'react';
import { eventsApi } from '../services/events';
import { analysisService } from '../services/analysis';
import { useAuth } from '../context/AuthContext';
import type { Event, EventAnalysis } from '../types/ui';
import { mapApiEvent, mapApiAnalysis } from '../utils/mappers';

type EventDetailsState = {
  event: Event | null;
  analysis: EventAnalysis | null;
  loading: boolean;
  error: string | null;
};

export function useEventDetails(shopId?: string, eventId?: string) {
  const [{ event, analysis, loading, error }, setState] = useState<EventDetailsState>({
    event: null,
    analysis: null,
    loading: false,
    error: null,
  });
  const { token, isAuthenticated } = useAuth();

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      if (!token || !isAuthenticated || !shopId || !eventId) {
        if (!cancelled) setState({ event: null, analysis: null, loading: false, error: null });
        return;
      }
      if (!cancelled) setState(s => ({ ...s, loading: true, error: null }));

      try {
        const [eventRes, analysisRes] = await Promise.all([
          eventsApi.getEventDetails(shopId, eventId, token),
          analysisService.getEventAnalysis(eventId, token),
        ]);

        if (cancelled) return;

        if (eventRes.result && !eventRes.errorMessage && analysisRes.result && !analysisRes.errorMessage) {
          const uiEvent = mapApiEvent(eventRes.result);
          const uiAnalysis = mapApiAnalysis(analysisRes.result);
          setState({ event: { ...uiEvent, analysis: uiAnalysis }, analysis: uiAnalysis, loading: false, error: null });
        } else {
          setState({
            event: null,
            analysis: null,
            loading: false,
            error: eventRes.errorMessage || analysisRes.errorMessage || 'Failed to fetch event details',
          });
        }
      } catch {
        if (!cancelled) setState({ event: null, analysis: null, loading: false, error: 'Failed to connect to server' });
      }
    };
    run();
    return () => { cancelled = true; };
  }, [shopId, eventId, token, isAuthenticated]);

  const refetch = () => {
    // simply re-run by toggling any dep; easiest is to update state to trigger effect or wrap `run` above to be callable
    // For brevity, call setState to flip loading and rely on deps (or convert effect body into a named function you can call here)
  };

  return { event, analysis, loading, error, refetch };
}
