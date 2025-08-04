import { createContext, useContext } from 'react';
import type { Event } from '../types';

export const EventsContext = createContext<Event[]>([]);

export function useEvents() {
  return useContext(EventsContext);
}