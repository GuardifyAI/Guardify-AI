import os
import cv2
import tempfile
from io import BytesIO
from data_science.src.azure.utils import create_logger


class FrameExtractor:
    ALLOWED_VIDEO_EXTENSIONS = ['.avi', '.mp4', '.mov', '.mkv']

    def __init__(self, every_n_frames, logger=None):
        """
        Initialize the FrameExtractor.

        Args:
            every_n_frames (int): Extract one frame every N frames.
            logger (logging.Logger, optional): Logger instance.
        """
        self.every_n_frames = every_n_frames
        self.logger = logger or create_logger("FrameExtractor", "extract_frames.log")

    def is_valid_video_file(self, filename: str) -> bool:
        """
        Check if a file is a valid video based on its extension.

        Args:
            filename (str): Name of the file.

        Returns:
            bool: True if valid video file, else False.
        """
        return any(filename.lower().endswith(ext) for ext in self.ALLOWED_VIDEO_EXTENSIONS)

    def extract_frames_from_stream(self, video_stream: bytes, blob_helper, frames_container: str, video_name: str) -> None:
        """
        Extract frames from a video stream and upload them directly to Azure blob storage.

        Args:
            video_stream (bytes): Video data as bytes
            blob_helper: AzureBlobHelper instance
            frames_container (str): Azure container name for frames
            video_name (str): Name of the video (used for frame naming)
        """
        temp_video = None
        cap = None
        try:
            # Create a temporary file to store the video
            temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_path = temp_video.name
            
            # Write video stream to temporary file
            temp_video.write(video_stream)
            temp_video.flush()
            temp_video.close()  # Close the file handle explicitly
            
            # Open video with OpenCV
            cap = cv2.VideoCapture(temp_path)
            
            if not cap.isOpened():
                self.logger.error(f"Cannot open video stream for: {video_name}")
                return

            frame_idx = 0
            success, frame = cap.read()

            while success:
                if frame_idx % self.every_n_frames == 0:
                    # Convert frame to bytes
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = BytesIO(buffer.tobytes())
                    
                    # Upload frame directly to Azure
                    frame_blob_path = f"{video_name}/frame_{frame_idx:04d}.jpg"
                    blob_helper.upload_bytes_as_blob(frames_container, frame_bytes.getvalue(), frame_blob_path)

                frame_idx += 1
                success, frame = cap.read()

            self.logger.info(f"Frames extracted and uploaded for video: {video_name}")
            
        except Exception as e:
            self.logger.error(f"Error processing video {video_name}: {str(e)}")
            raise
            
        finally:
            # Clean up resources
            if cap is not None:
                cap.release()
                
            # Clean up the temporary file
            try:
                if temp_video is not None:
                    # Add a small delay to ensure file handles are released
                    import time
                    time.sleep(0.1)
                    os.unlink(temp_path)
            except Exception as e:
                self.logger.warning(f"Error deleting temporary file: {str(e)}")

    def extract_frames(self, video_path: str, output_folder: str) -> None:
        """
        Legacy method for local file extraction. Kept for backwards compatibility.
        """
        os.makedirs(output_folder, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.logger.error(f"Cannot open video file: {video_path}")
            return

        frame_idx = 0
        success, frame = cap.read()

        while success:
            if frame_idx % self.every_n_frames == 0:
                frame_filename = f"frame_{frame_idx:04d}.jpg"
                frame_path = os.path.join(output_folder, frame_filename)
                cv2.imwrite(frame_path, frame)

            frame_idx += 1
            success, frame = cap.read()

        cap.release()
        self.logger.info(f"Frames extracted for video: {video_path}")
