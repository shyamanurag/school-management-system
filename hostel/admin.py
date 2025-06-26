from django.contrib import admin
from .models import (
    HostelBlock, 
    HostelRoom, 
    HostelAdmission, 
    HostelResident, 
    MessMenu, 
    MessAttendance, 
    HostelVisitor, 
    HostelDisciplinary, 
    HostelFeedback, 
    HostelReport
)

@admin.register(HostelBlock)
class HostelBlockAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school', 'block_type', 'total_capacity', 'current_occupancy', 'is_active']
    list_filter = ['school', 'block_type', 'is_active']
    search_fields = ['name', 'code']

@admin.register(HostelRoom)
class HostelRoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'block', 'room_type', 'total_beds', 'occupied_beds', 'status']
    list_filter = ['block', 'room_type', 'status']
    search_fields = ['room_number']

@admin.register(HostelAdmission)
class HostelAdmissionAdmin(admin.ModelAdmin):
    list_display = ['application_number', 'student', 'status', 'application_date', 'allocated_room']
    list_filter = ['status', 'application_date', 'preferred_block']
    search_fields = ['application_number', 'student__first_name', 'student__last_name']

@admin.register(HostelResident)
class HostelResidentAdmin(admin.ModelAdmin):
    list_display = ['admission', 'room', 'bed_number', 'check_in_date', 'is_active']
    list_filter = ['room__block', 'is_active']

@admin.register(MessMenu)
class MessMenuAdmin(admin.ModelAdmin):
    list_display = ['block', 'day_of_week', 'meal_type', 'week_number', 'is_active']
    list_filter = ['block', 'day_of_week', 'meal_type', 'is_active']

# Register your models here.
