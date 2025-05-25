import { useState } from 'react';
import './styles.css';
import ShopsBarChart from './components/ShopsBarChart';
import EventsLineChart from './components/EventsLineChart';

type Shop = {
  id: string;
  name: string;
  incidents: number;
};

type Event = {
  id: string;
  shopId: string;
  shopName: string;
  date: string;
  description: string;
};

const shops: Shop[] = [
  { id: 'shop1', name: 'Tel Aviv', incidents: 13 },
  { id: 'shop2', name: 'Haifa', incidents: 21 },
  { id: 'shop3', name: 'Eilat', incidents: 8 },
];

const events: Event[] = [
  { id: 'e1', shopId: 'shop2', shopName: 'Haifa', date: '2025-05-20T14:30:00', description: 'Shoplifting detected by Camera Y' },
  { id: 'e2', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-05-22T11:10:00', description: 'Suspicious activity at entrance' },
  { id: 'e3', shopId: 'shop2', shopName: 'Haifa', date: '2025-05-20T16:45:00', description: 'Shoplifting detected by Camera Z' },
  { id: 'e4', shopId: 'shop3', shopName: 'Eilat', date: '2025-05-20T09:20:00', description: 'Attempted theft, staff intervened' },
  { id: 'e5', shopId: 'shop2', shopName: 'Haifa', date: '2025-05-19T13:00:00', description: 'Shoplifting detected by Camera Y' },
  { id: 'e6', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-05-18T17:30:00', description: 'Suspicious bag left unattended' },
  { id: 'e7', shopId: 'shop3', shopName: 'Eilat', date: '2025-05-17T10:15:00', description: 'Shoplifting detected by Camera 2' },
];

export default function App() {
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
                  <div key={event.id} className={`event-card shop-${event.shopId}`}>
                    <div className="event-date">{new Date(event.date).toLocaleString()}</div>
                    <div className="event-shop">
                      <span className={`shop-badge shop-${event.shopId}`}>
                        {event.shopName}
                      </span>
                    </div>
                    <div className="event-desc">{event.description}</div>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}

        {activeTab === 'shop' && selectedShop && (
          <section className="selected-shop">
            <h2>Statistics for {shops.find(s => s.id === selectedShop)?.name}</h2>
            <p>Coming soon...</p>
          </section>
        )}
      </main>
    </div>
  );
}
