import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import AppContent from './AppContent';
import EventPage from './pages/EventPage';
import { EventsContext } from './context/EventsContext';
import { events } from './events';

export default function App() {
  return (
    <EventsContext.Provider value={events}>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/dashboard" element={<AppContent />} />
        <Route path="/event/:id" element={<EventPage />} />
      </Routes>
    </BrowserRouter>
    </EventsContext.Provider>
  );
}
// This is the main entry point for the Guardify UI application.
// It sets up the routing for the application, allowing users to navigate between the login page and the dashboard content.
// The `LoginPage` component is displayed at the root path ("/"), and the `AppContent` component is displayed at the "/dashboard" path.
