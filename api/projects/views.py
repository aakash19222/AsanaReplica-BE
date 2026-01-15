"""
Project views matching FastAPI behavior exactly.
Implements all project endpoints from FastAPI projects_api.py
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from common.errors import asana_not_found_error, asana_validation_error
from common.serializers import wrap_single_response, wrap_list_response, apply_opt_fields
from common.pagination import AsanaPagination
from common.auth import OAuth2ScopePermission
from .models import Project
from .serializers import (
    ProjectCompactSerializer,
    ProjectResponseSerializer,
    CreateProjectRequestSerializer,
    UpdateProjectRequestSerializer,
)
from api.workspaces.models import Workspace
from api.teams.models import Team
from api.users.models import User


class ProjectsViewSet(viewsets.ViewSet):
    """
    Project viewset matching FastAPI projects_api.py behavior.
    Required scope: projects:read
    """
    required_scopes = ['projects:read']
    permission_classes = [OAuth2ScopePermission]
    
    def list(self, request: Request) -> Response:
        """
        GET /projects
        Returns the compact project records for some filtered set of projects.
        Query params: workspace, team, archived, opt_fields, limit, offset
        """
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        workspace = request.query_params.get('workspace')
        team = request.query_params.get('team')
        archived = request.query_params.get('archived')
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Query projects from database
        queryset = Project.objects.all()
        
        # Apply filters
        if workspace:
            queryset = queryset.filter(workspace__gid=workspace)
        
        if team:
            # Filter projects by team membership
            from api.project_memberships.models import ProjectMembership
            project_ids = ProjectMembership.objects.filter(
                project__team__gid=team
            ).values_list('project_id', flat=True)
            queryset = queryset.filter(id__in=project_ids)
        
        if archived is not None:
            archived_bool = archived.lower() == 'true'
            queryset = queryset.filter(archived=archived_bool)
        
        queryset = queryset.order_by('name')
        
        # Apply pagination
        paginator = AsanaPagination()
        paginator.page_size = int(limit) if limit else 50
        
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = ProjectCompactSerializer(page, many=True)
            data = serializer.data
            
            if opt_fields:
                data = [apply_opt_fields(item, opt_fields) for item in data]
            
            return paginator.get_paginated_response(data)
        
        serializer = ProjectCompactSerializer(queryset, many=True)
        data = serializer.data
        
        if opt_fields:
            data = [apply_opt_fields(item, opt_fields) for item in data]
        
        return Response(wrap_list_response(data, next_page=None))
    
    def create(self, request: Request) -> Response:
        """
        POST /projects
        Creates a new project in a workspace or team.
        """
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = CreateProjectRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        
        # Extract fields
        name = data_dict.get('name') or request_data.get('name')
        workspace_gid = data_dict.get('workspace') or request_data.get('workspace')
        team_gid = data_dict.get('team') or request_data.get('team')
        notes = data_dict.get('notes') or request_data.get('notes')
        color = data_dict.get('color') or request_data.get('color')
        
        if not name:
            return asana_validation_error('Project name is required')
        
        if not workspace_gid:
            return asana_validation_error('Workspace is required')
        
        # Get workspace
        try:
            workspace = Workspace.objects.get(gid=workspace_gid)
        except Workspace.DoesNotExist:
            return asana_not_found_error('Workspace')
        
        # Create project
        project = Project.objects.create(
            name=name,
            workspace=workspace,
            notes=notes,
            color=color
        )
        
        # TODO: Handle team association if provided
        
        # Serialize and return
        response_serializer = ProjectResponseSerializer(project)
        data = response_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data), status=201)
    
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """
        GET /projects/{project_gid}
        Returns the complete project record for a single project.
        """
        project_gid = pk
        if not project_gid:
            return asana_not_found_error('Project')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        try:
            project = Project.objects.get(gid=project_gid)
        except Project.DoesNotExist:
            return asana_not_found_error('Project')
        
        serializer = ProjectResponseSerializer(project)
        data = serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    def update(self, request: Request, pk: str = None) -> Response:
        """
        PUT /projects/{project_gid}
        Updates a project. Only the fields provided in the data block will be updated.
        """
        project_gid = pk
        if not project_gid:
            return asana_not_found_error('Project')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = UpdateProjectRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        try:
            project = Project.objects.get(gid=project_gid)
        except Project.DoesNotExist:
            return asana_not_found_error('Project')
        
        # Update project fields
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        
        if 'name' in data_dict:
            project.name = data_dict['name']
        if 'notes' in data_dict:
            project.notes = data_dict['notes']
        if 'archived' in data_dict:
            project.archived = data_dict['archived']
        if 'color' in data_dict:
            project.color = data_dict['color']
        
        project.save()
        
        response_serializer = ProjectResponseSerializer(project)
        data = response_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    def destroy(self, request: Request, pk: str = None) -> Response:
        """
        DELETE /projects/{project_gid}
        Deletes a project.
        """
        project_gid = pk
        if not project_gid:
            return asana_not_found_error('Project')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        
        try:
            project = Project.objects.get(gid=project_gid)
            project.delete()
        except Project.DoesNotExist:
            return asana_not_found_error('Project')
        
        # Returns empty data record
        return Response({'data': {}})
