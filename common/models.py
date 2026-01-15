"""
Common model utilities.
"""
import uuid
from django.db import models


def generate_gid():
    """Generate a unique GID for Asana resources."""
    return str(uuid.uuid4())


class AsanaResourceMixin(models.Model):
    """
    Abstract base model for all Asana resources.
    Provides common fields like gid and resource_type.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        help_text="The base type of this resource."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
