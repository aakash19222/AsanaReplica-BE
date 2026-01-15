"""
UserTaskLists serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import UserTaskList


class UserTaskListCompactSerializer(serializers.ModelSerializer):
    """
    UserTaskList compact serializer.
    Matches UserTaskListCompact Pydantic model.
    """
    class Meta:
        model = UserTaskList
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class UserTaskListResponseSerializer(serializers.ModelSerializer):
    """
    UserTaskList full response serializer.
    Matches UserTaskListResponse Pydantic model.
    """
    class Meta:
        model = UserTaskList
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
