"""
Typeahead models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Typeahead(models.Model):
    """
    Typeahead model matching TypeaheadForWorkspace200Response Pydantic model.
    Note: This is typically a read-only endpoint, so this model may not be used for storage.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='typeahead',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=500,
        help_text="The name of the resource."
    )
    resource_subtype = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="The subtype of the resource."
    )
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='typeahead_results',
        help_text="The workspace this typeahead result belongs to."
    )

    class Meta:
        db_table = 'typeahead'
        ordering = ['name']

    def __str__(self):
        return self.name or self.gid
