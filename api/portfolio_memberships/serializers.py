"""
PortfolioMemberships serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import PortfolioMembership


class PortfolioMembershipCompactSerializer(serializers.ModelSerializer):
    """
    PortfolioMembership compact serializer.
    Matches PortfolioMembershipCompact Pydantic model.
    """
    class Meta:
        model = PortfolioMembership
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class PortfolioMembershipResponseSerializer(serializers.ModelSerializer):
    """
    PortfolioMembership full response serializer.
    Matches PortfolioMembershipResponse Pydantic model.
    """
    class Meta:
        model = PortfolioMembership
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
