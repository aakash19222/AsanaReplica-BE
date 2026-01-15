"""
AccessRequests serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import AccessRequest


class AccessRequestCompactSerializer(serializers.ModelSerializer):
    """
    AccessRequest compact serializer.
    Matches AccessRequestCompact Pydantic model.
    """
    class Meta:
        model = AccessRequest
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class AccessRequestResponseSerializer(serializers.ModelSerializer):
    """
    AccessRequest full response serializer.
    Matches AccessRequestResponse Pydantic model.
    """
    class Meta:
        model = AccessRequest
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
