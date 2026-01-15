"""
Rates URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RatesViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'rates', RatesViewSet, basename='rates')

urlpatterns = router.urls
