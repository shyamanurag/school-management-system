from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import TransportVendor, Vehicle, Driver, TransportRoute, StudentTransport

def transport_dashboard(request):
    """Transport management dashboard"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    
    # Statistics
    total_vehicles = Vehicle.objects.filter(is_active=True).count()
    total_drivers = Driver.objects.filter(is_active=True).count()
    total_routes = TransportRoute.objects.filter(is_active=True).count()
    total_vendors = TransportVendor.objects.filter(is_active=True).count()
    
    # Active assignments
    active_students = StudentTransport.objects.filter(is_active=True).count()
    
    # Recent data
    recent_vehicles = Vehicle.objects.filter(is_active=True).order_by('-created_at')[:5]
    recent_routes = TransportRoute.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    context = {
        'school_settings': school_settings,
        'total_vehicles': total_vehicles,
        'total_drivers': total_drivers,
        'total_routes': total_routes,
        'total_vendors': total_vendors,
        'active_students': active_students,
        'recent_vehicles': recent_vehicles,
        'recent_routes': recent_routes,
        'page_title': 'Transport Management Dashboard'
    }
    return render(request, 'transport/dashboard.html', context)

def vehicles_list(request):
    """List all vehicles"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    vehicles = Vehicle.objects.filter(is_active=True).select_related('vendor', 'driver').order_by('vehicle_number')
    
    context = {
        'school_settings': school_settings,
        'vehicles': vehicles,
        'page_title': 'Fleet Management - Vehicles'
    }
    return render(request, 'transport/vehicles_list.html', context)

def drivers_list(request):
    """List all drivers"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    drivers = Driver.objects.filter(is_active=True).order_by('name')
    
    context = {
        'school_settings': school_settings,
        'drivers': drivers,
        'page_title': 'Driver Management'
    }
    return render(request, 'transport/drivers_list.html', context)

def routes_list(request):
    """List all transport routes"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    routes = TransportRoute.objects.filter(is_active=True).order_by('route_name')
    
    context = {
        'school_settings': school_settings,
        'routes': routes,
        'page_title': 'Route Management'
    }
    return render(request, 'transport/routes_list.html', context)

def vendors_list(request):
    """List all transport vendors"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    vendors = TransportVendor.objects.filter(is_active=True).order_by('name')
    
    context = {
        'school_settings': school_settings,
        'vendors': vendors,
        'page_title': 'Vendor Management'
    }
    return render(request, 'transport/vendors_list.html', context)

def student_transport_list(request):
    """List all student transport assignments"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    assignments = StudentTransport.objects.filter(is_active=True).select_related('student', 'route', 'vehicle').order_by('student__first_name')
    
    context = {
        'school_settings': school_settings,
        'assignments': assignments,
        'page_title': 'Student Transport Assignments'
    }
    return render(request, 'transport/student_assignments.html', context)

def transport_reports(request):
    """Transport reports and analytics"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    
    # Route-wise student count
    route_stats = TransportRoute.objects.annotate(
        student_count=Count('student_transports', filter=Q(student_transports__is_active=True))
    ).filter(is_active=True)
    
    # Vehicle utilization
    vehicle_stats = Vehicle.objects.annotate(
        student_count=Count('student_transports', filter=Q(student_transports__is_active=True))
    ).filter(is_active=True)
    
    context = {
        'school_settings': school_settings,
        'route_stats': route_stats,
        'vehicle_stats': vehicle_stats,
        'page_title': 'Transport Reports & Analytics'
    }
    return render(request, 'transport/reports.html', context)

class RouteListView(ListView):
    model = TransportRoute
    template_name = 'transport/route_list.html'
    context_object_name = 'routes'

class RouteCreateView(CreateView):
    model = TransportRoute
    fields = ['route_name', 'pickup_points', 'drop_points', 'distance_km']
    template_name = 'transport/route_form.html'
    success_url = reverse_lazy('route-list')

class RouteUpdateView(UpdateView):
    model = TransportRoute
    fields = ['route_name', 'pickup_points', 'drop_points', 'distance_km']
    template_name = 'transport/route_form.html'
    success_url = reverse_lazy('route-list')

class RouteDeleteView(DeleteView):
    model = TransportRoute
    template_name = 'transport/route_confirm_delete.html'
    success_url = reverse_lazy('route-list')
