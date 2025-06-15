"""
Celery configuration for CERES project - Railway optimized
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

# Railway-optimized Celery configuration
app.conf.update(
    # Task routing
    task_routes={
        'sanctions_screening.*': {'queue': 'screening'},
        'document_processing.*': {'queue': 'documents'},
        'risk_assessment.*': {'queue': 'risk'},
        'case_management.*': {'queue': 'cases'},
    },
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Task execution
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes
    task_reject_on_worker_lost=True,
    
    # Result backend
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Error handling
    task_annotations={
        '*': {'rate_limit': '10/s'}
    },
)

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'update-screening-sources': {
        'task': 'sanctions_screening.tasks.update_screening_sources',
        'schedule': 3600.0,  # Run every hour
        'options': {'queue': 'screening'}
    },
    'process-pending-documents': {
        'task': 'document_processing.tasks.process_pending_documents',
        'schedule': 300.0,  # Run every 5 minutes
        'options': {'queue': 'documents'}
    },
    'cleanup-expired-sessions': {
        'task': 'customer_enrollment.tasks.cleanup_expired_sessions',
        'schedule': 86400.0,  # Run daily
        'options': {'queue': 'cases'}
    },
    'generate-compliance-reports': {
        'task': 'case_management.tasks.generate_compliance_reports',
        'schedule': 86400.0,  # Run daily
        'options': {'queue': 'cases'}
    },
    'health-check': {
        'task': 'ceres_project.tasks.health_check',
        'schedule': 60.0,  # Run every minute
        'options': {'queue': 'default'}
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

@app.task(bind=True, name='ceres_project.tasks.health_check')
def health_check(self):
    """Health check task for monitoring"""
    from django.utils import timezone
    return {'status': 'healthy', 'timestamp': str(timezone.now())}

# Error handling
@app.task(bind=True)
def handle_task_failure(self, task_id, error, traceback):
    """Handle task failures"""
    from django.core.mail import mail_admins
    mail_admins(
        f'Celery Task Failed: {task_id}',
        f'Error: {error}\nTraceback: {traceback}'
    )
