"""
Workspace serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaNamedResourceSerializer
from .models import Workspace


class WorkspaceCompactSerializer(serializers.ModelSerializer):
    """
    Workspace compact serializer.
    Matches WorkspaceCompact Pydantic model.
    """
    class Meta:
        model = Workspace
        fields = ['gid', 'resource_type', 'name']
        read_only_fields = ['gid', 'resource_type']


class WorkspaceResponseSerializer(serializers.ModelSerializer):
    """
    Workspace full response serializer.
    Matches WorkspaceResponse Pydantic model.
    """
    class Meta:
        model = Workspace
        fields = ['gid', 'resource_type', 'name', 'email_domains', 'is_organization']
        read_only_fields = ['gid', 'resource_type']


class UpdateWorkspaceRequestSerializer(serializers.Serializer):
    """
    Update workspace request serializer.
    Matches UpdateWorkspaceRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)


class AddUserForWorkspaceRequestSerializer(serializers.Serializer):
    """
    Add user to workspace request serializer.
    Matches AddUserForWorkspaceRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    user = serializers.CharField(required=False, allow_null=True)


class RemoveUserForWorkspaceRequestSerializer(serializers.Serializer):
    """
    Remove user from workspace request serializer.
    Matches RemoveUserForWorkspaceRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    user = serializers.CharField(required=False, allow_null=True)
