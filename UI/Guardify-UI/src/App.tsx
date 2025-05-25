import { useState } from 'react';
import Chart from 'chart.js/auto';
import { useEffect, useRef } from 'react';
import './styles.css';

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
  const [activeTab, setActiveTab] = useState<string>('dashboard'); // NEW: track active tab
  const shopCanvasRef = useRef<HTMLCanvasElement>(null);
  const eventsLineRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);
  const lineChartInstance = useRef<Chart | null>(null);

  // Sort events by date descending
  const sortedEvents = [...events].sort((a, b) => b.date.localeCompare(a.date));

  // Prepare data for line chart: count events per day
  const eventDates = events
    .map(e => e.date.slice(0, 10))
    .sort();
  const uniqueDates = Array.from(new Set(eventDates));
  const eventsPerDay = uniqueDates.map(date =>
    events.filter(e => e.date.startsWith(date)).length
  );

  useEffect(() => {
    // Bar chart for shop events
    if (shopCanvasRef.current) {
      if (chartInstance.current) chartInstance.current.destroy();

      chartInstance.current = new Chart(shopCanvasRef.current, {
        type: 'bar',
        data: {
          labels: shops.map(s => s.name),
          datasets: [{
            label: 'Total Events',
            data: shops.map(s => s.incidents),
            backgroundColor: '#30B3E1'
          }]
        },
        options: {
          plugins: { legend: { display: false } },
          responsive: true,
        }
      });
    }

    // Line chart for events over time
    if (eventsLineRef.current) {
      if (lineChartInstance.current) lineChartInstance.current.destroy();

      lineChartInstance.current = new Chart(eventsLineRef.current, {
        type: 'line',
        data: {
          labels: uniqueDates,
          datasets: [{
            label: 'Events per Day',
            data: eventsPerDay,
            borderColor: '#30B3E1',
            backgroundColor: 'rgba(48,179,225,0.15)',
            fill: true,
            tension: 0.3,
            pointRadius: 4,
            pointBackgroundColor: '#30B3E1'
          }]
        },
        options: {
          plugins: { legend: { display: false } },
          responsive: true,
          scales: {
            x: {
              title: { display: true, text: 'Date' }
            },
            y: {
              title: { display: true, text: 'Events' },
              beginAtZero: true,
            }
          }
        }
      });
    }
  }, [shops, events]);

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
          <p>All Shops Statistics</p>
        </header>

        {/* Statistics Graphs */}
        <section className="tiles">
          <div className="tile">
            <h2>Shops Events Overview</h2>
            <canvas ref={shopCanvasRef} width="300" height="200"></canvas>
          </div>
          <div className="tile">
            <h2>Events Trend Over Time</h2>
            <canvas ref={eventsLineRef} width="300" height="200"></canvas>
          </div>
        </section>

        {/* All Events Table */}
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

        {selectedShop && (
          <section className="selected-shop">
            <h2>Statistics for {shops.find(s => s.id === selectedShop)?.name}</h2>
            <p>Coming soon...</p>
          </section>
        )}
      </main>
    </div>
  );
}
