"""
Time Tracking Entry models matching FastAPI Pydantic models.
"""
from django.db import models
from django.core.validators import MinValueValidator
import uuid
from common.models import generate_gid


class TimeTrackingEntry(models.Model):
    """
    Time Tracking Entry model matching TimeTrackingEntryResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='time_tracking_entry',
        help_text="The base type of this resource."
    )
    duration_minutes = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Time in minutes tracked by the entry."
    )
    entered_on = models.DateField(
        help_text="The date on which this entry is entered."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Foreign keys
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='time_tracking_entries',
        help_text="The task this time tracking entry belongs to."
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='time_tracking_entries',
        help_text="The user who created this time tracking entry."
    )
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='time_tracking_entries',
        help_text="The workspace this time tracking entry belongs to."
    )

    class Meta:
        db_table = 'time_tracking_entries'
        ordering = ['-entered_on', '-created_at']

    def __str__(self):
        return f"Time Entry {self.gid} - {self.duration_minutes} min"
