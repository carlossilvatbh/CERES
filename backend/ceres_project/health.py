from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import os

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for monitoring"""
    return JsonResponse({
        "status": "healthy",
        "timestamp": timezone.now().isoformat(),
        "version": "2.0.0",
        "environment": os.environ.get("DJANGO_ENVIRONMENT", "unknown"),
        "debug": os.environ.get("DEBUG", "False")
    })
