"""
Story views matching FastAPI behavior exactly.
Implements all story endpoints from FastAPI stories_api.py
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from common.errors import asana_not_found_error, asana_validation_error
from common.serializers import wrap_single_response, wrap_list_response, apply_opt_fields
from common.pagination import AsanaPagination
from common.auth import OAuth2ScopePermission
from .models import Story
from .serializers import (
    StoryCompactSerializer,
    StoryResponseSerializer,
    UpdateStoryRequestSerializer,
)
from api.tasks.models import Task


class StoriesViewSet(viewsets.ViewSet):
    """
    Story viewset matching FastAPI stories_api.py behavior.
    Required scope: stories:read
    """
    required_scopes = ['stories:read']
    permission_classes = [OAuth2ScopePermission]
    
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """
        GET /stories/{story_gid}
        Returns the full record for a single story.
        """
        story_gid = pk
        if not story_gid:
            return asana_not_found_error('Story')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        try:
            story = Story.objects.get(gid=story_gid)
        except Story.DoesNotExist:
            return asana_not_found_error('Story')
        
        serializer = StoryResponseSerializer(story)
        data = serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    def update(self, request: Request, pk: str = None) -> Response:
        """
        PUT /stories/{story_gid}
        Updates the story and returns the full record for the updated story.
        Only comment stories can have their text updated, and only comment stories and attachment stories can be pinned.
        """
        story_gid = pk
        if not story_gid:
            return asana_not_found_error('Story')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        serializer = UpdateStoryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        try:
            story = Story.objects.get(gid=story_gid)
        except Story.DoesNotExist:
            return asana_not_found_error('Story')
        
        # Update story fields
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        
        # Only comment stories can have text updated
        if story.resource_subtype == 'comment_added':
            if 'text' in data_dict:
                story.text = data_dict['text']
            if 'html_text' in data_dict:
                story.html_text = data_dict['html_text']
        
        # Comment and attachment stories can be pinned
        if story.resource_subtype in ['comment_added', 'attachment_added']:
            if 'is_pinned' in data_dict:
                story.is_pinned = data_dict['is_pinned']
        
        story.save()
        
        response_serializer = StoryResponseSerializer(story)
        data = response_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    def destroy(self, request: Request, pk: str = None) -> Response:
        """
        DELETE /stories/{story_gid}
        Deletes a story. A user can only delete stories they have created.
        """
        story_gid = pk
        if not story_gid:
            return asana_not_found_error('Story')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        
        try:
            story = Story.objects.get(gid=story_gid)
            # TODO: Check if current user created the story
            story.delete()
        except Story.DoesNotExist:
            return asana_not_found_error('Story')
        
        # Returns empty data record
        return Response({'data': {}})
    
    @action(detail=False, methods=['get'], url_path='tasks/(?P<task_gid>[^/.]+)/stories')
    def get_stories_for_task(self, request: Request, task_gid: str = None) -> Response:
        """
        GET /tasks/{task_gid}/stories
        Returns the compact records for all stories on the task.
        """
        if not task_gid:
            return asana_not_found_error('Task')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Verify task exists
        try:
            task = Task.objects.get(gid=task_gid)
        except Task.DoesNotExist:
            return asana_not_found_error('Task')
        
        # Query stories for this task
        queryset = Story.objects.filter(task=task).order_by('-created_at')
        
        # Apply pagination
        paginator = AsanaPagination()
        paginator.page_size = int(limit) if limit else 50
        
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = StoryCompactSerializer(page, many=True)
            data = serializer.data
            
            if opt_fields:
                data = [apply_opt_fields(item, opt_fields) for item in data]
            
            return paginator.get_paginated_response(data)
        
        serializer = StoryCompactSerializer(queryset, many=True)
        data = serializer.data
        
        if opt_fields:
            data = [apply_opt_fields(item, opt_fields) for item in data]
        
        return Response(wrap_list_response(data, next_page=None))
