"""
GoalRelationships URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoalRelationshipsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'goal_relationships', GoalRelationshipsViewSet, basename='goalrelationships')

urlpatterns = router.urls
