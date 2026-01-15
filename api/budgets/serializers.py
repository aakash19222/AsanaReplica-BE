"""
Budgets serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Budget


class BudgetCompactSerializer(serializers.ModelSerializer):
    """
    Budget compact serializer.
    Matches BudgetCompact Pydantic model.
    """
    class Meta:
        model = Budget
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class BudgetResponseSerializer(serializers.ModelSerializer):
    """
    Budget full response serializer.
    Matches BudgetResponse Pydantic model.
    """
    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
