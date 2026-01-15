"""
Project Template models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class ProjectTemplate(models.Model):
    """
    Project Template model matching ProjectTemplateResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='project_template',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="Name of the project template."
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Free-form textual information associated with the project template."
    )
    public = models.BooleanField(
        default=False,
        help_text="True if the project template is public to its team."
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='project_templates',
        help_text="The team this project template belongs to."
    )
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='project_templates',
        help_text="The workspace this project template belongs to."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_templates'
        ordering = ['name']

    def __str__(self):
        return self.name or self.gid
