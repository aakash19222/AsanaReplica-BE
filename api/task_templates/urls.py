"""
TaskTemplates URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskTemplatesViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'task_templates', TaskTemplatesViewSet, basename='tasktemplates')

urlpatterns = router.urls
