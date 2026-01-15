"""
AuditLog URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'audit_log', AuditLogViewSet, basename='auditlog')

urlpatterns = router.urls
