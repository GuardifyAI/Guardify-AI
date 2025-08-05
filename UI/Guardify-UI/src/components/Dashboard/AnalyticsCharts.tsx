import EventsOverTime from '../Stats/EventsOverTime';
import EventsByHour from '../Stats/EventsByHour';
import EventCountBarChart from '../Stats/EventCountBarChart';
import EventsByCategory from '../Stats/EventsByCategory';
import React from 'react';

interface AnalyticsChartsProps {
  events: any[];
}

const AnalyticsCharts: React.FC<AnalyticsChartsProps> = ({ events }) => (
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
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Shop Events Overview</h3>
      <EventCountBarChart events={events} groupBy="shopId" />
    </div>
    <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Event Categories</h3>
      <EventsByCategory events={events} />
    </div>
  </div>
);

export default AnalyticsCharts;