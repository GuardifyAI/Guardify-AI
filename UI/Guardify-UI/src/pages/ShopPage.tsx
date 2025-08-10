import type { Event, Shop } from '../types';
import EventsGrid from '../components/EventsGrid';
import AnalyticsCharts from '../components/Dashboard/AnalyticsCharts';
import './ShopPage.css';

type Props = {
  shop: Shop;
  events: Event[];
  tab: 'dashboard' | 'statistics' | 'events' | 'cameras';
};

export default function ShopPage({ shop, events, tab }: Props) {
  const filteredEvents = events.filter((e) => e.shopId === shop.id);

  return (
    <div className="page-layout">
      {(tab === 'dashboard' || tab === 'statistics') && (
        <section className="tiles">
          {/* Use the new AnalyticsCharts component with shop ID */}
          <AnalyticsCharts shopId={shop.id} />
        </section>
      )}

      {tab === 'events' && (
        <section className="events-table-section">
          <h2>Events in {shop.name}</h2>
          <EventsGrid
            events={filteredEvents}
            showCameraFilter={true}
            className="!p-0 !shadow-none !border-none !bg-transparent"
          />
        </section>
      )}

      {tab === 'cameras' && (
        <section>
          <h2 style={{ fontSize: '1.8rem', marginBottom: '1rem' }}>
          Live Camera Feed – Coming Soon
          </h2>
          <img
            src="/images/live-camera.png"
            alt="Live camera icon"
            style={{
              width: '120px',
              marginBottom: '1rem'
            }}
          />
        </section>
      )}
    </div>
  );
}
