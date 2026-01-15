"""
CustomFieldSettings URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomFieldSettingsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'custom_field_settings', CustomFieldSettingsViewSet, basename='customfieldsettings')

urlpatterns = router.urls
