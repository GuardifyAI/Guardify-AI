import { Link } from 'react-router-dom';
import { Calendar, MapPin, Camera } from 'lucide-react';
import type { Event } from '../types';
import { getStatusInfo } from '../utils/statusUtils';

export default function EventCard({ event }: { event: Event }) {

  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const statusInfo = getStatusInfo(event.analysis.final_detection, event.analysis.final_confidence);

  return (
    <Link to={`/event/${event.id}`} className="block group">
      <div className="bg-white rounded-xl p-4 hover:shadow-medium transition-all duration-200 group-hover:scale-[1.02] border-2 border-gray-200 hover:border-primary-300">

        {/* Header with status + detection label */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-1">
              <statusInfo.icon className={`w-4 h-4 ${statusInfo.color}`} />
              <span className={`text-xs font-medium ${statusInfo.color}`}>{statusInfo.label}</span>
            </div>
            <div className={`text-xs font-medium px-2 py-1 rounded-full ${
              event.analysis.final_detection 
                ? 'bg-red-100 text-red-700' 
                : 'bg-green-100 text-green-700'
            }`}>
              {event.analysis.final_detection ? 'DETECTED' : 'NOT DETECTED'}
            </div>
          </div>
        </div>

        {/* Event Description */}
        <h3 className="font-medium text-gray-900 mb-3 line-clamp-2 group-hover:text-primary-600 transition-colors">
          {event.description}
        </h3>

        {/* Event Details */}
        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-gray-400" />
            <span>{formatDate(event.date)}</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <MapPin className="w-4 h-4 text-gray-400" />
            <span className="font-medium text-gray-700">{event.shopName}</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <Camera className="w-4 h-4 text-gray-400" />
            <span>{event.cameraName}</span>
          </div>
        </div>

        {/* Confidence Score */}
        <div className="mt-4 pt-3 border-t border-gray-100">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-500">Detection Confidence</span>
            <span className="font-medium text-gray-700">{event.analysis.final_confidence.toFixed(1)}%</span>
          </div>
          <div className="mt-1 w-full bg-gray-200 rounded-full h-1">
            <div 
              className={`h-1 rounded-full ${statusInfo.bgColor}`}
              style={{ width: `${event.analysis.final_confidence}%` }}
            ></div>
          </div>
        </div>

        {/* Hover indicator */}
        <div className="mt-3 flex items-center justify-end opacity-0 group-hover:opacity-100 transition-opacity">
          <span className="text-xs text-primary-600 font-medium">
            View details →
          </span>
        </div>
      </div>
    </Link>
  );
}
