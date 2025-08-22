from dataclasses import dataclass
from typing import List, Any


@dataclass
class AnalysisResultDTO:
    """
    Data Transfer Object for video analysis results from the agentic service.
    
    This represents the complete analysis result including iteration details
    and final decision information.
    """
    video_url: str
    final_confidence: float
    final_detection: str
    decision_reasoning: str
    iteration_results: List[Any]  # List of iteration dictionaries with detailed analysis