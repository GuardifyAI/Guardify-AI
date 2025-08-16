from dataclasses import dataclass


@dataclass
class AnalysisRequestBody:
    final_detection: bool
    final_confidence: float
    decision_reasoning: str
