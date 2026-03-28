"""
URL configuration for monitoring app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from monitoring.views import KeywordViewSet, FlagViewSet, ScanAPIView

router = DefaultRouter()
router.register(r'keywords', KeywordViewSet, basename='keyword')
router.register(r'flags', FlagViewSet, basename='flag')

urlpatterns = [
    path('', include(router.urls)),
    path('scan/', ScanAPIView.as_view(), name='scan'),
]
