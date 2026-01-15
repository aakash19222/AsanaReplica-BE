"""
Project Status models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class ProjectStatus(models.Model):
    """
    Project Status model matching ProjectStatusResponse Pydantic model.
    """
    COLOR_CHOICES = [
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('red', 'Red'),
        ('blue', 'Blue'),
    ]

    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='project_status',
        help_text="The base type of this resource."
    )
    title = models.CharField(
        max_length=255,
        help_text="The title of the project status update."
    )
    text = models.TextField(
        help_text="The text content of the status update."
    )
    html_text = models.TextField(
        null=True,
        blank=True,
        help_text="The text content of the status update with formatting as HTML."
    )
    color = models.CharField(
        max_length=50,
        choices=COLOR_CHOICES,
        help_text="The color associated with the status update."
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_statuses',
        help_text="The user who created the status update."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The time at which this resource was created."
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_statuses_created',
        help_text="The user who created the status update."
    )
    modified_at = models.DateTimeField(
        auto_now=True,
        help_text="The time at which this project status was last modified."
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='statuses',
        help_text="The project this status update belongs to."
    )

    class Meta:
        db_table = 'project_statuses'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.project}"
