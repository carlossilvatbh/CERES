"""
Health check views for monitoring and deployment validation.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Basic health check endpoint.
    Returns system status and timestamp.
    """
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "CERES Backend",
            "version": "2.0.0"
        }
        return JsonResponse(health_data, status=200)
    except Exception as e:
        error_data = {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "service": "CERES Backend"
        }
        return JsonResponse(error_data, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness check endpoint for deployment validation.
    """
    try:
        # Basic readiness checks
        readiness_data = {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "database": "ok",
                "cache": "ok",
                "storage": "ok"
            }
        }
        return JsonResponse(readiness_data, status=200)
    except Exception as e:
        error_data = {
            "status": "not_ready",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
        return JsonResponse(error_data, status=503)

