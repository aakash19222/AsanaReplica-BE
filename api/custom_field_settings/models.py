"""
Custom Field Setting models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class CustomFieldSetting(models.Model):
    """
    Custom Field Setting model matching CustomFieldSettingResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='custom_field_setting',
        help_text="The base type of this resource."
    )
    is_important = models.BooleanField(
        default=False,
        help_text="Whether this field should be shown on the task card."
    )
    custom_field = models.ForeignKey(
        'custom_fields.CustomField',
        on_delete=models.CASCADE,
        related_name='settings',
        help_text="The custom field in the setting."
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_field_settings',
        help_text="The project this custom field setting belongs to."
    )
    portfolio = models.ForeignKey(
        'portfolios.Portfolio',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_field_settings',
        help_text="The portfolio this custom field setting belongs to."
    )
    goal = models.ForeignKey(
        'goals.Goal',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_field_settings',
        help_text="The goal this custom field setting belongs to."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'custom_field_settings'
        ordering = ['-created_at']

    def __str__(self):
        return f"Custom Field Setting {self.gid}"
