"""
Video analysis Celery tasks for Guardify-AI.

This module contains Celery tasks for processing video analysis asynchronously.
"""
from typing import Optional, List, TypedDict
from celery import current_task

from backend.celery_app import celery_app
from backend.services.agentic_service import AgenticService
from backend.services.shops_service import ShopsService
from backend.services.events_service import EventsService
from backend.app.request_bodies.event_request_body import EventRequestBody
from backend.app.request_bodies.analysis_request_body import AnalysisRequestBody
from backend.db import db
from backend.services.event_description_service import EventDescriptionService
from utils.logger_utils import create_logger

# Create task-specific logger
logger = create_logger("CeleryAnalysisTasks", "celery_analysis.log")


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
    iteration_results: Optional[List[dict]]
    event_id: Optional[str]
    error: Optional[str]




def _store_analysis_results(task_id: str, analysis_result, video_url: str, shop_id: str, camera_name: str,
                            shops_service: ShopsService, task_result: AnalysisTaskResultDict) -> None:
    """
    Store analysis results in database using existing services.
    
    Args:
        task_id (str): Celery task ID for logging
        analysis_result: Analysis result object with final_confidence, final_detection, etc.
        video_url (str): Google Cloud Storage URI of the video
        shop_id (str): Shop ID for context
        camera_name (str): Name of the camera that recorded the video
        shops_service (ShopsService): Instance of shops service
        task_result (AnalysisTaskResultDict): Task result dictionary to update with event_id
        
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
    
    # Generate AI-powered event description from decision reasoning
    event_description_service = EventDescriptionService()
    detailed_description = event_description_service.generate_event_description(
        analysis_result.decision_reasoning or 'No reasoning provided'
    )
    
    logger.info(f"[CELERY-TASK:{task_id}] Generated AI event description: {detailed_description}")
    
    event_request = EventRequestBody(
        camera_id=camera.camera_id,  # Use the actual camera_id from the camera record
        description=detailed_description,  # Use summarized description for Event
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
    task_result["event_id"] = event_id
    
    logger.info(f"[CELERY-TASK:{task_id}] Successfully stored analysis results in database")


def _handle_task_error(self, task_id: str, video_url: str, shop_id: str, camera_name: str,
                       exc: Exception) -> AnalysisTaskResultDict:
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
        AnalysisTaskResultDict: Error result dictionary if not retrying
        
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
        return {
            "video_url": video_url,
            "final_confidence": 0.0,
            "final_detection": False,
            "decision_reasoning": f"Analysis failed (permanent error): {str(exc)}",
            "shop_id": shop_id,
            "camera_name": camera_name,
            "task_id": task_id
        }
    
    elif is_retryable and self.request.retries < self.max_retries:
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
        return {
            "video_url": video_url,
            "final_confidence": 0.0,
            "final_detection": False,
            "decision_reasoning": f"Analysis failed (max retries exceeded): {str(exc)}",
            "shop_id": shop_id,
            "camera_name": camera_name,
            "task_id": task_id
        }


@celery_app.task(bind=True, name='analyze_video')
def analyze_video(self,
                  camera_name: str,
                  video_url: str,
                  shop_id: str,
                  detection_threshold: float = 0.8,
                  iterations: int = 1) -> AnalysisTaskResultDict:
    """
    Analyze uploaded video using agentic AI strategy.
    
    This task performs asynchronous video analysis with automatic retry logic
    for transient failures and proper error handling.
    
    Args:
        camera_name (str): Name of the camera that recorded the video
        video_url (str): Google Cloud Storage URI of the video to analyze
        shop_id (str): Shop ID for context
        detection_threshold (float): Threshold for shoplifting detection (default: 0.8)
        iterations (int): Number of analysis iterations (default: 1)

    Returns:
        AnalysisTaskResultDict: Typed analysis result dictionary containing
            video_url, final_confidence, final_detection, decision_reasoning,
            shop_id, camera_name, task_id, and optionally iteration_results, event_id, error
            
    Raises:
        Retry: If analysis fails due to transient issues
    """
    task_id = self.request.id

    try:
        logger.info(
            f"[CELERY-TASK:{task_id}] Starting video analysis for camera '{camera_name}' in shop '{shop_id}': {video_url}")
        logger.info(
            f"[CELERY-TASK:{task_id}] Analysis parameters: threshold={detection_threshold}, iterations={iterations}")

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
            return {
                "video_url": video_url,
                "final_confidence": 0.0,
                "final_detection": False,
                "decision_reasoning": f"Shop verification failed: {str(shop_error)}",
                "shop_id": shop_id,
                "camera_name": camera_name,
                "task_id": task_id
            }

        # Perform video analysis with the passed parameters
        analysis_result = agentic_service.analyze_single_video(
            video_url,
            detection_threshold=detection_threshold,
            iterations=iterations
        )
        
        # Create structured task result with proper type conversion
        # Convert final_detection from string to boolean (agentic service returns string)
        final_detection_bool = analysis_result.final_detection.lower() == 'true'
        
        task_result: AnalysisTaskResultDict = {
            "video_url": analysis_result.video_url,
            "final_confidence": analysis_result.final_confidence,
            "final_detection": final_detection_bool,
            "decision_reasoning": analysis_result.decision_reasoning,
            "shop_id": shop_id,
            "camera_name": camera_name,
            "task_id": task_id
        }
        
        if analysis_result.iteration_results is not None:
            task_result["iteration_results"] = analysis_result.iteration_results
        
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
        
        return task_result
        
    except Exception as exc:
        return _handle_task_error(self, task_id, video_url, shop_id, camera_name, exc)


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