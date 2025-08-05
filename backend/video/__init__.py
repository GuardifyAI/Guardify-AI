"""
Video Recording and Upload System

This package provides a modular video recording system that captures camera streams
from Provision ISR platform and uploads them to Google Cloud Storage.

Components:
    - VideoRecorder: Handles camera authentication and recording process
    - VideoUploader: Manages concurrent upload operations in background threads
    - main: Command-line interface and orchestration logic

Usage:
    # Command line usage
    python -m backend.video.main --camera "Camera Name" --duration 30
    
    # Programmatic usage
    from backend.video import VideoRecorder, VideoUploader
    from gcp_client.google_client import GoogleClient
    
    google_client = GoogleClient(project, location, service_account_path)
    uploader = VideoUploader(google_client)
    recorder = VideoRecorder(uploader)
"""

from backend.video.video_recorder import VideoRecorder
from backend.video.video_uploader import VideoUploader

__all__ = ['VideoRecorder', 'VideoUploader']
__version__ = '1.0.0'