import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import AppContent from './AppContent';
import EventPage from './pages/EventPage';
import { EventsContext } from './context/EventsContext';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import { events } from './events';

export default function App() {
  return (
    <AuthProvider>
      <EventsContext.Provider value={events}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <AppContent />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/event/:id" 
              element={
                <ProtectedRoute>
                  <EventPage />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </BrowserRouter>
      </EventsContext.Provider>
    </AuthProvider>
  );
}
// This is the main entry point for the Guardify UI application.
// It sets up the routing for the application, allowing users to navigate between the login page and the dashboard content.
// The `LoginPage` component is displayed at the root path ("/"), and the `AppContent` component is displayed at the "/dashboard" path.
