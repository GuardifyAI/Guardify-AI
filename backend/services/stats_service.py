from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StatsService:
    """Service for computing aggregated statistics from events."""
    
    class StatsComputationError(Exception):
        """Custom exception for stats computation errors."""
        def __init__(self, message: str, cause: Optional[Exception] = None):
            super().__init__(message)
            self.cause = cause

    def compute_stats(self, events: List[Dict], include_category: bool = True) -> Dict:
        """
        Compute aggregated statistics from a list of events.
        
        Args:
            events: List of event dictionaries with timestamp, camera_name, etc.
            include_category: Boolean parameter - controls whether events_by_category is computed
            
        Returns:
            Dictionary containing computed statistics
            
        Raises:
            StatsComputationError: If computation fails
        """
        try:
            result = {
                "events_per_day": self.compute_events_per_day(events),
                "events_by_hour": self.compute_events_by_hour(events),
                "events_by_camera": self.compute_events_by_camera(events)
            }
            
            if include_category:
                result["events_by_category"] = self.compute_events_by_category(events)
                
            return result
        except Exception as e:
            raise self.StatsComputationError(f"Failed to compute stats: {str(e)}", cause=e)

    def compute_events_per_day(self, events: List[Dict]) -> Dict[str, int]:
        """
        Compute events aggregated by day.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Dictionary with YYYY-MM-DD keys and event counts as values
        """
        events_per_day = {}
        skipped_events = 0
        
        for event in events:
            try:
                # Handle both ISO string and datetime object
                timestamp = event.get("event_datetime")
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif isinstance(timestamp, datetime):
                    dt = timestamp
                else:
                    skipped_events += 1
                    continue
                    
                # Format as YYYY-MM-DD
                day_key = dt.strftime("%Y-%m-%d")
                events_per_day[day_key] = events_per_day.get(day_key, 0) + 1
                
            except (ValueError, AttributeError) as e:
                logger.warning(f"Skipping event with invalid timestamp: {e}")
                skipped_events += 1
                continue
        
        if skipped_events > 0:
            logger.info(f"Skipped {skipped_events} events with invalid timestamps")
        
        return events_per_day

    def compute_events_by_hour(self, events: List[Dict]) -> Dict[str, int]:
        """
        Compute events aggregated by hour.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Dictionary with "00".."23" keys and event counts as values
        """
        events_by_hour = {}
        skipped_events = 0
        
        for event in events:
            try:
                # Handle both ISO string and datetime object
                timestamp = event.get("event_datetime")
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif isinstance(timestamp, datetime):
                    dt = timestamp
                else:
                    skipped_events += 1
                    continue
                    
                # Format as HH (00-23)
                hour_key = dt.strftime("%H")
                events_by_hour[hour_key] = events_by_hour.get(hour_key, 0) + 1
                
            except (ValueError, AttributeError) as e:
                logger.warning(f"Skipping event with invalid timestamp: {e}")
                skipped_events += 1
                continue
        
        if skipped_events > 0:
            logger.info(f"Skipped {skipped_events} events with invalid timestamps")
        
        return events_by_hour

    def compute_events_by_camera(self, events: List[Dict]) -> Dict[str, int]:
        """
        Compute events aggregated by camera.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Dictionary with camera names as keys and event counts as values
        """
        events_by_camera = {}
        
        for event in events:
            camera_name = event.get("camera_name")
            
            # Skip events with missing or empty camera names
            if not camera_name or not str(camera_name).strip():
                continue
                
            # Normalize camera name (trim whitespace)
            normalized_name = str(camera_name).strip()
            events_by_camera[normalized_name] = events_by_camera.get(normalized_name, 0) + 1
        
        return events_by_camera

    def compute_events_by_category(self, events: List[Dict]) -> Dict[str, int]:
        """
        Compute events aggregated by category.
        
        TODO: This is a temporary implementation. The actual category field
        is not yet available in the Event entity. This will be implemented
        when the category field is added to the database schema.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Dictionary with category names as keys and event counts as values
        """
        # Temporary implementation - return empty dict since category field doesn't exist yet
        return {"TBD": 0} 