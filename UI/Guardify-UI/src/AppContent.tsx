import { useState } from 'react';
import './styles.css';
import { EventsContext } from './context/EventsContext';
import ShopsBarChart from './components/ShopsBarChart';
import EventsLineChart from './components/EventsLineChart';
import ShopPage from './pages/ShopPage';

import type { Event, Shop } from './types';
import EventCard from './components/EventCard';
import { useEvents } from './context/EventsContext';


const shops: Shop[] = [
  { id: 'shop1', name: 'Tel Aviv', incidents: 13 },
  { id: 'shop2', name: 'Haifa', incidents: 21 },
  { id: 'shop3', name: 'Eilat', incidents: 8 },
];


export default function AppContent() {
  const [selectedShop, setSelectedShop] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const events = useEvents();
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
