"""
Rate models matching FastAPI Pydantic models.
"""
from django.db import models
from decimal import Decimal
import uuid
from common.models import generate_gid


class Rate(models.Model):
    """
    Rate model matching RateResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='rate',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="The name of the rate."
    )
    rate = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="The rate amount."
    )
    currency_code = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        help_text="The currency code of the rate."
    )
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='rates',
        help_text="The workspace this rate belongs to."
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rates',
        help_text="The user this rate belongs to."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rates'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.rate} {self.currency_code or ''}"
