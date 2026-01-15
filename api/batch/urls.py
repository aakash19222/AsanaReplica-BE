"""
Batch URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BatchViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'batch', BatchViewSet, basename='batch')

urlpatterns = router.urls
