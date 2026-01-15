"""
Export models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Export(models.Model):
    """
    Export model matching ExportResponse Pydantic model.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
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
        default='export',
        help_text="The base type of this resource."
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="The status of the export."
    )
    download_url = models.URLField(
        null=True,
        blank=True,
        help_text="The URL to download the export."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exports'
        ordering = ['-created_at']

    def __str__(self):
        return f"Export {self.gid} - {self.status}"
