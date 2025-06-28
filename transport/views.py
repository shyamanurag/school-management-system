from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum, Avg, F
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import TransportVendor, Vehicle, Driver, TransportRoute, StudentTransport, BusStop, VehicleRouteAssignment, Route, RouteStop, BusTracking, MaintenanceRecord, FuelRecord, DriverSchedule, EmergencyContact
from core.models import Student, SchoolSettings, Grade
import csv
from django.http import HttpResponse, JsonResponse

def transport_dashboard(request):
    """Advanced Transport Management Dashboard"""
    school_settings = SchoolSettings.objects.first()
    
    # Vehicle Statistics
    vehicle_stats = {
        'total_vehicles': Vehicle.objects.count(),
        'active_vehicles': Vehicle.objects.filter(status='active').count(),
        'maintenance_vehicles': Vehicle.objects.filter(status='maintenance').count(),
        'inactive_vehicles': Vehicle.objects.filter(status='inactive').count(),
        'total_capacity': Vehicle.objects.filter(status='active').aggregate(
            total=Sum('capacity')
        )['total'] or 0,
    }
    
    # Driver Statistics
    driver_stats = {
        'total_drivers': Driver.objects.count(),
        'active_drivers': Driver.objects.filter(is_active=True).count(),
        'on_duty_drivers': DriverSchedule.objects.filter(
            date=timezone.now().date(),
            is_present=True
        ).count(),
        'available_drivers': Driver.objects.filter(
            is_active=True,
            current_status='available'
        ).count(),
    }
    
    # Route Statistics
    route_stats = {
        'total_routes': Route.objects.count(),
        'active_routes': Route.objects.filter(is_active=True).count(),
        'total_students': StudentTransport.objects.filter(is_active=True).count(),
        'total_stops': RouteStop.objects.count(),
    }
    
    # Today's Schedule
    today = timezone.now().date()
    todays_schedules = DriverSchedule.objects.filter(
        date=today
    ).select_related('driver', 'vehicle', 'route')
    
    # Recent Maintenance
    recent_maintenance = MaintenanceRecord.objects.select_related(
        'vehicle'
    ).order_by('-maintenance_date')[:10]
    
    # Vehicle Tracking Status
    vehicle_tracking = BusTracking.objects.filter(
        timestamp__date=today
    ).select_related('vehicle', 'route').order_by('-timestamp')[:20]
    
    # Monthly Fuel Consumption
    current_month = timezone.now().replace(day=1)
    monthly_fuel = FuelRecord.objects.filter(
        date__gte=current_month
    ).aggregate(
        total_liters=Sum('liters'),
        total_cost=Sum('cost')
    )
    
    # Route Efficiency Analysis
    route_efficiency = Route.objects.annotate(
        student_count=Count('studenttransport', 
                          filter=Q(studenttransport__is_active=True)),
        vehicle_capacity=F('vehicle__capacity')
    ).filter(is_active=True)
    
    # Emergency Alerts (vehicles overdue for maintenance)
    overdue_maintenance = Vehicle.objects.filter(
        next_maintenance_date__lt=today,
        status='active'
    )
    
    # Fuel alerts (low fuel vehicles)
    low_fuel_vehicles = Vehicle.objects.filter(
        fuel_level__lt=20,  # Less than 20%
        status='active'
    )
    
    context = {
        'page_title': 'Transport Management Dashboard',
        'school_settings': school_settings,
        'vehicle_stats': vehicle_stats,
        'driver_stats': driver_stats,
        'route_stats': route_stats,
        'todays_schedules': todays_schedules,
        'recent_maintenance': recent_maintenance,
        'vehicle_tracking': vehicle_tracking,
        'monthly_fuel': monthly_fuel,
        'route_efficiency': route_efficiency,
        'overdue_maintenance': overdue_maintenance,
        'low_fuel_vehicles': low_fuel_vehicles,
    }
    
    return render(request, 'transport/dashboard.html', context)

def vehicles_list(request):
    """List all vehicles"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    vehicles = Vehicle.objects.filter(is_active=True).order_by('vehicle_number')
    
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
    drivers = Driver.objects.filter(is_active=True).order_by('first_name')
    
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
    assignments = StudentTransport.objects.filter(is_active=True).select_related('student', 'route').order_by('student__first_name')
    
    context = {
        'school_settings': school_settings,
        'assignments': assignments,
        'page_title': 'Student Transport Assignments'
    }
    return render(request, 'transport/student_assignments.html', context)

def transport_reports(request):
    """Transport Reports and Analytics"""
    # Date range filtering
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    report_type = request.GET.get('report_type', 'summary')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Fuel consumption analysis
    fuel_records = FuelRecord.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('vehicle')
    
    total_fuel_cost = fuel_records.aggregate(total=Sum('cost'))['total'] or 0
    total_fuel_liters = fuel_records.aggregate(total=Sum('liters'))['total'] or 0
    
    # Vehicle-wise fuel consumption
    vehicle_fuel = fuel_records.values(
        'vehicle__registration_number'
    ).annotate(
        total_cost=Sum('cost'),
        total_liters=Sum('liters')
    ).order_by('-total_cost')
    
    # Maintenance costs
    maintenance_records = MaintenanceRecord.objects.filter(
        maintenance_date__range=[start_date, end_date]
    ).select_related('vehicle')
    
    total_maintenance_cost = maintenance_records.aggregate(
        total=Sum('cost')
    )['total'] or 0
    
    # Route efficiency analysis
    route_efficiency = Route.objects.annotate(
        student_count=Count('studenttransport', 
                          filter=Q(studenttransport__is_active=True)),
        capacity=F('vehicle__capacity'),
        utilization=F('student_count') * 100.0 / F('vehicle__capacity')
    ).filter(is_active=True).order_by('-utilization')
    
    # Driver performance (trips completed)
    driver_performance = DriverSchedule.objects.filter(
        date__range=[start_date, end_date],
        is_present=True
    ).values(
        'driver__name'
    ).annotate(
        trips_completed=Count('id')
    ).order_by('-trips_completed')
    
    context = {
        'page_title': 'Transport Reports & Analytics',
        'start_date': start_date,
        'end_date': end_date,
        'report_type': report_type,
        'total_fuel_cost': total_fuel_cost,
        'total_fuel_liters': total_fuel_liters,
        'total_maintenance_cost': total_maintenance_cost,
        'vehicle_fuel': vehicle_fuel,
        'route_efficiency': route_efficiency,
        'driver_performance': driver_performance,
    }
    
    return render(request, 'transport/transport_reports.html', context)

class RouteListView(ListView):
    model = Route
    template_name = 'transport/route_list.html'
    context_object_name = 'routes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Route.objects.select_related('vehicle').annotate(
            student_count=Count('studenttransport', 
                              filter=Q(studenttransport__is_active=True)),
            stop_count=Count('routestop'),
            capacity_utilization=F('student_count') * 100.0 / F('vehicle__capacity')
        )
        
        status_filter = self.request.GET.get('status', '')
        search_query = self.request.GET.get('search', '')
        
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status_filter == 'full':
            queryset = queryset.filter(capacity_utilization__gte=90)
        elif status_filter == 'underutilized':
            queryset = queryset.filter(capacity_utilization__lt=50)
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(route_code__icontains=search_query) |
                Q(start_location__icontains=search_query) |
                Q(end_location__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Route Management'
        return context

class RouteDetailView(DetailView):
    model = Route
    template_name = 'transport/route_detail.html'
    context_object_name = 'route'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route = self.object
        
        # Route stops
        context['stops'] = RouteStop.objects.filter(
            route=route
        ).order_by('stop_order')
        
        # Students on this route
        context['students'] = StudentTransport.objects.filter(
            route=route,
            is_active=True
        ).select_related('student', 'student__grade', 'pickup_stop', 'drop_stop')
        
        # Route efficiency metrics
        total_capacity = route.vehicle.capacity if route.vehicle else 0
        current_students = context['students'].count()
        context['capacity_utilization'] = (current_students / total_capacity * 100) if total_capacity > 0 else 0
        
        # Recent tracking data for this route
        context['recent_tracking'] = BusTracking.objects.filter(
            route=route
        ).order_by('-timestamp')[:10]
        
        context['page_title'] = f'Route: {route.name}'
        return context

class RouteCreateView(CreateView):
    model = TransportRoute
    fields = ['route_name', 'route_code', 'start_location', 'end_location', 'total_distance_km']
    template_name = 'transport/route_form.html'
    success_url = reverse_lazy('transport:route-list')

class RouteUpdateView(UpdateView):
    model = TransportRoute
    fields = ['route_name', 'route_code', 'start_location', 'end_location', 'total_distance_km']
    template_name = 'transport/route_form.html'
    success_url = reverse_lazy('transport:route-list')

class RouteDeleteView(DeleteView):
    model = TransportRoute
    template_name = 'transport/route_confirm_delete.html'
    success_url = reverse_lazy('transport:route-list')

class VehicleListView(ListView):
    model = Vehicle
    template_name = 'transport/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Vehicle.objects.annotate(
            total_students=Count('route__studenttransport', 
                               filter=Q(route__studenttransport__is_active=True)),
            maintenance_count=Count('maintenancerecord'),
            fuel_cost_month=Sum('fuelrecord__cost', 
                              filter=Q(fuelrecord__date__gte=timezone.now().replace(day=1)))
        )
        
        status_filter = self.request.GET.get('status', '')
        vehicle_type_filter = self.request.GET.get('type', '')
        search_query = self.request.GET.get('search', '')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if vehicle_type_filter:
            queryset = queryset.filter(vehicle_type=vehicle_type_filter)
        if search_query:
            queryset = queryset.filter(
                Q(registration_number__icontains=search_query) |
                Q(model__icontains=search_query) |
                Q(make__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Vehicle Management'
        context['vehicle_types'] = Vehicle.VEHICLE_TYPE_CHOICES
        context['status_choices'] = Vehicle.STATUS_CHOICES
        return context

class VehicleDetailView(DetailView):
    model = Vehicle
    template_name = 'transport/vehicle_detail.html'
    context_object_name = 'vehicle'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.object
        
        # Maintenance History
        context['maintenance_history'] = MaintenanceRecord.objects.filter(
            vehicle=vehicle
        ).order_by('-maintenance_date')[:20]
        
        # Fuel Records
        context['fuel_records'] = FuelRecord.objects.filter(
            vehicle=vehicle
        ).order_by('-date')[:20]
        
        # Current Route Assignment
        current_route = Route.objects.filter(
            vehicle=vehicle,
            is_active=True
        ).first()
        context['current_route'] = current_route
        
        # Students using this vehicle
        if current_route:
            context['students_on_route'] = StudentTransport.objects.filter(
                route=current_route,
                is_active=True
            ).select_related('student', 'pickup_stop', 'drop_stop')
        
        # Recent tracking data
        context['recent_tracking'] = BusTracking.objects.filter(
            vehicle=vehicle
        ).order_by('-timestamp')[:10]
        
        context['page_title'] = f'Vehicle: {vehicle.registration_number}'
        return context

@login_required
def assign_transport(request):
    """Assign transport to students"""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        route_id = request.POST.get('route_id')
        pickup_stop_id = request.POST.get('pickup_stop_id')
        drop_stop_id = request.POST.get('drop_stop_id')
        
        if all([student_id, route_id, pickup_stop_id, drop_stop_id]):
            student = get_object_or_404(Student, id=student_id)
            route = get_object_or_404(TransportRoute, id=route_id)
            pickup_stop = get_object_or_404(BusStop, id=pickup_stop_id)
            drop_stop = get_object_or_404(BusStop, id=drop_stop_id)
            
            # Check if student already has transport assignment
            existing = StudentTransport.objects.filter(
                student=student, is_active=True
            ).first()
            
            if existing:
                messages.warning(request, f'{student.full_name} already has transport assigned')
            else:
                StudentTransport.objects.create(
                    student=student,
                    route=route,
                    pickup_stop=pickup_stop,
                    drop_stop=drop_stop
                )
                messages.success(request, f'Transport assigned to {student.full_name}')
            
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

class StudentTransportListView(ListView):
    model = StudentTransport
    template_name = 'transport/student_assignments.html'
    context_object_name = 'assignments'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = StudentTransport.objects.select_related(
            'student', 'route', 'pickup_stop', 'drop_stop'
        ).filter(is_active=True).order_by('student__first_name')
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__admission_number__icontains=search) |
                Q(route__route_name__icontains=search)
            )
        
        # Route filter
        route_id = self.request.GET.get('route')
        if route_id:
            queryset = queryset.filter(route_id=route_id)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Student Transport Assignments'
        context['routes'] = TransportRoute.objects.filter(is_active=True).order_by('route_name')
        context['total_assignments'] = StudentTransport.objects.filter(is_active=True).count()
        return context

@login_required
def remove_transport_assignment(request, assignment_id):
    """Remove transport assignment"""
    assignment = get_object_or_404(StudentTransport, id=assignment_id)
    
    if request.method == 'POST':
        assignment.is_active = False
        assignment.save()
        messages.success(request, f'Transport assignment removed for {assignment.student.full_name}')
        return redirect('transport:student-assignments')
    
    context = {
        'page_title': 'Remove Transport Assignment',
        'assignment': assignment,
    }
    
    return render(request, 'transport/remove_assignment.html', context)

@login_required
def export_transport_data(request):
    """Export transport data to CSV"""
    data_type = request.GET.get('type', 'students')
    
    response = HttpResponse(content_type='text/csv')
    
    if data_type == 'students':
        response['Content-Disposition'] = 'attachment; filename="student_transport.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Student Name', 'Student ID', 'Grade', 'Route', 'Pickup Stop',
            'Drop Stop', 'Transport Fee', 'Status'
        ])
        
        students = StudentTransport.objects.filter(
            is_active=True
        ).select_related('student', 'student__grade', 'route', 'pickup_stop', 'drop_stop')
        
        for student_transport in students:
            writer.writerow([
                f"{student_transport.student.first_name} {student_transport.student.last_name}",
                student_transport.student.student_id,
                student_transport.student.grade.name if student_transport.student.grade else '',
                student_transport.route.name,
                student_transport.pickup_stop.name if student_transport.pickup_stop else '',
                student_transport.drop_stop.name if student_transport.drop_stop else '',
                student_transport.monthly_fee,
                'Active' if student_transport.is_active else 'Inactive'
            ])
    
    elif data_type == 'vehicles':
        response['Content-Disposition'] = 'attachment; filename="vehicle_data.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Registration Number', 'Make', 'Model', 'Year', 'Capacity',
            'Vehicle Type', 'Status', 'Current Route', 'Last Maintenance',
            'Next Maintenance', 'Fuel Level'
        ])
        
        vehicles = Vehicle.objects.select_related('route')
        
        for vehicle in vehicles:
            current_route = Route.objects.filter(vehicle=vehicle, is_active=True).first()
            writer.writerow([
                vehicle.registration_number,
                vehicle.make,
                vehicle.model,
                vehicle.year,
                vehicle.capacity,
                vehicle.get_vehicle_type_display(),
                vehicle.get_status_display(),
                current_route.name if current_route else '',
                vehicle.last_maintenance_date,
                vehicle.next_maintenance_date,
                f"{vehicle.fuel_level}%"
            ])
    
    return response

@login_required
def transport_analytics_api(request):
    """API endpoint for transport analytics data"""
    # Monthly fuel and maintenance costs
    monthly_data = []
    for i in range(12):
        month_start = (timezone.now().replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        fuel_cost = FuelRecord.objects.filter(
            date__range=[month_start, month_end]
        ).aggregate(total=Sum('cost'))['total'] or 0
        
        maintenance_cost = MaintenanceRecord.objects.filter(
            maintenance_date__range=[month_start, month_end]
        ).aggregate(total=Sum('cost'))['total'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'fuel_cost': float(fuel_cost),
            'maintenance_cost': float(maintenance_cost),
            'total_cost': float(fuel_cost + maintenance_cost)
        })
    
    # Vehicle status distribution
    vehicle_status = Vehicle.objects.values('status').annotate(
        count=Count('id')
    )
    
    # Route utilization
    route_utilization = Route.objects.annotate(
        student_count=Count('studenttransport', 
                          filter=Q(studenttransport__is_active=True)),
        capacity=F('vehicle__capacity')
    ).values('name', 'student_count', 'capacity')
    
    return JsonResponse({
        'monthly_trends': list(reversed(monthly_data)),
        'vehicle_status': list(vehicle_status),
        'route_utilization': list(route_utilization),
        'status': 'success'
    })
