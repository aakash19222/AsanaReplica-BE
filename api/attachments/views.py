"""
Attachment views matching FastAPI behavior exactly.
Implements all attachment endpoints from FastAPI attachments_api.py
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from common.errors import asana_not_found_error
from common.serializers import wrap_single_response, wrap_list_response, apply_opt_fields
from common.pagination import AsanaPagination
from common.auth import OAuth2ScopePermission
from .models import Attachment
from .serializers import (
    AttachmentCompactSerializer,
    AttachmentResponseSerializer,
)
from api.tasks.models import Task


class AttachmentsViewSet(viewsets.ViewSet):
    """
    Attachment viewset matching FastAPI attachments_api.py behavior.
    Required scope: attachments:read
    """
    required_scopes = ['attachments:read']
    permission_classes = [OAuth2ScopePermission]
    
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """
        GET /attachments/{attachment_gid}
        Get the full record for a single attachment.
        """
        attachment_gid = pk
        if not attachment_gid:
            return asana_not_found_error('Attachment')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        try:
            attachment = Attachment.objects.get(gid=attachment_gid)
        except Attachment.DoesNotExist:
            return asana_not_found_error('Attachment')
        
        serializer = AttachmentResponseSerializer(attachment)
        data = serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
    
    def destroy(self, request: Request, pk: str = None) -> Response:
        """
        DELETE /attachments/{attachment_gid}
        Deletes a specific, existing attachment.
        """
        attachment_gid = pk
        if not attachment_gid:
            return asana_not_found_error('Attachment')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        
        try:
            attachment = Attachment.objects.get(gid=attachment_gid)
            attachment.delete()
        except Attachment.DoesNotExist:
            return asana_not_found_error('Attachment')
        
        return Response({'data': {}})
    
    @action(detail=False, methods=['get'], url_path='tasks/(?P<task_gid>[^/.]+)/attachments')
    def get_attachments_for_task(self, request: Request, task_gid: str = None) -> Response:
        """
        GET /tasks/{task_gid}/attachments
        Returns the compact records for all attachments on the task.
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
        
        # Query attachments for this task
        queryset = Attachment.objects.filter(parent=task).order_by('-created_at')
        
        # Apply pagination
        paginator = AsanaPagination()
        paginator.page_size = int(limit) if limit else 50
        
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = AttachmentCompactSerializer(page, many=True)
            data = serializer.data
            
            if opt_fields:
                data = [apply_opt_fields(item, opt_fields) for item in data]
            
            return paginator.get_paginated_response(data)
        
        serializer = AttachmentCompactSerializer(queryset, many=True)
        data = serializer.data
        
        if opt_fields:
            data = [apply_opt_fields(item, opt_fields) for item in data]
        
        return Response(wrap_list_response(data, next_page=None))
