"""
Team models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Team(models.Model):
    """
    Team model matching TeamResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='team',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="The name of the team."
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="The description of the team."
    )
    html_description = models.TextField(
        null=True,
        blank=True,
        help_text="The description of the team with formatting as HTML."
    )
    organization = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='teams',
        help_text="The organization/workspace this team belongs to."
    )
    permalink_url = models.URLField(
        null=True,
        blank=True,
        help_text="A url that points directly to the object within Asana."
    )
    visibility = models.CharField(
        max_length=50,
        default='secret',
        choices=[
            ('secret', 'Secret'),
            ('request_to_join', 'Request To Join'),
            ('public_to_organization', 'Public To Organization'),
        ],
        help_text="The visibility of the team."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teams'
        ordering = ['name']

    def __str__(self):
        return self.name or self.gid
