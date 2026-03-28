"""
Main URL configuration for content monitoring system.
"""
from django.urls import path, include
from monitoring.views import DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('api/', include('monitoring.urls')),
]
