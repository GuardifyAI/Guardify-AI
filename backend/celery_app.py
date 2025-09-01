"""
Celery application configuration for Guardify-AI.

This module sets up the Celery application for handling asynchronous video analysis tasks.
"""

import os
from celery import Celery
from backend.app import create_app

def make_celery(app):
    """Create and configure Celery app with Flask application context."""
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    print(f"Using Redis URL: {redis_url}")  # Debug logging
    
    celery = Celery(
        app.import_name,
        broker=redis_url,
        backend=redis_url,
        include=['backend.celery_tasks.analysis_tasks']
    )
    
    # Update task base class to run within Flask app context
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Create Flask app and integrate with Celery
flask_app = create_app()
celery_app = make_celery(flask_app)

# Configure Celery settings
celery_app.conf.update(
    # Serialization settings
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    
    # Task routing
    task_routes={
        'analyze_video': {'queue': 'analysis'},
    },
    
    # Default retry settings
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Task execution settings
    task_soft_time_limit=1800,  # 30 minutes soft limit
    task_time_limit=2100,       # 35 minutes hard limit
    
    # Worker settings
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks to prevent memory leaks
    
    # Windows-specific settings to fix multiprocessing issues
    worker_pool='solo',  # Use single-threaded pool for Windows compatibility
    
    # Timezone
    timezone='UTC',
    enable_utc=True,
)

# Configure logging
celery_app.conf.update(
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
)

if __name__ == '__main__':
    celery_app.start()