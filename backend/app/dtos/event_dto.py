from dataclasses import dataclass
from datetime import datetime

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