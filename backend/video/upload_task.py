"""
Upload task data structures for video processing.

This module defines type-safe data structures for video upload tasks,
replacing the confusing tuple-based approach.
"""

from dataclasses import dataclass
from typing import Optional, Union, Tuple


@dataclass
class UploadTask:
    """
    Represents a video upload task with all necessary context.
    
    This dataclass provides type safety and clear structure for upload tasks,
    replacing the previous tuple-based approach that was error-prone.
    """
    bucket_name: str
    camera_name: str
    shop_id: Optional[str] = None
    
    @classmethod
    def from_tuple(cls, task_data: Union[Tuple[str, str], Tuple[str, str, str], Tuple[str, str, Optional[str]]]) -> 'UploadTask':
        """
        Create UploadTask from tuple data for backward compatibility.
        
        This method handles the legacy tuple format gracefully while providing
        type safety and clear error messages.
        
        Args:
            task_data: Tuple containing (bucket_name, camera_name[, shop_id])
            
        Returns:
            UploadTask: Properly structured upload task
            
        Raises:
            ValueError: If tuple format is invalid
        """
        if len(task_data) == 2:
            bucket_name, camera_name = task_data
            shop_id = None
        elif len(task_data) == 3:
            bucket_name, camera_name, shop_id = task_data
        else:
            raise ValueError(
                f"Invalid task data format. Expected tuple of length 2 or 3, "
                f"got length {len(task_data)}: {task_data}"
            )
            
        return cls(
            bucket_name=bucket_name,
            camera_name=camera_name,
            shop_id=shop_id
        )
    
    def to_tuple(self) -> Tuple[str, str, Optional[str]]:
        """
        Convert UploadTask to tuple format for compatibility.
        
        Returns:
            Tuple containing (bucket_name, camera_name, shop_id)
        """
        return (self.bucket_name, self.camera_name, self.shop_id)
    
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