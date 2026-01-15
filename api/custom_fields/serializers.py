"""
CustomFields serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import CustomField


class CustomFieldCompactSerializer(serializers.ModelSerializer):
    """
    CustomField compact serializer.
    Matches CustomFieldCompact Pydantic model.
    """
    class Meta:
        model = CustomField
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class CustomFieldResponseSerializer(serializers.ModelSerializer):
    """
    CustomField full response serializer.
    Matches CustomFieldResponse Pydantic model.
    """
    class Meta:
        model = CustomField
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
