"""
Database instance for the Guardify application.
This module contains the SQLAlchemy instance that is shared across the application.
"""

from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance
db = SQLAlchemy()
