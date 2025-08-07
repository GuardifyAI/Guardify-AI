import { useState } from 'react';
import ShopPage from './pages/ShopPage';
import Sidebar from './components/Sidebar'; 
import type { Shop } from './types';
import { useEvents } from './context/EventsContext';
import KeyMetrics from './components/Dashboard/KeyMetrics';
import AnalyticsCharts from './components/Dashboard/AnalyticsCharts';
import EventsGrid from './components/EventsGrid';


export default function AppContent() {
  const [selectedShop, setSelectedShop] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const events = useEvents();
  const shops: Shop[] = Array.from(
    events.reduce((map, event) => {
      if (!map.has(event.shopId)) {
        map.set(event.shopId, { id: event.shopId, name: event.shopName, incidents: 0 });
      }
      map.get(event.shopId)!.incidents += 1;
      return map;
    }, new Map<string, Shop>())
  ).map(([, shop]) => shop);
  
  const sortedEvents = [...events].sort((a, b) => b.date.localeCompare(a.date));
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar
        shops={shops}
        selectedShop={selectedShop}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        setSelectedShop={setSelectedShop}
      />

      <main className="lg:ml-72 p-4 lg:p-8 animate-fade-in">
        {/* Header */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl p-6 text-white shadow-strong">
            <h1 className="text-2xl lg:text-3xl font-bold mb-2">
              {selectedShop 
                ? `${shops.find(s => s.id === selectedShop)?.name} Management` 
                : 'Security Operations Center'
              }
            </h1>
            <p className="text-primary-100">
              {selectedShop 
                ? 'Detailed analytics and monitoring for this location' 
                : 'Real-time monitoring across all locations'
              }
            </p>
          </div>
        </div>

        {activeTab === 'dashboard' && (
          <>
            {/* Key Metrics */}
            <KeyMetrics events={events} shops={shops} />
            {/* Analytics Charts */}
            <AnalyticsCharts events={events} />
            {/* Recent Events */}
            <EventsGrid
              events={sortedEvents}
              showCameraFilter={true}
              maxEvents={8}
              showViewAllButton={true}
              onViewAll={() => {
                setSelectedShop(null);
                setActiveTab('events');
              }}
              title="Recent Security Events"
            />
          </>
        )}

        {activeTab === 'events' && !selectedShop && (
          <EventsGrid
            events={sortedEvents}
            showCameraFilter={true}
            title="All Security Events"
          />
        )}

        {selectedShop && ['statistics', 'events', 'cameras'].includes(activeTab) && (
          <div className="animate-slide-in">
            <ShopPage
              shop={shops.find(s => s.id === selectedShop)!}
              events={events}
              tab={activeTab as 'statistics' | 'events' | 'cameras'}
            />
          </div>
        )}
      </main>
    </div>
  );
}
