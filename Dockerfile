# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV DJANGO_ENVIRONMENT=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy backend requirements and install
COPY backend/requirements-production.txt /app/
RUN pip install --no-cache-dir -r requirements-production.txt

# Copy backend code
COPY backend/ /app/

# Create directories
RUN mkdir -p /app/staticfiles /app/media

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health/ || exit 1

# Expose port
EXPOSE $PORT

# Start command
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn ceres_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60"]
