"""
UserTaskLists URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserTaskListsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'user_task_lists', UserTaskListsViewSet, basename='usertasklists')

urlpatterns = router.urls
