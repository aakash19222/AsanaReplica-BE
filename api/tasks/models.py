"""
Task models matching FastAPI Pydantic models.
"""
from django.db import models
from django.core.validators import MinValueValidator
import uuid
from common.models import generate_gid


class Task(models.Model):
    """
    Task model matching TaskResponse Pydantic model.
    """
    RESOURCE_SUBTYPE_CHOICES = [
        ('default_task', 'Default Task'),
        ('milestone', 'Milestone'),
        ('approval', 'Approval'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('changes_requested', 'Changes Requested'),
    ]

    ASSIGNEE_STATUS_CHOICES = [
        ('today', 'Today'),
        ('upcoming', 'Upcoming'),
        ('later', 'Later'),
        ('new', 'New'),
        ('inbox', 'Inbox'),
    ]

    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='task',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=500,
        help_text="Name of the task."
    )
    resource_subtype = models.CharField(
        max_length=50,
        default='default_task',
        choices=RESOURCE_SUBTYPE_CHOICES,
        help_text="The subtype of this resource."
    )
    approval_status = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=APPROVAL_STATUS_CHOICES,
        help_text="Reflects the approval status of this task."
    )
    assignee_status = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ASSIGNEE_STATUS_CHOICES,
        help_text="Scheduling status of this task for the user it is assigned to."
    )
    completed = models.BooleanField(
        default=False,
        help_text="True if the task is currently marked complete, false if not."
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The time at which this task was completed."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The time at which this resource was created."
    )
    due_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The UTC date and time on which this task is due."
    )
    due_on = models.DateField(
        null=True,
        blank=True,
        help_text="The localized date on which this task is due."
    )
    html_notes = models.TextField(
        null=True,
        blank=True,
        help_text="The notes of the text with formatting as HTML."
    )
    liked = models.BooleanField(
        default=False,
        help_text="True if the task is liked by the authorized user."
    )
    modified_at = models.DateTimeField(
        auto_now=True,
        help_text="The time at which this task was last modified."
    )
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Free-form textual information associated with the task."
    )
    num_likes = models.IntegerField(
        default=0,
        help_text="The number of users who have liked this task."
    )
    num_subtasks = models.IntegerField(
        default=0,
        help_text="The number of subtasks on this task."
    )
    start_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time on which work begins for the task."
    )
    start_on = models.DateField(
        null=True,
        blank=True,
        help_text="The day on which work begins for the task."
    )
    actual_time_minutes = models.FloatField(
        null=True,
        blank=True,
        help_text="Sum of all Time Tracking entries in the Actual Time field."
    )
    permalink_url = models.URLField(
        null=True,
        blank=True,
        help_text="A url that points directly to the object within Asana."
    )
    
    # Foreign keys
    assignee = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        help_text="The user to whom this task is assigned."
    )
    assigned_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assigned',
        help_text="The user who assigned the task."
    )
    completed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_completed',
        help_text="The user who completed the task."
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_created',
        help_text="The user who created the task."
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks',
        help_text="The parent task of this task."
    )
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="The workspace this task is associated with."
    )

    class Meta:
        db_table = 'tasks'
        ordering = ['-modified_at']

    def __str__(self):
        return self.name or self.gid


class TaskDependency(models.Model):
    """
    Task dependency model - tasks that this task depends on.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='dependencies'
    )
    depends_on = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='dependents',
        help_text="The task that this task depends on."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_dependencies'
        unique_together = ['task', 'depends_on']


class TaskProject(models.Model):
    """
    Many-to-many relationship between tasks and projects.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='task_projects'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='project_tasks'
    )
    section = models.ForeignKey(
        'sections.Section',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='task_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_projects'
        unique_together = ['task', 'project']


class TaskFollower(models.Model):
    """
    Task follower model - users following this task.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='task_followers'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='followed_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_followers'
        unique_together = ['task', 'user']


class TaskTag(models.Model):
    """
    Many-to-many relationship between tasks and tags.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='task_tags'
    )
    tag = models.ForeignKey(
        'tags.Tag',
        on_delete=models.CASCADE,
        related_name='tag_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_tags'
        unique_together = ['task', 'tag']


class TaskLike(models.Model):
    """
    Task like model - users who liked this task.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='task_likes'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='liked_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_likes'
        unique_together = ['task', 'user']
