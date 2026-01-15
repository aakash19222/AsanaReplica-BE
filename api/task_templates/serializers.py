"""
TaskTemplates serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import TaskTemplate


class TaskTemplateCompactSerializer(serializers.ModelSerializer):
    """
    TaskTemplate compact serializer.
    Matches TaskTemplateCompact Pydantic model.
    """
    class Meta:
        model = TaskTemplate
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class TaskTemplateResponseSerializer(serializers.ModelSerializer):
    """
    TaskTemplate full response serializer.
    Matches TaskTemplateResponse Pydantic model.
    """
    class Meta:
        model = TaskTemplate
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
