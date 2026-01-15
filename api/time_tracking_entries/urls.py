"""
TimeTrackingEntries URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TimeTrackingEntriesViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'time_tracking_entries', TimeTrackingEntriesViewSet, basename='timetrackingentries')

urlpatterns = router.urls
