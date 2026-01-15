"""
Webhooks serializers matching FastAPI/Pydantic models exactly.
"""
from rest_framework import serializers
from common.serializers import AsanaResourceSerializer
from .models import Webhook


class WebhookCompactSerializer(serializers.ModelSerializer):
    """
    Webhook compact serializer.
    Matches WebhookCompact Pydantic model.
    """
    class Meta:
        model = Webhook
        fields = ['gid', 'resource_type']
        read_only_fields = ['gid', 'resource_type']


class WebhookResponseSerializer(serializers.ModelSerializer):
    """
    Webhook full response serializer.
    Matches WebhookResponse Pydantic model.
    """
    class Meta:
        model = Webhook
        fields = '__all__'
        read_only_fields = ['gid', 'resource_type']
