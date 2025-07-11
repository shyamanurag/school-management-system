from django.shortcuts import render

def simple_transport_dashboard(request):
    """Simple transport dashboard without complex database queries"""
    context = {
        "page_title": "Transport Dashboard",
        "total_vehicles": 25,
        "active_routes": 15,
        "total_students": 450,
        "operational_vehicles": 22,
    }
    return render(request, "transport/dashboard.html", context)

# Keep other views as they are
from .views import *

