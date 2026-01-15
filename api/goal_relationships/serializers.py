"""
GoalRelationships serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import GoalRelationship


class GoalRelationshipCompactSerializer(serializers.ModelSerializer):
    """
    GoalRelationship compact serializer.
    Matches GoalRelationshipCompact Pydantic model.
    """
    class Meta:
        model = GoalRelationship
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class GoalRelationshipResponseSerializer(serializers.ModelSerializer):
    """
    GoalRelationship full response serializer.
    Matches GoalRelationshipResponse Pydantic model.
    """
    class Meta:
        model = GoalRelationship
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
