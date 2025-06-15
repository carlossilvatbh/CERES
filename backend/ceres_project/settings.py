"""
Django settings for CERES project.
This file determines which settings to use based on the environment.
"""

import os
from decouple import config

# Determine which settings to use based on environment
ENVIRONMENT = config('DJANGO_ENVIRONMENT', default='production')

if ENVIRONMENT == 'local':
    from .settings.local import *
elif ENVIRONMENT == 'production':
    from .settings.production import *
else:
    # Default to production settings for safety
    from .settings.production import *

