from django.urls import path
from . import health_views

urlpatterns = [
    path('', health_views.health_check, name='health_check'),
    path('info/', health_views.api_info, name='api_info'),
]

