"""
Environment utilities for the Guardify-AI project.

This module provides functionality for loading and managing environment variables
across all components of the project.
"""

from dotenv import load_dotenv


def load_env_variables():
    """
    Load environment variables from a .env file.
    
    This function loads environment variables from a .env file located in the
    project root directory.
    """
    load_dotenv()
