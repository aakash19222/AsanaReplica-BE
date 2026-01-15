"""
CustomFields URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomFieldsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'custom_fields', CustomFieldsViewSet, basename='customfields')

urlpatterns = router.urls
