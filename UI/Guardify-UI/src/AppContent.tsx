import { useState } from 'react';
import ShopPage from './pages/ShopPage';
import Sidebar from './components/Sidebar'; 
import type { Shop } from './types/ui';
import { useEvents, useEventsContext } from './context/EventsContext';
import { useShops } from './hooks/useShops';
import KeyMetrics from './components/Dashboard/KeyMetrics';
import AnalyticsCharts from './components/Dashboard/AnalyticsCharts';
import EventsGrid from './components/EventsGrid';
import LoadingSpinner from './components/LoadingSpinnerProps';
import ErrorDisplay from './components/ErrorDisplay';

export default function AppContent() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');

  const events = useEvents();
  const { loading: eventsLoading, error: eventsError, selectedShop, setSelectedShop, refetch } = useEventsContext();
  
  // Use the shops API
  const { shops: fetchedShops, loading: shopsLoading, error: shopsError } = useShops();
  
  // Use shops directly from useShops
  const shops: Shop[] = fetchedShops;
  
  // Custom function to handle tab switching with events refresh
  const handleTabChange = (newTab: string) => {
    setActiveTab(newTab);
    // Only refresh events when switching TO the events tab to get latest data
    if (newTab === 'events') {
      refetch();
    }
  };
  
  // Sort events by date in descending order (newest first)
  const sortedEvents = [...events].sort((a, b) => {
    const dateA = new Date(a.date);
    const dateB = new Date(b.date);
    return dateB.getTime() - dateA.getTime();
  });
  
  // Show loading state
  if (shopsLoading || eventsLoading) {
    return <LoadingSpinner fullScreen message={shopsLoading ? "Loading shops..." : "Loading events..."} />;
  }

  // Show error state
  if (shopsError) {
    return <ErrorDisplay fullScreen title="Error Loading Shops" message={shopsError} onRetry={() => window.location.reload()} />;
  }

  if (eventsError) {
    return <ErrorDisplay fullScreen title="Error Loading Events" message={eventsError} onRetry={() => window.location.reload()} />;
  }

  // Show message if no shops exist
  if (!shops || shops.length === 0) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
        <Sidebar
          shops={[]}
          selectedShop={selectedShop}
          activeTab={activeTab}
          setActiveTab={handleTabChange}
          setSelectedShop={setSelectedShop}
        />
        <main className="lg:ml-72 p-4 lg:p-8 animate-fade-in flex flex-col items-center justify-center">
          <div className="bg-white rounded-xl shadow-md p-8 text-center">
            <h2 className="text-xl font-semibold mb-2 text-gray-800">No Shops Available</h2>
            <p className="text-gray-600">Please ask your administrator to add shops to the system.</p>
          </div>
        </main>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar
        shops={shops}
        selectedShop={selectedShop}
        activeTab={activeTab}
        setActiveTab={handleTabChange}
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
            <AnalyticsCharts />
            {/* Recent Events */}
            <EventsGrid
              events={sortedEvents}
              showCameraFilter={true}
              maxEvents={8}
              showViewAllButton={true}
              onViewAll={() => {
                setSelectedShop(null);
                handleTabChange('events');
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
              events={sortedEvents}
              tab={activeTab as 'statistics' | 'events' | 'cameras'}
            />
          </div>
        )}
      </main>
    </div>
  );
}
