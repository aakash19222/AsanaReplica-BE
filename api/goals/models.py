"""
Goal models matching FastAPI Pydantic models.
"""
from django.db import models
from common.models import generate_gid


class Goal(models.Model):
    """
    Goal model matching GoalResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='goal',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=500,
        help_text="The name of the goal."
    )
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Free-form textual information associated with the goal."
    )
    html_notes = models.TextField(
        null=True,
        blank=True,
        help_text="The notes of the goal with formatting as HTML."
    )
    due_on = models.DateField(
        null=True,
        blank=True,
        help_text="The localized day on which this goal is due."
    )
    start_on = models.DateField(
        null=True,
        blank=True,
        help_text="The day on which work for this goal begins."
    )
    is_workspace_level = models.BooleanField(
        default=False,
        help_text="Whether this goal is a workspace-level goal."
    )
    liked = models.BooleanField(
        default=False,
        help_text="True if the goal is liked by the authorized user."
    )
    status = models.CharField(
        max_length=50,
        default='green',
        choices=[
            ('green', 'Green'),
            ('yellow', 'Yellow'),
            ('red', 'Red'),
        ],
        help_text="The current status of this goal."
    )
    time_period = models.ForeignKey(
        'time_periods.TimePeriod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='goals',
        help_text="The time period this goal belongs to."
    )
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='goals',
        help_text="The workspace this goal belongs to."
    )
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_goals',
        help_text="The owner of the goal."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'goals'
        ordering = ['name']

    def __str__(self):
        return self.name or self.gid
