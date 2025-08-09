from dataclasses import dataclass
from typing import Dict

@dataclass
class StatsDTO:
    """Data class for holding computed statistics."""
    events_per_day: Dict[str, int]
    events_by_hour: Dict[str, int]
    events_by_camera: Dict[str, int]
    events_by_category: Dict[str, int] | None = None 