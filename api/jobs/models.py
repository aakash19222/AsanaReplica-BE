"""
Job models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Job(models.Model):
    """
    Job model matching JobResponse Pydantic model.
    Jobs represent processes that handle asynchronous tasks.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
    ]

    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='job',
        help_text="The base type of this resource."
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="The current status of this job."
    )
    new_project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs',
        help_text="The new project created by this job."
    )
    new_task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs',
        help_text="The new task created by this job."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Job {self.gid} - {self.status}"
