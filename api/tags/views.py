"""
Tags views matching FastAPI behavior exactly.
Implements all tag endpoints from FastAPI tags_api.py
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from common.errors import asana_not_found_error, asana_validation_error
from common.serializers import wrap_single_response, wrap_list_response, apply_opt_fields
from common.pagination import AsanaPagination
from common.auth import OAuth2ScopePermission
from .models import Tag
from .serializers import (
    TagCompactSerializer,
    TagResponseSerializer,
)
from api.workspaces.models import Workspace


class TagsViewSet(viewsets.ViewSet):
    """
    Tags viewset matching FastAPI tags_api.py behavior.
    Required scope: tags:read
    """
    required_scopes = ['tags:read']
    permission_classes = [OAuth2ScopePermission]
    
    def list(self, request: Request) -> Response:
        """
        GET /tags
        Returns the compact tag records for some filtered set of tags.
        Query params: workspace, opt_fields, limit, offset
        """
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        workspace = request.query_params.get('workspace')
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Query tags from database
        queryset = Tag.objects.all()
        
        # Filter by workspace if provided
        if workspace:
            queryset = queryset.filter(workspace__gid=workspace)
        
        queryset = queryset.order_by('name')
        
        # Apply pagination
        paginator = AsanaPagination()
        paginator.page_size = int(limit) if limit else 50
        
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = TagCompactSerializer(page, many=True)
            data = serializer.data
            
            if opt_fields:
                data = [apply_opt_fields(item, opt_fields) for item in data]
            
            return paginator.get_paginated_response(data)
        
        serializer = TagCompactSerializer(queryset, many=True)
        data = serializer.data
        
        if opt_fields:
            data = [apply_opt_fields(item, opt_fields) for item in data]
        
        return Response(wrap_list_response(data, next_page=None))
    
    def create(self, request: Request) -> Response:
        """
        POST /tags
        Creates a new tag.
        """
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        from rest_framework import serializers
        serializer = serializers.Serializer(data=request.data)
        serializer.fields['data'] = serializers.DictField(required=False, allow_null=True)
        serializer.fields['name'] = serializers.CharField(required=False, allow_null=True)
        serializer.fields['workspace'] = serializers.CharField(required=False, allow_null=True)
        serializer.fields['color'] = serializers.CharField(required=False, allow_null=True)
        
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        
        # Extract fields
        name = data_dict.get('name') or request_data.get('name')
        workspace_gid = data_dict.get('workspace') or request_data.get('workspace')
        color = data_dict.get('color') or request_data.get('color')
        
        if not name:
            return asana_validation_error('Tag name is required')
        
        if not workspace_gid:
            return asana_validation_error('Workspace is required')
        
        # Get workspace
        try:
            workspace = Workspace.objects.get(gid=workspace_gid)
        except Workspace.DoesNotExist:
            return asana_not_found_error('Workspace')
        
        # Create tag
        tag = Tag.objects.create(
            name=name,
            workspace=workspace,
            color=color
        )
        
        # Serialize and return
        response_serializer = TagResponseSerializer(tag)
        data = response_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data), status=201)
    
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """
        GET /tags/{tag_gid}
        Returns the complete tag record for a single tag.
        """
        tag_gid = pk
        if not tag_gid:
            return asana_not_found_error('Tag')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        try:
            tag = Tag.objects.get(gid=tag_gid)
        except Tag.DoesNotExist:
            return asana_not_found_error('Tag')
        
        serializer = TagResponseSerializer(tag)
        data = serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    def update(self, request: Request, pk: str = None) -> Response:
        """
        PUT /tags/{tag_gid}
        Updates a tag. Only the fields provided in the data block will be updated.
        """
        tag_gid = pk
        if not tag_gid:
            return asana_not_found_error('Tag')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Validate request body
        from rest_framework import serializers
        serializer = serializers.Serializer(data=request.data)
        serializer.fields['data'] = serializers.DictField(required=False, allow_null=True)
        serializer.fields['name'] = serializers.CharField(required=False, allow_null=True)
        serializer.fields['color'] = serializers.CharField(required=False, allow_null=True)
        
        if not serializer.is_valid():
            return asana_validation_error('Invalid request body')
        
        try:
            tag = Tag.objects.get(gid=tag_gid)
        except Tag.DoesNotExist:
            return asana_not_found_error('Tag')
        
        # Update tag fields
        request_data = serializer.validated_data
        data_dict = request_data.get('data', {})
        
        if 'name' in data_dict:
            tag.name = data_dict['name']
        if 'color' in data_dict:
            tag.color = data_dict['color']
        
        tag.save()
        
        response_serializer = TagResponseSerializer(tag)
        data = response_serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    def destroy(self, request: Request, pk: str = None) -> Response:
        """
        DELETE /tags/{tag_gid}
        Deletes a tag.
        """
        tag_gid = pk
        if not tag_gid:
            return asana_not_found_error('Tag')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        
        try:
            tag = Tag.objects.get(gid=tag_gid)
            tag.delete()
        except Tag.DoesNotExist:
            return asana_not_found_error('Tag')
        
        return Response({'data': {}})
