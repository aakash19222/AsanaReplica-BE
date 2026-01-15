"""
CustomFieldSettings serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import CustomFieldSetting


class CustomFieldSettingCompactSerializer(serializers.ModelSerializer):
    """
    CustomFieldSetting compact serializer.
    Matches CustomFieldSettingCompact Pydantic model.
    """
    class Meta:
        model = CustomFieldSetting
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class CustomFieldSettingResponseSerializer(serializers.ModelSerializer):
    """
    CustomFieldSetting full response serializer.
    Matches CustomFieldSettingResponse Pydantic model.
    """
    class Meta:
        model = CustomFieldSetting
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
