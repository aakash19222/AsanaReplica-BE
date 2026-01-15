"""
Membership models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Membership(models.Model):
    """
    Membership model matching MembershipResponse Pydantic model.
    Represents a membership relationship between a user and a resource.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='membership',
        help_text="The base type of this resource."
    )
    role = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=[
            ('admin', 'Admin'),
            ('editor', 'Editor'),
            ('commenter', 'Commenter'),
            ('viewer', 'Viewer'),
        ],
        help_text="The role of the user in the membership."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Foreign keys - can be project, portfolio, goal, etc.
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='generic_memberships',
        help_text="The user in the membership."
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='generic_memberships',
        help_text="The project in the membership."
    )
    portfolio = models.ForeignKey(
        'portfolios.Portfolio',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='generic_memberships',
        help_text="The portfolio in the membership."
    )
    goal = models.ForeignKey(
        'goals.Goal',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='generic_memberships',
        help_text="The goal in the membership."
    )

    class Meta:
        db_table = 'memberships'
        ordering = ['-created_at']

    def __str__(self):
        return f"Membership {self.gid}"
