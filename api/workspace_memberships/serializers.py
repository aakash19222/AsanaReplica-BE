"""
WorkspaceMemberships serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import WorkspaceMembership


class WorkspaceMembershipCompactSerializer(serializers.ModelSerializer):
    """
    WorkspaceMembership compact serializer.
    Matches WorkspaceMembershipCompact Pydantic model.
    """
    class Meta:
        model = WorkspaceMembership
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class WorkspaceMembershipResponseSerializer(serializers.ModelSerializer):
    """
    WorkspaceMembership full response serializer.
    Matches WorkspaceMembershipResponse Pydantic model.
    """
    class Meta:
        model = WorkspaceMembership
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
