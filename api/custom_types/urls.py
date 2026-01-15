"""
CustomTypes URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomTypesViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'custom_types', CustomTypesViewSet, basename='customtypes')

urlpatterns = router.urls
