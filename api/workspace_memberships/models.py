"""
Workspace Membership models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class WorkspaceMembership(models.Model):
    """
    Workspace Membership model matching WorkspaceMembershipResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='workspace_membership',
        help_text="The base type of this resource."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the workspace membership is active."
    )
    is_admin = models.BooleanField(
        default=False,
        help_text="Whether the user is an admin of the workspace."
    )
    is_guest = models.BooleanField(
        default=False,
        help_text="Whether the user is a guest of the workspace."
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='workspace_memberships',
        help_text="The user in the workspace membership."
    )
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='workspace_memberships',
        help_text="The workspace in the membership."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workspace_memberships'
        unique_together = ['user', 'workspace']
        ordering = ['-created_at']

    def __str__(self):
        return f"Workspace Membership {self.gid}"
