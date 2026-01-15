"""
WorkspaceMemberships URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceMembershipsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'workspace_memberships', WorkspaceMembershipsViewSet, basename='workspacememberships')

urlpatterns = router.urls
