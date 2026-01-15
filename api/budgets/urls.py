"""
Budgets URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BudgetsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'budgets', BudgetsViewSet, basename='budgets')

urlpatterns = router.urls
