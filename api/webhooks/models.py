"""
Webhook models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Webhook(models.Model):
    """
    Webhook model matching WebhookResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='webhook',
        help_text="The base type of this resource."
    )
    active = models.BooleanField(
        default=True,
        help_text="Whether the webhook is active."
    )
    resource = models.JSONField(
        help_text="The resource that triggers the webhook."
    )
    target = models.URLField(
        help_text="The URL to receive the webhook."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The time at which this resource was created."
    )
    last_failure_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The timestamp when the webhook last received an error."
    )
    last_failure_content = models.TextField(
        null=True,
        blank=True,
        help_text="The contents of the last error response."
    )
    last_success_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The timestamp when the webhook last successfully received an event."
    )

    class Meta:
        db_table = 'webhooks'
        ordering = ['-created_at']

    def __str__(self):
        return f"Webhook {self.gid}"
