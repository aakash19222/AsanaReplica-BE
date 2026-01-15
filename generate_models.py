#!/usr/bin/env python3
"""
Script to generate Django models for all remaining APIs.
"""
import os

# APIs that need models (excluding ones already created)
REMAINING_APIS = [
    ('access_requests', 'AccessRequest', 'Access Request'),
    ('allocations', 'Allocation', 'Allocation'),
    ('audit_log', 'AuditLogEvent', 'Audit Log Event'),
    ('batch', 'BatchRequest', 'Batch Request'),
    ('budgets', 'Budget', 'Budget'),
    ('custom_field_settings', 'CustomFieldSetting', 'Custom Field Setting'),
    ('custom_types', 'CustomType', 'Custom Type'),
    ('events', 'Event', 'Event'),
    ('exports', 'Export', 'Export'),
    ('goal_relationships', 'GoalRelationship', 'Goal Relationship'),
    ('goals', 'Goal', 'Goal'),
    ('jobs', 'Job', 'Job'),
    ('memberships', 'Membership', 'Membership'),
    ('organization_exports', 'OrganizationExport', 'Organization Export'),
    ('portfolio_memberships', 'PortfolioMembership', 'Portfolio Membership'),
    ('portfolios', 'Portfolio', 'Portfolio'),
    ('project_briefs', 'ProjectBrief', 'Project Brief'),
    ('project_memberships', 'ProjectMembership', 'Project Membership'),
    ('project_templates', 'ProjectTemplate', 'Project Template'),
    ('rates', 'Rate', 'Rate'),
    ('reactions', 'Reaction', 'Reaction'),
    ('rules', 'Rule', 'Rule'),
    ('status_updates', 'StatusUpdate', 'Status Update'),
    ('task_templates', 'TaskTemplate', 'Task Template'),
    ('team_memberships', 'TeamMembership', 'Team Membership'),
    ('time_periods', 'TimePeriod', 'Time Period'),
    ('time_tracking_entries', 'TimeTrackingEntry', 'Time Tracking Entry'),
    ('typeahead', 'Typeahead', 'Typeahead'),
    ('user_task_lists', 'UserTaskList', 'User Task List'),
    ('workspace_memberships', 'WorkspaceMembership', 'Workspace Membership'),
]

BASE_DIR = 'api'

for app_name, model_name, display_name in REMAINING_APIS:
    models_file = os.path.join(BASE_DIR, app_name, 'models.py')
    
    # Check if file already exists
    if os.path.exists(models_file):
        print(f"Skipping {app_name} - models.py already exists")
        continue
    
    code = f'''"""
{display_name} models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid


class {model_name}(models.Model):
    """
    {display_name} model matching FastAPI Pydantic model.
    TODO: Add fields based on FastAPI model definition.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=lambda: str(uuid.uuid4()),
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='{app_name.replace("_", "")}',
        help_text="The base type of this resource."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '{app_name}'
        ordering = ['-created_at']

    def __str__(self):
        return self.gid
'''
    
    with open(models_file, 'w') as f:
        f.write(code)
    
    print(f"Created models for {app_name}")

print("Done!")
