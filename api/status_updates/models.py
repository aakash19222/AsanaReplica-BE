"""
Status Update models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class StatusUpdate(models.Model):
    """
    Status Update model matching StatusUpdateResponse Pydantic model.
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
        default='status_update',
        help_text="The base type of this resource."
    )
    title = models.CharField(
        max_length=255,
        help_text="The title of the status update."
    )
    text = models.TextField(
        help_text="The text content of the status update."
    )
    html_text = models.TextField(
        null=True,
        blank=True,
        help_text="The text content of the status update with formatting as HTML."
    )
    status_type = models.CharField(
        max_length=50,
        default='on_track',
        choices=[
            ('on_track', 'On Track'),
            ('at_risk', 'At Risk'),
            ('off_track', 'Off Track'),
            ('on_hold', 'On Hold'),
            ('complete', 'Complete'),
            ('achieved', 'Achieved'),
            ('partial', 'Partial'),
            ('missed', 'Missed'),
            ('dropped', 'Dropped'),
        ],
        help_text="The type associated with the status update."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='status_updates_created',
        help_text="The user who created the status update."
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='status_updates',
        help_text="The user who authored the status update."
    )
    parent = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='status_updates',
        help_text="The project this status update belongs to."
    )
    portfolio = models.ForeignKey(
        'portfolios.Portfolio',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='status_updates',
        help_text="The portfolio this status update belongs to."
    )
    goal = models.ForeignKey(
        'goals.Goal',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='status_updates',
        help_text="The goal this status update belongs to."
    )

    class Meta:
        db_table = 'status_updates'
        ordering = ['-created_at']

    def __str__(self):
        return f"Status Update {self.title}"
