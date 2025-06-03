import { useParams } from 'react-router-dom';
import './EventPage.css';
import { useEvents } from '../context/EventsContext';


export default function EventPage() {
  const { id } = useParams<{ id: string }>();
  console.log('Event ID:', id);
  const events = useEvents();
  const event = events.find(e => e.id === id);

  if (!event) {
    return <p>Event not found.</p>;
  }

  return (
    <div className="page-layout">
    <div className="event-page">
      <h2>Event Details</h2>
      <p><strong>Date:</strong> {new Date(event.date).toLocaleString()}</p>
      <p><strong>Shop:</strong> {event.shopName}</p>
      <p><strong>Camera:</strong> {event.cameraName}</p>
      <p><strong>Description:</strong> {event.description}</p>

      <h4>Analysis</h4>
      <p><strong>Final Detection:</strong> {event.analysis.final_detection ? 'Yes' : 'No'}</p>
      <p><strong>Confidence:</strong> {event.analysis.final_confidence}%</p>
      <p><strong>Reasoning:</strong> {event.analysis.decision_reasoning}</p>

      <div className="video-container">
        <video controls width="100%">
          <source src={event.videoUrl} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>
    </div>
    </div>
  );
}
