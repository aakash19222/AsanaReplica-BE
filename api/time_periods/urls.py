"""
TimePeriods URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TimePeriodsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'time_periods', TimePeriodsViewSet, basename='timeperiods')

urlpatterns = router.urls
