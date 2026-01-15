"""
Project models matching FastAPI Pydantic models.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from common.models import generate_gid


class Project(models.Model):
    """
    Project model matching ProjectResponse Pydantic model.
    """
    ARCHIVED_CHOICES = [
        (False, 'Active'),
        (True, 'Archived'),
    ]

    COLOR_CHOICES = [
        ('dark-pink', 'Dark Pink'),
        ('dark-green', 'Dark Green'),
        ('dark-blue', 'Dark Blue'),
        ('dark-red', 'Dark Red'),
        ('dark-teal', 'Dark Teal'),
        ('dark-brown', 'Dark Brown'),
        ('dark-orange', 'Dark Orange'),
        ('dark-purple', 'Dark Purple'),
        ('dark-warm-gray', 'Dark Warm Gray'),
        ('light-pink', 'Light Pink'),
        ('light-green', 'Light Green'),
        ('light-blue', 'Light Blue'),
        ('light-red', 'Light Red'),
        ('light-teal', 'Light Teal'),
        ('light-brown', 'Light Brown'),
        ('light-orange', 'Light Orange'),
        ('light-purple', 'Light Purple'),
        ('light-warm-gray', 'Light Warm Gray'),
    ]

    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='project',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="Name of the project."
    )
    archived = models.BooleanField(
        default=False,
        help_text="Whether the project is archived."
    )
    color = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=COLOR_CHOICES,
        help_text="Color of the project."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The time at which this resource was created."
    )
    current_status = models.ForeignKey(
        'project_statuses.ProjectStatus',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        help_text="Current status of the project."
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="The day on which this project is due."
    )
    due_on = models.DateField(
        null=True,
        blank=True,
        help_text="The day on which this project is due."
    )
    html_notes = models.TextField(
        null=True,
        blank=True,
        help_text="The notes of the project with formatting as HTML."
    )
    is_template = models.BooleanField(
        default=False,
        help_text="Whether this project is a template."
    )
    modified_at = models.DateTimeField(
        auto_now=True,
        help_text="The time at which this project was last modified."
    )
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Free-form textual information associated with the project."
    )
    public = models.BooleanField(
        default=False,
        help_text="True if the project is public to its team."
    )
    start_on = models.DateField(
        null=True,
        blank=True,
        help_text="The day on which work for this project begins."
    )
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='projects',
        help_text="The workspace or organization this project is associated with."
    )

    class Meta:
        db_table = 'projects'
        ordering = ['name']

    def __str__(self):
        return self.name or self.gid
