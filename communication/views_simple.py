from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import SchoolSettings

@login_required
def communication_dashboard(request):
    school_settings = SchoolSettings.objects.first()
    context = {
        "page_title": "Communication Dashboard",
        "school_settings": school_settings,
        "total_notices": 0,
        "active_notices": 0,
        "unread_notifications": 0,
        "recent_notices": [],
        "recent_messages": [],
    }
    return render(request, "communication/dashboard.html", context)
