"""
Teams URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'teams', TeamsViewSet, basename='teams')

urlpatterns = router.urls
