from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import json
import datetime


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for monitoring system status
    """
    status = "healthy"
    checks = {}
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        status = "unhealthy"
    
    # Cache check
    try:
        cache.set("health_check", "test", 30)
        if cache.get("health_check") == "test":
            checks["cache"] = "connected"
        else:
            checks["cache"] = "error: cache not working"
            status = "unhealthy"
    except Exception as e:
        checks["cache"] = f"error: {str(e)}"
        status = "unhealthy"
    
    # Environment check
    environment = "production"
    if settings.DEBUG:
        environment = "development"
    
    response_data = {
        "status": status,
        "service": "CERES Backend API",
        "version": "1.0.0",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "environment": environment,
        "checks": checks
    }
    
    status_code = 200 if status == "healthy" else 503
    return JsonResponse(response_data, status=status_code)


@csrf_exempt
@require_http_methods(["GET"])
def api_info(request):
    """
    API information endpoint
    """
    return JsonResponse({
        "name": "CERES API",
        "description": "Customer Enrollment and Risk Evaluation System",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/api/docs/",
            "redoc": "/api/redoc/",
            "schema": "/api/schema/"
        },
        "endpoints": {
            "authentication": "/api/auth/",
            "customers": "/api/v1/customers/",
            "documents": "/api/v1/documents/",
            "screening": "/api/v1/screening/",
            "risk": "/api/v1/risk/",
            "cases": "/api/v1/cases/",
            "users": "/api/v1/users/"
        }
    })

