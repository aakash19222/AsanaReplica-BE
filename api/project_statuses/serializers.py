"""
ProjectStatuses serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import ProjectStatus


class ProjectStatusCompactSerializer(serializers.ModelSerializer):
    """
    ProjectStatus compact serializer.
    Matches ProjectStatusCompact Pydantic model.
    """
    class Meta:
        model = ProjectStatus
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class ProjectStatusResponseSerializer(serializers.ModelSerializer):
    """
    ProjectStatus full response serializer.
    Matches ProjectStatusResponse Pydantic model.
    """
    class Meta:
        model = ProjectStatus
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
