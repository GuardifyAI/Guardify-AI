"""
Data science utilities package.

This package contains utility functions for data science operations
including summary generation and analysis helpers.
"""
import os

# Constants - copied from parent utils.py to avoid circular imports
UNIFIED_MODEL = "unified"
AGENTIC_MODEL = "agentic"


def get_video_extension(video_path_or_uri: str) -> str:
    """
    Extract the video extension from a file path or URI.
    
    Args:
        video_path_or_uri (str): The full path or URI of the video file
        
    Returns:
        str: The video extension without the dot (e.g., 'mp4', 'avi')
    """
    extension = os.path.splitext(video_path_or_uri)[1].lower().lstrip('.')
    if not extension:
        raise ValueError(f"Invalid video path in: {video_path_or_uri}")
    return extension