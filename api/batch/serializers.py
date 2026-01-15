"""
Batch serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import BatchRequest


class BatchCompactSerializer(serializers.ModelSerializer):
    """
    Batch compact serializer.
    Matches BatchCompact Pydantic model.
    """
    class Meta:
        model = BatchRequest
        fields = ['gid']
        read_only_fields = ['gid']


class BatchResponseSerializer(serializers.ModelSerializer):
    """
    Batch full response serializer.
    Matches BatchResponse Pydantic model.
    """
    class Meta:
        model = BatchRequest
        fields = '__all__'
        read_only_fields = ['gid']
