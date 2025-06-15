# Railway Deployment Guide - CERES System

## Overview
This guide provides step-by-step instructions for deploying the CERES system on Railway.app with proper Celery workers and Redis configuration.

## Prerequisites
- Railway.app account
- GitHub repository access
- Redis add-on enabled on Railway

## Deployment Steps

### 1. Create Railway Project
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway new
```

### 2. Configure Environment Variables
Set the following environment variables in Railway dashboard:

```bash
# Django Core
SECRET_KEY=your-production-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=*.railway.app,yourdomain.com
DJANGO_SETTINGS_MODULE=ceres_project.settings

# CERES Specific
TESSERACT_CMD=/usr/bin/tesseract
POPPLER_PATH=/usr/bin
MEDIA_ROOT=/app/media
STATIC_ROOT=/app/staticfiles
```

### 3. Add Services
Railway will automatically detect the `railway.json` configuration and create:
- **Web Service**: Django application
- **Worker Service**: Celery worker
- **Beat Service**: Celery beat scheduler

### 4. Add Redis Database
1. Go to Railway dashboard
2. Click "Add Service" → "Database" → "Redis"
3. Railway will automatically set `REDIS_URL` environment variable

### 5. Add PostgreSQL Database
1. Go to Railway dashboard
2. Click "Add Service" → "Database" → "PostgreSQL"
3. Railway will automatically set `DATABASE_URL` environment variable

### 6. Deploy
```bash
# Connect to Railway project
railway link

# Deploy
railway up
```

## Service Configuration

### Web Service
- **Build Command**: Automatic (nixpacks.toml)
- **Start Command**: `cd backend && gunicorn ceres_project.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 30`
- **Port**: Automatic ($PORT)

### Worker Service
- **Build Command**: Automatic (nixpacks.toml)
- **Start Command**: `cd backend && celery -A ceres_project worker --loglevel=info --concurrency=2`
- **No Port Required**

### Beat Service
- **Build Command**: Automatic (nixpacks.toml)
- **Start Command**: `cd backend && celery -A ceres_project beat --loglevel=info`
- **No Port Required**

## Monitoring

### Health Checks
The system includes built-in health checks:
- Web: `/health/`
- Celery: Automatic health check task every minute

### Logs
Monitor logs for each service:
```bash
# Web service logs
railway logs --service=web

# Worker service logs
railway logs --service=worker

# Beat service logs
railway logs --service=beat
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify `DATABASE_URL` is set
   - Check PostgreSQL service is running

2. **Redis Connection Error**
   - Verify `REDIS_URL` is set
   - Check Redis service is running

3. **Celery Worker Not Starting**
   - Check worker service logs
   - Verify Redis connection
   - Ensure all dependencies are installed

4. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check `STATIC_ROOT` and `STATIC_URL` settings

### Performance Optimization

1. **Worker Scaling**
   - Increase worker concurrency for high load
   - Add more worker services if needed

2. **Database Optimization**
   - Enable connection pooling
   - Monitor query performance

3. **Redis Optimization**
   - Monitor memory usage
   - Configure appropriate eviction policies

## Security Considerations

1. **Environment Variables**
   - Use strong `SECRET_KEY`
   - Set `DEBUG=False` in production
   - Restrict `ALLOWED_HOSTS`

2. **Database Security**
   - Use Railway's managed databases
   - Enable SSL connections

3. **API Security**
   - Implement rate limiting
   - Use JWT authentication
   - Validate all inputs

## Maintenance

### Regular Tasks
1. Monitor system health
2. Update dependencies
3. Review logs for errors
4. Backup database regularly

### Updates
```bash
# Deploy updates
git push origin main
railway up
```

## Support
For issues with Railway deployment, check:
- Railway documentation
- CERES system logs
- GitHub issues

