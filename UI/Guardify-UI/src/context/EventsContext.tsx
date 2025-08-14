import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { Event } from '../types/ui';
import { eventsService } from '../services/events';
import { mapApiEvents } from '../utils/mappers';
import { useAuth } from './AuthContext';

interface EventsContextType {
  events: Event[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
  setSelectedShop: (shopId: string | null) => void;
  selectedShop: string | null;
}

const EventsContext = createContext<EventsContextType | undefined>(undefined);

export function useEvents() {
  const context = useContext(EventsContext);
  if (context === undefined) {
    throw new Error('useEvents must be used within an EventsProvider');
  }
  return context.events;
}

export function useEventsContext() {
  const context = useContext(EventsContext);
  if (context === undefined) {
    throw new Error('useEventsContext must be used within an EventsProvider');
  }
  return context;
}

interface EventsProviderProps {
  children: ReactNode;
}

export function EventsProvider({ children }: EventsProviderProps) {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedShop, setSelectedShop] = useState<string | null>(null);
  const { isAuthenticated, token } = useAuth();

  const fetchEvents = async (shopId?: string | null) => {
    if (!isAuthenticated || !token) {
      console.log('EventsContext: Not authenticated, clearing events');
      setEvents([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      console.log('EventsContext: Fetching events for shopId:', shopId);
      
      let response;
      if (shopId) {
        // Fetch shop-specific events
        console.log('EventsContext: Shop ID type:', typeof shopId, 'value:', JSON.stringify(shopId));
        response = await eventsService.getShopEvents(shopId, token, true); // include_analysis=1
      } else {
        // Fetch all events
        console.log('EventsContext: Calling getGlobalEvents');
        response = await eventsService.getGlobalEvents(token, true); // include_analysis=1
      }
      
      console.log('EventsContext: API response:', response);
      
      if (response.result && !response.errorMessage) {
        const mappedEvents = mapApiEvents(response.result);
        setEvents(mappedEvents);
      } else {
        console.error('EventsContext: API error:', response.errorMessage);
        setError(response.errorMessage || 'Failed to fetch events');
        setEvents([]);
      }
    } catch (err) {
      setError('Failed to load events');
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSetSelectedShop = (shopId: string | null) => {
    console.log('EventsContext: setSelectedShop called with:', shopId);
    setSelectedShop(shopId);
    fetchEvents(shopId);
  };

  useEffect(() => {
    fetchEvents(selectedShop);
  }, [isAuthenticated, token]);

  const value: EventsContextType = {
    events,
    loading,
    error,
    refetch: () => fetchEvents(selectedShop),
    setSelectedShop: handleSetSelectedShop,
    selectedShop,
  };

  return (
    <EventsContext.Provider value={value}>
      {children}
    </EventsContext.Provider>
  );
}