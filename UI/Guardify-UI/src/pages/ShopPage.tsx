import { useState } from 'react';
import type { Event, Shop } from '../types';
import EventCard from '../components/EventCard';
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

  const [selectedCamera, setSelectedCamera] = useState<string | 'all'>('all');
  const cameraOptions = Array.from(new Set(filteredEvents.map((e) => e.cameraName)));
  const displayedEvents =
    selectedCamera === 'all'
      ? filteredEvents
      : filteredEvents.filter((e) => e.cameraName === selectedCamera);

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
          <EventsByCategorySimple events={filteredEvents} />
        </section>
      )}

      {tab === 'events' && (
        <section className="events-table-section">
          <h2>Events in {shop.name}</h2>

          <div className="filter-section">
            <label htmlFor="cameraFilter">Filter by Camera: </label>
            <select
              id="cameraFilter"
              value={selectedCamera}
              onChange={(e) => setSelectedCamera(e.target.value)}
            >
              <option value="all">All Cameras</option>
              {cameraOptions.map((cam) => (
                <option key={cam} value={cam}>
                  {cam}
                </option>
              ))}
            </select>
          </div>

          <div className="events-grid">
            {displayedEvents.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
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
