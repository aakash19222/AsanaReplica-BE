"""
Tag models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Tag(models.Model):
    """
    Tag model matching TagResponse Pydantic model.
    """
    COLOR_CHOICES = [
        ('dark-pink', 'Dark Pink'),
        ('dark-green', 'Dark Green'),
        ('dark-blue', 'Dark Blue'),
        ('dark-red', 'Dark Red'),
        ('dark-teal', 'Dark Teal'),
        ('dark-brown', 'Dark Brown'),
        ('dark-orange', 'Dark Orange'),
        ('dark-purple', 'Dark Purple'),
        ('dark-warm-gray', 'Dark Warm Gray'),
        ('light-pink', 'Light Pink'),
        ('light-green', 'Light Green'),
        ('light-blue', 'Light Blue'),
        ('light-red', 'Light Red'),
        ('light-teal', 'Light Teal'),
        ('light-brown', 'Light Brown'),
        ('light-orange', 'Light Orange'),
        ('light-purple', 'Light Purple'),
        ('light-warm-gray', 'Light Warm Gray'),
    ]

    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='tag',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="The name of the tag."
    )
    color = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=COLOR_CHOICES,
        help_text="Color of the tag."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='tags',
        help_text="The workspace this tag belongs to."
    )
    followers = models.ManyToManyField(
        'users.User',
        related_name='followed_tags',
        blank=True,
        help_text="Array of users following this tag."
    )

    class Meta:
        db_table = 'tags'
        ordering = ['name']

    def __str__(self):
        return self.name or self.gid
