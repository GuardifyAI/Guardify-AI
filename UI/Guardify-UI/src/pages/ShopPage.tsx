import EventsOverTime from '../components/Stats/EventsOverTime';
import EventsByHour from '../components/Stats/EventsByHour';
import EventCountBarChart from '../components/Stats/EventCountBarChart';
import EventsByCategory from '../components/Stats/EventsByCategory';
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
          <EventsOverTime events={filteredEvents} />
          <EventsByHour events={filteredEvents} />
          <EventCountBarChart
            events={filteredEvents}
            groupBy="camera"
            title={`Events by Camera in ${shop.name}`}
          />
          <EventsByCategory events={events} />
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
