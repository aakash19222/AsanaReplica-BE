"""
Story URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoriesViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'stories', StoriesViewSet, basename='story')

urlpatterns = router.urls
