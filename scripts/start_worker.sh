#!/bin/bash

# Start Celery Worker for Railway.app
echo "Starting Celery Worker..."

# Set environment variables
export DJANGO_SETTINGS_MODULE=ceres_project.settings
export C_FORCE_ROOT=1

# Start worker with optimized settings for Railway
cd /app/backend && celery -A ceres_project worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=1000 \
    --time-limit=600 \
    --soft-time-limit=300 \
    --queues=default,screening,documents,risk,cases \
    --hostname=worker@%h

