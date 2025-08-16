"""
Video analysis Celery tasks for Guardify-AI.

This module contains Celery tasks for processing video analysis asynchronously.
"""

import os
import sys
from typing import Dict, Any
from celery import current_task

# BULLETPROOF PATH SETUP
# Use hardcoded absolute path to ensure it works
PROJECT_ROOT = r"C:\Users\asafl\PycharmProjects\Guardify-AI"
BACKEND_PATH = r"C:\Users\asafl\PycharmProjects\Guardify-AI\backend"

# Force add to sys.path using insert(0) to put them first
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, BACKEND_PATH) 

# Debug: Print what we actually added
print(f"[CELERY-DEBUG] Added PROJECT_ROOT to sys.path: {PROJECT_ROOT}")
print(f"[CELERY-DEBUG] Added BACKEND_PATH to sys.path: {BACKEND_PATH}")
print(f"[CELERY-DEBUG] First 5 sys.path entries: {sys.path[:5]}")
print(f"[CELERY-DEBUG] PROJECT_ROOT exists: {os.path.exists(PROJECT_ROOT)}")
print(f"[CELERY-DEBUG] BACKEND_PATH exists: {os.path.exists(BACKEND_PATH)}")

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
        analysis_result = agentic_service.analyze_single_video(video_url)
        
        # Add context information to result
        analysis_result.update({
            "shop_id": shop_id,
            "camera_name": camera_name,
            "task_id": task_id
        })
        
        logger.info(
            f"[CELERY-TASK:{task_id}] Analysis completed for {video_url}: "
            f"detected={analysis_result['final_detection']}, "
            f"confidence={analysis_result['final_confidence']:.3f}"
        )
        
        # TODO: Store analysis results in database here in the future
        # For now, just log the results
        
        return analysis_result
        
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