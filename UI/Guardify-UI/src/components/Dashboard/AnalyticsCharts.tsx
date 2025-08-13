import EventsOverTime from '../Stats/EventsOverTime';
import EventsByHour from '../Stats/EventsByHour';
import EventCountBarChart from '../Stats/EventCountBarChart';
import EventsByCategory from '../Stats/EventsByCategory';
import { useStats } from '../../hooks/useStats';
import LoadingSpinner from '../LoadingSpinnerProps';
import ErrorDisplay from '../ErrorDisplay';
import React from 'react';

interface AnalyticsChartsProps {
  shopId?: string; // If provided, show shop stats; otherwise show global stats
}

const AnalyticsCharts: React.FC<AnalyticsChartsProps> = ({ shopId }) => {
  const { stats, loading, error } = useStats(shopId);

  if (loading) {
    return <LoadingSpinner message="Loading analytics..." />;
  }

  if (error) {
    return <ErrorDisplay title="Error Loading Analytics" message={error} />;
  }

  if (!stats) {
    return <ErrorDisplay title="No Data" message="No analytics data available" />;
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 mb-6 lg:mb-8">
      <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Events Per Day</h3>
        <EventsOverTime data={stats.eventsPerDay} />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Events by Hour</h3>
        <EventsByHour data={stats.eventsByHour} />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Events by Camera</h3>
        <EventCountBarChart data={stats.eventsByCamera} title="Events by Camera" />
      </div>
      {stats.eventsByCategory && (
        <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Event Categories</h3>
          <EventsByCategory data={stats.eventsByCategory} />
        </div>
      )}
    </div>
  );
};

export default AnalyticsCharts;