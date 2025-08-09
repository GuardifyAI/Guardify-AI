from typing import List, Dict, Optional
from datetime import datetime
import logging
from collections import Counter
from dataclasses import dataclass
from backend.app.entities.event import EventDTO, Event
from sqlalchemy import func, extract
from backend.db import db
from backend.app.entities.camera import Camera

logger = logging.getLogger(__name__)


class StatsService:
    """Service for computing aggregated statistics from events using SQLAlchemy aggregations."""
    
    @dataclass
    class StatsDTO:
        """Data class for holding computed statistics."""
        events_per_day: Dict[str, int]
        events_by_hour: Dict[str, int]
        events_by_camera: Dict[str, int]
        events_by_category: Optional[Dict[str, int]] = None

    class StatsComputationError(Exception):
        """Custom exception for stats computation errors."""
        def __init__(self, message: str, cause: Optional[Exception] = None):
            super().__init__(message)
            self.cause = cause

    def compute_stats_from_dtos(self, events: List[EventDTO], include_category: bool = True) -> StatsDTO:
        """
        Compute aggregated statistics from a list of events.
        
        Args:
            events: List of EventDTO objects with timestamp, camera_name, etc.
            include_category: Boolean parameter - controls whether events_by_category is computed
            
        Returns:
            StatsDTO object containing computed statistics
            
        Raises:
            StatsComputationError: If computation fails
        """
        try:
            # Since we already have the events as DTOs, we'll compute stats from them
            # In a real implementation, you might want to pass the shop_id and do DB queries
            events_per_day = self.compute_events_per_day_from_dtos(events)
            events_by_hour = self.compute_events_by_hour_from_dtos(events)
            events_by_camera = self.compute_events_by_camera_from_dtos(events)
            events_by_category = self.compute_events_by_category_from_dtos(events) if include_category else None
            
            return self.StatsDTO(
                events_per_day=events_per_day,
                events_by_hour=events_by_hour,
                events_by_camera=events_by_camera,
                events_by_category=events_by_category
            )
        except Exception as e:
            raise self.StatsComputationError(f"Failed to compute stats: {str(e)}", cause=e)

    def compute_stats_from_db(self, shop_id: str, include_category: bool = True) -> StatsDTO:
        """
        Compute aggregated statistics directly from database using SQLAlchemy aggregations.
        
        Args:
            shop_id: The shop ID to compute stats for
            include_category: Boolean parameter - controls whether events_by_category is computed
            
        Returns:
            StatsDTO object containing computed statistics
            
        Raises:
            StatsComputationError: If computation fails
        """
        try:
            events_per_day = self.compute_events_per_day_from_db(shop_id)
            events_by_hour = self.compute_events_by_hour_from_db(shop_id)
            events_by_camera = self.compute_events_by_camera_from_db(shop_id)
            events_by_category = self.compute_events_by_category_from_db(shop_id) if include_category else None
            
            return self.StatsDTO(
                events_per_day=events_per_day,
                events_by_hour=events_by_hour,
                events_by_camera=events_by_camera,
                events_by_category=events_by_category
            )
        except Exception as e:
            raise self.StatsComputationError(f"Failed to compute stats from DB: {str(e)}", cause=e)

    def compute_events_per_day_from_db(self, shop_id: str) -> Dict[str, int]:
        """
        Compute events aggregated by day using SQLAlchemy.
        
        Args:
            shop_id: The shop ID to compute stats for
            
        Returns:
            Dictionary with YYYY-MM-DD keys and event counts as values
        """
        # Use SQLAlchemy's func.date() and func.count() for aggregation
        result = db.session.query(
            func.date(Event.event_timestamp).label('day'),
            func.count(Event.event_id).label('count')
        ).filter(
            Event.shop_id == shop_id,
            Event.event_timestamp.isnot(None)
        ).group_by(
            func.date(Event.event_timestamp)
        ).all()
        
        return {str(day): count for day, count in result}

    def compute_events_by_hour_from_db(self, shop_id: str) -> Dict[str, int]:
        """
        Compute events aggregated by hour using SQLAlchemy.
        
        Args:
            shop_id: The shop ID to compute stats for
            
        Returns:
            Dictionary with "00".."23" keys and event counts as values
        """
        # Use SQLAlchemy's func.extract() for hour extraction
        result = db.session.query(
            func.extract('hour', Event.event_timestamp).label('hour'),
            func.count(Event.event_id).label('count')
        ).filter(
            Event.shop_id == shop_id,
            Event.event_timestamp.isnot(None)
        ).group_by(
            func.extract('hour', Event.event_timestamp)
        ).all()
        
        return {f"{int(hour):02d}": count for hour, count in result}

    def compute_events_by_camera_from_db(self, shop_id: str) -> Dict[str, int]:
        """
        Compute events aggregated by camera using SQLAlchemy.
        
        Args:
            shop_id: The shop ID to compute stats for
            
        Returns:
            Dictionary with camera names as keys and event counts as values
        """
        # Use SQLAlchemy's func.count() with camera join to get camera names
        result = db.session.query(
            Camera.camera_name,
            func.count(Event.event_id).label('count')
        ).join(
            Event, Event.camera_id == Camera.camera_id
        ).filter(
            Event.shop_id == shop_id,
            Event.camera_id.isnot(None),
            Camera.camera_name.isnot(None)
        ).group_by(
            Camera.camera_name
        ).all()
        
        return {camera_name: count for camera_name, count in result}

    def compute_events_by_category_from_db(self, shop_id: str) -> Dict[str, int]:
        """
        Compute events aggregated by category using SQLAlchemy.
        
        TODO: This is a temporary implementation. The actual category field
        is not yet available in the Event entity. This will be implemented
        when the category field is added to the database schema.
        
        Args:
            shop_id: The shop ID to compute stats for
            
        Returns:
            Dictionary with category names as keys and event counts as values
        """
        # Temporary implementation - return empty dict since category field doesn't exist yet
        return {"TBD": 0}

    # Keep the DTO-based methods for backward compatibility
    def compute_events_per_day_from_dtos(self, events: List[EventDTO]) -> Dict[str, int]:
        """Compute events aggregated by day from DTOs using Counter."""
        # Extract valid timestamps and format as YYYY-MM-DD
        valid_timestamps = []
        for event in events:
            try:
                timestamp = event.event_timestamp
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif isinstance(timestamp, datetime):
                    dt = timestamp
                else:
                    continue
                    
                valid_timestamps.append(dt.strftime("%Y-%m-%d"))
            except (ValueError, AttributeError):
                continue
        
        # Use Counter for efficient counting
        return dict(Counter(valid_timestamps))

    def compute_events_by_hour_from_dtos(self, events: List[EventDTO]) -> Dict[str, int]:
        """Compute events aggregated by hour from DTOs using Counter."""
        # Extract valid timestamps and format as HH
        valid_hours = []
        for event in events:
            try:
                timestamp = event.event_timestamp
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif isinstance(timestamp, datetime):
                    dt = timestamp
                else:
                    continue
                    
                valid_hours.append(dt.strftime("%H"))
            except (ValueError, AttributeError):
                continue
        
        # Use Counter for efficient counting
        return dict(Counter(valid_hours))

    def compute_events_by_camera_from_dtos(self, events: List[EventDTO]) -> Dict[str, int]:
        """Compute events aggregated by camera from DTOs using Counter."""
        # Extract valid camera names
        valid_cameras = []
        for event in events:
            camera_name = event.camera_name
            if camera_name and str(camera_name).strip():
                valid_cameras.append(str(camera_name).strip())
        
        # Use Counter for efficient counting
        return dict(Counter(valid_cameras))

    def compute_events_by_category_from_dtos(self, events: List[EventDTO]) -> Dict[str, int]:
        """Compute events aggregated by category from DTOs using Counter."""
        # Temporary implementation - return empty dict since category field doesn't exist yet
        return {"TBD": 0} 