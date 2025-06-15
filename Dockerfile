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
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy production requirements and install Python dependencies
COPY backend/requirements-production.txt /app/
RUN pip install --no-cache-dir -r requirements-production.txt

# Copy project
COPY backend/ /app/

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "ceres_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "30"]

