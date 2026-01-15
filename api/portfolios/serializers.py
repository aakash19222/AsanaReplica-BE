"""
Portfolios serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Portfolio


class PortfolioCompactSerializer(serializers.ModelSerializer):
    """
    Portfolio compact serializer.
    Matches PortfolioCompact Pydantic model.
    """
    class Meta:
        model = Portfolio
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class PortfolioResponseSerializer(serializers.ModelSerializer):
    """
    Portfolio full response serializer.
    Matches PortfolioResponse Pydantic model.
    """
    class Meta:
        model = Portfolio
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
