"""
Budget models matching FastAPI Pydantic models.
"""
from django.db import models
from decimal import Decimal
import uuid
from common.models import generate_gid


class Budget(models.Model):
    """
    Budget model matching BudgetResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='budget',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="The name of the budget."
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="The amount of the budget."
    )
    currency_code = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        help_text="The currency code of the budget."
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='budgets',
        help_text="The project this budget belongs to."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budgets'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.amount} {self.currency_code or ''}"
