"""
Team views matching FastAPI behavior exactly.
Implements all team endpoints from FastAPI teams_api.py
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from common.errors import asana_not_found_error, asana_validation_error
from common.serializers import wrap_single_response, wrap_list_response, apply_opt_fields
from common.pagination import AsanaPagination
from common.auth import OAuth2ScopePermission
from .models import Team
from .serializers import (
    TeamCompactSerializer,
    TeamResponseSerializer,
    CreateTeamRequestSerializer,
    AddUserForTeamRequestSerializer,
    RemoveUserForTeamRequestSerializer,
)
from api.workspaces.models import Workspace
from api.users.models import User
from api.team_memberships.models import TeamMembership


class TeamsViewSet(viewsets.ViewSet):
    """
    Team viewset matching FastAPI teams_api.py behavior.
    Required scope: teams:read
    """
    required_scopes = ['teams:read']
    permission_classes = [OAuth2ScopePermission]
    
    def create(self, request: Request) -> Response:
        """
        POST /teams
        Creates a team within the current workspace.
        """
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = CreateTeamRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        
        # Extract fields
        name = data_dict.get('name') or request_data.get('name')
        organization_gid = data_dict.get('organization') or request_data.get('organization')
        description = data_dict.get('description') or request_data.get('description')
        
        if not name:
            return asana_validation_error('Team name is required')
        
        if not organization_gid:
            return asana_validation_error('Organization is required')
        
        # Get workspace/organization
        try:
            organization = Workspace.objects.get(gid=organization_gid)
        except Workspace.DoesNotExist:
            return asana_not_found_error('Organization')
        
        # Create team
        team = Team.objects.create(
            name=name,
            organization=organization,
            description=description
        )
        
        # Serialize and return
        response_serializer = TeamResponseSerializer(team)
        data = response_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data), status=201)
    
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """
        GET /teams/{team_gid}
        Returns the complete record for a single team.
        """
        team_gid = pk
        if not team_gid:
            return asana_not_found_error('Team')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        try:
            team = Team.objects.get(gid=team_gid)
        except Team.DoesNotExist:
            return asana_not_found_error('Team')
        
        serializer = TeamResponseSerializer(team)
        data = serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    def update(self, request: Request, pk: str = None) -> Response:
        """
        PUT /teams/{team_gid}
        Updates a team. Only the fields provided in the data block will be updated.
        """
        team_gid = pk
        if not team_gid:
            return asana_not_found_error('Team')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = CreateTeamRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        try:
            team = Team.objects.get(gid=team_gid)
        except Team.DoesNotExist:
            return asana_not_found_error('Team')
        
        # Update team fields
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        
        if 'name' in data_dict:
            team.name = data_dict['name']
        if 'description' in data_dict:
            team.description = data_dict['description']
        
        team.save()
        
        response_serializer = TeamResponseSerializer(team)
        data = response_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    @action(detail=False, methods=['get'], url_path='workspaces/(?P<workspace_gid>[^/.]+)/teams')
    def get_teams_for_workspace(self, request: Request, workspace_gid: str = None) -> Response:
        """
        GET /workspaces/{workspace_gid}/teams
        Returns the compact records for all teams in the workspace visible to the authorized user.
        """
        if not workspace_gid:
            return asana_not_found_error('Workspace')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(gid=workspace_gid)
        except Workspace.DoesNotExist:
            return asana_not_found_error('Workspace')
        
        # Query teams for this workspace
        queryset = Team.objects.filter(organization=workspace).order_by('name')
        
        # Apply pagination
        paginator = AsanaPagination()
        paginator.page_size = int(limit) if limit else 50
        
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = TeamCompactSerializer(page, many=True)
            data = serializer.data
            
            if opt_fields:
                data = [apply_opt_fields(item, opt_fields) for item in data]
            
            return paginator.get_paginated_response(data)
        
        serializer = TeamCompactSerializer(queryset, many=True)
        data = serializer.data
        
        if opt_fields:
            data = [apply_opt_fields(item, opt_fields) for item in data]
        
        return Response(wrap_list_response(data, next_page=None))
    
    @action(detail=True, methods=['post'], url_path='addUser')
    def add_user(self, request: Request, pk: str = None) -> Response:
        """
        POST /teams/{team_gid}/addUser
        Adds a user to a team.
        """
        team_gid = pk
        if not team_gid:
            return asana_not_found_error('Team')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = AddUserForTeamRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        # Get team
        try:
            team = Team.objects.get(gid=team_gid)
        except Team.DoesNotExist:
            return asana_not_found_error('Team')
        
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
        
        # Add user to team (create TeamMembership relationship)
        TeamMembership.objects.get_or_create(user=user, team=team)
        
        # Serialize and return user
        from api.users.serializers import UserResponseSerializer
        user_serializer = UserResponseSerializer(user)
        data = user_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    @action(detail=True, methods=['post'], url_path='removeUser')
    def remove_user(self, request: Request, pk: str = None) -> Response:
        """
        POST /teams/{team_gid}/removeUser
        Removes a user from a team.
        """
        team_gid = pk
        if not team_gid:
            return asana_not_found_error('Team')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        
        # Validate request body
        serializer = RemoveUserForTeamRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        # Get team
        try:
            team = Team.objects.get(gid=team_gid)
        except Team.DoesNotExist:
            return asana_not_found_error('Team')
        
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
        
        # Remove user from team
        TeamMembership.objects.filter(user=user, team=team).delete()
        
        # Returns empty data record
        return Response({'data': {}})
