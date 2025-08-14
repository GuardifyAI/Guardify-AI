from dataclasses import dataclass
from typing import Optional


@dataclass
class StartRecordingRequestBody:
    camera_name: str
    duration: Optional[int] = 30


@dataclass
class StopRecordingRequestBody:
    camera_name: str
