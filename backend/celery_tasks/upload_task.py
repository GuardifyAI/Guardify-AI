from dataclasses import dataclass
from typing import Optional


@dataclass
class UploadTask:
    """
    Represents a video upload task with all necessary context.
    
    This dataclass provides type safety and structure for the upload task data.
    This class is essential for the communication between the recorder and uploader components:
      - video_recorder.py creates UploadTask objects to queue uploads
      - video_uploader.py processes these UploadTask objects from the queue
    """
    bucket_name: str
    camera_name: str
    shop_id: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation for logging."""
        shop_info = f" (shop: {self.shop_id})" if self.shop_id else ""
        return f"UploadTask[{self.camera_name} -> {self.bucket_name}{shop_info}]"
    
    def validate(self) -> None:
        """
        Validate the upload task data.
        
        Raises:
            ValueError: If any required fields are invalid
        """
        if not self.bucket_name or not self.bucket_name.strip():
            raise ValueError("bucket_name cannot be empty")
            
        if not self.camera_name or not self.camera_name.strip():
            raise ValueError("camera_name cannot be empty")
            
        # Shop ID is optional, but if provided, should not be empty
        if self.shop_id is not None and not self.shop_id.strip():
            raise ValueError("shop_id cannot be empty string (use None instead)")