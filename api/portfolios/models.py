"""
Portfolio models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Portfolio(models.Model):
    """
    Portfolio model matching PortfolioResponse Pydantic model.
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

    PRIVACY_CHOICES = [
        ('public_to_domain', 'Public To Domain'),
        ('members_only', 'Members Only'),
    ]

    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='portfolio',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="The name of the portfolio."
    )
    archived = models.BooleanField(
        default=False,
        help_text="True if the portfolio is archived."
    )
    color = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=COLOR_CHOICES,
        help_text="Color of the portfolio."
    )
    start_on = models.DateField(
        null=True,
        blank=True,
        help_text="The day on which work for this portfolio begins."
    )
    due_on = models.DateField(
        null=True,
        blank=True,
        help_text="The day on which this portfolio is due."
    )
    default_access_level = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=[
            ('admin', 'Admin'),
            ('editor', 'Editor'),
            ('viewer', 'Viewer'),
        ],
        help_text="The default access level when inviting new members."
    )
    privacy_setting = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=PRIVACY_CHOICES,
        help_text="The privacy setting of the portfolio."
    )
    public = models.BooleanField(
        default=False,
        help_text="True if the portfolio is public to its workspace members."
    )
    permalink_url = models.URLField(
        null=True,
        blank=True,
        help_text="A url that points directly to the object within Asana."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Foreign keys
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='portfolios',
        help_text="The workspace this portfolio belongs to."
    )
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_portfolios',
        help_text="The owner of the portfolio."
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='portfolios_created',
        help_text="The user who created the portfolio."
    )

    class Meta:
        db_table = 'portfolios'
        ordering = ['name']

    def __str__(self):
        return self.name or self.gid


class PortfolioProject(models.Model):
    """
    Many-to-many relationship between portfolios and projects.
    """
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='portfolio_projects'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='project_portfolios'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'portfolio_projects'
        unique_together = ['portfolio', 'project']
