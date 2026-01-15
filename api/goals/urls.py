"""
Goals URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoalsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'goals', GoalsViewSet, basename='goals')

urlpatterns = router.urls
