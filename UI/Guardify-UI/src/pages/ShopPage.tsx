import type { Event, Shop } from '../types';
import EventsGrid from '../components/EventsGrid';
import EventsOverTime from '../components/Stats/EventsOverTime';
import EventsByHour from '../components/Stats/EventsByHour';
import EventCountBarChart from '../components/Stats/EventCountBarChart';
import EventsByCategorySimple from '../components/Stats/EventsByCategory';
import './ShopPage.css';

type Props = {
  shop: Shop;
  events: Event[];
  tab: 'statistics' | 'events' | 'cameras';
};

export default function ShopPage({ shop, events, tab }: Props) {
  const filteredEvents = events.filter((e) => e.shopId === shop.id);

  return (
    <div className="page-layout">
      {tab === 'statistics' && (
        <section className="tiles">
          <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Events Over Time</h3>
            <EventsOverTime events={filteredEvents} />
          </div>
          <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Events by Hour</h3>
            <EventsByHour events={filteredEvents} />
          </div>
          <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Events by Camera</h3>
            <EventCountBarChart
              events={filteredEvents}
              groupBy="camera"
            />
          </div>
          <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Event Categories</h3>
            <EventsByCategorySimple events={filteredEvents} />
          </div>
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
