import { useState } from 'react';
import { TrendingUp, AlertTriangle, Shield, Activity } from 'lucide-react';
import EventCountBarChart from './components/Stats/EventCountBarChart';
import EventsOverTime from './components/Stats/EventsOverTime';
import EventsByHour from './components/Stats/EventsByHour';
import EventsByCategory from './components/Stats/EventsByCategory';
import ShopPage from './pages/ShopPage';
import Sidebar from './components/Sidebar'; 

import type { Shop } from './types';
import EventCard from './components/EventCard';
import { useEvents } from './context/EventsContext';

const shops: Shop[] = [
  { id: 'shop1', name: 'Tel Aviv', incidents: 13 },
  { id: 'shop2', name: 'Haifa', incidents: 21 },
  { id: 'shop3', name: 'Eilat', incidents: 8 },
];

export default function AppContent() {
  const [selectedShop, setSelectedShop] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const events = useEvents();
  const sortedEvents = [...events].sort((a, b) => b.date.localeCompare(a.date));
  
  const totalIncidents = shops.reduce((sum, shop) => sum + shop.incidents, 0);
  const activeShops = shops.length;
  const recentEvents = events.filter(event => {
    const eventDate = new Date(event.date);
    const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
    return eventDate > twentyFourHoursAgo;
  }).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar
        shops={shops}
        selectedShop={selectedShop}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        setSelectedShop={setSelectedShop}
      />

      <main className="lg:ml-64 p-4 lg:p-8 animate-fade-in">
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
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-6 lg:mb-8">
              <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100 hover:shadow-medium transition-shadow duration-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Incidents</p>
                    <p className="text-3xl font-bold text-gray-900">{totalIncidents}</p>
                  </div>
                  <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                    <AlertTriangle className="w-6 h-6 text-red-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <span className="text-red-600 font-medium">+12%</span>
                  <span className="text-gray-600 ml-2">from last month</span>
                </div>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100 hover:shadow-medium transition-shadow duration-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Active Locations</p>
                    <p className="text-3xl font-bold text-gray-900">{activeShops}</p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                    <Shield className="w-6 h-6 text-green-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <span className="text-green-600 font-medium">100%</span>
                  <span className="text-gray-600 ml-2">operational status</span>
                </div>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100 hover:shadow-medium transition-shadow duration-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Recent Events (24h)</p>
                    <p className="text-3xl font-bold text-gray-900">{recentEvents}</p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                    <Activity className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <span className="text-blue-600 font-medium">Live</span>
                  <span className="text-gray-600 ml-2">monitoring active</span>
                </div>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100 hover:shadow-medium transition-shadow duration-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Detection Rate</p>
                    <p className="text-3xl font-bold text-gray-900">94.2%</p>
                  </div>
                  <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-purple-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <span className="text-green-600 font-medium">+2.1%</span>
                  <span className="text-gray-600 ml-2">from last week</span>
                </div>
              </div>
            </div>

            {/* Analytics Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 mb-6 lg:mb-8">
              <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Events Over Time</h3>
                <EventsOverTime events={events} />
              </div>
              
              <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Events by Hour</h3>
                <EventsByHour events={events} />
              </div>
              
              <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Shop Activity Overview</h3>
                <EventCountBarChart
                  events={events}
                  groupBy="shopId"
                  title="Shops Events Overview"
                />
              </div>
              
              <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Event Categories</h3>
                <EventsByCategory events={events} />
              </div>
            </div>

            {/* Recent Events */}
            <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Recent Security Events</h3>
                <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
                  {sortedEvents.length} total events
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {sortedEvents.slice(0, 6).map(event => (
                  <EventCard key={event.id} event={event} />
                ))}
              </div>
              {sortedEvents.length > 6 && (
                <div className="mt-6 text-center">
                  <button className="text-primary-600 hover:text-primary-700 font-medium">
                    View all events →
                  </button>
                </div>
              )}
            </div>
          </>
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
