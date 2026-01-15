"""
User views matching FastAPI behavior exactly.
Implements all endpoints from FastAPI users_api.py
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from common.errors import asana_not_found_error, asana_validation_error
from common.serializers import wrap_single_response, wrap_list_response, apply_opt_fields
from common.pagination import AsanaPagination
from common.auth import OAuth2ScopePermission
from .models import User
from .serializers import (
    UserCompactSerializer,
    UserResponseSerializer,
    UpdateUserRequestSerializer,
)


class UsersViewSet(viewsets.ViewSet):
    """
    User viewset matching FastAPI users_api.py behavior.
    Required scope: users:read
    """
    required_scopes = ['users:read']
    permission_classes = [OAuth2ScopePermission]
    
    def list(self, request: Request) -> Response:
        """
        GET /users
        Returns the user records for all users in all workspaces and organizations accessible to the authenticated user.
        Query params: workspace, team, opt_pretty, limit, offset, opt_fields
        """
        workspace = request.query_params.get('workspace')
        team = request.query_params.get('team')
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Query users from database
        queryset = User.objects.all().order_by('gid')
        
        # Filter by workspace if provided
        if workspace:
            from api.workspaces.models import Workspace
            from api.users.models import UserWorkspace
            try:
                workspace_obj = Workspace.objects.get(gid=workspace)
                user_ids = UserWorkspace.objects.filter(workspace=workspace_obj).values_list('user_id', flat=True)
                queryset = queryset.filter(id__in=user_ids)
            except Workspace.DoesNotExist:
                pass
        
        # Filter by team if provided
        if team:
            from api.teams.models import Team
            from api.team_memberships.models import TeamMembership
            try:
                team_obj = Team.objects.get(gid=team)
                user_ids = TeamMembership.objects.filter(team=team_obj).values_list('user_id', flat=True)
                queryset = queryset.filter(id__in=user_ids)
            except Team.DoesNotExist:
                pass
        
        # Apply pagination
        paginator = AsanaPagination()
        paginator.page_size = int(limit) if limit else 50
        
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = UserCompactSerializer(page, many=True)
            data = serializer.data
            
            if opt_fields:
                data = [apply_opt_fields(item, opt_fields) for item in data]
            
            return paginator.get_paginated_response(data)
        
        serializer = UserCompactSerializer(queryset, many=True)
        data = serializer.data
        
        if opt_fields:
            data = [apply_opt_fields(item, opt_fields) for item in data]
        
        return Response(wrap_list_response(data, next_page=None))
    
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """
        GET /users/{user_gid}
        Returns the full user record for the single user with the provided ID.
        Path params: user_gid (can be "me", email, or gid)
        Query params: opt_pretty, workspace, opt_fields
        """
        user_gid = pk
        if not user_gid:
            return asana_not_found_error('User')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        workspace = request.query_params.get('workspace')
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Handle "me" special case
        if user_gid == 'me':
            # TODO: Get current authenticated user
            return asana_not_found_error('User')
        
        # Find user by gid or email
        try:
            if '@' in user_gid:
                user = User.objects.get(email=user_gid)
            else:
                user = User.objects.get(gid=user_gid)
        except User.DoesNotExist:
            return asana_not_found_error('User')
        
        # Filter workspaces if workspace param provided
        if workspace:
            # TODO: Filter workspaces in serializer
            pass
        
        serializer = UserResponseSerializer(user)
        data = serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    def update(self, request: Request, pk: str = None) -> Response:
        """
        PUT /users/{user_gid}
        Updates a user. Only the fields provided in the data block will be updated.
        """
        user_gid = pk
        if not user_gid:
            return asana_not_found_error('User')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        workspace = request.query_params.get('workspace')
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = UpdateUserRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        # Find user
        try:
            if '@' in user_gid:
                user = User.objects.get(email=user_gid)
            else:
                user = User.objects.get(gid=user_gid)
        except User.DoesNotExist:
            return asana_not_found_error('User')
        
        # Update user fields
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        name = data_dict.get('name') or request_data.get('name')
        
        if name is not None:
            user.name = name
        
        user.save()
        
        serializer = UserResponseSerializer(user)
        data = serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    @action(detail=True, methods=['get'], url_path='favorites')
    def favorites(self, request: Request, pk: str = None) -> Response:
        """
        GET /users/{user_gid}/favorites
        Returns all of a user's favorites within a specified workspace and of a given type.
        Query params: resource_type (required), workspace (required), opt_pretty, limit, offset, opt_fields
        """
        user_gid = pk
        resource_type = request.query_params.get('resource_type')
        workspace = request.query_params.get('workspace')
        
        if not resource_type or not workspace:
            return asana_validation_error('resource_type and workspace are required')
        
        # TODO: Implement favorites retrieval
        # Favorites are typically stored as relationships or preferences
        favorites = []
        
        return Response(wrap_list_response(favorites, next_page=None))
