"""
Task Template models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class TaskTemplate(models.Model):
    """
    Task Template model matching TaskTemplateResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='task_template',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=500,
        help_text="Name of the task template."
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Free-form textual information associated with the task template."
    )
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='task_templates',
        help_text="The workspace this task template belongs to."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task_templates'
        ordering = ['name']

    def __str__(self):
        return self.name or self.gid
