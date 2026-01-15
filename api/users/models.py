"""
User models matching FastAPI Pydantic models.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
from common.models import generate_gid


class UserManager(BaseUserManager):
    """Custom user manager."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(models.Model):
    """
    User model matching UserResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='user',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The user's name."
    )
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        help_text="The user's email address."
    )
    photo_url = models.URLField(
        null=True,
        blank=True,
        help_text="URL to the user's photo."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['name', 'email']

    def __str__(self):
        return self.name or self.email or self.gid


class UserWorkspace(models.Model):
    """
    Many-to-many relationship between users and workspaces.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_workspaces'
    )

    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='workspace_users'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_workspaces'
        unique_together = ['user', 'workspace']
