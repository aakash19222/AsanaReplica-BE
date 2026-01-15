"""
Audit Log models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class AuditLogEvent(models.Model):
    """
    Audit Log Event model matching AuditLogEventResponse Pydantic model.
    """
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('deleted', 'Deleted'),
        ('changed', 'Changed'),
        ('added', 'Added'),
        ('removed', 'Removed'),
    ]

    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='audit_log_event',
        help_text="The base type of this resource."
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text="The type of action taken."
    )
    actor = models.JSONField(
        null=True,
        blank=True,
        help_text="The user or application that triggered the event."
    )
    context = models.JSONField(
        null=True,
        blank=True,
        help_text="The context of the event."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The time at which this event occurred."
    )
    details = models.JSONField(
        null=True,
        blank=True,
        help_text="The details of the event."
    )
    resource = models.JSONField(
        null=True,
        blank=True,
        help_text="The resource that was affected."
    )

    class Meta:
        db_table = 'audit_log_events'
        ordering = ['-created_at']

    def __str__(self):
        return f"Audit Log Event {self.gid} - {self.action}"
