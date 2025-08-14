from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from backend.app.dtos.analysis_dto import AnalysisDTO

@dataclass
class EventDTO:
    event_id: str
    shop_id: str
    camera_id: str
    event_timestamp: datetime | None
    description: str | None
    video_url: str | None
    shop_name: str | None
    camera_name: str | None
    event_datetime: str | None
    analysis: Optional[AnalysisDTO] = field(default=None)
