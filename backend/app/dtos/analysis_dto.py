from dataclasses import dataclass
from datetime import datetime

@dataclass
class AnalysisDTO:
    event_id: str
    final_detection: bool | None
    final_confidence: float | None
    decision_reasoning: str | None
    analysis_timestamp: datetime | None 