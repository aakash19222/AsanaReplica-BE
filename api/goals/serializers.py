"""
Goals serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Goal


class GoalCompactSerializer(serializers.ModelSerializer):
    """
    Goal compact serializer.
    Matches GoalCompact Pydantic model.
    """
    class Meta:
        model = Goal
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class GoalResponseSerializer(serializers.ModelSerializer):
    """
    Goal full response serializer.
    Matches GoalResponse Pydantic model.
    """
    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
