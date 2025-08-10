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
