import os
import logging
import base64
from dotenv import load_dotenv


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
        >>> get_video_extension('/path/to/video.mp4')
        'mp4'
        >>> get_video_extension('gs://bucket/video.avi')
        'avi'
        >>> get_video_extension('inalid_file')
        raises value error
    """
    extension = os.path.splitext(video_path_or_uri)[1].lower().lstrip('.')
    if not extension:
        raise ValueError(f"Invalid video path in: {video_path_or_uri}")
    return extension