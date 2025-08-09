from typing import List, Dict, Optional
from datetime import datetime
from collections import Counter
from dataclasses import dataclass
from backend.app.entities.event import EventDTO, Event
from sqlalchemy import func, extract
from backend.db import db
from backend.app.entities.camera import Camera
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os


class StatsService:
    """Service for computing aggregated statistics from events using SQLAlchemy aggregations."""
    
    def __init__(self):
        """Initialize the StatsService with scikit-learn classifier."""
        try:
            self.classifier = self._load_or_create_classifier()
        except Exception:
            self.classifier = None
    
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
        Compute events aggregated by category using scikit-learn's built-in classifier.
        
        Args:
            shop_id: The shop ID to compute stats for
            
        Returns:
            Dictionary with category names as keys and event counts as values
        """
        # Get all events for this shop with descriptions
        events = db.session.query(
            Event.description
        ).filter(
            Event.shop_id == shop_id,
            Event.description.isnot(None),
            Event.description != ""
        ).all()
        
        # Classify each event description
        categories = []
        for event in events:
            if event.description:
                category = self._classify_event_description(event.description)
                categories.append(category.title())
        
        # Count categories using Counter
        return dict(Counter(categories))

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
        """Compute events aggregated by category from DTOs using scikit-learn's built-in classifier."""
        # Classify each event description
        categories = []
        for event in events:
            if event.description and event.description.strip():
                category = self._classify_event_description(event.description)
                categories.append(category)
        
        # Use Counter for efficient counting
        return dict(Counter(categories))

    # Helper functions moved to bottom
    def _load_or_create_classifier(self):
        """Load existing classifier or create a new one with training data."""
        classifier_path = "security_classifier.pkl"
        
        # Try to load existing classifier
        if os.path.exists(classifier_path):
            try:
                with open(classifier_path, 'rb') as f:
                    classifier = pickle.load(f)
                return classifier
            except Exception:
                pass
        
        # Create new classifier with training data
        training_texts = [
            # Suspicious behavior
            "suspicious person entering",
            "suspicious activity detected",
            "person acting suspiciously",
            "suspicious behavior at checkout",
            "suspicious movement",
            "suspicious person detected",
            "suspicious activity",
            
            # Unauthorized access
            "unauthorized person",
            "unauthorized entry",
            "unauthorized access attempt",
            "unauthorized person detected",
            "unauthorized access",
            
            # Theft
            "theft detected",
            "stealing merchandise",
            "robbery in progress",
            "stolen items",
            "theft",
            "robbery",
            
            # Vandalism
            "vandalism detected",
            "damage to property",
            "destruction of property",
            "graffiti found",
            "vandalism",
            "damage",
            
            # Loitering
            "person loitering",
            "loitering detected",
            "person hanging around",
            "loitering",
            
            # Trespassing
            "trespassing detected",
            "unauthorized entry",
            "trespasser detected",
            "trespassing",
            
            # Normal activity
            "normal customer activity",
            "regular shopping",
            "customer purchasing",
            "normal behavior",
            "normal activity",
            "customer shopping",
        ]
        
        training_labels = [
            "suspicious behavior", "suspicious behavior", "suspicious behavior", "suspicious behavior", "suspicious behavior", "suspicious behavior", "suspicious behavior",
            "unauthorized access", "unauthorized access", "unauthorized access", "unauthorized access", "unauthorized access",
            "theft", "theft", "theft", "theft", "theft", "theft",
            "vandalism", "vandalism", "vandalism", "vandalism", "vandalism", "vandalism",
            "loitering", "loitering", "loitering", "loitering",
            "trespassing", "trespassing", "trespassing", "trespassing",
            "normal activity", "normal activity", "normal activity", "normal activity", "normal activity", "normal activity",
        ]
        
        # Create pipeline with TF-IDF vectorizer and Naive Bayes classifier
        classifier = Pipeline([
            ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english')),
            ('clf', MultinomialNB())
        ])
        
        # Train the classifier
        classifier.fit(training_texts, training_labels)
        
        # Save the classifier
        try:
            with open(classifier_path, 'wb') as f:
                pickle.dump(classifier, f)
        except Exception:
            pass
        
        return classifier

    def _classify_event_description(self, description: str) -> str:
        """
        Classify an event description into a category using scikit-learn's built-in classifier.
        
        Args:
            description: The event description to classify
            
        Returns:
            str: The classified category
        """
        if not description or not description.strip():
            return "other"
        
        if not self.classifier:
            return "other"
        
        try:
            # Use scikit-learn's built-in classifier
            category = self.classifier.predict([description])[0]
            return category
        except Exception:
            return "other"