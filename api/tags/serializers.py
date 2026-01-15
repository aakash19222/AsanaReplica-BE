"""
Tag serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaNamedResourceSerializer
from .models import Tag


class TagCompactSerializer(serializers.ModelSerializer):
    """
    Tag compact serializer.
    Matches TagCompact Pydantic model.
    """
    class Meta:
        model = Tag
        fields = ['gid', 'resource_type', 'name']
        read_only_fields = ['gid', 'resource_type']


class TagResponseSerializer(serializers.ModelSerializer):
    """
    Tag full response serializer.
    Matches TagResponse Pydantic model.
    """
    class Meta:
        model = Tag
        fields = ['gid', 'resource_type', 'name', 'color']
        read_only_fields = ['gid', 'resource_type']
