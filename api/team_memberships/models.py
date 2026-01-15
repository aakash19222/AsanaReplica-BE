"""
Team Membership models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class TeamMembership(models.Model):
    """
    Team Membership model matching TeamMembershipResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='team_membership',
        help_text="The base type of this resource."
    )
    is_admin = models.BooleanField(
        default=False,
        help_text="Whether the user is an admin of the team."
    )
    is_guest = models.BooleanField(
        default=False,
        help_text="Whether the user is a guest of the team."
    )
    is_limited_access = models.BooleanField(
        default=False,
        help_text="Whether the user has limited access to the team."
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='team_memberships',
        help_text="The user in the team membership."
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='team_memberships',
        help_text="The team in the membership."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'team_memberships'
        unique_together = ['user', 'team']
        ordering = ['-created_at']

    def __str__(self):
        return f"Team Membership {self.gid}"
