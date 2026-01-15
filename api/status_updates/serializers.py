"""
StatusUpdates serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import StatusUpdate


class StatusUpdateCompactSerializer(serializers.ModelSerializer):
    """
    StatusUpdate compact serializer.
    Matches StatusUpdateCompact Pydantic model.
    """
    class Meta:
        model = StatusUpdate
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class StatusUpdateResponseSerializer(serializers.ModelSerializer):
    """
    StatusUpdate full response serializer.
    Matches StatusUpdateResponse Pydantic model.
    """
    class Meta:
        model = StatusUpdate
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
