from django.conf import settings
from .models import School, SystemConfiguration

def school_context(request):
    """Add school context to all templates"""
    context = {}
    
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            # Get user's school from profile
            if hasattr(request.user, 'profile'):
                school = request.user.profile.school
                context['current_school'] = school
                
                # Get system configurations for the school
                configs = SystemConfiguration.objects.filter(school=school)
                school_config = {}
                for config in configs:
                    school_config[config.key] = config.value
                
                context['school_config'] = school_config
        except:
            pass
    
    # Add global settings
    context['settings'] = settings
    context['school_system_config'] = getattr(settings, 'SCHOOL_CONFIG', {})
    
    return context 