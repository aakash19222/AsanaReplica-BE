"""
ProjectTemplates URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectTemplatesViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'project_templates', ProjectTemplatesViewSet, basename='projecttemplates')

urlpatterns = router.urls
