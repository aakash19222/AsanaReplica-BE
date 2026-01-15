"""
Base serializers for Asana API responses.

All responses must match FastAPI/Pydantic model format exactly.
"""
from rest_framework import serializers
from typing import Optional, List, Any, Dict


class AsanaResourceSerializer(serializers.Serializer):
    """
    Base serializer for Asana resources.
    Matches AsanaResource Pydantic model.
    """
    gid = serializers.CharField(required=False, allow_null=True, help_text="Globally unique identifier of the resource, as a string.")
    resource_type = serializers.CharField(required=False, allow_null=True, help_text="The base type of this resource.")


class AsanaNamedResourceSerializer(AsanaResourceSerializer):
    """
    Base serializer for named Asana resources.
    Matches AsanaNamedResource Pydantic model.
    """
    name = serializers.CharField(required=False, allow_null=True, help_text="The name of the object.")


class ErrorSerializer(serializers.Serializer):
    """
    Error object serializer.
    Matches Error Pydantic model.
    """
    message = serializers.CharField(required=False, allow_null=True, help_text="Message providing more detail about the error that occurred, if available.")
    help = serializers.CharField(required=False, allow_null=True, help_text="Additional information directing developers to resources on how to address and fix the problem, if available.")
    phrase = serializers.CharField(required=False, allow_null=True, help_text="*500 errors only*. A unique error phrase which can be used when contacting developer support to help identify the exact occurrence of the problem in Asana's logs.")


class ErrorResponseSerializer(serializers.Serializer):
    """
    Error response serializer.
    Matches ErrorResponse Pydantic model.
    """
    errors = ErrorSerializer(many=True, required=False, allow_null=True)


class NextPageSerializer(serializers.Serializer):
    """
    Next page pagination serializer.
    Matches NextPage Pydantic model.
    """
    offset = serializers.CharField(required=False, allow_null=True, help_text="Pagination offset for the request.")
    path = serializers.CharField(required=False, allow_null=True, help_text="A relative path containing the query parameters to fetch for next_page")
    uri = serializers.CharField(required=False, allow_null=True, help_text="A full uri containing the query parameters to fetch for next_page")


def wrap_single_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrap a single resource in Asana response format.
    Matches Get*200Response format for single items.
    
    Example:
    {
        "data": {...}
    }
    """
    return {'data': data}


def wrap_list_response(data: List[Dict[str, Any]], next_page: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Wrap a list of resources in Asana response format.
    Matches Get*200Response format for lists.
    
    Example:
    {
        "data": [...],
        "next_page": {...} or null
    }
    """
    response = {'data': data}
    if next_page is not None:
        response['next_page'] = next_page
    else:
        response['next_page'] = None
    return response


def apply_opt_fields(data: Dict[str, Any], opt_fields: Optional[List[str]]) -> Dict[str, Any]:
    """
    Apply opt_fields filtering to response data.
    
    If opt_fields is provided, only include those fields.
    If opt_fields is None, include all default fields.
    """
    if opt_fields is None:
        return data
    
    # Split comma-separated string if needed
    if isinstance(opt_fields, str):
        opt_fields = [f.strip() for f in opt_fields.split(',')]
    
    # Filter data to only include requested fields
    # Note: This is a simplified implementation
    # In production, you might need to handle nested fields (e.g., "workspace.name")
    filtered_data = {}
    for field in opt_fields:
        if field in data:
            filtered_data[field] = data[field]
        # Handle nested fields (basic support)
        elif '.' in field:
            parts = field.split('.')
            current = data
            try:
                for part in parts:
                    if isinstance(current, dict):
                        current = current.get(part)
                    elif isinstance(current, list) and part.isdigit():
                        current = current[int(part)]
                    else:
                        current = None
                        break
                if current is not None:
                    filtered_data[field] = current
            except (KeyError, IndexError, ValueError, TypeError):
                pass
    
    return filtered_data if filtered_data else data
