"""
TeamMemberships URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamMembershipsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'team_memberships', TeamMembershipsViewSet, basename='teammemberships')

urlpatterns = router.urls
