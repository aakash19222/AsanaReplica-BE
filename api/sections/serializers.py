"""
Section serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaNamedResourceSerializer
from .models import Section
from api.projects.serializers import ProjectCompactSerializer


class SectionCompactSerializer(serializers.ModelSerializer):
    """
    Section compact serializer.
    Matches SectionCompact Pydantic model.
    """
    class Meta:
        model = Section
        fields = ['gid', 'resource_type', 'name']
        read_only_fields = ['gid', 'resource_type']


class SectionResponseSerializer(serializers.ModelSerializer):
    """
    Section full response serializer.
    Matches SectionResponse Pydantic model.
    """
    project = ProjectCompactSerializer(read_only=True)
    
    class Meta:
        model = Section
        fields = ['gid', 'resource_type', 'name', 'created_at', 'project']
        read_only_fields = ['gid', 'resource_type', 'created_at']


class UpdateSectionRequestSerializer(serializers.Serializer):
    """
    Update section request serializer.
    Matches UpdateSectionRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)


class InsertSectionForProjectRequestSerializer(serializers.Serializer):
    """
    Insert section for project request serializer.
    Matches InsertSectionForProjectRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    section = serializers.CharField(required=False, allow_null=True)
    insert_before = serializers.CharField(required=False, allow_null=True)
    insert_after = serializers.CharField(required=False, allow_null=True)


class AddTaskForSectionRequestSerializer(serializers.Serializer):
    """
    Add task for section request serializer.
    Matches AddTaskForSectionRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    task = serializers.CharField(required=False, allow_null=True)
    insert_before = serializers.CharField(required=False, allow_null=True)
    insert_after = serializers.CharField(required=False, allow_null=True)
