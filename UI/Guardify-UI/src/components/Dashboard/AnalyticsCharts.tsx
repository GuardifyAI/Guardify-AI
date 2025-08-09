import EventsOverTime from '../Stats/EventsOverTime';
import EventsByHour from '../Stats/EventsByHour';
import EventCountBarChart from '../Stats/EventCountBarChart';
import EventsByCategory from '../Stats/EventsByCategory';
import { useGlobalStats } from '../../hooks/useGlobalStats';
import React from 'react';

const AnalyticsCharts: React.FC = () => {
  const { stats, loading, error } = useGlobalStats();

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 mb-6 lg:mb-8">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
        <h3 className="text-red-800 font-semibold mb-2">Error Loading Analytics</h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
        <p className="text-gray-600">No analytics data available</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 mb-6 lg:mb-8">
      <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Events Per Day</h3>
        <EventsOverTime data={stats.events_per_day} />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Events by Hour</h3>
        <EventsByHour data={stats.events_by_hour} />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Events by Camera</h3>
        <EventCountBarChart data={stats.events_by_camera} title="Events by Camera" />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Event Categories</h3>
        <EventsByCategory data={stats.events_by_category} />
      </div>
    </div>
  );
};

export default AnalyticsCharts;