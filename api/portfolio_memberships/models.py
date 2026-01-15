"""
Portfolio Membership models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class PortfolioMembership(models.Model):
    """
    Portfolio Membership model matching PortfolioMembershipResponse Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    resource_type = models.CharField(
        max_length=50,
        default='portfolio_membership',
        help_text="The base type of this resource."
    )
    portfolio = models.ForeignKey(
        'portfolios.Portfolio',
        on_delete=models.CASCADE,
        related_name='portfolio_memberships',
        help_text="The portfolio in the membership."
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='portfolio_memberships',
        help_text="The user in the membership."
    )
    access_level = models.CharField(
        max_length=50,
        default='viewer',
        choices=[
            ('admin', 'Admin'),
            ('editor', 'Editor'),
            ('viewer', 'Viewer'),
        ],
        help_text="The access level of the user in the portfolio."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'portfolio_memberships'
        unique_together = ['portfolio', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Portfolio Membership {self.gid}"
