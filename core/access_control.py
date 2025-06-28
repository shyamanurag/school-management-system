
"""
Production User Access Control
Role-based access limits and session management
"""

from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

# User limits per role
USER_LIMITS = {
    'SUPER_ADMIN': {'max_users': 2, 'session_limit': 3},
    'PRINCIPAL': {'max_users': 1, 'session_limit': 2}, 
    'ADMIN_STAFF': {'max_users': 5, 'session_limit': 2},
    'TEACHER': {'max_users': 100, 'session_limit': 2},
    'ACCOUNTANT': {'max_users': 3, 'session_limit': 2},
    'LIBRARIAN': {'max_users': 2, 'session_limit': 1},
    'STUDENT': {'max_users': 2000, 'session_limit': 1}
}

def role_required(allowed_roles):
    """Decorator to require specific roles for view access"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user_roles = [group.name for group in request.user.groups.all()]
            
            # Allow superusers
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check if user has required role
            if not any(role in allowed_roles for role in user_roles):
                messages.error(request, f'Access denied. Required roles: {", ".join(allowed_roles)}')
                return HttpResponseForbidden('Access denied - insufficient permissions')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def check_user_session_limit(user):
    """Check if user has exceeded session limits"""
    user_roles = [group.name for group in user.groups.all()]
    
    if not user_roles:
        return True
    
    # Get most restrictive limit
    min_limit = min([USER_LIMITS.get(role, {}).get('session_limit', 1) for role in user_roles])
    
    # Count active sessions (simplified check)
    from django.contrib.sessions.models import Session
    from django.utils import timezone
    
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_sessions = 0
    
    for session in active_sessions:
        try:
            session_data = session.get_decoded()
            if session_data.get('_auth_user_id') == str(user.id):
                user_sessions += 1
        except:
            continue
    
    return user_sessions <= min_limit

def get_user_role_info(user):
    """Get user role information"""
    if user.is_superuser:
        return {'role': 'SUPER_ADMIN', 'permissions': 'ALL', 'level': 'ADMIN'}
    
    user_groups = user.groups.all()
    if user_groups:
        primary_role = user_groups.first().name
        permission_count = user_groups.first().permissions.count()
        return {
            'role': primary_role,
            'permissions': permission_count,
            'level': 'ADMIN' if 'ADMIN' in primary_role else 'USER'
        }
    
    return {'role': 'NO_ROLE', 'permissions': 0, 'level': 'GUEST'}
