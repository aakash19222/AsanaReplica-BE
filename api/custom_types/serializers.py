"""
CustomTypes serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import CustomType


class CustomTypeCompactSerializer(serializers.ModelSerializer):
    """
    CustomType compact serializer.
    Matches CustomTypeCompact Pydantic model.
    """
    class Meta:
        model = CustomType
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class CustomTypeResponseSerializer(serializers.ModelSerializer):
    """
    CustomType full response serializer.
    Matches CustomTypeResponse Pydantic model.
    """
    class Meta:
        model = CustomType
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
