import uuid
from backend.app.entities.event import Event
from backend.app.dtos import EventDTO
from backend.app.request_bodies.event_request_body import EventRequestBody
from backend.db import db
from data_science.src.utils import load_env_variables
load_env_variables()


class EventsService:

    def create_event(self, shop_id: str, event_req_body: EventRequestBody) -> EventDTO:
        """
        Create a new event entity in the Events table.
        
        Args:
            shop_id (str): The shop ID
            event_req_body (EventRequestBody): The event request data
            
        Returns:
            Event: The created event entity
            
        Raises:
            Exception: If there's an error during database operations
        """
        try:
            # Generate UUID for event_id
            event_id = str(uuid.uuid4())
            
            # Create Event entity
            new_event = Event(
                event_id=event_id,
                shop_id=shop_id,
                camera_id=event_req_body.camera_id,
                event_timestamp=event_req_body.event_timestamp,
                description=event_req_body.description,
                video_url=event_req_body.video_url
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
