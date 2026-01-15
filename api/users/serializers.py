"""
User serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaNamedResourceSerializer
from .models import User
from api.workspaces.serializers import WorkspaceCompactSerializer


class UserCompactSerializer(serializers.ModelSerializer):
    """
    User compact serializer.
    Matches UserCompact Pydantic model.
    """
    class Meta:
        model = User
        fields = ['gid', 'resource_type', 'name']
        read_only_fields = ['gid', 'resource_type']


class UserResponseSerializer(serializers.ModelSerializer):
    """
    User full response serializer.
    Matches UserResponse Pydantic model.
    """
    workspaces = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['gid', 'resource_type', 'name', 'email', 'photo_url', 'workspaces']
        read_only_fields = ['gid', 'resource_type', 'email', 'workspaces']
    
    def get_workspaces(self, obj):
        """Get workspaces for this user."""
        from api.workspaces.models import Workspace
        workspaces = Workspace.objects.filter(workspace_users__user=obj).distinct()
        return WorkspaceCompactSerializer(workspaces, many=True).data
    
    def to_representation(self, instance):
        """Customize representation to match FastAPI format."""
        ret = super().to_representation(instance)
        # Rename photo_url to photo object structure if needed
        if ret.get('photo_url'):
            ret['photo'] = {'image_128x128': ret.pop('photo_url')}
        return ret


class UpdateUserRequestSerializer(serializers.Serializer):
    """
    Update user request serializer.
    Matches UpdateUserRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)
