"""
Celery utilities for task dispatch and availability checking.

This module provides common utilities for working with Celery tasks,
including availability checking and task dispatching functions.
"""
from typing import Optional
import logging
from backend.celery_tasks.analysis_tasks import analyze_video


def check_celery_availability(logger: logging.Logger) -> bool:
    """
    Check if Celery is available for task dispatch.
    
    Args:
        logger (logging.Logger): Logger instance for logging messages
        
    Returns:
        bool: True if Celery is available, False otherwise
    """
    try:
        logger.info("Celery tasks are available for video analysis")
        return True
    except ImportError as e:
        logger.warning(f"Celery tasks not available: {e}")
        return False
    except Exception as e:
        logger.error(f"Error checking Celery availability: {e}")
        return False


def dispatch_video_analysis_task(
    camera_name: str, 
    video_url: str, 
    shop_id: str,
    logger: logging.Logger
) -> Optional[str]:
    """
    Dispatch video analysis task using Celery.
    
    Args:
        camera_name (str): Name of the camera that recorded the video
        video_url (str): Google Cloud Storage URI of the video to analyze
        shop_id (str): Shop ID for context
        logger (logging.Logger): Logger instance for logging messages
        
    Returns:
        Optional[str]: Task ID if dispatch was successful, None otherwise
    """
    if not shop_id:
        logger.warning(f"No shop_id provided - skipping analysis for {video_url}")
        return None
        
    try:
        # Dispatch Celery task asynchronously
        task = analyze_video.delay(camera_name, video_url, shop_id)
        
        logger.info(
            f"Dispatched analysis task for camera '{camera_name}' (task_id: {task.id}): {video_url}"
        )
        
        return task.id
        
    except Exception as e:
        logger.error(f"Failed to dispatch analysis task for {video_url}: {e}")
        return None