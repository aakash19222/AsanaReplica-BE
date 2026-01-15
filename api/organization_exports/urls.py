"""
OrganizationExports URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationExportsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'organization_exports', OrganizationExportsViewSet, basename='organizationexports')

urlpatterns = router.urls
