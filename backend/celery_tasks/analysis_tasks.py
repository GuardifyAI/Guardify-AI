"""
Video analysis Celery tasks for Guardify-AI.

This module contains Celery tasks for processing video analysis asynchronously.
"""

import os
import sys
import uuid
from typing import Dict, Any
from celery import current_task

from backend.app.dtos.analysis_result_dto import AnalysisResultDTO

# BULLETPROOF PATH SETUP
# Use hardcoded absolute path to ensure it works
PROJECT_ROOT = r"C:\Users\asafl\PycharmProjects\Guardify-AI"
BACKEND_PATH = r"C:\Users\asafl\PycharmProjects\Guardify-AI\backend"

# Force add to sys.path using insert(0) to put them first
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, BACKEND_PATH)

# Test imports at module level to catch issues early
try:
    import backend
    print(f"[CELERY-DEBUG] Successfully imported backend module at module level")
except ImportError as e:
    print(f"[CELERY-DEBUG] Failed to import backend module at module level: {e}")

try:
    from backend.services import agentic_service
    print(f"[CELERY-DEBUG] Successfully imported agentic_service at module level")
except ImportError as e:
    print(f"[CELERY-DEBUG] Failed to import agentic_service at module level: {e}")

from backend.celery_app import celery_app
from utils.logger_utils import create_logger

# Create task-specific logger
logger = create_logger("CeleryAnalysisTasks", "celery_analysis.log")


@celery_app.task(bind=True, name='analyze_video')
def analyze_video(self, camera_name: str, video_url: str, shop_id: str) -> Dict[str, Any]:
    """
    Analyze uploaded video using agentic AI strategy.
    
    This task performs asynchronous video analysis with automatic retry logic
    for transient failures and proper error handling.
    
    Args:
        camera_name (str): Name of the camera that recorded the video
        video_url (str): Google Cloud Storage URI of the video to analyze
        shop_id (str): Shop ID for context
        
    Returns:
        Dict[str, Any]: Analysis result containing:
            - video_url: str
            - final_confidence: float
            - final_detection: str (True/False)
            - decision_reasoning: str
            - shop_id: str
            - camera_name: str
            - task_id: str
            
    Raises:
        Retry: If analysis fails due to transient issues
    """
    task_id = self.request.id

    try:
        logger.info(f"[CELERY-TASK:{task_id}] Starting video analysis for camera '{camera_name}' in shop '{shop_id}': {video_url}")

        # Debug: Log Python path
        logger.info(f"[CELERY-TASK:{task_id}] Python path first 5: {sys.path[:5]}")
        logger.info(f"[CELERY-TASK:{task_id}] Working directory: {os.getcwd()}")
        logger.info(f"[CELERY-TASK:{task_id}] PROJECT_ROOT in sys.path: {PROJECT_ROOT in sys.path}")
        logger.info(f"[CELERY-TASK:{task_id}] BACKEND_PATH in sys.path: {BACKEND_PATH in sys.path}")
        
        # Import services - now with Flask app context, database access will work
        logger.info(f"[CELERY-TASK:{task_id}] Importing services with Flask context...")
        from backend.services.agentic_service import AgenticService
        from backend.services.shops_service import ShopsService
        logger.info(f"[CELERY-TASK:{task_id}] Successfully imported services")
        
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
                "final_detection": "False",
                "decision_reasoning": f"Shop verification failed: {str(shop_error)}",
                "shop_id": shop_id,
                "camera_name": camera_name,
                "task_id": task_id,
                "error": str(shop_error)
            }
        
        # Perform video analysis
        logger.info(f"[CELERY-TASK:{task_id}] About to call analyze_single_video")
        
        analysis_result = agentic_service.analyze_single_video(video_url)

        logger.info(f"[CELERY-TASK:{task_id}] analyze_single_video returned: {type(analysis_result)}")
        
        # Add context information to result (convert to dict for return)
        result_dict = {
            "video_url": analysis_result.video_url,
            "final_confidence": analysis_result.final_confidence,
            "final_detection": analysis_result.final_detection,
            "decision_reasoning": analysis_result.decision_reasoning,
            "iteration_results": analysis_result.iteration_results,
            "shop_id": shop_id,
            "camera_name": camera_name,
            "task_id": task_id
        }
        
        logger.info(
            f"[CELERY-TASK:{task_id}] Analysis completed for {video_url}: "
            f"detected={analysis_result.final_detection}, "
            f"confidence={analysis_result.final_confidence:.3f}"
        )
        
        # Debug: Log analysis result structure
        try:
            logger.info(f"[CELERY-TASK:{task_id}] Analysis result type: {type(analysis_result)}")
            logger.info(f"[CELERY-TASK:{task_id}] ABOUT TO START DATABASE STORAGE")
        except Exception as debug_error:
            logger.error(f"[CELERY-TASK:{task_id}] Error in debug logging: {debug_error}")
            raise
        
        # Store analysis results in database using existing services
        try:
            logger.info(f"[CELERY-TASK:{task_id}] ENTERING DATABASE STORAGE SECTION")
            logger.info(f"[CELERY-TASK:{task_id}] Storing analysis results in database...")
            
            # Import services and request bodies
            from backend.services.events_service import EventsService
            from backend.app.request_bodies.event_request_body import EventRequestBody
            from backend.app.request_bodies.analysis_request_body import AnalysisRequestBody
            from backend.app.entities.camera import Camera
            from backend.db import db, save_and_refresh
            
            # Find or create camera record
            camera = Camera.query.filter_by(camera_name=camera_name, shop_id=shop_id).first()
            if not camera:
                logger.info(f"[CELERY-TASK:{task_id}] Creating new camera record for '{camera_name}' in shop '{shop_id}'")
                camera = Camera(
                    camera_id=str(uuid.uuid4()),
                    shop_id=shop_id,
                    camera_name=camera_name
                )
                save_and_refresh(camera)
                logger.info(f"[CELERY-TASK:{task_id}] Created camera: {camera.camera_id}")
            else:
                logger.info(f"[CELERY-TASK:{task_id}] Found existing camera: {camera.camera_id}")
            
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
            
            # Create Analysis using EventsService
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
            
            # Add event_id to result dict for reference
            result_dict['event_id'] = event_id
            
            logger.info(f"[CELERY-TASK:{task_id}] Successfully stored analysis results in database")
            
        except Exception as db_error:
            # Log database error but don't fail the entire analysis
            logger.error(f"[CELERY-TASK:{task_id}] Failed to store analysis results in database: {db_error}")
            logger.warning(f"[CELERY-TASK:{task_id}] Analysis results not persisted, but task will continue normally")
            # Rollback any partial database changes
            try:
                db.session.rollback()
            except Exception:
                pass
        
        return result_dict
        
    except Exception as exc:
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
                "final_detection": "False",
                "decision_reasoning": f"Analysis failed (permanent error): {str(exc)}",
                "shop_id": shop_id,
                "camera_name": camera_name,
                "task_id": task_id,
                "error": str(exc)
            }
        
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
            return {
                "video_url": video_url,
                "final_confidence": 0.0,
                "final_detection": "False",
                "decision_reasoning": f"Analysis failed (max retries exceeded): {str(exc)}",
                "shop_id": shop_id,
                "camera_name": camera_name,
                "task_id": task_id,
                "error": str(exc)
            }


@celery_app.task(name='health_check')
def health_check() -> Dict[str, str]:
    """
    Simple health check task to verify Celery is working.
    
    Returns:
        Dict[str, str]: Health status information
    """
    return {
        "status": "healthy",
        "message": "Celery is working correctly",
        "timestamp": str(current_task.request.id) if current_task else "unknown"
    }