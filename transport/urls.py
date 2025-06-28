from django.urls import path
from .simple_views import simple_transport_dashboard

# Simple Transport URLs to avoid database errors
urlpatterns = [
    # Transport Dashboard
    path("", simple_transport_dashboard, name="dashboard"),
]
