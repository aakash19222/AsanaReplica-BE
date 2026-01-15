"""
Typeahead URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TypeaheadViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'typeahead', TypeaheadViewSet, basename='typeahead')

urlpatterns = router.urls
