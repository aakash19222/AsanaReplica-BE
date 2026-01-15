"""
Workspace URL configuration.
Matches FastAPI routes exactly.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspacesViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'workspaces', WorkspacesViewSet, basename='workspace')

urlpatterns = router.urls
