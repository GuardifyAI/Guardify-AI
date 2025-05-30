import EventsLineChart from '../components/EventsLineChart';
import CameraStats from '../components/CameraStats';
import type { Event, Shop } from '../types';
import EventCard from '../components/EventCard';

type Props = {
  shop: Shop;
  events: Event[];
  tab: 'statistics' | 'events' | 'cameras';
};

export default function ShopPage({ shop, events, tab }: Props) {
  const filteredEvents = events.filter(e => e.shopId === shop.id);
  const sortedEvents = [...filteredEvents].sort((a, b) => b.date.localeCompare(a.date));

  return (
    <div className="page-layout">
      {tab === 'statistics' && (
        <section className="tiles">
          <div className="tile">
            <h2>Events Trend Over Time</h2>
            <EventsLineChart events={filteredEvents} />
          </div>
          <CameraStats events={filteredEvents} />
        </section>
      )}

      {tab === 'events' && (
        <section className="events-table-section">
          <h2>Events in {shop.name}</h2>
          <div className="events-grid">
            {sortedEvents.map(event => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        </section>
      )}

      {tab === 'cameras' && (
        <section>
          <h2>Cameras in {shop.name}</h2>
          <p>Camera list and filtering to be implemented</p>
        </section>
      )}
    </div>
  );
}
