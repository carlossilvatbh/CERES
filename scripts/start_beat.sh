#!/bin/bash

# Start Celery Beat for Railway.app
echo "Starting Celery Beat..."

# Set environment variables
export DJANGO_SETTINGS_MODULE=ceres_project.settings
export C_FORCE_ROOT=1

# Start beat scheduler
cd /app/backend && celery -A ceres_project beat \
    --loglevel=info \
    --scheduler=django_celery_beat.schedulers:DatabaseScheduler

