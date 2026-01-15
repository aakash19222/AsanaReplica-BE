"""
Project Brief models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class ProjectBrief(models.Model):
    """
    Project Brief model matching ProjectBriefResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='project_brief',
        help_text="The base type of this resource."
    )
    title = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="The title of the project brief."
    )
    html_text = models.TextField(
        null=True,
        blank=True,
        help_text="HTML formatted text for the project brief."
    )
    text = models.TextField(
        null=True,
        blank=True,
        help_text="Plain text of the project brief."
    )
    permalink_url = models.URLField(
        null=True,
        blank=True,
        help_text="A url that points directly to the object within Asana."
    )
    project = models.OneToOneField(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='project_brief',
        help_text="The project this brief belongs to."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_briefs'
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f"Brief for {self.project}"
