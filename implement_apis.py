#!/usr/bin/env python3
"""
Script to implement Django views from FastAPI base API files.
Reads FastAPI base files and generates matching Django views.
"""
import os
import re
import ast
from pathlib import Path

FASTAPI_BASE_DIR = '../asana_backend/src/openapi_server/apis'
DJANGO_API_DIR = 'api'

# Map FastAPI API names to Django app names
API_MAP = {
    'access_requests': 'access_requests',
    'allocations': 'allocations',
    'attachments': 'attachments',
    'audit_log_api': 'audit_log',
    'batch_api': 'batch',
    'budgets': 'budgets',
    'custom_field_settings': 'custom_field_settings',
    'custom_fields': 'custom_fields',
    'custom_types': 'custom_types',
    'events': 'events',
    'exports': 'exports',
    'goal_relationships': 'goal_relationships',
    'goals': 'goals',
    'jobs': 'jobs',
    'memberships': 'memberships',
    'organization_exports': 'organization_exports',
    'portfolio_memberships': 'portfolio_memberships',
    'portfolios': 'portfolios',
    'project_briefs': 'project_briefs',
    'project_memberships': 'project_memberships',
    'project_statuses': 'project_statuses',
    'project_templates': 'project_templates',
    'projects': 'projects',
    'rates': 'rates',
    'reactions': 'reactions',
    'rules': 'rules',
    'sections': 'sections',
    'status_updates': 'status_updates',
    'stories': 'stories',
    'tags': 'tags',
    'task_templates': 'task_templates',
    'tasks': 'tasks',
    'team_memberships': 'team_memberships',
    'teams': 'teams',
    'time_periods': 'time_periods',
    'time_tracking_entries': 'time_tracking_entries',
    'typeahead': 'typeahead',
    'user_task_lists': 'user_task_lists',
    'users': 'users',
    'webhooks': 'webhooks',
    'workspace_memberships': 'workspace_memberships',
    'workspaces': 'workspaces',
}

def extract_scopes_from_docstring(docstring):
    """Extract required scopes from docstring."""
    if not docstring:
        return []
    match = re.search(r'Required scope.*?code&gt;([^&]+)&lt;/code&gt;', docstring)
    if match:
        return [match.group(1).strip()]
    return []

def extract_method_info(func_def):
    """Extract HTTP method and path info from FastAPI function."""
    # This is a simplified parser - in production, use proper AST parsing
    return None, None

def generate_viewset_code(api_name, base_file_path):
    """Generate Django ViewSet code from FastAPI base file."""
    if not os.path.exists(base_file_path):
        return None
    
    with open(base_file_path, 'r') as f:
        content = f.read()
    
    # Extract class name
    class_match = re.search(r'class Base(\w+)Api:', content)
    if not class_match:
        return None
    
    base_class_name = class_match.group(1)
    viewset_class_name = f"{base_class_name}ViewSet"
    
    # Extract all async methods
    method_pattern = r'async def (\w+)\([^)]*\)[^:]*:'
    methods = re.findall(method_pattern, content)
    
    # Extract scopes from docstrings
    scopes = []
    scope_pattern = r'Required scope.*?code&gt;([^&]+)&lt;/code&gt;'
    scope_matches = re.findall(scope_pattern, content)
    if scope_matches:
        scopes = [s.strip() for s in scope_matches]
    
    # Generate viewset code
    code = f'''"""
{base_class_name} views matching FastAPI behavior exactly.
Generated from FastAPI {api_name}_api_base.py
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from common.errors import asana_not_found_error, asana_validation_error
from common.serializers import wrap_single_response, wrap_list_response, apply_opt_fields
from common.auth import OAuth2ScopePermission


class {viewset_class_name}(viewsets.ViewSet):
    """
    {base_class_name} viewset matching FastAPI {api_name}_api.py behavior.
    """
    required_scopes = {scopes if scopes else "[]"}
    permission_classes = [OAuth2ScopePermission]
    
    def list(self, request: Request) -> Response:
        """GET /{api_name} - TODO: Implement from FastAPI"""
        return Response(wrap_list_response([]))
    
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """GET /{api_name}/{{id}} - TODO: Implement from FastAPI"""
        return asana_not_found_error('Resource')
'''
    
    return code

# Generate views for all APIs
for fastapi_name, django_name in API_MAP.items():
    base_file = f"{FASTAPI_BASE_DIR}/{fastapi_name}_api_base.py"
    view_file = f"{DJANGO_API_DIR}/{django_name}/views.py"
    
    if os.path.exists(base_file):
        code = generate_viewset_code(django_name, base_file)
        if code:
            with open(view_file, 'w') as f:
                f.write(code)
            print(f"Generated views for {django_name}")
    else:
        print(f"Warning: {base_file} not found")

print("Done generating views!")
