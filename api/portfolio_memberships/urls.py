"""
PortfolioMemberships URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PortfolioMembershipsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'portfolio_memberships', PortfolioMembershipsViewSet, basename='portfoliomemberships')

urlpatterns = router.urls
