import { createContext, useContext } from 'react';
import type { Event } from '../types';

export const EventsContext = createContext<Event[]>([]);

export function useEvents() {
  return useContext(EventsContext);
}

// import { createContext, useContext, useEffect, useState } from 'react';
// import type { Event } from '../types';
// import { fetchAllEvents } from '../api/api';

// type EventsContextType = {
//   events: Event[];
//   isLoading: boolean;
//   error: string | null;
// };

// const EventsContext = createContext<EventsContextType>({
//   events: [],
//   isLoading: true,
//   error: null,
// });

// export function EventsProvider({ children }: { children: React.ReactNode }) {
//   const [events, setEvents] = useState<Event[]>([]);
//   const [isLoading, setIsLoading] = useState(true);
//   const [error, setError] = useState<string | null>(null);

//   useEffect(() => {
//     fetchAllEvents()
//       .then(setEvents)
//       .catch((err) => setError(err.message))
//       .finally(() => setIsLoading(false));
//   }, []);

//   return (
//     <EventsContext.Provider value={{ events, isLoading, error }}>
//       {children}
//     </EventsContext.Provider>
//   );
// }

// export function useEventsContext() {
//   return useContext(EventsContext);
// }
