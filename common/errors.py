"""
Asana-style error handling for Django REST Framework.

Matches FastAPI error response format exactly:
{
    "errors": [
        {
            "message": "...",
            "help": "...",
            "phrase": "..."  # Only for 500 errors
        }
    ]
}
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError
import traceback
import uuid


def asana_exception_handler(exc, context):
    """
    Custom exception handler that returns Asana-formatted error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If response is None, it's an unhandled exception
    if response is None:
        return _handle_unhandled_exception(exc, context)
    
    # Convert DRF response to Asana format
    errors = []
    
    if isinstance(response.data, dict):
        # Handle field errors
        if 'detail' in response.data:
            # Single error message
            errors.append({
                'message': str(response.data['detail']),
                'help': None,
                'phrase': None
            })
        else:
            # Field errors or multiple errors
            for field, messages in response.data.items():
                if isinstance(messages, list):
                    for message in messages:
                        errors.append({
                            'message': f"{field}: {message}",
                            'help': None,
                            'phrase': None
                        })
                else:
                    errors.append({
                        'message': f"{field}: {messages}",
                        'help': None,
                        'phrase': None
                    })
    elif isinstance(response.data, list):
        # List of errors
        for message in response.data:
            errors.append({
                'message': str(message),
                'help': None,
                'phrase': None
            })
    else:
        # Single error
        errors.append({
            'message': str(response.data),
            'help': None,
            'phrase': None
        })
    
    # Add error phrase for 500 errors
    if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        error_phrase = _generate_error_phrase()
        for error in errors:
            error['phrase'] = error_phrase
    
    # Map status codes to match Asana behavior
    status_code = response.status_code
    if status_code == status.HTTP_401_UNAUTHORIZED:
        # Asana uses 401 for authentication errors
        pass
    elif status_code == status.HTTP_403_FORBIDDEN:
        # Asana uses 403 for authorization errors
        pass
    elif status_code == status.HTTP_404_NOT_FOUND:
        # Asana uses 404 for not found
        pass
    elif status_code == status.HTTP_400_BAD_REQUEST:
        # Asana uses 400 for bad requests
        pass
    
    return Response(
        {'errors': errors},
        status=status_code
    )


def _handle_unhandled_exception(exc, context):
    """
    Handle exceptions that DRF doesn't catch.
    """
    errors = [{
        'message': str(exc),
        'help': 'An unexpected error occurred. Please check the request format and try again.',
        'phrase': _generate_error_phrase()
    }]
    
    return Response(
        {'errors': errors},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def _generate_error_phrase() -> str:
    """
    Generate a unique error phrase for 500 errors.
    Similar to Asana's node-asana-phrase library.
    """
    # Simple implementation - in production, use a proper phrase generator
    import random
    adjectives = ['swift', 'calm', 'bright', 'quiet', 'bold', 'gentle']
    nouns = ['tiger', 'eagle', 'river', 'mountain', 'ocean', 'forest']
    return f"{random.choice(adjectives)}-{random.choice(nouns)}-{uuid.uuid4().hex[:8]}"


def asana_validation_error(message: str, help_text: str = None) -> Response:
    """
    Create an Asana-formatted validation error response.
    """
    errors = [{
        'message': message,
        'help': help_text,
        'phrase': None
    }]
    return Response(
        {'errors': errors},
        status=status.HTTP_400_BAD_REQUEST
    )


def asana_not_found_error(resource_type: str = "Resource") -> Response:
    """
    Create an Asana-formatted 404 error response.
    """
    errors = [{
        'message': f"{resource_type} not found",
        'help': 'The requested resource does not exist or you do not have access to it.',
        'phrase': None
    }]
    return Response(
        {'errors': errors},
        status=status.HTTP_404_NOT_FOUND
    )


def asana_unauthorized_error() -> Response:
    """
    Create an Asana-formatted 401 error response.
    """
    errors = [{
        'message': 'A valid authentication token was not provided with the request.',
        'help': 'Please provide a valid authentication token in the Authorization header.',
        'phrase': None
    }]
    return Response(
        {'errors': errors},
        status=status.HTTP_401_UNAUTHORIZED
    )


def asana_forbidden_error() -> Response:
    """
    Create an Asana-formatted 403 error response.
    """
    errors = [{
        'message': 'The authentication and request syntax was valid but the server is refusing to complete the request.',
        'help': 'You may not have access to the requested resource or action.',
        'phrase': None
    }]
    return Response(
        {'errors': errors},
        status=status.HTTP_403_FORBIDDEN
    )
