"""
Settings module selector for CERES project
Automatically selects the appropriate settings based on environment
"""
import os
from decouple import config

# Determine which settings to use
ENVIRONMENT = config('DJANGO_ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'development':
    from .development import *
else:
    # Default to development
    from .development import *

# Override with any environment-specific settings
if 'RAILWAY_ENVIRONMENT' in os.environ:
    # We're on Railway, use production settings
    from .production import *

