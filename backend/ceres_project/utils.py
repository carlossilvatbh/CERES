"""
Utility functions for CERES project
"""
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

def success_response(data=None, message="Success", status_code=status.HTTP_200_OK, meta=None):
    """
    Standard success response format
    """
    response_data = {
        "success": True,
        "message": message,
        "data": data,
    }
    if meta is not None:
        response_data["meta"] = meta
    return Response(response_data, status=status_code)

def error_response(message="Error", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Standard error response format
    """
    response_data = {
        "success": False,
        "message": message,
        "errors": errors
    }
    return Response(response_data, status=status_code)

def paginated_response(queryset, serializer_class, request, message="Success"):
    """
    Standard paginated response format
    """
    paginator = PageNumberPagination()
    paginator.page_size = 20
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(paginated_queryset, many=True, context={'request': request})
    
    return paginator.get_paginated_response({
        "success": True,
        "message": message,
        "data": serializer.data
    })

def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    """
    from rest_framework.views import exception_handler
    
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            "success": False,
            "message": "An error occurred",
            "errors": response.data
        }
        response.data = custom_response_data
    
    return response

