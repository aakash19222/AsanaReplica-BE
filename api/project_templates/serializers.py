"""
ProjectTemplates serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import ProjectTemplate


class ProjectTemplateCompactSerializer(serializers.ModelSerializer):
    """
    ProjectTemplate compact serializer.
    Matches ProjectTemplateCompact Pydantic model.
    """
    class Meta:
        model = ProjectTemplate
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class ProjectTemplateResponseSerializer(serializers.ModelSerializer):
    """
    ProjectTemplate full response serializer.
    Matches ProjectTemplateResponse Pydantic model.
    """
    class Meta:
        model = ProjectTemplate
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
