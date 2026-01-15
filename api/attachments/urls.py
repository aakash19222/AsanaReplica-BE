"""
Attachment URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttachmentsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'attachments', AttachmentsViewSet, basename='attachment')

urlpatterns = router.urls
