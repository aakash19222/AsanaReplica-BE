"""
Memberships URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MembershipsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'memberships', MembershipsViewSet, basename='memberships')

urlpatterns = router.urls
