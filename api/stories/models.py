"""
Story models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Story(models.Model):
    """
    Story model matching StoryResponse Pydantic model.
    Stories represent the activity stream of a task.
    """
    RESOURCE_SUBTYPE_CHOICES = [
        ('comment_added', 'Comment Added'),
        ('attachment_added', 'Attachment Added'),
        ('dependency_added', 'Dependency Added'),
        ('dependency_removed', 'Dependency Removed'),
        ('dependency_marked_complete', 'Dependency Marked Complete'),
        ('dependency_marked_incomplete', 'Dependency Marked Incomplete'),
        ('duplicate_added', 'Duplicate Added'),
        ('duplicate_removed', 'Duplicate Removed'),
        ('follower_added', 'Follower Added'),
        ('follower_removed', 'Follower Removed'),
        ('liked', 'Liked'),
        ('unliked', 'Unliked'),
        ('marked_complete', 'Marked Complete'),
        ('marked_incomplete', 'Marked Incomplete'),
        ('assigned', 'Assigned'),
        ('unassigned', 'Unassigned'),
        ('section_changed', 'Section Changed'),
        ('section_moved', 'Section Moved'),
        ('added_to_project', 'Added To Project'),
        ('removed_from_project', 'Removed From Project'),
        ('tag_added', 'Tag Added'),
        ('tag_removed', 'Tag Removed'),
        ('custom_field_changed', 'Custom Field Changed'),
        ('custom_field_deleted', 'Custom Field Deleted'),
        ('custom_field_restored', 'Custom Field Restored'),
        ('custom_field_updated', 'Custom Field Updated'),
        ('milestone_added', 'Milestone Added'),
        ('milestone_removed', 'Milestone Removed'),
        ('approval_status_changed', 'Approval Status Changed'),
        ('approval_requested', 'Approval Requested'),
        ('approval_approved', 'Approval Approved'),
        ('approval_rejected', 'Approval Rejected'),
        ('approval_request_removed', 'Approval Request Removed'),
        ('approval_request_updated', 'Approval Request Updated'),
        ('approval_request_removed_from_task', 'Approval Request Removed From Task'),
    ]

    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='story',
        help_text="The base type of this resource."
    )
    resource_subtype = models.CharField(
        max_length=100,
        choices=RESOURCE_SUBTYPE_CHOICES,
        help_text="The subtype of this resource."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The time at which this resource was created."
    )
    text = models.TextField(
        null=True,
        blank=True,
        help_text="The plain text of the comment to add. Cannot be used with html_text."
    )
    html_text = models.TextField(
        null=True,
        blank=True,
        help_text="HTML formatted text for a comment. This will not include the name of the creator."
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text="Whether the story is pinned."
    )
    sticker_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="The name of the sticker in this story."
    )
    
    # Foreign keys
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stories_created',
        help_text="The user who created the story."
    )
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='stories',
        help_text="The task this story belongs to."
    )
    target = models.ForeignKey(
        'tasks.Task',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='target_stories',
        help_text="The target of the story."
    )

    class Meta:
        db_table = 'stories'
        ordering = ['-created_at']

    def __str__(self):
        return f"Story {self.gid} on {self.task}"
