from django.urls import path
from . import views_simple

app_name = "communication"

urlpatterns = [
    path("", views_simple.communication_dashboard, name="dashboard"),
]
