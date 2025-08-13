import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Calendar, MapPin, Camera, Eye, Shield } from 'lucide-react';
import './EventPage.css';
import { useEvents } from '../context/EventsContext';
import { getEventStatusInfo } from '../utils/statusUtils';

export default function EventPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const events = useEvents();
  const event = events.find(e => e.id === id);

  if (!event) {
    return (
      <div className="page-layout">
        <div className="event-page">
          <button 
            onClick={() => navigate(-1)}
            className="back-button"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>
          <div className="error-message">
            <p>Event not found.</p>
          </div>
        </div>
      </div>
    );
  }

  const statusInfo = getEventStatusInfo(event.analysis);
  const hasAnalysis = event.analysis && 
    event.analysis.finalDetection !== undefined && 
    event.analysis.finalConfidence !== undefined;
    
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="page-layout">
      <div className="event-page">
        {/* Back Button */}
        <button 
          onClick={() => navigate(-1)}
          className="back-button"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>

        {/* Header Section */}
        <div className="event-header">
          <div className="event-title-section">
            <h1 className="event-title">Event Details</h1>
            <div className="event-meta">
              <span className="event-id">ID: {event.id}</span>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="event-content-grid">
          {/* Event Info Card */}
          <div className="event-info-card">
            <h3 className="card-title">
              <Eye className="w-5 h-5" />
              Event Information
            </h3>
            <div className="info-grid">
              <div className="info-item">
                <Calendar className="w-4 h-4 text-gray-400" />
                <div>
                  <span className="info-label">Date & Time</span>
                  <span className="info-value">{formatDate(event.date)}</span>
                </div>
              </div>
              <div className="info-item">
                <MapPin className="w-4 h-4 text-gray-400" />
                <div>
                  <span className="info-label">Location</span>
                  <span className="info-value">{event.shopName}</span>
                </div>
              </div>
              <div className="info-item">
                <Camera className="w-4 h-4 text-gray-400" />
                <div>
                  <span className="info-label">Camera</span>
                  <span className="info-value">{event.cameraName}</span>
                </div>
              </div>
            </div>
            <div className="description-section">
              <span className="info-label">Description</span>
              <p className="description-text">{event.description}</p>
            </div>
          </div>

          {/* Analysis Card */}
          <div className="analysis-card">
            <h3 className="card-title">
              <Shield className="w-5 h-5" />
              Security Analysis
            </h3>

            {hasAnalysis ? (
              <>
                {/* Status Section*/}
                <div className="status-section">
                  <div className="status-row">
                    <div className="status-indicator">
                      <statusInfo.icon className={`w-6 h-6 ${statusInfo.color}`} />
                      <div className="status-info">
                        <span className="status-label-small">Security Level</span>
                        <span className={`status-value ${statusInfo.color}`}>{statusInfo.label}</span>
                      </div>
                    </div>
                    <div className={`detection-badge ${
                      event.analysis!.finalDetection 
                        ? 'bg-red-100 text-red-700' 
                        : 'bg-green-100 text-green-700'
                    }`}>
                      {event.analysis!.finalDetection ? 'DETECTED' : 'NOT DETECTED'}
                    </div>
                  </div>
                </div>

                <div className="analysis-content">
                  <div className="confidence-section">
                    <div className="confidence-header">
                      <span className="info-label">Detection Confidence</span>
                      <span className="confidence-value">{(event.analysis!.finalConfidence || 0).toFixed(1)}%</span>
                    </div>
                    <div className="confidence-bar">
                      <div 
                        className={`confidence-fill ${statusInfo.bgColor}`}
                        style={{ width: `${event.analysis!.finalConfidence || 0}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="reasoning-section">
                    <span className="info-label">Decision Reasoning</span>
                    <p className="reasoning-text">{event.analysis!.decisionReasoning || 'No reasoning provided'}</p>
                  </div>
                </div>
              </>
            ) : (
              <div className="no-analysis-section">
                <div className="status-section">
                  <div className="status-row">
                    <div className="status-indicator">
                      <statusInfo.icon className={`w-6 h-6 ${statusInfo.color}`} />
                      <div className="status-info">
                        <span className="status-label-small">Security Level</span>
                        <span className={`status-value ${statusInfo.color}`}>{statusInfo.label}</span>
                      </div>
                    </div>
                    <div className="detection-badge bg-gray-100 text-gray-600">
                      NOT PROVIDED
                    </div>
                  </div>
                </div>
                <div className="no-analysis-content">
                  <p className="text-gray-500 text-center">
                    This event has not been analyzed yet. Analysis may be in progress or unavailable for this event.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Video Section */}
        <div className="video-section">
          <h3 className="section-title">Security Footage</h3>
          <div className="video-container">
            <video controls width="100%">
              <source src={event.videoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        </div>
      </div>
    </div>
  );
}