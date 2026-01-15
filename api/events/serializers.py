"""
Event serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Event


class EventCompactSerializer(serializers.ModelSerializer):
    """
    Event compact serializer.
    Matches EventCompact Pydantic model.
    """
    class Meta:
        model = Event
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class EventResponseSerializer(serializers.ModelSerializer):
    """
    Event response serializer.
    Matches EventResponse Pydantic model.
    """
    class Meta:
        model = Event
        fields = ['gid', 'resource_type', 'action', 'resource', 'parent', 'created_at']
        read_only_fields = ['gid', 'resource_type', 'created_at']
