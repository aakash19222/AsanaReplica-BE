"""
Event models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Event(models.Model):
    """
    Event model matching EventResponse Pydantic model.
    Events represent changes to resources in Asana.
    """
    ACTION_CHOICES = [
        ('added', 'Added'),
        ('changed', 'Changed'),
        ('deleted', 'Deleted'),
        ('undeleted', 'Undeleted'),
    ]

    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='event',
        help_text="The base type of this resource."
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text="The type of action taken on the resource."
    )
    resource = models.JSONField(
        help_text="The resource that triggered the event."
    )
    parent = models.JSONField(
        null=True,
        blank=True,
        help_text="The parent of the resource, if applicable."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The time at which this event occurred."
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        help_text="The user who triggered the event."
    )

    class Meta:
        db_table = 'events'
        ordering = ['-created_at']

    def __str__(self):
        return f"Event {self.gid} - {self.action}"
