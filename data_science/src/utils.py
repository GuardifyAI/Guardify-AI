import os
import logging
import base64
from dotenv import load_dotenv
import cv2
import pickle

# options for a strategy to run
UNIFIED_MODEL = "unified"
AGENTIC_MODEL = "agentic"


def create_logger(name: str, log_file: str) -> logging.Logger:
    """
    Create a logger that writes messages both to a log file and to the console.
    """
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(logs_dir, exist_ok=True)  # Create logs/ folder if missing

    log_path = os.path.join(logs_dir, log_file)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def load_env_variables():
    """
    Load environment variables from a .env file.
    """
    load_dotenv()


def encode_image_to_base64(image_source) -> str:
    """
    Encode an image to base64 string.

    Args:
        image_source: Either a file path (str) or image data (bytes)

    Returns:
        str: Base64 encoded image string
    """
    try:
        if isinstance(image_source, str):
            # Handle file path
            with open(image_source, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        elif isinstance(image_source, bytes):
            # Handle bytes data directly
            return base64.b64encode(image_source).decode('utf-8')
        else:
            raise ValueError(f"Unsupported image source type: {type(image_source)}")
    except Exception as e:
        raise Exception(f"Error encoding image: {str(e)}")


def restructure_analysis(analysis_text: str, video_name: str = None) -> dict:
    """
    Restructure the raw analysis text into a structured dictionary.
    """
    if not analysis_text or analysis_text.startswith("Error:"):
        return None

    # Initialize result structure
    result = {
        "sequence_name": video_name,
        "summary_of_video": "",
        "shoplifting_determination": "No",
        "confidence_level": "0%",
        "key_behaviors": []
    }

    # Split the analysis into sections
    sections = analysis_text.split("###")

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract section title and content
        parts = section.split(":", 1)
        if len(parts) != 2:
            continue

        title, content = parts[0].strip(), parts[1].strip()

        if "Summary of Current Batch" in title:
            result["summary_of_video"] = content
        elif "Shoplifting Determination" in title:
            result["shoplifting_determination"] = content.strip().split()[0]  # Take first word (Yes/No)
        elif "Confidence Level" in title:
            result["confidence_level"] = content.strip().split()[0]  # Take first word (XX%)
        elif "Key Behaviors Supporting Conclusion" in title:
            # Extract bullet points
            behaviors = [b.strip("- ").strip() for b in content.split("\n") if b.strip().startswith("-")]
            result["key_behaviors"] = behaviors

    return result


def get_video_extension(video_path_or_uri: str) -> str:
    """
    Extract the video extension from a file path or URI.
    
    Args:
        video_path_or_uri (str): The full path or URI of the video file
        
    Returns:
        str: The video extension without the dot (e.g., 'mp4', 'avi')
        
    Examples:
        get_video_extension('/path/to/video.mp4')
        'mp4'
        get_video_extension('gs://bucket/video.avi')
        'avi'
        get_video_extension('inalid_file')
        raises value error
    """
    extension = os.path.splitext(video_path_or_uri)[1].lower().lstrip('.')
    if not extension:
        raise ValueError(f"Invalid video path in: {video_path_or_uri}")
    return extension

def extract_frames(every_n_frames: int, video_path: str, output_folder: str) -> None:
    """
    Legacy method for local file extraction. Kept for backwards compatibility.
    """
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Cannot open video file: {video_path}")
        return

    frame_idx = 0
    saved_frame_idx = 0
    success, frame = cap.read()

    while success:
        if frame_idx % every_n_frames == 0:
            frame_filename = f"{saved_frame_idx}.png"
            frame_path = os.path.join(output_folder, frame_filename)
            cv2.imwrite(frame_path, frame)
            saved_frame_idx += 1

        frame_idx += 1
        success, frame = cap.read()

    cap.release()
    print(f"Frames extracted for video: {video_path}")


def extract_frames_for_all_videos_in_folder(
        every_n_frames: int,
        input_folder_path: str,
        output_folder_path: str,
) -> None:
    """
    Extracts frames from all mp4 and avi videos in the input folder.

    Args:
        every_n_frames (int): Number of frames to skip between extractions.
        input_folder_path (str): Path to the folder containing videos.
        output_folder_path (str): Path to the folder where frames will be saved.
    """
    # Get all .mp4 and .avi files in the input folder
    video_files = [
        f for f in os.listdir(input_folder_path)
        if f.lower().endswith(('.mp4', '.avi'))
    ]

    if not video_files:
        print("No video files found in the input folder.")
        return

    for video_file in video_files:
        video_name, _ = os.path.splitext(video_file)
        video_path = os.path.join(input_folder_path, video_file)
        output_subfolder = os.path.join(output_folder_path, video_name)

        print(f"Extracting frames from: {video_file}")
        extract_frames(every_n_frames, video_path, output_subfolder)

def load_pickle_object(pickle_path: str):
    """
    Load and return a Python object from a pickle file.

    Args:
        pickle_path: Path to the pickle file.

    Returns:
        The object stored in the pickle file.
    """
    with open(pickle_path, 'rb') as f:
        obj = pickle.load(f)
    return obj