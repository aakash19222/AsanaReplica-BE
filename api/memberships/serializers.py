"""
Memberships serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Membership


class MembershipCompactSerializer(serializers.ModelSerializer):
    """
    Membership compact serializer.
    Matches MembershipCompact Pydantic model.
    """
    class Meta:
        model = Membership
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class MembershipResponseSerializer(serializers.ModelSerializer):
    """
    Membership full response serializer.
    Matches MembershipResponse Pydantic model.
    """
    class Meta:
        model = Membership
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
