"""
Project Membership models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class ProjectMembership(models.Model):
    """
    Project Membership model matching ProjectMembershipResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='project_membership',
        help_text="The base type of this resource."
    )
    write_access = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=[
            ('full_write', 'Full Write'),
            ('comment_only', 'Comment Only'),
        ],
        help_text="Whether the user has full access to the project or comment-only access."
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='project_memberships',
        help_text="The project in the membership."
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='project_memberships',
        help_text="The user in the membership."
    )
    section = models.ForeignKey(
        'sections.Section',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_memberships',
        help_text="The section in the membership."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_memberships'
        ordering = ['-created_at']

    def __str__(self):
        return f"Project Membership {self.gid}"
