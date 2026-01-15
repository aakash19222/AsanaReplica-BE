"""
ProjectMemberships serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import ProjectMembership


class ProjectMembershipCompactSerializer(serializers.ModelSerializer):
    """
    ProjectMembership compact serializer.
    Matches ProjectMembershipCompact Pydantic model.
    """
    class Meta:
        model = ProjectMembership
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class ProjectMembershipResponseSerializer(serializers.ModelSerializer):
    """
    ProjectMembership full response serializer.
    Matches ProjectMembershipResponse Pydantic model.
    """
    class Meta:
        model = ProjectMembership
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
