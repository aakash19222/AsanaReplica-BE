"""
Workspace models matching FastAPI Pydantic models.
"""
from django.db import models
from common.models import generate_gid


class Workspace(models.Model):
    """
    Workspace model matching WorkspaceResponse Pydantic model.
    A workspace is the highest-level organizational unit in Asana.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='workspace',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The name of the workspace."
    )
    email_domains = models.JSONField(
        default=list,
        null=True,
        blank=True,
        help_text="The email domains that are associated with this workspace."
    )
    is_organization = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Whether the workspace is an *organization*."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workspaces'
        ordering = ['name']

    def __str__(self):
        return self.name or self.gid
