"""
Section views matching FastAPI behavior exactly.
Implements all section endpoints from FastAPI sections_api.py
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from common.errors import asana_not_found_error, asana_validation_error
from common.serializers import wrap_single_response, wrap_list_response, apply_opt_fields
from common.pagination import AsanaPagination
from common.auth import OAuth2ScopePermission
from .models import Section
from .serializers import (
    SectionCompactSerializer,
    SectionResponseSerializer,
    UpdateSectionRequestSerializer,
    InsertSectionForProjectRequestSerializer,
    AddTaskForSectionRequestSerializer,
)
from api.projects.models import Project
from api.tasks.models import Task, TaskProject


class SectionsViewSet(viewsets.ViewSet):
    """
    Section viewset matching FastAPI sections_api.py behavior.
    Required scope: project_sections:read
    """
    required_scopes = ['project_sections:read']
    permission_classes = [OAuth2ScopePermission]
    
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """
        GET /sections/{section_gid}
        Returns the complete record for a single section.
        """
        section_gid = pk
        if not section_gid:
            return asana_not_found_error('Section')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        try:
            section = Section.objects.get(gid=section_gid)
        except Section.DoesNotExist:
            return asana_not_found_error('Section')
        
        serializer = SectionResponseSerializer(section)
        data = serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    def update(self, request: Request, pk: str = None) -> Response:
        """
        PUT /sections/{section_gid}
        Updates a section.
        """
        section_gid = pk
        if not section_gid:
            return asana_not_found_error('Section')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = UpdateSectionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        try:
            section = Section.objects.get(gid=section_gid)
        except Section.DoesNotExist:
            return asana_not_found_error('Section')
        
        # Update section fields
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        
        if 'name' in data_dict:
            section.name = data_dict['name']
        
        section.save()
        
        response_serializer = SectionResponseSerializer(section)
        data = response_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    def destroy(self, request: Request, pk: str = None) -> Response:
        """
        DELETE /sections/{section_gid}
        Deletes a section.
        """
        section_gid = pk
        if not section_gid:
            return asana_not_found_error('Section')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        
        try:
            section = Section.objects.get(gid=section_gid)
            section.delete()
        except Section.DoesNotExist:
            return asana_not_found_error('Section')
        
        return Response({'data': {}})
    
    @action(detail=False, methods=['get'], url_path='projects/(?P<project_gid>[^/.]+)/sections')
    def get_sections_for_project(self, request: Request, project_gid: str = None) -> Response:
        """
        GET /projects/{project_gid}/sections
        Returns the compact records for all sections in the specified project.
        """
        if not project_gid:
            return asana_not_found_error('Project')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Verify project exists
        try:
            project = Project.objects.get(gid=project_gid)
        except Project.DoesNotExist:
            return asana_not_found_error('Project')
        
        # Query sections for this project
        queryset = Section.objects.filter(project=project).order_by('name')
        
        # Apply pagination
        paginator = AsanaPagination()
        paginator.page_size = int(limit) if limit else 50
        
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = SectionCompactSerializer(page, many=True)
            data = serializer.data
            
            if opt_fields:
                data = [apply_opt_fields(item, opt_fields) for item in data]
            
            return paginator.get_paginated_response(data)
        
        serializer = SectionCompactSerializer(queryset, many=True)
        data = serializer.data
        
        if opt_fields:
            data = [apply_opt_fields(item, opt_fields) for item in data]
        
        return Response(wrap_list_response(data, next_page=None))
    
    @action(detail=False, methods=['post'], url_path='projects/(?P<project_gid>[^/.]+)/sections/insert')
    def insert_section_for_project(self, request: Request, project_gid: str = None) -> Response:
        """
        POST /projects/{project_gid}/sections/insert
        Moves or reorders a section in a project.
        """
        if not project_gid:
            return asana_not_found_error('Project')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = InsertSectionForProjectRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        try:
            project = Project.objects.get(gid=project_gid)
        except Project.DoesNotExist:
            return asana_not_found_error('Project')
        
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        section_gid = data_dict.get('section') or request_data.get('section')
        insert_before = data_dict.get('insert_before') or request_data.get('insert_before')
        insert_after = data_dict.get('insert_after') or request_data.get('insert_after')
        
        if not section_gid:
            return asana_validation_error('Section is required')
        
        try:
            section = Section.objects.get(gid=section_gid, project=project)
        except Section.DoesNotExist:
            return asana_not_found_error('Section')
        
        # TODO: Implement insert_before/insert_after logic for ordering
        # For now, just return the section
        
        response_serializer = SectionResponseSerializer(section)
        data = response_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    @action(detail=True, methods=['post'], url_path='addTask')
    def add_task(self, request: Request, pk: str = None) -> Response:
        """
        POST /sections/{section_gid}/addTask
        Adds a task to a section.
        """
        section_gid = pk
        if not section_gid:
            return asana_not_found_error('Section')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = AddTaskForSectionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        try:
            section = Section.objects.get(gid=section_gid)
        except Section.DoesNotExist:
            return asana_not_found_error('Section')
        
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        task_gid = data_dict.get('task') or request_data.get('task')
        
        if not task_gid:
            return asana_validation_error('Task is required')
        
        try:
            task = Task.objects.get(gid=task_gid)
        except Task.DoesNotExist:
            return asana_not_found_error('Task')
        
        # Add task to section (update TaskProject relationship)
        task_project = TaskProject.objects.filter(
            task=task,
            project=section.project
        ).first()
        
        if task_project:
            task_project.section = section
            task_project.save()
        else:
            # Create new TaskProject relationship
            TaskProject.objects.create(
                task=task,
                project=section.project,
                section=section
            )
        
        # Return task
        from api.tasks.serializers import TaskResponseSerializer
        task_serializer = TaskResponseSerializer(task)
        data = task_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
