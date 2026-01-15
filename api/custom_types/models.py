"""
Custom Type models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class CustomType(models.Model):
    """
    Custom Type model matching CustomTypeResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='custom_type',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="The name of the custom type."
    )
    enabled = models.BooleanField(
        default=True,
        help_text="Whether the custom type is enabled."
    )
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='custom_types',
        help_text="The workspace this custom type belongs to."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custom_types'
        ordering = ['name']

    def __str__(self):
        return self.name or self.gid


class CustomTypeStatusOption(models.Model):
    """
    Custom Type Status Option model.
    """
    custom_type = models.ForeignKey(
        CustomType,
        on_delete=models.CASCADE,
        related_name='status_options',
        help_text="The custom type this status option belongs to."
    )
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="The name of the status option."
    )
    enabled = models.BooleanField(
        default=True,
        help_text="Whether the status option is enabled."
    )
    color = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Color of the status option."
    )

    class Meta:
        db_table = 'custom_type_status_options'
        ordering = ['name']

    def __str__(self):
        return f"{self.custom_type.name} - {self.name}"
