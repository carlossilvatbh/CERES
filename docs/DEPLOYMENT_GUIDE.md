# CERES Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the CERES (Compliance and Risk Evaluation System) to Railway.app and other production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Railway.app Deployment](#railwayapp-deployment)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Redis Configuration](#redis-configuration)
6. [Celery Workers](#celery-workers)
7. [Static Files](#static-files)
8. [Domain Configuration](#domain-configuration)
9. [Monitoring Setup](#monitoring-setup)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying CERES, ensure you have:

- Railway.app account
- GitHub repository with CERES code
- Basic understanding of Django deployment
- Access to email service (optional, for notifications)

## Railway.app Deployment

### Step 1: Create Railway Project

1. Log in to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your CERES repository
5. Railway will automatically detect the Django application

### Step 2: Configure Services

CERES requires multiple services for full functionality:

#### Main Web Service
- **Service Name**: `web`
- **Build Command**: Automatic (uses nixpacks.toml)
- **Start Command**: `gunicorn ceres_project.wsgi:application --bind 0.0.0.0:$PORT`

#### PostgreSQL Database
1. Click "Add Service" → "Database" → "PostgreSQL"
2. Railway will automatically provision a PostgreSQL instance
3. Note the `DATABASE_URL` environment variable

#### Redis Cache
1. Click "Add Service" → "Database" → "Redis"
2. Railway will automatically provision a Redis instance
3. Note the `REDIS_URL` environment variable

#### Celery Worker (Optional but Recommended)
1. Click "Add Service" → "Empty Service"
2. Name it `worker`
3. Connect to the same GitHub repository
4. Set start command: `./scripts/start_worker.sh`

#### Celery Beat (Optional)
1. Click "Add Service" → "Empty Service"
2. Name it `beat`
3. Connect to the same GitHub repository
4. Set start command: `./scripts/start_beat.sh`

### Step 3: Environment Variables

Configure the following environment variables in Railway:

#### Required Variables
```bash
# Django Configuration
SECRET_KEY=your-super-secret-key-here
DEBUG=False
DJANGO_ENVIRONMENT=production
ALLOWED_HOSTS=.railway.app,.up.railway.app

# Database (automatically set by Railway)
DATABASE_URL=postgresql://user:password@host:port/database

# Redis (automatically set by Railway)
REDIS_URL=redis://host:port/database

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### Optional Variables
```bash
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@your-domain.com

# External APIs
OPENSANCTIONS_API_KEY=your-opensanctions-api-key

# Custom Domain
CUSTOM_DOMAIN=your-domain.com
FRONTEND_URL=https://your-frontend-domain.com

# Feature Flags
OCR_ENABLED=True
SCREENING_ENABLED=True
CACHE_ENABLED=True
ALERTS_ENABLED=True

# Performance Tuning
MAX_DOCUMENT_SIZE=52428800  # 50MB
DEFAULT_SCREENING_THRESHOLD=80
CACHE_TTL_SCREENING=86400   # 24 hours
CACHE_TTL_OCR=7200         # 2 hours

# Monitoring
HEALTH_CHECK_ENABLED=True
```

## Environment Configuration

### Development Environment

For local development, create a `.env` file:

```bash
# .env
DEBUG=True
SECRET_KEY=dev-secret-key
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/1
DJANGO_ENVIRONMENT=development

# Optional for testing
CELERY_TASK_ALWAYS_EAGER=True
```

### Production Environment

Production settings are automatically loaded when `RAILWAY_ENVIRONMENT` is detected or `DJANGO_ENVIRONMENT=production`.

## Database Setup

### Initial Migration

After deployment, run initial migrations:

1. Open Railway service terminal
2. Run migrations:
```bash
python manage.py migrate
```

3. Create superuser:
```bash
python manage.py createsuperuser
```

4. Collect static files:
```bash
python manage.py collectstatic --noinput
```

### Database Backup

Set up regular database backups:

```bash
# Create backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql $DATABASE_URL < backup_file.sql
```

## Redis Configuration

### Redis Memory Optimization

Configure Redis for optimal performance:

```bash
# Redis configuration (if using custom Redis)
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Redis Monitoring

Monitor Redis performance:

```bash
# Connect to Redis
redis-cli -u $REDIS_URL

# Check memory usage
INFO memory

# Monitor commands
MONITOR
```

## Celery Workers

### Worker Configuration

The Celery worker handles background tasks:

```bash
# scripts/start_worker.sh
#!/bin/bash
cd backend
celery -A ceres_project worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=1000 \
    --time-limit=300 \
    --soft-time-limit=240
```

### Beat Configuration

The Celery beat scheduler handles periodic tasks:

```bash
# scripts/start_beat.sh
#!/bin/bash
cd backend
celery -A ceres_project beat \
    --loglevel=info \
    --scheduler=django_celery_beat.schedulers:DatabaseScheduler
```

### Monitoring Celery

Monitor Celery workers:

```bash
# Check worker status
celery -A ceres_project inspect active

# Check scheduled tasks
celery -A ceres_project inspect scheduled

# Monitor in real-time
celery -A ceres_project events
```

## Static Files

### WhiteNoise Configuration

CERES uses WhiteNoise for serving static files in production:

```python
# settings/production.py
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... other middleware
]
```

### Collecting Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput

# Clear static files cache
python manage.py collectstatic --clear --noinput
```

## Domain Configuration

### Custom Domain Setup

1. In Railway dashboard, go to your service
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Update DNS records:
   - Add CNAME record pointing to Railway domain
   - Add A record if using root domain

5. Update environment variables:
```bash
CUSTOM_DOMAIN=your-domain.com
ALLOWED_HOSTS=your-domain.com,.railway.app
```

### SSL Certificate

Railway automatically provides SSL certificates for custom domains.

## Monitoring Setup

### Health Checks

CERES includes comprehensive health checks:

```bash
# Check application health
curl https://your-app.railway.app/health/

# Check specific components
curl https://your-app.railway.app/health/ | jq '.checks.database'
```

### Metrics Collection

Enable Prometheus metrics:

```bash
# Get metrics
curl https://your-app.railway.app/metrics/

# Monitor specific metrics
curl https://your-app.railway.app/metrics/ | grep ceres_cpu_usage
```

### Log Monitoring

Monitor application logs:

```bash
# Railway CLI
railway logs --service web

# Filter logs
railway logs --service web | grep ERROR

# Follow logs in real-time
railway logs --service web --follow
```

## Performance Optimization

### Database Optimization

```python
# settings/production.py
DATABASES = {
    'default': {
        # ... database config
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
        }
    }
}
```

### Cache Optimization

```python
# Optimize cache settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 20,
                'retry_on_timeout': True,
            },
        },
        'TIMEOUT': 3600,
    }
}
```

### Gunicorn Optimization

```bash
# Optimized Gunicorn command
gunicorn ceres_project.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class gevent \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --preload
```

## Security Configuration

### Production Security Settings

```python
# settings/production.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
```

### API Security

```python
# Rate limiting
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database connectivity
python manage.py dbshell

# Verify DATABASE_URL
echo $DATABASE_URL
```

#### 2. Redis Connection Errors
```bash
# Test Redis connection
redis-cli -u $REDIS_URL ping

# Check Redis memory
redis-cli -u $REDIS_URL info memory
```

#### 3. Static Files Not Loading
```bash
# Recollect static files
python manage.py collectstatic --clear --noinput

# Check STATIC_ROOT
python manage.py shell -c "from django.conf import settings; print(settings.STATIC_ROOT)"
```

#### 4. Celery Workers Not Starting
```bash
# Check worker logs
railway logs --service worker

# Test Celery connection
celery -A ceres_project inspect ping
```

#### 5. High Memory Usage
```bash
# Monitor memory usage
python manage.py shell -c "
import psutil
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'CPU: {psutil.cpu_percent()}%')
"
```

### Debug Mode

For debugging in production (use carefully):

```bash
# Temporarily enable debug
railway variables set DEBUG=True

# Check logs
railway logs --service web --follow

# Disable debug
railway variables set DEBUG=False
```

### Performance Debugging

```bash
# Check slow queries
python manage.py shell -c "
from django.db import connection
for query in connection.queries:
    if float(query['time']) > 0.1:
        print(f'Slow query: {query}')
"

# Monitor cache performance
python manage.py shell -c "
from core.cache_manager import cache_manager
print(cache_manager.get_cache_info())
"
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/tmp/backups"
mkdir -p $BACKUP_DIR
pg_dump $DATABASE_URL > $BACKUP_DIR/ceres_backup_$(date +%Y%m%d_%H%M%S).sql
```

### File Backup

```bash
# Backup uploaded files
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
    nixpacks.toml \
    railway.json \
    .env.railway \
    scripts/
```

### Recovery Procedure

1. **Database Recovery**:
```bash
# Restore database
psql $DATABASE_URL < backup_file.sql
```

2. **Application Recovery**:
```bash
# Redeploy from backup
git checkout backup-branch
git push origin main --force
```

3. **Verify Recovery**:
```bash
# Check health
curl https://your-app.railway.app/health/

# Test functionality
python manage.py test
```

## Scaling

### Horizontal Scaling

```bash
# Scale web workers
railway scale --service web --replicas 3

# Scale Celery workers
railway scale --service worker --replicas 2
```

### Vertical Scaling

```bash
# Increase memory/CPU
railway scale --service web --memory 1GB --cpu 1000m
```

### Database Scaling

```bash
# Upgrade PostgreSQL plan
railway database upgrade --plan pro

# Add read replicas (if supported)
railway database replica create
```

## Maintenance

### Regular Maintenance Tasks

```bash
# Weekly tasks
python manage.py clearsessions
python manage.py cleanup_old_alerts
python manage.py update_screening_sources

# Monthly tasks
python manage.py optimize_database
python manage.py cleanup_old_logs
python manage.py generate_monthly_reports
```

### Update Procedure

1. **Backup current deployment**
2. **Test updates in staging**
3. **Deploy to production**:
```bash
git push origin main
```
4. **Run migrations**:
```bash
python manage.py migrate
```
5. **Verify deployment**:
```bash
curl https://your-app.railway.app/health/
```

---

For additional support, contact the development team or refer to the [API Documentation](API_DOCUMENTATION.md).

