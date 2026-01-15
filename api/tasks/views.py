"""
Task views matching FastAPI behavior exactly.
Implements all task endpoints from FastAPI tasks_api.py
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.utils import timezone
from datetime import datetime, date
from common.errors import asana_not_found_error, asana_validation_error
from common.serializers import wrap_single_response, wrap_list_response, apply_opt_fields
from common.pagination import AsanaPagination
from common.auth import OAuth2ScopePermission
from .models import Task, TaskDependency, TaskProject, TaskFollower, TaskTag, TaskLike
from .serializers import (
    TaskCompactSerializer,
    TaskResponseSerializer,
    CreateTaskRequestSerializer,
)
from api.projects.models import Project
from api.workspaces.models import Workspace
from api.users.models import User
from api.tags.models import Tag
from api.sections.models import Section


class TasksViewSet(viewsets.ViewSet):
    """
    Task viewset matching FastAPI tasks_api.py behavior.
    Required scope: tasks:read
    """
    required_scopes = ['tasks:read']
    permission_classes = [OAuth2ScopePermission]
    
    def list(self, request: Request) -> Response:
        """
        GET /tasks
        Returns the compact task records for some filtered set of tasks.
        Query params: assignee, project, section, workspace, completed_since, modified_since, opt_fields, limit, offset
        """
        # Get query parameters
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        assignee = request.query_params.get('assignee')
        project = request.query_params.get('project')
        section = request.query_params.get('section')
        workspace = request.query_params.get('workspace')
        completed_since = request.query_params.get('completed_since')
        modified_since = request.query_params.get('modified_since')
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Query tasks from database
        queryset = Task.objects.all()
        
        # Apply filters
        if assignee:
            queryset = queryset.filter(assignee__gid=assignee)
        
        if project:
            task_ids = TaskProject.objects.filter(project__gid=project).values_list('task_id', flat=True)
            queryset = queryset.filter(id__in=task_ids)
        
        if section:
            task_ids = TaskProject.objects.filter(section__gid=section).values_list('task_id', flat=True)
            queryset = queryset.filter(id__in=task_ids)
        
        if workspace:
            queryset = queryset.filter(workspace__gid=workspace)
        
        if completed_since:
            try:
                completed_since_dt = datetime.fromisoformat(completed_since.replace('Z', '+00:00'))
                queryset = queryset.filter(completed_at__gte=completed_since_dt)
            except (ValueError, AttributeError):
                pass
        
        if modified_since:
            try:
                modified_since_dt = datetime.fromisoformat(modified_since.replace('Z', '+00:00'))
                queryset = queryset.filter(modified_at__gte=modified_since_dt)
            except (ValueError, AttributeError):
                pass
        
        # Order by modified_at descending
        queryset = queryset.order_by('-modified_at')
        
        # Apply pagination
        paginator = AsanaPagination()
        paginator.page_size = int(limit) if limit else 50
        
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = TaskCompactSerializer(page, many=True)
            data = serializer.data
            
            if opt_fields:
                data = [apply_opt_fields(item, opt_fields) for item in data]
            
            return paginator.get_paginated_response(data)
        
        serializer = TaskCompactSerializer(queryset, many=True)
        data = serializer.data
        
        if opt_fields:
            data = [apply_opt_fields(item, opt_fields) for item in data]
        
        return Response(wrap_list_response(data, next_page=None))
    
    def create(self, request: Request) -> Response:
        """
        POST /tasks
        Creates a new task.
        """
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = CreateTaskRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        
        # Extract fields
        name = data_dict.get('name') or request_data.get('name')
        workspace_gid = data_dict.get('workspace') or request_data.get('workspace')
        project_gids = data_dict.get('projects') or request_data.get('projects', [])
        parent_gid = data_dict.get('parent') or request_data.get('parent')
        assignee_gid = data_dict.get('assignee') or request_data.get('assignee')
        due_on = data_dict.get('due_on') or request_data.get('due_on')
        notes = data_dict.get('notes') or request_data.get('notes')
        
        if not name:
            return asana_validation_error('Task name is required')
        
        # Get workspace (required)
        if not workspace_gid and not project_gids:
            return asana_validation_error('Workspace or project is required')
        
        if workspace_gid:
            try:
                workspace = Workspace.objects.get(gid=workspace_gid)
            except Workspace.DoesNotExist:
                return asana_not_found_error('Workspace')
        else:
            # Get workspace from first project
            try:
                first_project = Project.objects.get(gid=project_gids[0])
                workspace = first_project.workspace
            except (Project.DoesNotExist, IndexError):
                return asana_not_found_error('Project')
        
        # Create task
        task = Task.objects.create(
            name=name,
            workspace=workspace,
            notes=notes,
            due_on=due_on
        )
        
        # Set parent if provided
        if parent_gid:
            try:
                parent = Task.objects.get(gid=parent_gid)
                task.parent = parent
                task.save()
            except Task.DoesNotExist:
                pass
        
        # Set assignee if provided
        if assignee_gid:
            try:
                assignee = User.objects.get(gid=assignee_gid)
                task.assignee = assignee
                task.save()
            except User.DoesNotExist:
                pass
        
        # Add to projects
        for project_gid in project_gids:
            try:
                project = Project.objects.get(gid=project_gid)
                TaskProject.objects.get_or_create(task=task, project=project)
            except Project.DoesNotExist:
                pass
        
        # Serialize and return
        response_serializer = TaskResponseSerializer(task)
        data = response_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data), status=201)
    
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """
        GET /tasks/{task_gid}
        Returns the complete task record for a single task.
        """
        task_gid = pk
        if not task_gid:
            return asana_not_found_error('Task')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        try:
            task = Task.objects.get(gid=task_gid)
        except Task.DoesNotExist:
            return asana_not_found_error('Task')
        
        serializer = TaskResponseSerializer(task)
        data = serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    def update(self, request: Request, pk: str = None) -> Response:
        """
        PUT /tasks/{task_gid}
        Updates a task. Only the fields provided in the data block will be updated.
        """
        task_gid = pk
        if not task_gid:
            return asana_not_found_error('Task')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = CreateTaskRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        try:
            task = Task.objects.get(gid=task_gid)
        except Task.DoesNotExist:
            return asana_not_found_error('Task')
        
        # Update task fields
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        
        if 'name' in data_dict:
            task.name = data_dict['name']
        if 'notes' in data_dict:
            task.notes = data_dict['notes']
        if 'completed' in data_dict:
            task.completed = data_dict['completed']
            if data_dict['completed']:
                task.completed_at = timezone.now()
        if 'due_on' in data_dict:
            task.due_on = data_dict['due_on']
        if 'assignee' in data_dict:
            assignee_gid = data_dict['assignee']
            if assignee_gid:
                try:
                    task.assignee = User.objects.get(gid=assignee_gid)
                except User.DoesNotExist:
                    pass
            else:
                task.assignee = None
        
        task.save()
        
        response_serializer = TaskResponseSerializer(task)
        data = response_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    def destroy(self, request: Request, pk: str = None) -> Response:
        """
        DELETE /tasks/{task_gid}
        Deletes a task.
        """
        task_gid = pk
        if not task_gid:
            return asana_not_found_error('Task')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        
        try:
            task = Task.objects.get(gid=task_gid)
            task.delete()
        except Task.DoesNotExist:
            return asana_not_found_error('Task')
        
        # Returns empty data record
        return Response({'data': {}})
