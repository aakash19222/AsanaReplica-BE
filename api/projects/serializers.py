"""
Project serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaNamedResourceSerializer
from .models import Project
from api.users.serializers import UserCompactSerializer
from api.workspaces.serializers import WorkspaceCompactSerializer


class ProjectCompactSerializer(serializers.ModelSerializer):
    """
    Project compact serializer.
    Matches ProjectCompact Pydantic model.
    """
    class Meta:
        model = Project
        fields = ['gid', 'resource_type', 'name']
        read_only_fields = ['gid', 'resource_type']


class ProjectResponseSerializer(serializers.ModelSerializer):
    """
    Project full response serializer.
    Matches ProjectResponse Pydantic model.
    """
    workspace = WorkspaceCompactSerializer(read_only=True)
    members = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'gid', 'resource_type', 'name', 'archived', 'color',
            'created_at', 'due_on', 'html_notes', 'is_template',
            'modified_at', 'notes', 'public', 'start_on',
            'workspace', 'members'
        ]
        read_only_fields = ['gid', 'resource_type', 'created_at', 'modified_at']
    
    def get_members(self, obj):
        """Get members for this project."""
        from api.project_memberships.models import ProjectMembership
        from api.users.models import User
        user_ids = ProjectMembership.objects.filter(project=obj).values_list('user_id', flat=True)
        users = User.objects.filter(id__in=user_ids)
        return UserCompactSerializer(users, many=True).data


class CreateProjectRequestSerializer(serializers.Serializer):
    """
    Create project request serializer.
    Matches CreateProjectRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)
    workspace = serializers.CharField(required=False, allow_null=True)
    team = serializers.CharField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_null=True)
    color = serializers.CharField(required=False, allow_null=True)


class UpdateProjectRequestSerializer(serializers.Serializer):
    """
    Update project request serializer.
    Matches UpdateProjectRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)
    archived = serializers.BooleanField(required=False, allow_null=True)
    color = serializers.CharField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_null=True)
