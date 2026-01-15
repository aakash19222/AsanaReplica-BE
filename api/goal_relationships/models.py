"""
Goal Relationship models matching FastAPI Pydantic models.
"""
from django.db import models
from common.models import generate_gid


class GoalRelationship(models.Model):
    """
    Goal Relationship model matching GoalRelationshipResponse Pydantic model.
    """
    SUPPORTING_RESOURCE_TYPE_CHOICES = [
        ('project', 'Project'),
        ('task', 'Task'),
    ]

    CONTRIBUTOR_TYPE_CHOICES = [
        ('project', 'Project'),
        ('task', 'Task'),
    ]

    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource."
    )
    resource_type = models.CharField(
        max_length=50,
        default='goal_relationship',
        help_text="The base type of this resource."
    )
    contribution_weight = models.FloatField(
        null=True,
        blank=True,
        help_text="The weight that the supporting resource's progress contributes to the supported goal."
    )
    supporting_resource = models.JSONField(
        null=True,
        blank=True,
        help_text="The supporting resource that contributes to the goal."
    )
    supported_goal = models.ForeignKey(
        'goals.Goal',
        on_delete=models.CASCADE,
        related_name='goal_relationships',
        help_text="The goal that is being supported."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'goal_relationships'
        ordering = ['-created_at']

    def __str__(self):
        return f"Goal Relationship {self.gid}"
