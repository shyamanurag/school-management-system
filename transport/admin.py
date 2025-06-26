from django.contrib import admin
from .models import (
    TransportVendor,
    Vehicle,
    Driver,
    TransportRoute,
    BusStop,
    VehicleRouteAssignment,
    StudentTransport,
    VehicleTracking,
    TransportAlert,
    VehicleMaintenance,
    TransportReport
)

@admin.register(TransportVendor)
class TransportVendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school', 'contact_person', 'phone', 'is_active']
    list_filter = ['school', 'is_active']
    search_fields = ['name', 'code', 'contact_person']

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_number', 'vehicle_type', 'school', 'vendor', 'capacity', 'is_active']
    list_filter = ['vehicle_type', 'school', 'vendor', 'is_active']
    search_fields = ['vehicle_number', 'model', 'make']

@admin.register(Driver)  
class DriverAdmin(admin.ModelAdmin):
    list_display = ['employee', 'license_number', 'school', 'experience_years', 'is_active']
    list_filter = ['school', 'is_active']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'license_number']

@admin.register(TransportRoute)
class TransportRouteAdmin(admin.ModelAdmin):
    list_display = ['route_name', 'route_code', 'school', 'total_distance_km', 'is_active']
    list_filter = ['school', 'is_active']
    search_fields = ['route_name', 'route_code']

@admin.register(StudentTransport)
class StudentTransportAdmin(admin.ModelAdmin):
    list_display = ['student', 'route', 'bus_stop', 'monthly_fee', 'is_active']
    list_filter = ['route', 'is_active']
    search_fields = ['student__first_name', 'student__last_name']

# Register your models here.
