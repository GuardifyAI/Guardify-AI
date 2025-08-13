"""
Logging utilities for the Guardify-AI project.

This module provides standardized logging functionality that can be used
across all components of the project (backend, data science, etc.).
"""

import logging
from pathlib import Path


def create_logger(name: str, log_file: str, logs_dir: str = None) -> logging.Logger:
    """
    Create a logger that writes messages both to a log file and to the console.
    
    Args:
        name (str): Name of the logger
        log_file (str): Name of the log file
        logs_dir (str, optional): Directory to store logs. If None, creates 'logs' 
                                  directory in the project root.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Determine logs directory
    if logs_dir is None:
        # Use project root/logs as default
        project_root = Path(__file__).resolve().parent.parent
        logs_dir = project_root / 'logs'
    else:
        logs_dir = Path(logs_dir)
    
    # Create logs directory if it doesn't exist
    logs_dir.mkdir(exist_ok=True)
    
    log_path = logs_dir / log_file
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times if logger already exists
    if logger.handlers:
        return logger
        
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
