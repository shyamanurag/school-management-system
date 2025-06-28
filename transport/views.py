from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
from .models import TransportVendor, Vehicle, Driver, TransportRoute, StudentTransport, BusStop
from core.models import SchoolSettings, Student
import csv

@login_required
def transport_dashboard(request):
    \"\"\"Transport Management Dashboard\"\"\"
    school_settings = SchoolSettings.objects.first()
    
    # Core Statistics
    total_vehicles = Vehicle.objects.count()
    active_vehicles = Vehicle.objects.filter(is_active=True).count()
    total_drivers = Driver.objects.count()
    active_drivers = Driver.objects.filter(is_active=True).count()
    total_routes = TransportRoute.objects.count()
    active_routes = TransportRoute.objects.filter(is_active=True).count()
    total_students = StudentTransport.objects.filter(is_active=True).count()
    
    # Recent data
    recent_vehicles = Vehicle.objects.select_related('vendor').order_by('-created_at')[:10]
    recent_routes = TransportRoute.objects.order_by('-created_at')[:10]
    
    context = {
        'page_title': 'Transport Management Dashboard',
        'school_settings': school_settings,
        'stats': {
            'total_vehicles': total_vehicles,
            'active_vehicles': active_vehicles,
            'total_drivers': total_drivers,
            'active_drivers': active_drivers,
            'total_routes': total_routes,
            'active_routes': active_routes,
            'total_students': total_students,
        },
        'recent_vehicles': recent_vehicles,
        'recent_routes': recent_routes,
    }
    
    return render(request, 'transport/dashboard.html', context)

class VehicleListView(ListView):
    model = Vehicle
    template_name = 'transport/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 20
    
    def get_queryset(self):
        return Vehicle.objects.select_related('vendor').order_by('vehicle_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Vehicle Management'
        return context

class VehicleDetailView(DetailView):
    model = Vehicle
    template_name = 'transport/vehicle_detail.html'
    context_object_name = 'vehicle'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.get_object()
        context['page_title'] = f'Vehicle: {vehicle.vehicle_number}'
        return context

class RouteListView(ListView):
    model = TransportRoute
    template_name = 'transport/route_list.html'
    context_object_name = 'routes'
    paginate_by = 20
    
    def get_queryset(self):
        return TransportRoute.objects.annotate(
            student_count=Count('student_subscriptions', filter=Q(student_subscriptions__is_active=True))
        ).order_by('route_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Route Management'
        return context

class RouteDetailView(DetailView):
    model = TransportRoute
    template_name = 'transport/route_detail.html'
    context_object_name = 'route'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route = self.get_object()
        
        # Students on this route
        context['students'] = StudentTransport.objects.filter(
            route=route, is_active=True
        ).select_related('student')
        
        context['page_title'] = f'Route: {route.route_name}'
        return context

class StudentTransportListView(ListView):
    model = StudentTransport
    template_name = 'transport/student_assignments.html'
    context_object_name = 'assignments'
    paginate_by = 25
    
    def get_queryset(self):
        return StudentTransport.objects.select_related(
            'student', 'route'
        ).filter(is_active=True).order_by('student__first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Student Transport Assignments'
        return context

@login_required
def assign_transport(request):
    \"\"\"Assign transport to students\"\"\"
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        route_id = request.POST.get('route_id')
        
        if student_id and route_id:
            student = get_object_or_404(Student, id=student_id)
            route = get_object_or_404(TransportRoute, id=route_id)
            
            # Check if student already has transport
            existing = StudentTransport.objects.filter(
                student=student, is_active=True
            ).first()
            
            if existing:
                messages.warning(request, f'{student.first_name} {student.last_name} already has transport assigned')
            else:
                StudentTransport.objects.create(
                    student=student,
                    route=route,
                    subscription_type='MONTHLY',
                    transport_type='BOTH_WAYS',
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date().replace(month=12, day=31),
                    monthly_fee=route.monthly_fee,
                    total_fee=route.monthly_fee,
                    net_fee=route.monthly_fee,
                    emergency_contact_1=student.contact_number or '+911234567890'
                )
                messages.success(request, f'Transport assigned to {student.first_name} {student.last_name}')
            
            return redirect('transport:student-assignments')
    
    # GET request
    students = Student.objects.filter(is_active=True).order_by('first_name')
    routes = TransportRoute.objects.filter(is_active=True).order_by('route_name')
    
    context = {
        'page_title': 'Assign Transport',
        'students': students,
        'routes': routes,
    }
    
    return render(request, 'transport/assign_transport.html', context)

@login_required
def transport_reports(request):
    \"\"\"Transport Reports\"\"\"
    return render(request, 'transport/reports.html', {'page_title': 'Transport Reports'})

@login_required
def export_transport_data(request):
    \"\"\"Export transport data to CSV\"\"\"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=\"transport_data_export.csv\"'
    
    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Route', 'Subscription Type', 'Monthly Fee', 'Status'])
    
    assignments = StudentTransport.objects.select_related('student', 'route').filter(is_active=True)
    for assignment in assignments:
        writer.writerow([
            f\"{assignment.student.first_name} {assignment.student.last_name}\",
            assignment.route.route_name,
            assignment.get_subscription_type_display(),
            assignment.monthly_fee,
            'Active' if assignment.is_active else 'Inactive'
        ])
    
    return response
