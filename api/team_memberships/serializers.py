"""
TeamMemberships serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import TeamMembership


class TeamMembershipCompactSerializer(serializers.ModelSerializer):
    """
    TeamMembership compact serializer.
    Matches TeamMembershipCompact Pydantic model.
    """
    class Meta:
        model = TeamMembership
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class TeamMembershipResponseSerializer(serializers.ModelSerializer):
    """
    TeamMembership full response serializer.
    Matches TeamMembershipResponse Pydantic model.
    """
    class Meta:
        model = TeamMembership
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
