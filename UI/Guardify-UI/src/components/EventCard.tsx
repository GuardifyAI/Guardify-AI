import { Link } from 'react-router-dom';
import type { Event } from '../types';

export default function EventCard({ event }: { event: Event }) {
  return (
    <Link to={`/event/${event.id}`} className="event-card-link">
      <div className={`event-card shop-${event.shopId}`}>
        <div className="event-date">{new Date(event.date).toLocaleString()}</div>
        <div className="event-shop">
          <span className={`shop-badge shop-${event.shopId}`}>
            {event.shopName} – {event.  cameraName}
          </span>
        </div>
        <div className="event-desc">{event.description}</div>
      </div>
    </Link>
  );
}
