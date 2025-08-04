import { Link } from 'react-router-dom';
import { Calendar, MapPin, Camera, AlertTriangle, CheckCircle } from 'lucide-react';
import type { Event } from '../types';

export default function EventCard({ event }: { event: Event }) {
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-red-600 bg-red-100';
    if (confidence >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 80) return 'High Risk';
    if (confidence >= 60) return 'Medium Risk';
    return 'Low Risk';
  };

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

  return (
    <Link to={`/event/${event.id}`} className="block group">
      <div className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-medium transition-all duration-200 hover:border-primary-300 group-hover:scale-[1.02]">
        {/* Header with status and confidence */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            {event.analysis.final_detection ? (
              <div className="flex items-center space-x-1">
                <AlertTriangle className="w-4 h-4 text-red-500" />
                <span className="text-xs font-medium text-red-600">INCIDENT</span>
              </div>
            ) : (
              <div className="flex items-center space-x-1">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-xs font-medium text-green-600">SAFE</span>
              </div>
            )}
          </div>
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${getConfidenceColor(event.analysis.final_confidence)}`}>
            {getConfidenceLabel(event.analysis.final_confidence)}
          </span>
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
              className={`h-1 rounded-full ${
                event.analysis.final_confidence >= 80 ? 'bg-red-500' :
                event.analysis.final_confidence >= 60 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
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
