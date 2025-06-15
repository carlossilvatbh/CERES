"""
Celery configuration for CERES project.
Production-ready async task processing.
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ceres_project.settings')

app = Celery('ceres')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery configuration
app.conf.update(
    # Task routing
    task_routes={
        'sanctions_screening.tasks.*': {'queue': 'screening'},
        'document_processing.tasks.*': {'queue': 'documents'},
        'risk_assessment.tasks.*': {'queue': 'risk'},
        'case_management.tasks.*': {'queue': 'cases'},
    },
    
    # Task execution
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task result backend
    result_backend=settings.CELERY_RESULT_BACKEND,
    result_expires=3600,  # 1 hour
    
    # Task execution settings
    task_always_eager=False,
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_eager_result=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Security
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'update-screening-sources': {
            'task': 'sanctions_screening.tasks.update_screening_sources',
            'schedule': 3600.0,  # Every hour
        },
        'cleanup-old-results': {
            'task': 'core.tasks.cleanup_old_results',
            'schedule': 86400.0,  # Daily
        },
        'generate-daily-reports': {
            'task': 'case_management.tasks.generate_daily_reports',
            'schedule': 86400.0,  # Daily at midnight
        },
    },
)

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')

