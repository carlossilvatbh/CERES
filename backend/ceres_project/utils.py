"""
CERES utility functions and custom exception handlers
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import uuid
import logging

logger = logging.getLogger('ceres')

def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error responses
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'success': False,
            'data': None,
            'meta': {
                'timestamp': datetime.now().isoformat(),
                'request_id': str(uuid.uuid4()),
                'version': '1.0'
            },
            'errors': []
        }
        
        if hasattr(response.data, 'items'):
            # Handle field-specific errors
            for field, messages in response.data.items():
                if isinstance(messages, list):
                    for message in messages:
                        custom_response_data['errors'].append({
                            'code': 'VALIDATION_ERROR',
                            'message': str(message),
                            'field': field,
                            'details': str(message)
                        })
                else:
                    custom_response_data['errors'].append({
                        'code': 'VALIDATION_ERROR',
                        'message': str(messages),
                        'field': field,
                        'details': str(messages)
                    })
        else:
            # Handle general errors
            custom_response_data['errors'].append({
                'code': 'GENERAL_ERROR',
                'message': str(response.data),
                'field': None,
                'details': str(response.data)
            })
        
        response.data = custom_response_data
        
        # Log the error
        logger.error(f"API Error: {exc}", extra={
            'request_id': custom_response_data['meta']['request_id'],
            'status_code': response.status_code,
            'exception': str(exc)
        })
    
    return response

def success_response(data=None, meta=None, status_code=status.HTTP_200_OK):
    """
    Generate a consistent success response
    """
    response_data = {
        'success': True,
        'data': data,
        'meta': {
            'timestamp': datetime.now().isoformat(),
            'request_id': str(uuid.uuid4()),
            'version': '1.0'
        },
        'errors': []
    }
    
    if meta:
        response_data['meta'].update(meta)
    
    return Response(response_data, status=status_code)

def paginated_response(data, paginator, request):
    """
    Generate a paginated response
    """
    return success_response(
        data=data,
        meta={
            'pagination': {
                'page': paginator.page.number,
                'per_page': paginator.per_page,
                'total': paginator.page.paginator.count,
                'total_pages': paginator.page.paginator.num_pages,
                'has_next': paginator.page.has_next(),
                'has_previous': paginator.page.has_previous(),
            }
        }
    )

