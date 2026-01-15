"""
TimeTrackingEntries serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import TimeTrackingEntry


class TimeTrackingEntryCompactSerializer(serializers.ModelSerializer):
    """
    TimeTrackingEntry compact serializer.
    Matches TimeTrackingEntryCompact Pydantic model.
    """
    class Meta:
        model = TimeTrackingEntry
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class TimeTrackingEntryResponseSerializer(serializers.ModelSerializer):
    """
    TimeTrackingEntry full response serializer.
    Matches TimeTrackingEntryResponse Pydantic model.
    """
    class Meta:
        model = TimeTrackingEntry
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
