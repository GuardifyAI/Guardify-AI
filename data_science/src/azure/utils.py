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


def load_env_variables():
    """
    Load environment variables from a .env file.
    """
    load_dotenv()


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
    summary_match = re.search(r"### Summary of Video:\s*(.*?)(?=\n### Shoplifting Determination:)", analysis_text, re.DOTALL | re.IGNORECASE)
    summary = summary_match.group(1).strip() if summary_match else "N/A"

    conclusion_match = re.search(r"### Shoplifting Determination:\s*(Yes|No|Inconclusive)", analysis_text, re.IGNORECASE)
    conclusion = conclusion_match.group(1) if conclusion_match else "N/A"

    confidence_match = re.search(r"### Confidence Level:\s*(\d{1,3})%", analysis_text, re.IGNORECASE)
    confidence = f"{confidence_match.group(1)}%" if confidence_match else "N/A"

    behaviors_match = re.search(r"### Key Behaviors Supporting Conclusion:\s*(.*)", analysis_text, re.DOTALL | re.IGNORECASE)
    key_behaviors = behaviors_match.group(1).strip() if behaviors_match else "N/A"

    return {
        "summary_of_video": summary,
        "conclusion": conclusion,
        "confidence_level": confidence,
        "key_behaviors": key_behaviors
    }