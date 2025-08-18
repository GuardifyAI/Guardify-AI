import type { Event, Shop } from '../types/ui';
import EventsGrid from '../components/EventsGrid';
import AnalyticsCharts from '../components/Dashboard/AnalyticsCharts';
import CamerasList from '../components/CamerasList';
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
          <CamerasList shopId={shop.id} shopName={shop.name} />
        </section>
      )}
    </div>
  );
}
