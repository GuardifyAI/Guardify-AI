import type { Event } from '../types';

export default function EventCard({ event }: { event: Event }) {
  return (
    <div className={`event-card shop-${event.shopId}`}>
      <div className="event-date">{new Date(event.date).toLocaleString()}</div>
      <div className="event-shop">
        <span className={`shop-badge shop-${event.shopId}`}>
          {event.shopName} – {event.cameraName}
        </span>
      </div>
      <div className="event-desc">{event.description}</div>
    </div>
  );
}
