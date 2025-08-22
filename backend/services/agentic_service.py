import os
from utils.logger_utils import create_logger
from data_science.src.model.pipeline.shoplifting_analyzer import create_agentic_analyzer
from google_client.google_client import GoogleClient
from backend.app.dtos.analysis_result_dto import AnalysisResultDTO


class AgenticService:
    """
    Service for analyzing videos using the agentic AI strategy.
    
    This service provides synchronous video analysis capabilities
    using the agentic model approach.
    """

    def __init__(self, shops_service):
        """Initialize the agentic service."""
        self.shops_service = shops_service
        self.logger = create_logger("AgenticService", "agentic_service.log")
        
        # Initialize Google client for single video analysis
        self.google_client = GoogleClient(
            project=os.getenv("GOOGLE_PROJECT_ID"),
            location=os.getenv("GOOGLE_PROJECT_LOCATION"),
            service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
        )

    def analyze_single_video(self, video_url: str) -> AnalysisResultDTO:
        """
        Analyze a single video using the agentic strategy (synchronous).

        Args:
            video_url (str): Google Cloud Storage URI of the video to analyze

        Returns:
            AnalysisResultDTO: Analysis result containing:
                - video_url: str
                - final_confidence: float  
                - final_detection: str
                - decision_reasoning: str
                - iteration_results: List[Any]

        Raises:
            Exception: If analysis fails or video is invalid
        """
        try:
            self.logger.info(f"Starting single video analysis for: {video_url}")
            
            # Create agentic analyzer
            shoplifting_analyzer = create_agentic_analyzer(
                detection_threshold=0.45,  # Default threshold
                logger=self.logger
            )
            
            # Analyze the video
            analysis_result = shoplifting_analyzer.analyze_video_from_bucket(
                video_url,
                iterations=3,  # Default iterations
                pickle_analysis=False  # Don't save pickle for API calls
            )
            
            # Extract required fields from analysis result
            result = AnalysisResultDTO(
                video_url=video_url,
                final_confidence=analysis_result.get("final_confidence", 0.0),
                final_detection=str(analysis_result.get("final_detection", False)),
                decision_reasoning=analysis_result.get("decision_reasoning", "No reasoning provided"),
                iteration_results=analysis_result.get("iteration_results", [])  # Include iteration data
            )
            
            self.logger.info(f"Single video analysis completed for: {video_url}")
            self.logger.info(f"Result: detected={result.final_detection}, confidence={result.final_confidence:.3f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze video {video_url}: {str(e)}")
            raise Exception(f"Video analysis failed: {str(e)}")

