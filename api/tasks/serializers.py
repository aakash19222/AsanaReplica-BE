"""
Task serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaNamedResourceSerializer
from .models import Task
from api.users.serializers import UserCompactSerializer
from api.projects.serializers import ProjectCompactSerializer
from api.tags.serializers import TagCompactSerializer


class TaskCompactSerializer(serializers.ModelSerializer):
    """
    Task compact serializer.
    Matches TaskCompact Pydantic model.
    """
    class Meta:
        model = Task
        fields = ['gid', 'resource_type', 'name']
        read_only_fields = ['gid', 'resource_type']


class TaskResponseSerializer(serializers.ModelSerializer):
    """
    Task full response serializer.
    Matches TaskResponse Pydantic model.
    """
    assignee = UserCompactSerializer(read_only=True)
    created_by = UserCompactSerializer(read_only=True)
    completed_by = UserCompactSerializer(read_only=True)
    assigned_by = UserCompactSerializer(read_only=True)
    workspace = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    dependencies = serializers.SerializerMethodField()
    dependents = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'gid', 'resource_type', 'name', 'resource_subtype',
            'approval_status', 'assignee_status', 'completed',
            'completed_at', 'created_at', 'due_at', 'due_on',
            'html_notes', 'liked', 'modified_at', 'notes',
            'num_likes', 'num_subtasks', 'start_at', 'start_on',
            'actual_time_minutes', 'permalink_url',
            'assignee', 'created_by', 'completed_by', 'assigned_by',
            'workspace', 'projects', 'tags', 'followers',
            'dependencies', 'dependents', 'parent'
        ]
        read_only_fields = [
            'gid', 'resource_type', 'created_at', 'modified_at',
            'completed_at', 'num_likes', 'num_subtasks'
        ]
    
    def get_workspace(self, obj):
        """Get workspace compact representation."""
        if obj.workspace:
            return {
                'gid': obj.workspace.gid,
                'resource_type': 'workspace',
                'name': obj.workspace.name
            }
        return None
    
    def get_projects(self, obj):
        """Get projects for this task."""
        from .models import TaskProject
        from api.projects.models import Project
        project_ids = TaskProject.objects.filter(task=obj).values_list('project_id', flat=True)
        projects = Project.objects.filter(id__in=project_ids)
        return ProjectCompactSerializer(projects, many=True).data
    
    def get_tags(self, obj):
        """Get tags for this task."""
        from .models import TaskTag
        from api.tags.models import Tag
        tag_ids = TaskTag.objects.filter(task=obj).values_list('tag_id', flat=True)
        tags = Tag.objects.filter(id__in=tag_ids)
        return TagCompactSerializer(tags, many=True).data
    
    def get_followers(self, obj):
        """Get followers for this task."""
        from .models import TaskFollower
        from api.users.models import User
        user_ids = TaskFollower.objects.filter(task=obj).values_list('user_id', flat=True)
        users = User.objects.filter(id__in=user_ids)
        return UserCompactSerializer(users, many=True).data
    
    def get_dependencies(self, obj):
        """Get dependencies as compact resources."""
        from .models import TaskDependency
        dependencies = TaskDependency.objects.filter(depends_on=obj)
        return [{'gid': dep.task.gid, 'resource_type': 'task'} for dep in dependencies]
    
    def get_dependents(self, obj):
        """Get dependents as compact resources."""
        from .models import TaskDependency
        dependents = TaskDependency.objects.filter(depends_on=obj)
        return [{'gid': dep.task.gid, 'resource_type': 'task'} for dep in dependents]
    
    def get_parent(self, obj):
        """Get parent task."""
        if obj.parent:
            return {
                'gid': obj.parent.gid,
                'resource_type': 'task',
                'name': obj.parent.name
            }
        return None


class CreateTaskRequestSerializer(serializers.Serializer):
    """
    Create task request serializer.
    Matches CreateTaskRequest Pydantic model.
    """
    data = serializers.DictField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)
    workspace = serializers.CharField(required=False, allow_null=True)
    projects = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True
    )
    parent = serializers.CharField(required=False, allow_null=True)
    assignee = serializers.CharField(required=False, allow_null=True)
    due_on = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_null=True)
