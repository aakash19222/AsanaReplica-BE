"""
Exports serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Export


class ExportCompactSerializer(serializers.ModelSerializer):
    """
    Export compact serializer.
    Matches ExportCompact Pydantic model.
    """
    class Meta:
        model = Export
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class ExportResponseSerializer(serializers.ModelSerializer):
    """
    Export full response serializer.
    Matches ExportResponse Pydantic model.
    """
    class Meta:
        model = Export
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
