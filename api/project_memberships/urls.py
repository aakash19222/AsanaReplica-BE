"""
ProjectMemberships URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectMembershipsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'project_memberships', ProjectMembershipsViewSet, basename='projectmemberships')

urlpatterns = router.urls
