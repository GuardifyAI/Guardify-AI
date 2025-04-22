import os
import logging
import base64
import re
from typing import Dict
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


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to a base64 string.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def restructure_analysis(analysis_text: str) -> Dict[str, str]:
    """
    Parse the analysis text into a structured dictionary.
    """
    # Try to match both old and new summary section headers
    summary_match = re.search(r"### Summary of (?:Current Batch|Video):\s*(.*?)(?=\n###)", analysis_text, re.DOTALL | re.IGNORECASE)
    summary = summary_match.group(1).strip() if summary_match else ""

    # Get the connection to previous analysis if it exists
    connection_match = re.search(r"### Connection to Previous Analysis:\s*(.*?)(?=\n###)", analysis_text, re.DOTALL | re.IGNORECASE)
    if connection_match:
        connection = connection_match.group(1).strip()
        if summary:
            summary = summary + "\n\nConnection to Previous Analysis:\n" + connection

    conclusion_match = re.search(r"### Shoplifting Determination:\s*(Yes|No|Inconclusive)", analysis_text, re.IGNORECASE)
    conclusion = conclusion_match.group(1) if conclusion_match else "N/A"

    confidence_match = re.search(r"### Confidence Level:\s*(\d{1,3})%", analysis_text, re.IGNORECASE)
    confidence = f"{confidence_match.group(1)}%" if confidence_match else "N/A"

    behaviors_match = re.search(r"### Key Behaviors Supporting Conclusion:\s*(.*?)(?=\n###|$)", analysis_text, re.DOTALL | re.IGNORECASE)
    key_behaviors = behaviors_match.group(1).strip() if behaviors_match else "N/A"

    # Extract bullet points from behaviors if they exist
    behaviors_list = []
    if key_behaviors != "N/A":
        behaviors_list = [b.strip() for b in key_behaviors.split('\n') if b.strip().startswith('-')]
        key_behaviors = '\n'.join(behaviors_list) if behaviors_list else key_behaviors

    # Extract bullet points from summary if they exist
    summary_list = []
    if summary:
        summary_list = [s.strip() for s in summary.split('\n') if s.strip().startswith('-')]
        summary = '\n'.join(summary_list) if summary_list else summary

    return {
        "summary_of_video": summary if summary else "N/A",
        "shoplifting_determination": conclusion,
        "confidence_level": confidence,
        "key_behaviors": key_behaviors
    }