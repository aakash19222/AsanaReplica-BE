"""
AccessRequests URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccessRequestsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'access_requests', AccessRequestsViewSet, basename='accessrequests')

urlpatterns = router.urls
