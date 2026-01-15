"""
Access Request models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class AccessRequest(models.Model):
    """
    Access Request model matching AccessRequestResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='access_request',
        help_text="The base type of this resource."
    )
    resource = models.JSONField(
        help_text="The resource that is being requested access to."
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='access_requests',
        help_text="The user requesting access."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'access_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Access Request {self.gid}"
