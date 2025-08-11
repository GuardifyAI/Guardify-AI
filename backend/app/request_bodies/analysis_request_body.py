from dataclasses import dataclass


@dataclass
class AnalysisRequestBody:
    final_detection: str
    final_confidence: float
    decision_reasoning: str
