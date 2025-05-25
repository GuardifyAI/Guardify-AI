// src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import AppContent from './AppContent';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/dashboard" element={<AppContent />} />
      </Routes>
    </BrowserRouter>
  );
}
// This is the main entry point for the Guardify UI application.
// It sets up the routing for the application, allowing users to navigate between the login page and the dashboard content.
// The `LoginPage` component is displayed at the root path ("/"), and the `AppContent` component is displayed at the "/dashboard" path.
