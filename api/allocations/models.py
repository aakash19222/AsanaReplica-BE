"""
Allocation models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Allocation(models.Model):
    """
    Allocation model matching AllocationResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='allocation',
        help_text="The base type of this resource."
    )
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='allocations',
        help_text="The task this allocation belongs to."
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='allocations',
        help_text="The user this allocation belongs to."
    )
    time_period = models.ForeignKey(
        'time_periods.TimePeriod',
        on_delete=models.CASCADE,
        related_name='allocations',
        help_text="The time period this allocation belongs to."
    )
    effort_allocation = models.FloatField(
        null=True,
        blank=True,
        help_text="The effort allocation in hours."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'allocations'
        unique_together = ['task', 'user', 'time_period']
        ordering = ['-created_at']

    def __str__(self):
        return f"Allocation {self.gid}"
