import uuid
from backend.app.entities.event import Event
from backend.app.dtos import EventDTO
from backend.db import db
from data_science.src.utils import load_env_variables
load_env_variables()


class EventsService:

    def create_event(self, event: EventDTO) -> EventDTO:
        """
        Create a new event entity in the Events table.
        
        Args:
            event (EventDTO): The event data transfer object containing event details
            
        Returns:
            Event: The created event entity
            
        Raises:
            Exception: If there's an error during database operations
        """
        try:
            # Generate UUID for event_id
            event_id = str(uuid.uuid4())
            
            # Create Event entity from DTO
            new_event = Event(
                event_id=event_id,
                shop_id=event.shop_id,
                camera_id=event.camera_id,
                event_timestamp=event.event_timestamp,
                description=event.description,
                video_url=event.video_url
            )
            
            # Add to database session
            db.session.add(new_event)
            
            # Commit the transaction
            db.session.commit()
            
            # Refresh to get the assigned event_id
            db.session.refresh(new_event)
            
            # Convert to DTO - this might be where the error occurs
            result_dto = new_event.to_dto()
            return result_dto
            
        except Exception as e:
            # Rollback in case of error
            db.session.rollback()
            raise Exception(f"Failed to create event: {str(e)}")
