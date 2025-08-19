"""
Video analysis Celery tasks for Guardify-AI.

This module contains Celery tasks for processing video analysis asynchronously.
"""
from typing import Optional, List, TypedDict
from celery import current_task
from dataclasses import dataclass

from backend.celery_app import celery_app
from backend.services.agentic_service import AgenticService
from backend.services.shops_service import ShopsService
from backend.services.events_service import EventsService
from backend.app.request_bodies.event_request_body import EventRequestBody
from backend.app.request_bodies.analysis_request_body import AnalysisRequestBody
from backend.db import db
from utils.logger_utils import create_logger

# Create task-specific logger
logger = create_logger("CeleryAnalysisTasks", "celery_analysis.log")


class StructuredObservations(TypedDict, total=False):
    """
    TypedDict for structured computer vision observations.
    
    Contains the organized results from computer vision analysis.
    """
    person_count: str
    primary_actions: str
    object_interactions: str
    spatial_movement: str
    behavioral_patterns: str
    clothing_description: str
    environmental_context: str


class DetailedAnalysis(TypedDict, total=False):
    """
    TypedDict for detailed AI analysis results.
    
    Contains the structured output from the AI analysis model,
    including evidence assessment and behavioral observations.
    """
    evidence_tier: str
    key_behaviors: List[str]
    concealment_actions: List[str]
    movement_patterns: List[str]
    decision_reasoning: str
    observed_behavior: str  # For unified model
    reasoning: str  # For unified model


class AnalysisIteration(TypedDict):
    """
    TypedDict for a single analysis iteration result.
    
    Represents the detailed analysis from one iteration of the AI model,
    including computer vision observations and LLM analysis.
    """
    iteration: int
    cv_observations: str
    structured_observations: StructuredObservations
    analysis_response: str
    detected: bool
    confidence: float
    detailed_analysis: DetailedAnalysis
    timestamp: str


class AnalysisTaskResultDict(TypedDict, total=False):
    """
    TypedDict for analysis task result dictionary.
    
    This provides type safety for the dictionary format returned by Celery tasks,
    while allowing optional fields to be omitted.
    """
    video_url: str
    final_confidence: float
    final_detection: bool
    decision_reasoning: str
    shop_id: str
    camera_name: str
    task_id: str
    iteration_results: Optional[List[AnalysisIteration]]
    event_id: Optional[str]
    error: Optional[str]


@dataclass
class AnalysisTaskResult:
    """
    Standardized result type for video analysis tasks.
    
    This dataclass provides type safety for the analysis task return values,
    ensuring consistent structure across all analysis task responses.
    """
    video_url: str
    final_confidence: float
    final_detection: bool
    decision_reasoning: str
    shop_id: str
    camera_name: str
    task_id: str
    iteration_results: Optional[List[AnalysisIteration]] = None
    event_id: Optional[str] = None
    
    def to_dict(self) -> AnalysisTaskResultDict:
        """Convert to typed dictionary for Celery task return."""
        result: AnalysisTaskResultDict = {
            "video_url": self.video_url,
            "final_confidence": self.final_confidence,
            "final_detection": self.final_detection,
            "decision_reasoning": self.decision_reasoning,
            "shop_id": self.shop_id,
            "camera_name": self.camera_name,
            "task_id": self.task_id
        }
        
        if self.iteration_results is not None:
            result["iteration_results"] = self.iteration_results
        if self.event_id is not None:
            result["event_id"] = self.event_id
            
        return result


def _store_analysis_results(task_id: str, analysis_result, video_url: str, shop_id: str, camera_name: str, shops_service: ShopsService, task_result: AnalysisTaskResult) -> None:
    """
    Store analysis results in database using existing services.
    
    Args:
        task_id (str): Celery task ID for logging
        analysis_result: Analysis result object with final_confidence, final_detection, etc.
        video_url (str): Google Cloud Storage URI of the video
        shop_id (str): Shop ID for context
        camera_name (str): Name of the camera that recorded the video
        shops_service (ShopsService): Instance of shops service
        task_result (AnalysisTaskResult): Task result object to update with event_id
        
    Raises:
        Exception: If database storage fails
    """
    logger.info(f"[CELERY-TASK:{task_id}] Storing analysis results in database...")
    
    # Find or create camera record using shops_service helper
    logger.info(f"[CELERY-TASK:{task_id}] Finding or creating camera record for '{camera_name}' in shop '{shop_id}'")
    camera = shops_service.find_or_create_camera(shop_id, camera_name)
    logger.info(f"[CELERY-TASK:{task_id}] Camera resolved: {camera.camera_id}")
    
    # Create Event using ShopsService
    logger.info(f"[CELERY-TASK:{task_id}] Creating event record...")
    
    # Extract detailed reasoning from each iteration if available
    detailed_description = analysis_result.decision_reasoning or 'No reasoning provided'
    
    # Check if we have iteration_results with detailed analysis
    if analysis_result.iteration_results:
        iteration_reasonings = []
        for i, iteration in enumerate(analysis_result.iteration_results, 1):
            if 'detailed_analysis' in iteration and 'decision_reasoning' in iteration['detailed_analysis']:
                reasoning = iteration['detailed_analysis']['decision_reasoning']
                iteration_reasonings.append(f"Iteration {i}: {reasoning}")
        
        if iteration_reasonings:
            detailed_description = "\n\n".join(iteration_reasonings)
            logger.info(f"[CELERY-TASK:{task_id}] Using detailed iteration reasoning from {len(iteration_reasonings)} iterations")
    
    event_request = EventRequestBody(
        camera_id=camera.camera_id,  # Use the actual camera_id from the camera record
        description=detailed_description,  # Use detailed iteration reasoning
        video_url=video_url
    )
    
    event_dto = shops_service.create_shop_event(shop_id, event_request)
    event_id = event_dto.event_id
    logger.info(f"[CELERY-TASK:{task_id}] Created event: {event_id}")
    
    # Create Analysis using ShopsService helper
    logger.info(f"[CELERY-TASK:{task_id}] Creating analysis record for event: {event_id}")
    
    # Convert final_detection string to boolean
    final_detection_bool = analysis_result.final_detection.lower() == 'true' if isinstance(analysis_result.final_detection, str) else analysis_result.final_detection
    
    analysis_request = AnalysisRequestBody(
        final_detection=final_detection_bool,  # Pass boolean directly, not string
        final_confidence=float(analysis_result.final_confidence),
        decision_reasoning=analysis_result.decision_reasoning
    )
    
    events_service = EventsService()
    analysis_dto = events_service.create_event_analysis(event_id, analysis_request)
    logger.info(f"[CELERY-TASK:{task_id}] Created analysis record for event: {event_id}")
    
    # Add event_id to task result for reference
    task_result.event_id = event_id
    
    logger.info(f"[CELERY-TASK:{task_id}] Successfully stored analysis results in database")


def _handle_task_error(self, task_id: str, video_url: str, shop_id: str, camera_name: str, exc: Exception) -> AnalysisTaskResult:
    """
    Handle task errors and determine if retry is needed.
    
    Args:
        self: Celery task instance (for retry functionality)
        task_id (str): Celery task ID for logging
        video_url (str): Google Cloud Storage URI of the video
        shop_id (str): Shop ID for context
        camera_name (str): Name of the camera that recorded the video
        exc (Exception): The exception that occurred
        
    Returns:
        AnalysisTaskResult: Error result object if not retrying
        
    Raises:
        Retry: If error is retryable and max retries not exceeded
    """
    # Determine if this is a retryable error
    error_str = str(exc).lower()
    
    # Retryable errors (network, temporary service issues)
    retryable_errors = [
        'timeout', 'connection', 'network', 'temporary', 'service unavailable',
        'rate limit', '502', '503', '504', 'dns', 'ssl'
    ]
    
    # Non-retryable errors (permanent failures)
    permanent_errors = [
        'permission denied', '403', '404', 'file not found', 'not found',
        'invalid', 'malformed', 'authentication failed', '401'
    ]
    
    is_retryable = any(error in error_str for error in retryable_errors)
    is_permanent = any(error in error_str for error in permanent_errors)
    
    if is_permanent:
        logger.error(f"[CELERY-TASK:{task_id}] Permanent error analyzing {video_url}: {exc}")
        # Return error result instead of retrying
        return AnalysisTaskResult(
            video_url=video_url,
            final_confidence=0.0,
            final_detection=False,
            decision_reasoning=f"Analysis failed (permanent error): {str(exc)}",
            shop_id=shop_id,
            camera_name=camera_name,
            task_id=task_id
        )
    
    elif is_retryable or self.request.retries < self.max_retries:
        # Calculate exponential backoff
        countdown = min(300, (2 ** self.request.retries) * 60)  # Max 5 minutes
        
        logger.warning(
            f"[CELERY-TASK:{task_id}] Retryable error analyzing {video_url} "
            f"(attempt {self.request.retries + 1}/{self.max_retries + 1}): {exc}. "
            f"Retrying in {countdown} seconds..."
        )
        
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=countdown, max_retries=3)
    
    else:
        # Max retries exceeded
        logger.error(
            f"[CELERY-TASK:{task_id}] Max retries exceeded for {video_url}: {exc}"
        )
        return AnalysisTaskResult(
            video_url=video_url,
            final_confidence=0.0,
            final_detection=False,
            decision_reasoning=f"Analysis failed (max retries exceeded): {str(exc)}",
            shop_id=shop_id,
            camera_name=camera_name,
            task_id=task_id
        )


@celery_app.task(bind=True, name='analyze_video')
def analyze_video(self, camera_name: str, video_url: str, shop_id: str) -> AnalysisTaskResultDict:
    """
    Analyze uploaded video using agentic AI strategy.
    
    This task performs asynchronous video analysis with automatic retry logic
    for transient failures and proper error handling.
    
    Args:
        camera_name (str): Name of the camera that recorded the video
        video_url (str): Google Cloud Storage URI of the video to analyze
        shop_id (str): Shop ID for context
        
    Returns:
        AnalysisTaskResultDict: Typed analysis result dictionary containing
            video_url, final_confidence, final_detection, decision_reasoning,
            shop_id, camera_name, task_id, and optionally iteration_results, event_id, error
            
    Raises:
        Retry: If analysis fails due to transient issues
    """
    task_id = self.request.id

    try:
        logger.info(f"[CELERY-TASK:{task_id}] Starting video analysis for camera '{camera_name}' in shop '{shop_id}': {video_url}")

        # Initialize services (now running within Flask app context)
        shops_service = ShopsService()
        agentic_service = AgenticService(shops_service)
        logger.info(f"[CELERY-TASK:{task_id}] Services initialized successfully")
        
        # Verify shop exists (database access should work now)
        try:
            logger.info(f"[CELERY-TASK:{task_id}] Verifying shop '{shop_id}' exists...")
            shops_service.verify_shop_exists(shop_id)
            logger.info(f"[CELERY-TASK:{task_id}] Shop verification successful")
        except Exception as shop_error:
            logger.error(f"[CELERY-TASK:{task_id}] Shop verification failed for '{shop_id}': {shop_error}")
            # Don't retry for shop verification failures - likely a permanent error
            return AnalysisTaskResult(
                video_url=video_url,
                final_confidence=0.0,
                final_detection=False,
                decision_reasoning=f"Shop verification failed: {str(shop_error)}",
                shop_id=shop_id,
                camera_name=camera_name,
                task_id=task_id
            ).to_dict()
        
        # Perform video analysis
        analysis_result = agentic_service.analyze_single_video(video_url)
        
        # Create structured task result with proper type conversion
        # Convert final_detection from string to boolean (agentic service returns string)
        final_detection_bool = analysis_result.final_detection.lower() == 'true'
        
        task_result = AnalysisTaskResult(
            video_url=analysis_result.video_url,
            final_confidence=analysis_result.final_confidence,
            final_detection=final_detection_bool,
            decision_reasoning=analysis_result.decision_reasoning,
            shop_id=shop_id,
            camera_name=camera_name,
            task_id=task_id,
            iteration_results=analysis_result.iteration_results
        )
        
        logger.info(
            f"[CELERY-TASK:{task_id}] Analysis completed for {video_url}: "
            f"detected={analysis_result.final_detection}, "
            f"confidence={analysis_result.final_confidence:.3f}"
        )
        
        # Store analysis results in database using existing services
        try:
            _store_analysis_results(task_id, analysis_result, video_url, shop_id, camera_name, shops_service, task_result)
            
        except Exception as db_error:
            # Log database error but don't fail the entire analysis
            logger.error(f"[CELERY-TASK:{task_id}] Failed to store analysis results in database: {db_error}")
            logger.warning(f"[CELERY-TASK:{task_id}] Analysis results not persisted, but task will continue normally")
            # Rollback any partial database changes
            try:
                db.session.rollback()
            except Exception:
                pass
        
        return task_result.to_dict()
        
    except Exception as exc:
        return _handle_task_error(self, task_id, video_url, shop_id, camera_name, exc).to_dict()


class HealthCheckResult(TypedDict):
    """TypedDict for health check task result."""
    status: str
    message: str
    timestamp: str


@celery_app.task(name='health_check')
def health_check() -> HealthCheckResult:
    """
    Simple health check task to verify Celery is working.
    
    Returns:
        HealthCheckResult: Health status information with typed structure
    """
    return {
        "status": "healthy",
        "message": "Celery is working correctly",
        "timestamp": str(current_task.request.id) if current_task else "unknown"
    }