"""
Reactions serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Reaction


class ReactionCompactSerializer(serializers.ModelSerializer):
    """
    Reaction compact serializer.
    Matches ReactionCompact Pydantic model.
    """
    class Meta:
        model = Reaction
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class ReactionResponseSerializer(serializers.ModelSerializer):
    """
    Reaction full response serializer.
    Matches ReactionResponse Pydantic model.
    """
    class Meta:
        model = Reaction
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
