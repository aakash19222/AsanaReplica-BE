"""
Section models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Section(models.Model):
    """
    Section model matching SectionResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='section',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="The name of the section."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='sections',
        help_text="The project this section belongs to."
    )

    class Meta:
        db_table = 'sections'
        ordering = ['name']

    def __str__(self):
        return self.name or self.gid
