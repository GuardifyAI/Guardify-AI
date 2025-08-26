import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import AppContent from './AppContent';
import EventPage from './pages/EventPage';
import { EventsProvider } from './context/EventsContext';
import { AuthProvider } from './context/AuthContext';
import { SettingsProvider } from './context/SettingsContext';
import ProtectedRoute from './components/ProtectedRoute';

export default function App() {
  return (
    <AuthProvider>
      <SettingsProvider>
        <EventsProvider>
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
      </EventsProvider>
    </SettingsProvider>
    </AuthProvider>
  );
}
