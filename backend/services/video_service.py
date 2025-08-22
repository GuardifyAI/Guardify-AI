import os
from google_client.google_client import GoogleClient


class VideoService:
    """Service for handling video-related operations including signed URL generation."""
    
    def __init__(self):
        """Initialize the VideoService with Google Cloud client."""
        self.google_client = GoogleClient(
            project=os.getenv("GOOGLE_PROJECT_ID"),
            location=os.getenv("GOOGLE_PROJECT_LOCATION"),
            service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
        )
    
    def get_signed_video_url(self, video_url: str, expiration_hours: int = 1) -> str:
        """
        Generate a signed URL for a GCS video URL.
        
        Args:
            video_url (str): The original GCS URL (gs://bucket/path/to/video.mp4)
            expiration_hours (int): How many hours the signed URL should be valid
            
        Returns:
            str: A signed URL that can be used to access the video directly
            
        Raises:
            ValueError: If the video_url is not a valid GCS URL
            Exception: If there's an error generating the signed URL
        """
        try:
            # Extract bucket and blob from the GCS URL
            bucket_name, blob_name = self.google_client.extract_bucket_and_blob_from_gs_url(video_url)
            
            # Generate and return the signed URL
            signed_url = self.google_client.generate_signed_url(
                bucket_name=bucket_name,
                blob_name=blob_name,
                expiration_hours=expiration_hours
            )
            
            return signed_url
            
        except ValueError as e:
            raise ValueError(f"Invalid video URL format: {e}")
        except Exception as e:
            raise Exception(f"Failed to generate signed URL: {e}")
