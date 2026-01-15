"""
Rules serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Rule


class RuleCompactSerializer(serializers.ModelSerializer):
    """
    Rule compact serializer.
    Matches RuleCompact Pydantic model.
    """
    class Meta:
        model = Rule
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class RuleResponseSerializer(serializers.ModelSerializer):
    """
    Rule full response serializer.
    Matches RuleResponse Pydantic model.
    """
    class Meta:
        model = Rule
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
