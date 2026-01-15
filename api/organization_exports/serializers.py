"""
OrganizationExports serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import OrganizationExport


class OrganizationExportCompactSerializer(serializers.ModelSerializer):
    """
    OrganizationExport compact serializer.
    Matches OrganizationExportCompact Pydantic model.
    """
    class Meta:
        model = OrganizationExport
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class OrganizationExportResponseSerializer(serializers.ModelSerializer):
    """
    OrganizationExport full response serializer.
    Matches OrganizationExportResponse Pydantic model.
    """
    class Meta:
        model = OrganizationExport
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
