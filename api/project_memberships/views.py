"""
ProjectMemberships views matching FastAPI behavior exactly.
Implements all project_memberships endpoints from FastAPI project_memberships_api.py
"""
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from common.errors import asana_not_found_error, asana_validation_error
from common.serializers import wrap_single_response, wrap_list_response, apply_opt_fields
from common.pagination import AsanaPagination
from common.auth import OAuth2ScopePermission
from .models import ProjectMembership
from .serializers import (
    ProjectMembershipCompactSerializer,
    ProjectMembershipResponseSerializer,
)


class ProjectMembershipsViewSet(viewsets.ViewSet):
    """
    ProjectMemberships viewset matching FastAPI project_memberships_api.py behavior.
    """
    required_scopes = []
    permission_classes = [OAuth2ScopePermission]
    
    def list(self, request: Request) -> Response:
        """
        GET /project_memberships
        Returns the compact records for all project_memberships.
        """
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        # Query from database
        queryset = ProjectMembership.objects.all()
        
        # Apply pagination
        paginator = AsanaPagination()
        paginator.page_size = int(limit) if limit else 50
        
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = ProjectMembershipCompactSerializer(page, many=True)
            data = serializer.data
            
            if opt_fields:
                data = [apply_opt_fields(item, opt_fields) for item in data]
            
            return paginator.get_paginated_response(data)
        
        serializer = ProjectMembershipCompactSerializer(queryset, many=True)
        data = serializer.data
        
        if opt_fields:
            data = [apply_opt_fields(item, opt_fields) for item in data]
        
        return Response(wrap_list_response(data, next_page=None))
    
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """
        GET /project_memberships/{id}
        Returns the complete record for a single project_memberships resource.
        """
        resource_gid = pk
        if not resource_gid:
            return asana_not_found_error('ProjectMembership')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        try:
            resource = ProjectMembership.objects.get(gid=resource_gid)
        except ProjectMembership.DoesNotExist:
            return asana_not_found_error('ProjectMembership')
        
        serializer = ProjectMembershipResponseSerializer(resource)
        data = serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
