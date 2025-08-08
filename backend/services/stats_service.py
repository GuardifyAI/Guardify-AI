from typing import List, Dict, Optional
from datetime import datetime
import logging
from backend.app.entities.event import EventDTO, Event
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class StatsService:
    """Service for computing aggregated statistics from events using SQLAlchemy aggregations."""
    
    class StatsComputationError(Exception):
        """Custom exception for stats computation errors."""
        def __init__(self, message: str, cause: Optional[Exception] = None):
            super().__init__(message)
            self.cause = cause

    def compute_stats(self, events: List[EventDTO], include_category: bool = True) -> Dict:
        """
        Compute aggregated statistics from a list of events.
        
        Args:
            events: List of EventDTO objects with timestamp, camera_name, etc.
            include_category: Boolean parameter - controls whether events_by_category is computed
            
        Returns:
            Dictionary containing computed statistics
            
        Raises:
            StatsComputationError: If computation fails
        """
        try:
            # Since we already have the events as DTOs, we'll compute stats from them
            # In a real implementation, you might want to pass the shop_id and do DB queries
            result = {
                "events_per_day": self.compute_events_per_day_from_dtos(events),
                "events_by_hour": self.compute_events_by_hour_from_dtos(events),
                "events_by_camera": self.compute_events_by_camera_from_dtos(events)
            }
            
            if include_category:
                result["events_by_category"] = self.compute_events_by_category_from_dtos(events)
                
            return result
        except Exception as e:
            raise self.StatsComputationError(f"Failed to compute stats: {str(e)}", cause=e)

    def compute_stats_from_db(self, shop_id: str, include_category: bool = True) -> Dict:
        """
        Compute aggregated statistics directly from database using SQLAlchemy aggregations.
        
        Args:
            shop_id: The shop ID to compute stats for
            include_category: Boolean parameter - controls whether events_by_category is computed
            
        Returns:
            Dictionary containing computed statistics
            
        Raises:
            StatsComputationError: If computation fails
        """
        try:
            from backend.db import db
            
            result = {
                "events_per_day": self.compute_events_per_day_from_db(shop_id),
                "events_by_hour": self.compute_events_by_hour_from_db(shop_id),
                "events_by_camera": self.compute_events_by_camera_from_db(shop_id)
            }
            
            if include_category:
                result["events_by_category"] = self.compute_events_by_category_from_db(shop_id)
                
            return result
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
        from backend.db import db
        
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
        from backend.db import db
        
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
        from backend.db import db
        
        # Use SQLAlchemy's func.count() with camera relationship
        result = db.session.query(
            Event.camera_id,
            func.count(Event.event_id).label('count')
        ).filter(
            Event.shop_id == shop_id,
            Event.camera_id.isnot(None)
        ).group_by(
            Event.camera_id
        ).all()
        
        # Convert camera_id to camera_name (you might want to join with Camera table)
        camera_stats = {}
        for camera_id, count in result:
            # For now, we'll use camera_id as key. In a real implementation,
            # you'd join with the Camera table to get camera names
            camera_stats[f"Camera_{camera_id}"] = count
        
        return camera_stats

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
        """Compute events aggregated by day from DTOs (fallback method)."""
        events_per_day = {}
        skipped_events = 0
        
        for event in events:
            try:
                timestamp = event.event_timestamp
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif isinstance(timestamp, datetime):
                    dt = timestamp
                else:
                    skipped_events += 1
                    continue
                    
                day_key = dt.strftime("%Y-%m-%d")
                events_per_day[day_key] = events_per_day.get(day_key, 0) + 1
                
            except (ValueError, AttributeError) as e:
                logger.warning(f"Skipping event with invalid timestamp: {e}")
                skipped_events += 1
                continue
        
        if skipped_events > 0:
            logger.info(f"Skipped {skipped_events} events with invalid timestamps")
        
        return events_per_day

    def compute_events_by_hour_from_dtos(self, events: List[EventDTO]) -> Dict[str, int]:
        """Compute events aggregated by hour from DTOs (fallback method)."""
        events_by_hour = {}
        skipped_events = 0
        
        for event in events:
            try:
                timestamp = event.event_timestamp
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif isinstance(timestamp, datetime):
                    dt = timestamp
                else:
                    skipped_events += 1
                    continue
                    
                hour_key = dt.strftime("%H")
                events_by_hour[hour_key] = events_by_hour.get(hour_key, 0) + 1
                
            except (ValueError, AttributeError) as e:
                logger.warning(f"Skipping event with invalid timestamp: {e}")
                skipped_events += 1
                continue
        
        if skipped_events > 0:
            logger.info(f"Skipped {skipped_events} events with invalid timestamps")
        
        return events_by_hour

    def compute_events_by_camera_from_dtos(self, events: List[EventDTO]) -> Dict[str, int]:
        """Compute events aggregated by camera from DTOs (fallback method)."""
        events_by_camera = {}
        
        for event in events:
            camera_name = event.camera_name
            
            if not camera_name or not str(camera_name).strip():
                continue
                
            normalized_name = str(camera_name).strip()
            events_by_camera[normalized_name] = events_by_camera.get(normalized_name, 0) + 1
        
        return events_by_camera

    def compute_events_by_category_from_dtos(self, events: List[EventDTO]) -> Dict[str, int]:
        """Compute events aggregated by category from DTOs (fallback method)."""
        # Temporary implementation - return empty dict since category field doesn't exist yet
        return {"TBD": 0} 