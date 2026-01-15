"""
Batch API models matching FastAPI Pydantic models.
"""
from django.db import models
import uuid
from common.models import generate_gid


class BatchRequest(models.Model):
    """
    Batch Request model matching BatchRequest Pydantic model.
    """
    gid = models.CharField(
        max_length=255,
        unique=True,
        default=generate_gid,
        help_text="Globally unique identifier of the resource, as a string."
    )
    actions = models.JSONField(
        help_text="Array of actions to perform."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'batch_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Batch Request {self.gid}"


class BatchResponse(models.Model):
    """
    Batch Response model matching BatchResponse Pydantic model.
    """
    batch_request = models.OneToOneField(
        BatchRequest,
        on_delete=models.CASCADE,
        related_name='batch_response',
        help_text="The batch request this response belongs to."
    )
    responses = models.JSONField(
        help_text="Array of responses from the batch request."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'batch_responses'

    def __str__(self):
        return f"Batch Response for {self.batch_request.gid}"
