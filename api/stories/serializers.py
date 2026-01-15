"""
Story serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Story
from api.users.serializers import UserCompactSerializer
from api.tasks.serializers import TaskCompactSerializer


class StoryCompactSerializer(serializers.ModelSerializer):
    """
    Story compact serializer.
    Matches StoryCompact Pydantic model.
    """
    class Meta:
        model = Story
        fields = ['gid', 'resource_type', 'created_at', 'resource_subtype']
        read_only_fields = ['gid', 'resource_type', 'created_at']


class StoryResponseSerializer(serializers.ModelSerializer):
    """
    Story full response serializer.
    Matches StoryResponse Pydantic model.
    """
    created_by = UserCompactSerializer(read_only=True)
    task = TaskCompactSerializer(read_only=True)
    
    class Meta:
        model = Story
        fields = [
            'gid', 'resource_type', 'created_at', 'resource_subtype',
            'text', 'html_text', 'is_pinned', 'sticker_name',
            'created_by', 'task'
        ]
        read_only_fields = ['gid', 'resource_type', 'created_at', 'created_by']


class UpdateStoryRequestSerializer(serializers.Serializer):
    """
    Update story request serializer.
    Matches UpdateStoryRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    text = serializers.CharField(required=False, allow_null=True)
    html_text = serializers.CharField(required=False, allow_null=True)
    is_pinned = serializers.BooleanField(required=False, allow_null=True)
