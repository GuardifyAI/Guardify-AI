from dataclasses import dataclass
from typing import Optional


@dataclass
class StartRecordingRequestBody:
    camera_name: str
    duration: Optional[int] = 30
    detection_threshold: Optional[float] = 0.8
    analysis_iterations: Optional[int] = 1


@dataclass
class StopRecordingRequestBody:
    camera_name: str
