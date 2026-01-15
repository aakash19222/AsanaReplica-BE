"""
Webhooks URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebhooksViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'webhooks', WebhooksViewSet, basename='webhooks')

urlpatterns = router.urls
