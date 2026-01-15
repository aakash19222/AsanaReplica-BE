"""
Portfolios URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PortfoliosViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'portfolios', PortfoliosViewSet, basename='portfolios')

urlpatterns = router.urls
