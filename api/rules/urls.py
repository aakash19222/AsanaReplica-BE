"""
Rules URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RulesViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'rules', RulesViewSet, basename='rules')

urlpatterns = router.urls
