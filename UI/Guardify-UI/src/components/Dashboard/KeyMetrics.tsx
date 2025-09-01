import { AlertTriangle, Shield, Activity, TrendingUp } from 'lucide-react';
import React from 'react';
import { subMonths, subWeeks } from 'date-fns';
import type { Shop } from '../../types/ui';

interface KeyMetricsProps {
  events: any[];
  shops: Shop[];
}

const KeyMetrics: React.FC<KeyMetricsProps> = ({ events, shops }) => {
  // Total number of incidents (based on all events)
  const totalIncidents = events.length;

  // Number of active shops
  const activeShops = shops.length;

  // Events from the last 24 hours
  const recentEvents = events.filter(event => {
    const eventDate = new Date(event.date);
    const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
    return eventDate > twentyFourHoursAgo;
  }).length;

  // Detection rate (all time)
  const detectedEvents = events.filter(event => event.analysis?.final_detection).length;
  const detectionRate = events.length === 0 ? 0 : (detectedEvents / events.length) * 100;

  // Weekly detection rate change
  const now = new Date();
  const startOfThisWeek = subWeeks(now, 0);
  const startOfLastWeek = subWeeks(now, 1);

  const eventsThisWeek = events.filter(event => {
    const d = new Date(event.date);
    return d >= startOfThisWeek && d < now;
  });

  const eventsLastWeek = events.filter(event => {
    const d = new Date(event.date);
    return d >= startOfLastWeek && d < startOfThisWeek;
  });

  const detectedThisWeek = eventsThisWeek.filter(event => event.analysis?.final_detection).length;
  const detectedLastWeek = eventsLastWeek.filter(event => event.analysis?.final_detection).length;

  const rateThisWeek = eventsThisWeek.length === 0 ? 0 : (detectedThisWeek / eventsThisWeek.length) * 100;
  const rateLastWeek = eventsLastWeek.length === 0 ? 0 : (detectedLastWeek / eventsLastWeek.length) * 100;

  const detectionRateChange = rateLastWeek === 0 ? 0 : rateThisWeek - rateLastWeek;

  // Monthly incident change
  const lastMonth = subMonths(now, 1);

  const incidentsThisMonth = events.filter(event => {
    const d = new Date(event.date);
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
  }).length;

  const incidentsLastMonth = events.filter(event => {
    const d = new Date(event.date);
    return d.getMonth() === lastMonth.getMonth() && d.getFullYear() === lastMonth.getFullYear();
  }).length;

  const percentChange = incidentsLastMonth === 0
    ? 100
    : ((incidentsThisMonth - incidentsLastMonth) / incidentsLastMonth) * 100;

  return (
    <div className="metrics-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-6 lg:mb-8">
      
      {/* Total Incidents */}
      <div className="metric-card bg-white rounded-xl p-6 shadow-soft border border-gray-100 hover:shadow-medium transition-shadow duration-200">
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
          <span className="text-red-600 font-medium">
            {percentChange >= 0 ? '+' : ''}{percentChange.toFixed(2)}%
          </span>
          <span className="text-gray-600 ml-2">from last month</span>
        </div>
      </div>

      {/* Active Locations */}
      <div className="metric-card bg-white rounded-xl p-6 shadow-soft border border-gray-100 hover:shadow-medium transition-shadow duration-200">
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

      {/* Recent Events (24h) */}
      <div className="metric-card bg-white rounded-xl p-6 shadow-soft border border-gray-100 hover:shadow-medium transition-shadow duration-200">
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

      {/* Detection Rate */}
      <div className="metric-card bg-white rounded-xl p-6 shadow-soft border border-gray-100 hover:shadow-medium transition-shadow duration-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">Detection Rate</p>
            <p className="text-3xl font-bold text-gray-900">{detectionRate.toFixed(1)}%</p>
          </div>
          <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
            <TrendingUp className="w-6 h-6 text-purple-600" />
          </div>
        </div>
        <div className="mt-4 flex items-center text-sm">
          <span className={detectionRateChange >= 0 ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
            {detectionRateChange >= 0 ? '+' : ''}{detectionRateChange.toFixed(1)}%
          </span>
          <span className="text-gray-600 ml-2">from last week</span>
        </div>
      </div>

    </div>
  );
};

export default KeyMetrics;
