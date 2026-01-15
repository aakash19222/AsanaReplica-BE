"""
Jobs serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Job


class JobCompactSerializer(serializers.ModelSerializer):
    """
    Job compact serializer.
    Matches JobCompact Pydantic model.
    """
    class Meta:
        model = Job
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class JobResponseSerializer(serializers.ModelSerializer):
    """
    Job full response serializer.
    Matches JobResponse Pydantic model.
    """
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
