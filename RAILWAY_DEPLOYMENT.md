# Railway.app Deployment Configuration
# This file contains Railway-specific settings for CERES deployment

# Railway automatically provides these environment variables:
# - DATABASE_URL (PostgreSQL connection string)
# - PORT (application port)
# - RAILWAY_ENVIRONMENT (production/staging)

# Required environment variables for Railway:
# - SECRET_KEY (Django secret key)
# - DEBUG (set to False for production)

# Optional environment variables:
# - ALLOWED_HOSTS (defaults to '*' for Railway compatibility)

# Railway deployment notes:
# 1. Root Directory should be set to "backend"
# 2. Build Command: pip install -r requirements.txt
# 3. Start Command: python manage.py migrate && python manage.py runserver 0.0.0.0:$PORT
# 4. PostgreSQL database will be automatically connected via DATABASE_URL

