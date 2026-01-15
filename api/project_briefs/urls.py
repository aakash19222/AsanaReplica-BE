"""
ProjectBriefs URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectBriefsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'project_briefs', ProjectBriefsViewSet, basename='projectbriefs')

urlpatterns = router.urls
