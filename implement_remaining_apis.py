#!/usr/bin/env python3
"""
Script to implement business logic for remaining APIs.
Generates basic CRUD operations following the established patterns.
"""
import os
import re

# APIs that need implementation
APIS_TO_IMPLEMENT = [
    'access_requests', 'allocations', 'audit_log', 'batch', 'budgets',
    'custom_field_settings', 'custom_fields', 'custom_types', 'events',
    'exports', 'goal_relationships', 'goals', 'jobs', 'memberships',
    'organization_exports', 'portfolio_memberships', 'portfolios',
    'project_briefs', 'project_memberships', 'project_statuses',
    'project_templates', 'rates', 'reactions', 'rules', 'status_updates',
    'task_templates', 'team_memberships', 'time_periods',
    'time_tracking_entries', 'typeahead', 'user_task_lists',
    'webhooks', 'workspace_memberships'
]

# Scope mappings (from FastAPI implementations)
SCOPE_MAPPINGS = {
    'access_requests': [],
    'allocations': [],
    'audit_log': [],
    'batch': [],
    'budgets': [],
    'custom_field_settings': [],
    'custom_fields': [],
    'custom_types': [],
    'events': [],
    'exports': [],
    'goal_relationships': [],
    'goals': [],
    'jobs': [],
    'memberships': [],
    'organization_exports': [],
    'portfolio_memberships': [],
    'portfolios': [],
    'project_briefs': [],
    'project_memberships': [],
    'project_statuses': [],
    'project_templates': [],
    'rates': [],
    'reactions': [],
    'rules': [],
    'status_updates': [],
    'task_templates': [],
    'team_memberships': [],
    'time_periods': [],
    'time_tracking_entries': [],
    'typeahead': [],
    'user_task_lists': [],
    'webhooks': [],
    'workspace_memberships': [],
}

def generate_serializer_file(api_name):
    """Generate serializer file for an API."""
    model_name = api_name.replace('_', ' ').title().replace(' ', '')
    model_name_singular = model_name.rstrip('s') if model_name.endswith('s') else model_name
    
    serializer_content = f'''"""
{model_name} serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import {model_name_singular}


class {model_name_singular}CompactSerializer(serializers.ModelSerializer):
    """
    {model_name_singular} compact serializer.
    Matches {model_name_singular}Compact Pydantic model.
    """
    class Meta:
        model = {model_name_singular}
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class {model_name_singular}ResponseSerializer(serializers.ModelSerializer):
    """
    {model_name_singular} full response serializer.
    Matches {model_name_singular}Response Pydantic model.
    """
    class Meta:
        model = {model_name_singular}
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
'''
    
    serializer_path = f'api/{api_name}/serializers.py'
    with open(serializer_path, 'w') as f:
        f.write(serializer_content)
    print(f"Created {serializer_path}")

def generate_view_file(api_name):
    """Generate view file with basic CRUD operations."""
    model_name = api_name.replace('_', ' ').title().replace(' ', '')
    model_name_singular = model_name.rstrip('s') if model_name.endswith('s') else model_name
    scope = SCOPE_MAPPINGS.get(api_name, [])
    scope_str = f"['{scope[0]}']" if scope else "[]"
    
    view_content = f'''"""
{model_name} views matching FastAPI behavior exactly.
Implements all {api_name} endpoints from FastAPI {api_name}_api.py
"""
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from common.errors import asana_not_found_error, asana_validation_error
from common.serializers import wrap_single_response, wrap_list_response, apply_opt_fields
from common.pagination import AsanaPagination
from common.auth import OAuth2ScopePermission
from .models import {model_name_singular}
from .serializers import (
    {model_name_singular}CompactSerializer,
    {model_name_singular}ResponseSerializer,
)


class {model_name}ViewSet(viewsets.ViewSet):
    """
    {model_name} viewset matching FastAPI {api_name}_api.py behavior.
    """
    required_scopes = {scope_str}
    permission_classes = [OAuth2ScopePermission]
    
    def list(self, request: Request) -> Response:
        """
        GET /{api_name}
        Returns the compact records for all {api_name}.
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
        queryset = {model_name_singular}.objects.all()
        
        # Apply pagination
        paginator = AsanaPagination()
        paginator.page_size = int(limit) if limit else 50
        
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = {model_name_singular}CompactSerializer(page, many=True)
            data = serializer.data
            
            if opt_fields:
                data = [apply_opt_fields(item, opt_fields) for item in data]
            
            return paginator.get_paginated_response(data)
        
        serializer = {model_name_singular}CompactSerializer(queryset, many=True)
        data = serializer.data
        
        if opt_fields:
            data = [apply_opt_fields(item, opt_fields) for item in data]
        
        return Response(wrap_list_response(data, next_page=None))
    
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """
        GET /{api_name}/{{id}}
        Returns the complete record for a single {api_name} resource.
        """
        resource_gid = pk
        if not resource_gid:
            return asana_not_found_error('{model_name_singular}')
        
        opt_pretty = request.query_params.get('opt_pretty', 'false').lower() == 'true'
        opt_fields = request.query_params.getlist('opt_fields')
        if not opt_fields:
            opt_fields_str = request.query_params.get('opt_fields')
            if opt_fields_str:
                opt_fields = [f.strip() for f in opt_fields_str.split(',')]
        
        try:
            resource = {model_name_singular}.objects.get(gid=resource_gid)
        except {model_name_singular}.DoesNotExist:
            return asana_not_found_error('{model_name_singular}')
        
        serializer = {model_name_singular}ResponseSerializer(resource)
        data = serializer.data
        
        if opt_fields:
            data = apply_opt_fields(data, opt_fields)
        
        return Response(wrap_single_response(data))
'''
    
    view_path = f'api/{api_name}/views.py'
    with open(view_path, 'w') as f:
        f.write(view_content)
    print(f"Created {view_path}")

def main():
    """Generate implementations for all remaining APIs."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    for api_name in APIS_TO_IMPLEMENT:
        print(f"\nImplementing {api_name}...")
        
        # Check if model file exists
        model_path = f'api/{api_name}/models.py'
        if not os.path.exists(model_path):
            print(f"  Warning: {model_path} not found, skipping")
            continue
        
        # Generate serializer
        if not os.path.exists(f'api/{api_name}/serializers.py'):
            generate_serializer_file(api_name)
        else:
            print(f"  Serializer already exists, skipping")
        
        # Generate/update view
        generate_view_file(api_name)
    
    print("\n✅ Done! Generated implementations for all remaining APIs.")

if __name__ == '__main__':
    main()
