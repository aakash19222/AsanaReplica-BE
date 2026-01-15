"""
Typeahead serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Typeahead


class TypeaheadCompactSerializer(serializers.ModelSerializer):
    """
    Typeahead compact serializer.
    Matches TypeaheadCompact Pydantic model.
    """
    class Meta:
        model = Typeahead
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class TypeaheadResponseSerializer(serializers.ModelSerializer):
    """
    Typeahead full response serializer.
    Matches TypeaheadResponse Pydantic model.
    """
    class Meta:
        model = Typeahead
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
