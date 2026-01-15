"""
Asana-style pagination for Django REST Framework.

Matches FastAPI pagination format exactly:
- Uses offset tokens (strings) instead of page numbers
- Returns next_page object with offset, path, and uri
- Limit must be between 1 and 100
"""
from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
from typing import Optional, List, Any


class AsanaPagination(BasePagination):
    """
    Asana-style pagination using offset tokens.
    
    Response format:
    {
        "data": [...],
        "next_page": {
            "offset": "...",
            "path": "...",
            "uri": "..."
        } or null
    }
    """
    page_size = 50
    page_size_query_param = 'limit'
    max_page_size = 100
    offset_query_param = 'offset'
    
    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset.
        Returns a page object, or `None` if pagination is not configured.
        """
        self.request = request
        self.queryset = queryset
        
        # Get limit from query params (1-100)
        limit = self.get_page_size(request)
        if limit is None:
            return None
        
        # Get offset token from query params
        offset_token = request.query_params.get(self.offset_query_param)
        
        # Decode offset to get the actual offset value
        if offset_token:
            try:
                offset = int(offset_token)
            except (ValueError, TypeError):
                offset = 0
        else:
            offset = 0
        
        # Apply offset and limit
        self.offset = offset
        self.limit = limit
        
        # Get total count (for determining if there's a next page)
        self.count = self.get_count(queryset)
        
        # Apply pagination
        if offset >= self.count:
            # Offset beyond available items, return empty
            self.page = []
            self.has_next = False
        else:
            self.page = list(queryset[offset:offset + limit])
            self.has_next = (offset + limit) < self.count
        
        return self.page
    
    def get_paginated_response(self, data):
        """
        Return a paginated style Response object with Asana format.
        """
        response_data = {
            'data': data,
        }
        
        # Add next_page if there are more results
        if self.has_next:
            next_offset = str(self.offset + self.limit)
            next_page = self._build_next_page(next_offset)
            response_data['next_page'] = next_page
        else:
            response_data['next_page'] = None
        
        return Response(response_data)
    
    def _build_next_page(self, offset: str) -> dict:
        """
        Build next_page object with offset, path, and uri.
        """
        # Get current request URL
        request = self.request
        parsed_url = urlparse(request.build_absolute_uri())
        query_params = parse_qs(parsed_url.query)
        
        # Update offset in query params
        query_params[self.offset_query_param] = [offset]
        
        # Build path (relative)
        path = parsed_url.path
        if query_params:
            path += '?' + urlencode(query_params, doseq=True)
        
        # Build full URI
        query_string = urlencode(query_params, doseq=True)
        uri = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            query_string,
            parsed_url.fragment
        ))
        
        return {
            'offset': offset,
            'path': path,
            'uri': uri
        }
    
    def get_count(self, queryset):
        """
        Determine the object count for the queryset.
        """
        try:
            return queryset.count()
        except (AttributeError, TypeError):
            return len(queryset)
    
    def get_page_size(self, request):
        """
        Get page size from request, validate it's between 1 and 100.
        """
        if self.page_size_query_param:
            try:
                limit = int(request.query_params.get(self.page_size_query_param, self.page_size))
                # Validate limit is between 1 and 100
                if limit < 1:
                    limit = 1
                elif limit > self.max_page_size:
                    limit = self.max_page_size
                return limit
            except (KeyError, ValueError, TypeError):
                pass
        return self.page_size
