import { useState } from 'react';
import ShopPage from './pages/ShopPage';
import Sidebar from './components/Sidebar'; 
import type { Shop, ApiShop } from './types';
import { useEvents } from './context/EventsContext';
import { useShops } from './hooks/useShops';
import KeyMetrics from './components/Dashboard/KeyMetrics';
import AnalyticsCharts from './components/Dashboard/AnalyticsCharts';
import EventsGrid from './components/EventsGrid';

export default function AppContent() {
  const [selectedShop, setSelectedShop] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const events = useEvents();
  
  // Use the real shops API instead of deriving from events
  const { shops: apiShops, loading: shopsLoading, error: shopsError } = useShops();
  
  // Convert API shops to the format expected by the UI components
  const shops: Shop[] = (apiShops as ApiShop[]).map(shop => ({
    id: shop.shop_id,
    name: shop.name,
    incidents: events.filter(event => event.shopId === shop.shop_id).length // Count incidents
  }));
  
  const sortedEvents = [...events].sort((a, b) => b.date.localeCompare(a.date));
  
  // Show loading state
  if (shopsLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading shops...</p>
        </div>
      </div>
    );
  }
  
  // Show error state
  if (shopsError) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
            <h3 className="text-red-800 font-semibold mb-2">Error Loading Shops</h3>
            <p className="text-red-600 mb-4">{shopsError}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }
  
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

        {/* Debug info - remove this after testing */}
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold text-blue-800 mb-2">API Debug Info:</h3>
          <p className="text-blue-700">Found {apiShops.length} shops from API</p>
          <details className="mt-2">
            <summary className="cursor-pointer text-blue-600">Show shop details</summary>
            <pre className="mt-2 text-sm bg-blue-100 p-2 rounded overflow-auto">
              {JSON.stringify(apiShops, null, 2)}
            </pre>
          </details>
        </div>

        {activeTab === 'dashboard' && (
          <>
            {/* Key Metrics */}
            <KeyMetrics events={events} shops={shops} />
            {/* Analytics Charts */}
            <AnalyticsCharts />
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
