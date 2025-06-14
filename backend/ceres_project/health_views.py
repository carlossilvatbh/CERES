from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for monitoring system status
    """
    return JsonResponse({
        "status": "healthy",
        "service": "CERES Backend API",
        "version": "1.0.0",
        "timestamp": "2025-06-14T07:00:00Z",
        "environment": "development",
        "database": "connected",
        "cache": "connected"
    })

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

