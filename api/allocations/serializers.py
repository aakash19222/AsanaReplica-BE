"""
Allocations serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Allocation


class AllocationCompactSerializer(serializers.ModelSerializer):
    """
    Allocation compact serializer.
    Matches AllocationCompact Pydantic model.
    """
    class Meta:
        model = Allocation
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class AllocationResponseSerializer(serializers.ModelSerializer):
    """
    Allocation full response serializer.
    Matches AllocationResponse Pydantic model.
    """
    class Meta:
        model = Allocation
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
