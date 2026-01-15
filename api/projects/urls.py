"""
Project URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'projects', ProjectsViewSet, basename='project')

urlpatterns = router.urls
