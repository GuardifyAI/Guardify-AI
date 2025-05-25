import { useState } from 'react';
import './styles.css';
import ShopsBarChart from './components/ShopsBarChart';
import EventsLineChart from './components/EventsLineChart';
import ShopPage from './pages/ShopPage';
import type { Event, Shop } from './types';
import EventCard from './components/EventCard';

const shops: Shop[] = [
  { id: 'shop1', name: 'Tel Aviv', incidents: 13 },
  { id: 'shop2', name: 'Haifa', incidents: 21 },
  { id: 'shop3', name: 'Eilat', incidents: 8 },
];

const events: Event[] = [
  { id: 'e1', shopId: 'shop2', shopName: 'Haifa', date: '2025-05-20T14:30:00', description: 'Shoplifting detected by Camera Y', cameraId: 'cam2', cameraName: 'Camera Y' },
  { id: 'e2', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-05-22T11:10:00', description: 'Suspicious activity at entrance', cameraId: 'cam1', cameraName: 'Entrance Camera' },
  { id: 'e3', shopId: 'shop2', shopName: 'Haifa', date: '2025-05-20T16:45:00', description: 'Shoplifting detected by Camera Z', cameraId: 'cam3', cameraName: 'Camera Z' },
  { id: 'e4', shopId: 'shop3', shopName: 'Eilat', date: '2025-05-20T09:20:00', description: 'Attempted theft, staff intervened', cameraId: 'cam5', cameraName: 'Back Entrance' },
  { id: 'e5', shopId: 'shop2', shopName: 'Haifa', date: '2025-05-19T13:00:00', description: 'Shoplifting detected by Camera Y', cameraId: 'cam2', cameraName: 'Camera Y' },
  { id: 'e6', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-05-18T17:30:00', description: 'Suspicious bag left unattended', cameraId: 'cam1', cameraName: 'Entrance Camera' },
  { id: 'e7', shopId: 'shop3', shopName: 'Eilat', date: '2025-05-17T10:15:00', description: 'Shoplifting detected by Camera 2', cameraId: 'cam4', cameraName: 'Camera 2' },
  { id: 'e8', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-05-21T15:20:00', description: 'Customer acting suspiciously near register', cameraId: 'cam6', cameraName: 'Register Cam' },
  { id: 'e9', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-05-20T12:40:00', description: 'Unusual crowd gathering at front', cameraId: 'cam1', cameraName: 'Entrance Camera' },
  { id: 'e10', shopId: 'shop2', shopName: 'Haifa', date: '2025-05-21T08:50:00', description: 'Suspicious motion after closing time', cameraId: 'cam3', cameraName: 'Camera Z' },
  { id: 'e11', shopId: 'shop3', shopName: 'Eilat', date: '2025-05-22T13:05:00', description: 'Back door opened unexpectedly', cameraId: 'cam5', cameraName: 'Back Entrance' },
  { id: 'e12', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-05-22T19:30:00', description: 'Shoplifting attempt stopped by staff', cameraId: 'cam1', cameraName: 'Entrance Camera' },
  { id: 'e13', shopId: 'shop2', shopName: 'Haifa', date: '2025-05-23T10:00:00', description: 'Customer running out with unpaid item', cameraId: 'cam2', cameraName: 'Camera Y' }
];

export default function AppContent() {
  const [selectedShop, setSelectedShop] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('dashboard');

  const sortedEvents = [...events].sort((a, b) => b.date.localeCompare(a.date));

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <img src="/images/logo.png" alt="Guardify Logo" className="logo" />
        <div className="user-info">
          <strong>John Doe</strong>
          <p>Guardify Manager</p>
        </div>
        <nav>
          <ul className="sidebar-tabs">
            <li>
              <button
                className={`sidebar-tab${activeTab === 'dashboard' ? ' active' : ''}`}
                onClick={() => {
                  setActiveTab('dashboard');
                  setSelectedShop(null);
                }}
              >
                All Shops Statistics
              </button>
            </li>
            {shops.map(shop => (
              <li key={shop.id}>
                <button
                  className={`sidebar-tab${selectedShop === shop.id ? ' active' : ''}`}
                  onClick={() => {
                    setActiveTab('shop');
                    setSelectedShop(shop.id);
                  }}
                >
                  {shop.name}
                </button>
              </li>
            ))}
            <li>
              <button
                className={`sidebar-tab${activeTab === 'settings' ? ' active' : ''}`}
                onClick={() => {
                  setActiveTab('settings');
                  setSelectedShop(null);
                }}
              >
                Settings
              </button>
            </li>
            <li>
              <button
                className={`sidebar-tab${activeTab === 'logout' ? ' active' : ''}`}
                onClick={() => {
                  setActiveTab('logout');
                  setSelectedShop(null);
                  // Add logout logic here if needed
                }}
              >
                Logout
              </button>
            </li>
          </ul>
        </nav>
      </aside>

      <main className="main">
        <header className="header">
          <h1>Guardify AI Dashboard</h1>
          <p>{selectedShop ? `Shop: ${shops.find(s => s.id === selectedShop)?.name}` : 'All Shops Statistics'}</p>
        </header>

        {activeTab === 'dashboard' && (
          <>
            <section className="tiles">
              <div className="tile">
                <h2>Shops Events Overview</h2>
                <ShopsBarChart shops={shops} />
              </div>
              <div className="tile">
                <h2>Events Trend Over Time</h2>
                <EventsLineChart events={events} />
              </div>
            </section>

            <section className="events-table-section">
              <h2>All Events (Sorted by Date)</h2>
              <div className="events-grid">
                {sortedEvents.map(event => (
                  <EventCard key={event.id} event={event} />
                ))}
              </div>
            </section>
          </>
        )}

        {activeTab === 'shop' && selectedShop && (
          <section className="selected-shop">
            <ShopPage
              shop={shops.find(s => s.id === selectedShop)!}
              events={events}
            />
          </section>
        )}
      </main>
    </div>
  );
}
