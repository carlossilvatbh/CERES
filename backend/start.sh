#!/bin/bash

# Railway startup script for CERES backend

echo "🚀 Starting CERES backend deployment..."

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y libpq-dev python3-dev gcc tesseract-ocr libmagic1

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Run Django checks
echo "🔍 Running Django system checks..."
python manage.py check --deploy

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Start the application
echo "✅ Starting Gunicorn server..."
exec gunicorn ceres_project.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class gthread \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --log-level info \
    --access-logfile - \
    --error-logfile -

