"""
Allocations URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AllocationsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'allocations', AllocationsViewSet, basename='allocations')

urlpatterns = router.urls
