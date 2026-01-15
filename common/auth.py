"""
Asana-style authentication for Django REST Framework.

Supports:
1. Personal Access Token (Bearer token)
2. OAuth2 (Bearer token with scopes)

Matches FastAPI security_api.py behavior.
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser
import re


class PersonalAccessTokenAuthentication(BaseAuthentication):
    """
    Authenticate using Personal Access Token (Bearer token).
    
    Matches FastAPI get_token_personalAccessToken behavior.
    """
    def authenticate(self, request):
        """
        Authenticate the request using Bearer token.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        # Check for Bearer token
        match = re.match(r'^Bearer\s+(.+)$', auth_header)
        if not match:
            return None
        
        token = match.group(1)
        
        # TODO: Validate token against database or external service
        # For now, accept any non-empty token
        if not token:
            raise AuthenticationFailed('Invalid token')
        
        # TODO: Get user from token
        # For now, return a placeholder user
        # In production, you would:
        # 1. Look up token in database
        # 2. Get associated user
        # 3. Check token expiration
        
        return (None, token)  # (user, token)
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return 'Bearer'


class OAuth2Authentication(BaseAuthentication):
    """
    Authenticate using OAuth2 Bearer token with scope validation.
    
    Matches FastAPI get_token_oauth2 behavior.
    """
    def authenticate(self, request):
        """
        Authenticate the request using OAuth2 Bearer token.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        # Check for Bearer token
        match = re.match(r'^Bearer\s+(.+)$', auth_header)
        if not match:
            return None
        
        token = match.group(1)
        
        # TODO: Validate OAuth2 token
        # For now, accept any non-empty token
        if not token:
            raise AuthenticationFailed('Invalid token')
        
        # TODO: Validate token and extract scopes
        # In production, you would:
        # 1. Validate token with OAuth2 provider
        # 2. Extract scopes from token
        # 3. Store scopes in request for permission checking
        
        # Store token in request for scope checking
        request.auth_token = token
        request.auth_scopes = ['default']  # TODO: Extract from token
        
        return (None, token)  # (user, token)
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return 'Bearer'


class OAuth2ScopePermission(BasePermission):
    """
    Permission class to check OAuth2 scopes.
    
    Usage:
    permission_classes = [OAuth2ScopePermission]
    required_scopes = ['workspaces:read']
    """
    def has_permission(self, request, view):
        """
        Check if the request has the required OAuth2 scopes.
        """
        # If not using OAuth2, allow (fall back to other auth)
        if not hasattr(request, 'auth_scopes'):
            return True
        
        # Get required scopes from view
        required_scopes = getattr(view, 'required_scopes', [])
        if not required_scopes:
            return True
        
        # Check if any required scope is present
        user_scopes = getattr(request, 'auth_scopes', [])
        
        # 'default' scope grants access to all endpoints
        if 'default' in user_scopes:
            return True
        
        # Check if any required scope matches
        for scope in required_scopes:
            if scope in user_scopes:
                return True
        
        return False


def get_required_scopes(view_class):
    """
    Extract required scopes from view class.
    Can be set as a class attribute or method.
    """
    if hasattr(view_class, 'required_scopes'):
        return view_class.required_scopes
    return []
