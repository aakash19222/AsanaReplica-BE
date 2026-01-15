"""
Rule models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class Rule(models.Model):
    """
    Rule model matching RuleResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='rule',
        help_text="The base type of this resource."
    )
    name = models.CharField(
        max_length=255,
        help_text="The name of the rule."
    )
    enabled = models.BooleanField(
        default=True,
        help_text="Whether the rule is enabled."
    )
    trigger = models.JSONField(
        help_text="The trigger configuration for the rule."
    )
    action = models.JSONField(
        help_text="The action configuration for the rule."
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='rules',
        help_text="The project this rule belongs to."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rules'
        ordering = ['name']

    def __str__(self):
        return self.name or self.gid
