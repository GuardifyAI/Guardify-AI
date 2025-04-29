import os
import logging
import base64
from dotenv import load_dotenv


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
    file_handler = logging.FileHandler(log_path)
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
            # Clean and extract determination
            determination = content.strip().split()[0]  # Take first word (Yes/No)
            result["shoplifting_determination"] = determination.replace("*", "").strip()
        elif "Confidence Level" in title:
            # Clean and extract confidence
            confidence = content.strip().split()[0]  # Take first word (XX%)
            result["confidence_level"] = confidence.replace("*", "").strip()
        elif "Key Behaviors Supporting Conclusion" in title:
            # Extract bullet points and clean them
            behaviors = []
            current_behavior = None
            
            for line in content.split("\n"):
                line = line.strip()
                if not line:
                    continue
                    
                # Skip header lines (those with asterisks)
                if line.startswith("**") and line.endswith("**"):
                    continue
                # Skip header lines with colons
                if ":" in line and any(header in line.lower() for header in ["observed", "locations", "movements", "missing"]):
                    continue
                    
                # If it's a bullet point or we have text to add
                if line.startswith("-"):
                    if current_behavior:  # Store previous behavior if exists
                        behaviors.append(current_behavior)
                    current_behavior = line.strip("- ").strip()
                elif current_behavior:  # Continuation of previous behavior
                    current_behavior += " " + line
                else:  # New behavior without bullet point
                    current_behavior = line
            
            # Add the last behavior if exists
            if current_behavior:
                behaviors.append(current_behavior)
                
            # Remove any empty strings and clean asterisks
            behaviors = [b.replace("*", "").strip() for b in behaviors if b.strip()]
            result["key_behaviors"] = behaviors

    return result