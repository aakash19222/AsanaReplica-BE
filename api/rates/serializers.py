"""
Rates serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Rate


class RateCompactSerializer(serializers.ModelSerializer):
    """
    Rate compact serializer.
    Matches RateCompact Pydantic model.
    """
    class Meta:
        model = Rate
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class RateResponseSerializer(serializers.ModelSerializer):
    """
    Rate full response serializer.
    Matches RateResponse Pydantic model.
    """
    class Meta:
        model = Rate
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
