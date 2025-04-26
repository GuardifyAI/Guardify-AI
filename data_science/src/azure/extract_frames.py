import os
import cv2
from typing import Optional
from data_science.src.azure.utils import create_logger
from tqdm import tqdm
import concurrent.futures

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

    def process_directory(self, input_dir, output_dir):
        """
        Process all video files in a directory and its subdirectories

        Args:
            input_dir: Directory containing video files
            output_dir: Base directory to save extracted frames
        """

        def rename_non_ascii_videos(directory):
            for filename in os.listdir(directory):
                old_path = os.path.join(directory, filename)
                if os.path.isfile(old_path):
                    # Check if filename starts with non-ASCII and rename
                    if not filename.isascii():
                        parts = filename.split('_', 1)
                        if len(parts) == 2:
                            new_filename = 'exit1_' + parts[1]
                            new_path = os.path.join(directory, new_filename)

                            # Check if target file already exists
                            if os.path.exists(new_path):
                                print(f"Skipped: {new_filename} already exists.")
                            else:
                                os.rename(old_path, new_path)
                                print(f"Renamed: {filename} -> {new_filename}")

        rename_non_ascii_videos(input_dir)

        os.makedirs(output_dir, exist_ok=True)
        video_files = []

        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith(tuple(self.ALLOWED_VIDEO_EXTENSIONS)):
                    video_path = os.path.join(root, file)
                    rel_path = os.path.relpath(root, input_dir)
                    sequence_name = os.path.basename(rel_path)
                    file_name = os.path.splitext(file)[0]

                    if rel_path == '.':
                        this_output_dir = os.path.join(output_dir, file_name)
                    else:
                        this_output_dir = os.path.join(output_dir, f"{sequence_name}_{file_name}")

                    video_files.append((video_path, this_output_dir))

        self.logger.info(f"Processing {len(video_files)} video files...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_video = {
                executor.submit(self.extract_frames, video_path, this_output_dir): (video_path, this_output_dir)
                for video_path, this_output_dir in video_files
            }

            total_frames = 0
            for future in tqdm(concurrent.futures.as_completed(future_to_video), total=len(video_files)):
                video_path, this_output_dir = future_to_video[future]
                try:
                    frames = future.result()
                    total_frames += frames
                    self.logger.info(f"Extracted {frames} frames from {os.path.basename(video_path)} to {this_output_dir}")
                except Exception as e:
                    self.logger.info(f"Error processing {video_path}: {e}")

        self.logger.info(f"Extraction complete. Total frames extracted: {total_frames}")
