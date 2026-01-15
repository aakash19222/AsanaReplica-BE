"""
User URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsersViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'users', UsersViewSet, basename='user')

urlpatterns = router.urls
