"""
ProjectBriefs serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import ProjectBrief


class ProjectBriefCompactSerializer(serializers.ModelSerializer):
    """
    ProjectBrief compact serializer.
    Matches ProjectBriefCompact Pydantic model.
    """
    class Meta:
        model = ProjectBrief
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class ProjectBriefResponseSerializer(serializers.ModelSerializer):
    """
    ProjectBrief full response serializer.
    Matches ProjectBriefResponse Pydantic model.
    """
    class Meta:
        model = ProjectBrief
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
