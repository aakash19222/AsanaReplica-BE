"""
Jobs URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'jobs', JobsViewSet, basename='jobs')

urlpatterns = router.urls
