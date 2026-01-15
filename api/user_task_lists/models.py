"""
User Task List models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class UserTaskList(models.Model):
    """
    User Task List model matching UserTaskListResponse Pydantic model.
    Represents a user's "My Tasks" list.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='user_task_list',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="The name of the user task list."
    )
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='user_task_lists',
        help_text="The owner of the user task list."
    )
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='user_task_lists',
        help_text="The workspace this user task list belongs to."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_task_lists'
        unique_together = ['owner', 'workspace']
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.owner}"
