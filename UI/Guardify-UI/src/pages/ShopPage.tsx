import EventsLineChart from '../components/EventsLineChart';
import CameraStats from '../components/CameraStats';
import type { Event, Shop } from '../types';
import EventCard from '../components/EventCard';

type Props = {
  shop: Shop;
  events: Event[];
};

export default function ShopPage({ shop, events }: Props) {
  const filteredEvents = events.filter(e => e.shopId === shop.id);
  const sortedEvents = [...filteredEvents].sort((a, b) => b.date.localeCompare(a.date));

  return (
    <div>
      <h2>Statistics for {shop.name}</h2>

      <section className="tiles">
        <div className="tile">
          <h2>Events Trend Over Time</h2>
          <EventsLineChart events={filteredEvents} />
        </div>
          <CameraStats events={filteredEvents} />
      </section>

      <section className="events-table-section">
        <h2>Events in {shop.name}</h2>
        <div className="events-grid">
            {sortedEvents.map(event => (
              <EventCard event={event} />
            ))}
        </div>
      </section>
    </div>
  );
}
