"""
Team serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaNamedResourceSerializer
from .models import Team
from api.workspaces.serializers import WorkspaceCompactSerializer


class TeamCompactSerializer(serializers.ModelSerializer):
    """
    Team compact serializer.
    Matches TeamCompact Pydantic model.
    """
    class Meta:
        model = Team
        fields = ['gid', 'resource_type', 'name']
        read_only_fields = ['gid', 'resource_type']


class TeamResponseSerializer(serializers.ModelSerializer):
    """
    Team full response serializer.
    Matches TeamResponse Pydantic model.
    """
    organization = WorkspaceCompactSerializer(read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'gid', 'resource_type', 'name', 'description',
            'html_description', 'organization', 'permalink_url',
            'visibility', 'created_at', 'updated_at'
        ]
        read_only_fields = ['gid', 'resource_type', 'created_at', 'updated_at']


class CreateTeamRequestSerializer(serializers.Serializer):
    """
    Create team request serializer.
    Matches CreateTeamRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)
    organization = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)


class AddUserForTeamRequestSerializer(serializers.Serializer):
    """
    Add user for team request serializer.
    Matches AddUserForTeamRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    user = serializers.CharField(required=False, allow_null=True)


class RemoveUserForTeamRequestSerializer(serializers.Serializer):
    """
    Remove user for team request serializer.
    Matches RemoveUserForTeamRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    user = serializers.CharField(required=False, allow_null=True)
