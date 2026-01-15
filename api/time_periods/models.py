"""
Time Period models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class TimePeriod(models.Model):
    """
    Time Period model matching TimePeriodResponse Pydantic model.
    """
    PERIOD_CHOICES = [
        ('week', 'Week'),
        ('month', 'Month'),
        ('quarter', 'Quarter'),
        ('year', 'Year'),
    ]

    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='time_period',
        help_text="The base type of this resource."
    )
    display_name = models.CharField(
        max_length=255,
        help_text="A string representing the cadence code and the fiscal year."
    )
    end_on = models.DateField(
        help_text="The localized end date of the time period."
    )
    period = models.CharField(
        max_length=50,
        choices=PERIOD_CHOICES,
        help_text="The cadence and index of the time period."
    )
    start_on = models.DateField(
        help_text="The localized start date of the time period."
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text="The parent time period."
    )

    class Meta:
        db_table = 'time_periods'
        ordering = ['-start_on']

    def __str__(self):
        return self.display_name or self.gid
