"""
Reactions URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReactionsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'reactions', ReactionsViewSet, basename='reactions')

urlpatterns = router.urls
