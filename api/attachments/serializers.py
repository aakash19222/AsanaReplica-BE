"""
Attachment serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Attachment
from api.users.serializers import UserCompactSerializer
from api.tasks.serializers import TaskCompactSerializer


class AttachmentCompactSerializer(serializers.ModelSerializer):
    """
    Attachment compact serializer.
    Matches AttachmentCompact Pydantic model.
    """
    class Meta:
        model = Attachment
        fields = ['gid', 'resource_type', 'name', 'resource_subtype']
        read_only_fields = ['gid', 'resource_type']


class AttachmentResponseSerializer(serializers.ModelSerializer):
    """
    Attachment full response serializer.
    Matches AttachmentResponse Pydantic model.
    """
    created_by = UserCompactSerializer(read_only=True)
    parent = TaskCompactSerializer(read_only=True)
    
    class Meta:
        model = Attachment
        fields = [
            'gid', 'resource_type', 'name', 'resource_subtype',
            'created_at', 'download_url', 'host', 'parent',
            'permanent_url', 'view_url', 'size', 'created_by'
        ]
        read_only_fields = ['gid', 'resource_type', 'created_at', 'created_by']
