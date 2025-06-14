"""
Celery configuration for CERES project
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

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'update-screening-sources': {
        'task': 'sanctions_screening.tasks.update_screening_sources',
        'schedule': 3600.0,  # Run every hour
    },
    'process-pending-documents': {
        'task': 'document_processing.tasks.process_pending_documents',
        'schedule': 300.0,  # Run every 5 minutes
    },
    'cleanup-expired-sessions': {
        'task': 'customer_enrollment.tasks.cleanup_expired_sessions',
        'schedule': 86400.0,  # Run daily
    },
    'generate-compliance-reports': {
        'task': 'case_management.tasks.generate_compliance_reports',
        'schedule': 86400.0,  # Run daily
    },
}

app.conf.timezone = 'America/Sao_Paulo'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

