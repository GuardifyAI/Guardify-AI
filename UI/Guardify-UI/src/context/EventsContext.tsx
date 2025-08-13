import { createContext, useContext } from 'react';
import type { Event } from '../types/ui';

export const EventsContext = createContext<Event[]>([]);

export function useEvents() {
  return useContext(EventsContext);
}