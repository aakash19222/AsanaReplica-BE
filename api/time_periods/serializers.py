"""
TimePeriods serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import TimePeriod


class TimePeriodCompactSerializer(serializers.ModelSerializer):
    """
    TimePeriod compact serializer.
    Matches TimePeriodCompact Pydantic model.
    """
    class Meta:
        model = TimePeriod
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class TimePeriodResponseSerializer(serializers.ModelSerializer):
    """
    TimePeriod full response serializer.
    Matches TimePeriodResponse Pydantic model.
    """
    class Meta:
        model = TimePeriod
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
