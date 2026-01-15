"""
Reaction models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Reaction(models.Model):
    """
    Reaction model matching ReactionResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='reaction',
        help_text="The base type of this resource."
    )
    emoji = models.CharField(
        max_length=10,
        help_text="The emoji used for the reaction."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Foreign keys - can be on task, story, status update, etc.
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='reactions',
        help_text="The user who created the reaction."
    )
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reactions',
        help_text="The task this reaction belongs to."
    )
    story = models.ForeignKey(
        'stories.Story',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reactions',
        help_text="The story this reaction belongs to."
    )
    status_update = models.ForeignKey(
        'status_updates.StatusUpdate',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reactions',
        help_text="The status update this reaction belongs to."
    )

    class Meta:
        db_table = 'reactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Reaction {self.emoji} by {self.user}"
