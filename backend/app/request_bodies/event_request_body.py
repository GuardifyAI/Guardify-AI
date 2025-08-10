from dataclasses import dataclass
from datetime import datetime


@dataclass
class EventRequestBody:
    camera_id: str
    description: str
    event_timestamp: datetime
    video_url: str
