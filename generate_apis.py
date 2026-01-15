#!/usr/bin/env python
"""
Script to generate Django API app structure for all Asana APIs.
"""
import os

APIS = [
    ('access_requests', 'access_requests', 'AccessRequestsConfig'),
    ('allocations', 'allocations', 'AllocationsConfig'),
    ('audit_log', 'audit_log', 'AuditLogConfig'),
    ('batch', 'batch', 'BatchConfig'),
    ('budgets', 'budgets', 'BudgetsConfig'),
    ('custom_field_settings', 'custom_field_settings', 'CustomFieldSettingsConfig'),
    ('custom_fields', 'custom_fields', 'CustomFieldsConfig'),
    ('custom_types', 'custom_types', 'CustomTypesConfig'),
    ('events', 'events', 'EventsConfig'),
    ('exports', 'exports', 'ExportsConfig'),
    ('goal_relationships', 'goal_relationships', 'GoalRelationshipsConfig'),
    ('goals', 'goals', 'GoalsConfig'),
    ('jobs', 'jobs', 'JobsConfig'),
    ('memberships', 'memberships', 'MembershipsConfig'),
    ('organization_exports', 'organization_exports', 'OrganizationExportsConfig'),
    ('portfolio_memberships', 'portfolio_memberships', 'PortfolioMembershipsConfig'),
    ('portfolios', 'portfolios', 'PortfoliosConfig'),
    ('project_briefs', 'project_briefs', 'ProjectBriefsConfig'),
    ('project_memberships', 'project_memberships', 'ProjectMembershipsConfig'),
    ('project_statuses', 'project_statuses', 'ProjectStatusesConfig'),
    ('project_templates', 'project_templates', 'ProjectTemplatesConfig'),
    ('rates', 'rates', 'RatesConfig'),
    ('reactions', 'reactions', 'ReactionsConfig'),
    ('rules', 'rules', 'RulesConfig'),
    ('status_updates', 'status_updates', 'StatusUpdatesConfig'),
    ('tags', 'tags', 'TagsConfig'),
    ('task_templates', 'task_templates', 'TaskTemplatesConfig'),
    ('team_memberships', 'team_memberships', 'TeamMembershipsConfig'),
    ('teams', 'teams', 'TeamsConfig'),
    ('time_periods', 'time_periods', 'TimePeriodsConfig'),
    ('time_tracking_entries', 'time_tracking_entries', 'TimeTrackingEntriesConfig'),
    ('typeahead', 'typeahead', 'TypeaheadConfig'),
    ('user_task_lists', 'user_task_lists', 'UserTaskListsConfig'),
    ('webhooks', 'webhooks', 'WebhooksConfig'),
    ('workspace_memberships', 'workspace_memberships', 'WorkspaceMembershipsConfig'),
]

BASE_DIR = 'api'

for app_name, module_name, config_class in APIS:
    app_dir = os.path.join(BASE_DIR, app_name)
    os.makedirs(app_dir, exist_ok=True)
    
    # __init__.py
    with open(os.path.join(app_dir, '__init__.py'), 'w') as f:
        f.write(f"default_app_config = 'api.{app_name}.apps.{config_class}'\n")
    
    # apps.py
    with open(os.path.join(app_dir, 'apps.py'), 'w') as f:
        f.write(f"""from django.apps import AppConfig


class {config_class}(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.{app_name}'
""")
    
    # views.py
    with open(os.path.join(app_dir, 'views.py'), 'w') as f:
        f.write(f'''"""
{config_class.replace("Config", "")} views matching FastAPI behavior exactly.
TODO: Implement all endpoints from FastAPI {app_name}_api.py
"""
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from common.errors import asana_not_found_error
from common.serializers import wrap_single_response, wrap_list_response
from common.auth import OAuth2ScopePermission


class {config_class.replace("Config", "ViewSet")}(viewsets.ViewSet):
    """
    {config_class.replace("Config", "")} viewset matching FastAPI {app_name}_api.py behavior.
    """
    required_scopes = []  # TODO: Set required scopes
    permission_classes = [OAuth2ScopePermission]
    
    def list(self, request: Request) -> Response:
        """GET /{app_name} - TODO: Implement"""
        return Response(wrap_list_response([]))
    
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """GET /{app_name}/{{id}} - TODO: Implement"""
        return asana_not_found_error('Resource')
''')
    
    # urls.py
    with open(os.path.join(app_dir, 'urls.py'), 'w') as f:
        f.write(f'''"""
{config_class.replace("Config", "")} URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import {config_class.replace("Config", "ViewSet")}

router = DefaultRouter()
router.register(r'{app_name}', {config_class.replace("Config", "ViewSet")}, basename='{app_name.replace("_", "")}')

urlpatterns = router.urls
''')
    
    print(f"Created {app_name}")

print("Done!")
