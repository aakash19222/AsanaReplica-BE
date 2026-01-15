"""
Custom Field models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class CustomField(models.Model):
    """
    Custom Field model matching CustomFieldResponse Pydantic model.
    """
    TYPE_CHOICES = [
        ('text', 'Text'),
        ('enum', 'Enum'),
        ('multi_enum', 'Multi Enum'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('people', 'People'),
        ('formula', 'Formula'),
    ]

    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='custom_field',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="The name of the custom field."
    )
    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        help_text="The type of the custom field."
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="The description of the custom field."
    )
    enabled = models.BooleanField(
        default=True,
        help_text="Whether the custom field is enabled."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='custom_fields',
        help_text="The workspace this custom field belongs to."
    )

    class Meta:
        db_table = 'custom_fields'
        ordering = ['name']

    def __str__(self):
        return self.name or self.gid


class CustomFieldEnumOption(models.Model):
    """
    Custom Field Enum Option model.
    """
    custom_field = models.ForeignKey(
        CustomField,
        on_delete=models.CASCADE,
        related_name='enum_options',
        help_text="The custom field this option belongs to."
    )
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="The name of the enum option."
    )
    enabled = models.BooleanField(
        default=True,
        help_text="Whether the enum option is enabled."
    )
    color = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Color of the enum option."
    )
    insert_before = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inserted_after',
        help_text="The enum option to insert before."
    )
    insert_after = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inserted_before',
        help_text="The enum option to insert after."
    )

    class Meta:
        db_table = 'custom_field_enum_options'
        ordering = ['name']

    def __str__(self):
        return f"{self.custom_field.name} - {self.name}"
