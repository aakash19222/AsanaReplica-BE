"""
Events URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'events', EventsViewSet, basename='events')

urlpatterns = router.urls
