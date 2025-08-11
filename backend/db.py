"""
Database instance for the Guardify application.
This module contains the SQLAlchemy instance that is shared across the application.
"""

from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance
db = SQLAlchemy()

def save_and_refresh(entity):
    """
    Add an entity to the database session, commit the transaction, and refresh the entity.
    
    Args:
        entity: The database entity to save
        
    Returns:
        The refreshed entity
        
    Raises:
        Exception: If there's an error during database operations
    """
    try:
        db.session.add(entity)
        db.session.commit()
        db.session.refresh(entity)
        return entity
    except Exception as e:
        db.session.rollback()
        raise e