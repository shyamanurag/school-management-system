from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

def landing_page(request):
    """Landing page with school management dashboard"""
    # Import models locally to avoid module-level import failures
    from core.models import SchoolSettings, AcademicYear, Campus, Department, Building, Room
    
    # Get school settings
    school_settings = SchoolSettings.objects.first()
    
    context = {
        'school_settings': school_settings,
        'total_campuses': Campus.objects.filter(is_active=True).count(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'total_rooms': Room.objects.filter(is_active=True).count(),
        'total_academic_years': AcademicYear.objects.filter(is_active=True).count(),
        'current_academic_year': AcademicYear.objects.filter(is_current=True).first(),
    }
    return render(request, 'landing.html', context)

def school_settings_view(request):
    """School settings view"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    context = {
        'school_settings': school_settings,
        'page_title': 'School Settings'
    }
    return render(request, 'school/settings.html', context)



def departments_list(request):
    """List all departments"""
    from core.models import Department
    
    departments = Department.objects.filter(is_active=True).order_by('name')
    context = {
        'departments': departments,
        'page_title': 'Departments Management'
    }
    return render(request, 'departments/list.html', context)

def campuses_list(request):
    """List all campuses"""
    from core.models import Campus
    
    campuses = Campus.objects.filter(is_active=True).order_by('name')
    context = {
        'campuses': campuses,
        'page_title': 'Campus Management'
    }
    return render(request, 'campuses/list.html', context)

def campus_detail(request, campus_id):
    """Campus detail view"""
    from core.models import Campus, Room
    
    campus = get_object_or_404(Campus, id=campus_id, is_active=True)
    
    context = {
        'campus': campus,
        'buildings': campus.buildings.filter(is_active=True),
        'total_rooms': Room.objects.filter(building__campus=campus, is_active=True).count(),
        'page_title': f'{campus.name} - Details'
    }
    return render(request, 'campuses/detail.html', context)

def rooms_list(request):
    """List all rooms"""
    from core.models import Room
    
    rooms = Room.objects.filter(is_active=True).select_related('building__campus').order_by('building__campus__name', 'building__name', 'room_number')
    context = {
        'rooms': rooms,
        'page_title': 'Rooms Management'
    }
    return render(request, 'rooms/list.html', context)

def academic_years_list(request):
    """List all academic years"""
    from core.models import AcademicYear
    
    academic_years = AcademicYear.objects.filter(is_active=True).order_by('-start_date')
    context = {
        'academic_years': academic_years,
        'page_title': 'Academic Years'
    }
    return render(request, 'academic_years/list.html', context)

# Error handlers - Keep these simple and independent of models
def handler404(request, exception):
    """Custom 404 error handler - Simple version without model dependencies"""
    from django.shortcuts import render
    return render(request, 'landing.html', {
        'error': 'Page not found',
        'error_code': '404',
        'school_settings': None,
        'total_campuses': 0,
        'total_departments': 0,
        'total_rooms': 0,
        'total_academic_years': 0,
        'current_academic_year': None,
    }, status=404)

def handler500(request):
    """Custom 500 error handler - Simple version without model dependencies"""
    from django.shortcuts import render
    return render(request, 'landing.html', {
        'error': 'Server error. Please try again later.',
        'error_code': '500',
        'school_settings': None,
        'total_campuses': 0,
        'total_departments': 0,
        'total_rooms': 0,
        'total_academic_years': 0,
        'current_academic_year': None,
    }, status=500)
