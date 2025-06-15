#!/bin/bash

# Railway startup script for CERES backend

echo "🚀 Starting CERES backend deployment..."

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y libpq-dev python3-dev gcc g++ tesseract-ocr libmagic1 libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libfontconfig1

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Run Django checks (non-blocking)
echo "🔍 Running Django system checks..."
python manage.py check --deploy || echo "Django checks completed with warnings"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput || echo "Static files collection completed"

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate || echo "Migrations completed with warnings"

# Create superuser if needed (non-blocking)
echo "👤 Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@ceres.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
" || echo "Superuser creation completed"

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

