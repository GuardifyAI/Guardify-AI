import os
import cv2
from data_science.src.azure.utils import create_logger


class FrameExtractor:
    ALLOWED_VIDEO_EXTENSIONS = ['.avi', '.mp4', '.mov', '.mkv']

    def __init__(self, every_n_frames: int = 8, logger=None):
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

    def extract_frames(self, video_path: str, output_folder: str) -> None:
        """
        Extract frames from a video file and save them.

        Args:
            video_path (str): Path to the input video.
            output_folder (str): Directory to save the extracted frames.
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
