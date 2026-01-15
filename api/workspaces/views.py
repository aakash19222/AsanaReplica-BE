"""
Workspace views matching FastAPI behavior exactly.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from typing import Optional, List
import json

from common.errors import asana_not_found_error, asana_validation_error
from common.serializers import wrap_single_response, wrap_list_response, apply_opt_fields
from common.pagination import AsanaPagination
from common.auth import OAuth2ScopePermission
from .models import Workspace
from .serializers import (
    WorkspaceCompactSerializer,
    WorkspaceResponseSerializer,
    UpdateWorkspaceRequestSerializer,
    AddUserForWorkspaceRequestSerializer,
    RemoveUserForWorkspaceRequestSerializer,
)
from api.users.models import User, UserWorkspace
from api.users.serializers import UserResponseSerializer


class WorkspacesViewSet(viewsets.ViewSet):
    """
    Workspace viewset matching FastAPI workspaces_api.py behavior.
    
    Required scope: workspaces:read
    """
    required_scopes = ['workspaces:read']
    permission_classes = [OAuth2ScopePermission]
    
    def list(self, request: Request) -> Response:
        """
        GET /workspaces
        Returns the compact records for all workspaces visible to the authorized user.
        
        Query params:
        - opt_pretty: bool (optional)
        - limit: int (1-100, optional)
        - offset: str (optional)
        - opt_fields: List[str] (optional)
        """
        # Get query parameters
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Query workspaces from database
        queryset = Workspace.objects.all().order_by('name')
        
        # Apply pagination
        paginator = AsanaPagination()
        paginator.page_size = int(limit) if limit else 50
        paginator.max_page_size = 100
        
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = WorkspaceCompactSerializer(page, many=True)
            data = serializer.data
            
            # Apply opt_fields if specified
            if opt_fields:
                data = [apply_opt_fields(item, opt_fields) for item in data]
            
            return paginator.get_paginated_response(data)
        
        # Fallback if pagination not applied
        serializer = WorkspaceCompactSerializer(queryset, many=True)
        data = serializer.data
        
        if opt_fields:
            data = [apply_opt_fields(item, opt_fields) for item in data]
        
        return Response(wrap_list_response(data, next_page=None))
    
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """
        GET /workspaces/{workspace_gid}
        Returns the full workspace record for a single workspace.
        
        Path params:
        - workspace_gid: str (required)
        
        Query params:
        - opt_pretty: bool (optional)
        - opt_fields: List[str] (optional)
        """
        workspace_gid = pk
        
        if not workspace_gid:
            return asana_not_found_error('Workspace')
        
        # Get query parameters
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Query workspace from database
        try:
            workspace = Workspace.objects.get(gid=workspace_gid)
        except Workspace.DoesNotExist:
            return asana_not_found_error('Workspace')
        
        # Serialize workspace
        serializer = WorkspaceResponseSerializer(workspace)
        data = serializer.data
        
        # Apply opt_fields if specified
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        # Wrap in Asana response format
        return Response(wrap_single_response(data))
    
    def update(self, request: Request, pk: str = None) -> Response:
        """
        PUT /workspaces/{workspace_gid}
        Updates a workspace. Only the fields provided in the data block will be updated.
        
        Path params:
        - workspace_gid: str (required)
        
        Body:
        - UpdateWorkspaceRequest
        """
        workspace_gid = pk
        
        if not workspace_gid:
            return asana_not_found_error('Workspace')
        
        # Get query parameters
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = UpdateWorkspaceRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        # Get workspace from database
        try:
            workspace = Workspace.objects.get(gid=workspace_gid)
        except Workspace.DoesNotExist:
            return asana_not_found_error('Workspace')
        
        # Extract data from request
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        name = data_dict.get('name') or request_data.get('name')
        
        # Update workspace fields
        if name is not None:
            workspace.name = name
        
        workspace.save()
        
        # Serialize updated workspace
        response_serializer = WorkspaceResponseSerializer(workspace)
        data = response_serializer.data
        
        # Apply opt_fields if specified
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        # Wrap in Asana response format
        return Response(wrap_single_response(data))
    
    @action(detail=True, methods=['post'], url_path='addUser')
    def add_user(self, request: Request, pk: str = None) -> Response:
        """
        POST /workspaces/{workspace_gid}/addUser
        Adds a user to a workspace or organization.
        
        Path params:
        - workspace_gid: str (required)
        
        Body:
        - AddUserForWorkspaceRequest
        """
        workspace_gid = pk
        
        if not workspace_gid:
            return asana_not_found_error('Workspace')
        
        # Get query parameters
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = AddUserForWorkspaceRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        # Get workspace
        try:
            workspace = Workspace.objects.get(gid=workspace_gid)
        except Workspace.DoesNotExist:
            return asana_not_found_error('Workspace')
        
        # Extract user identifier from request
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        user_identifier = data_dict.get('user') or request_data.get('user')
        
        if not user_identifier:
            return asana_validation_error('User identifier is required')
        
        # Find user by gid or email
        try:
            if '@' in user_identifier:
                user = User.objects.get(email=user_identifier)
            else:
                user = User.objects.get(gid=user_identifier)
        except User.DoesNotExist:
            return asana_not_found_error('User')
        
        # Add user to workspace (create UserWorkspace relationship)
        UserWorkspace.objects.get_or_create(user=user, workspace=workspace)
        
        # Serialize and return user
        user_serializer = UserResponseSerializer(user)
        data = user_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    @action(detail=True, methods=['post'], url_path='removeUser')
    def remove_user(self, request: Request, pk: str = None) -> Response:
        """
        POST /workspaces/{workspace_gid}/removeUser
        Removes a user from a workspace or organization.
        
        Path params:
        - workspace_gid: str (required)
        
        Body:
        - RemoveUserForWorkspaceRequest
        """
        workspace_gid = pk
        
        if not workspace_gid:
            return asana_not_found_error('Workspace')
        
        # Get query parameters
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        
        # Validate request body
        serializer = RemoveUserForWorkspaceRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        # Get workspace
        try:
            workspace = Workspace.objects.get(gid=workspace_gid)
        except Workspace.DoesNotExist:
            return asana_not_found_error('Workspace')
        
        # Extract user identifier from request
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        user_identifier = data_dict.get('user') or request_data.get('user')
        
        if not user_identifier:
            return asana_validation_error('User identifier is required')
        
        # Find user by gid or email
        try:
            if '@' in user_identifier:
                user = User.objects.get(email=user_identifier)
            else:
                user = User.objects.get(gid=user_identifier)
        except User.DoesNotExist:
            return asana_not_found_error('User')
        
        # Remove user from workspace
        UserWorkspace.objects.filter(user=user, workspace=workspace).delete()
        
        # Returns empty data record
        return Response({'data': {}})
    
    @action(detail=True, methods=['get'], url_path='events')
    def events(self, request: Request, pk: str = None) -> Response:
        """
        GET /workspaces/{workspace_gid}/events
        Returns the full record for all events that have occurred since the sync token was created.
        
        Path params:
        - workspace_gid: str (required)
        
        Query params:
        - opt_pretty: bool (optional)
        - sync: str (optional)
        """
        workspace_gid = pk
        
        if not workspace_gid:
            return asana_not_found_error('Workspace')
        
        # Get query parameters
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        sync = request.query_params.get('sync')
        
        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(gid=workspace_gid)
        except Workspace.DoesNotExist:
            return asana_not_found_error('Workspace')
        
        # Query events for this workspace
        from api.events.models import Event
        queryset = Event.objects.filter(
            resource__contains={'workspace': workspace_gid}
        ).order_by('-created_at')
        
        # TODO: Implement sync token logic for incremental updates
        # For now, return all events (limited to 1000 as per Asana spec)
        from api.events.serializers import EventResponseSerializer
        events = queryset[:1000]
        serializer = EventResponseSerializer(events, many=True)
        data = serializer.data
        
        # Determine if there are more events
        has_more = queryset.count() > 1000
        
        # Generate sync token (simplified - in production use proper token generation)
        import base64
        import json
        sync_token = base64.b64encode(json.dumps({'workspace': workspace_gid, 'count': len(events)}).encode()).decode() if not sync else sync
        
        return Response({
            'data': data,
            'has_more': has_more,
            'sync': sync_token
        })
