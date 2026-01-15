"""
Attachment models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Attachment(models.Model):
    """
    Attachment model matching AttachmentResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='attachment',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=500,
        help_text="The name of the file."
    )
    resource_subtype = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="The service hosting the attachment."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The time at which this resource was created."
    )
    download_url = models.URLField(
        null=True,
        blank=True,
        help_text="The URL containing the content of the attachment."
    )
    host = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="The service hosting the attachment."
    )
    parent = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text="The task this attachment is attached to."
    )
    permanent_url = models.URLField(
        null=True,
        blank=True,
        help_text="The service hosting the attachment."
    )
    view_url = models.URLField(
        null=True,
        blank=True,
        help_text="The URL where the attachment can be viewed."
    )
    size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="The size of the attachment in bytes."
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attachments_created',
        help_text="The user who created the attachment."
    )

    class Meta:
        db_table = 'attachments'
        ordering = ['-created_at']

    def __str__(self):
        return self.name or self.gid
