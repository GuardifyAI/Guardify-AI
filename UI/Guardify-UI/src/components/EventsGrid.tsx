import React, { useState } from 'react';
import EventCard from './EventCard';
import type { Event } from '../types/ui';

interface EventsGridProps {
  events: Event[];
  showCameraFilter?: boolean;
  maxEvents?: number;
  showViewAllButton?: boolean;
  onViewAll?: () => void;
  className?: string;
  title?: string;
}

const EventsGrid: React.FC<EventsGridProps> = ({
  events,
  showCameraFilter = true,
  maxEvents,
  showViewAllButton = false,
  onViewAll,
  className = '',
  title
}) => {
  const [selectedCamera, setSelectedCamera] = useState<string | 'all'>('all');
  
  // Get unique camera options from events
  const cameraOptions = Array.from(new Set(events.map((e) => e.cameraName)));
  
  // Filter events by selected camera
  const filteredEvents = selectedCamera === 'all'
    ? events
    : events.filter((e) => e.cameraName === selectedCamera);
  
  // Apply max events limit if specified
  const displayedEvents = maxEvents 
    ? filteredEvents.slice(0, maxEvents)
    : filteredEvents;

  return (
    <div className={`bg-white rounded-xl p-6 shadow-soft border border-gray-100 ${className}`}>
      {title && (
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
            {filteredEvents.length} total events
          </span>
        </div>
      )}
      
      {showCameraFilter && cameraOptions.length > 0 && (
        <div className="camera-filter-section">
          <label htmlFor="eventsCameraFilter">Filter by Camera: </label>
          <select
            id="eventsCameraFilter"
            value={selectedCamera}
            onChange={(e) => setSelectedCamera(e.target.value)}
          >
            <option value="all">All Cameras</option>
            {cameraOptions.map((cam) => (
              <option key={cam} value={cam}>
                {cam}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="events-grid-4col">
        {displayedEvents.map(event => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>
      
      {displayedEvents.length === 0 && (
        <div className="text-gray-500 text-center py-8">No events found.</div>
      )}
      
      {showViewAllButton && filteredEvents.length > (maxEvents || 0) && onViewAll && (
        <div className="mt-6 text-center">
          <button
            className="text-primary-600 hover:text-primary-700 font-medium"
            onClick={onViewAll}
          >
            View all events →
          </button>
        </div>
      )}
    </div>
  );
};

export default EventsGrid;