from dataclasses import dataclass


@dataclass
class EventRequestBody:
    camera_id: str
    description: str
    video_url: str
