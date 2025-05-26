import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import AppContent from './AppContent';
import EventPage from './pages/EventPage';
import { EventsContext } from './context/EventsContext';
import type { Event } from './types';

const events: Event[] = [
  { id: 'e1', shopId: 'shop2', shopName: 'Haifa', date: '2025-05-20T14:30:00', description: 'Shoplifting detected by Camera Y', cameraId: 'cam2', cameraName: 'Camera Y', videoUrl: "/videos/shop_lifter_0.mp4" },
  { id: 'e2', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-05-22T11:10:00', description: 'Suspicious activity at entrance', cameraId: 'cam1', cameraName: 'Entrance Camera', videoUrl: "/videos/shop_lifter_0.mp4" },
  { id: 'e3', shopId: 'shop2', shopName: 'Haifa', date: '2025-05-20T16:45:00', description: 'Shoplifting detected by Camera Z', cameraId: 'cam3', cameraName: 'Camera Z', videoUrl: "/videos/shop_lifter_0.mp4" },
  { id: 'e4', shopId: 'shop3', shopName: 'Eilat', date: '2025-05-20T09:20:00', description: 'Attempted theft, staff intervened', cameraId: 'cam5', cameraName: 'Back Entrance', videoUrl: "/videos/shop_lifter_0.mp4" },
  { id: 'e5', shopId: 'shop2', shopName: 'Haifa', date: '2025-05-19T13:00:00', description: 'Shoplifting detected by Camera Y', cameraId: 'cam2', cameraName: 'Camera Y', videoUrl: "/videos/shop_lifter_0.mp4" },
  { id: 'e6', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-05-18T17:30:00', description: 'Suspicious bag left unattended', cameraId: 'cam1', cameraName: 'Entrance Camera', videoUrl: "/videos/shop_lifter_0.mp4" },
  { id: 'e7', shopId: 'shop3', shopName: 'Eilat', date: '2025-05-17T10:15:00', description: 'Shoplifting detected by Camera 2', cameraId: 'cam4', cameraName: 'Camera 2', videoUrl: "/videos/shop_lifter_0.mp4" },
  { id: 'e8', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-05-21T15:20:00', description: 'Customer acting suspiciously near register', cameraId: 'cam6', cameraName: 'Register Cam', videoUrl: "/videos/shop_lifter_0.mp4"},
  { id: 'e9', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-05-20T12:40:00', description: 'Unusual crowd gathering at front', cameraId: 'cam1', cameraName: 'Entrance Camera', videoUrl: "/videos/shop_lifter_0.mp4" },
  { id: 'e10', shopId: 'shop2', shopName: 'Haifa', date: '2025-05-21T08:50:00', description: 'Suspicious motion after closing time', cameraId: 'cam3', cameraName: 'Camera Z', videoUrl: "/videos/shop_lifter_0.mp4" },
  { id: 'e11', shopId: 'shop3', shopName: 'Eilat', date: '2025-05-22T13:05:00', description: 'Back door opened unexpectedly', cameraId: 'cam5', cameraName: 'Back Entrance', videoUrl: "/videos/shop_lifter_0.mp4" },
  { id: 'e12', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-05-22T19:30:00', description: 'Shoplifting attempt stopped by staff', cameraId: 'cam1', cameraName: 'Entrance Camera', videoUrl: "/videos/shop_lifter_0.mp4" },
  { id: 'e13', shopId: 'shop2', shopName: 'Haifa', date: '2025-05-23T10:00:00', description: 'Customer running out with unpaid item', cameraId: 'cam2', cameraName: 'Camera Y', videoUrl: "/videos/shop_lifter_0.mp4" },
];

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
