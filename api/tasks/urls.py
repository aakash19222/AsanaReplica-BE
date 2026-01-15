"""
Task URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TasksViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'tasks', TasksViewSet, basename='task')

urlpatterns = router.urls
