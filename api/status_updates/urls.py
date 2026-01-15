"""
StatusUpdates URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StatusUpdatesViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'status_updates', StatusUpdatesViewSet, basename='statusupdates')

urlpatterns = router.urls
