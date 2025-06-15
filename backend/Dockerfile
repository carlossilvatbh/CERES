FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        pkg-config \
        python3-dev \
        gcc \
        libc6-dev \
        libffi-dev \
        libssl-dev \
        tesseract-ocr \
        libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p staticfiles media

# Collect static files (with fallback)
RUN python manage.py collectstatic --noinput || echo "Static files collection failed, continuing..."

EXPOSE 8000

CMD ["gunicorn", "ceres_project.wsgi:application", "--bind", "0.0.0.0:8000"]

