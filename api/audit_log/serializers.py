"""
AuditLog serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import AuditLogEvent


class AuditLogCompactSerializer(serializers.ModelSerializer):
    """
    AuditLog compact serializer.
    Matches AuditLogCompact Pydantic model.
    """
    class Meta:
        model = AuditLogEvent
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class AuditLogResponseSerializer(serializers.ModelSerializer):
    """
    AuditLog full response serializer.
    Matches AuditLogResponse Pydantic model.
    """
    class Meta:
        model = AuditLogEvent
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
