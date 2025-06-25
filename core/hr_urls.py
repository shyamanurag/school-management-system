from django.urls import path
from . import hr_views

app_name = 'hr'

urlpatterns = [
    # HR Dashboard
    path('dashboard/', hr_views.hr_dashboard, name='dashboard'),
    
    # HR Analytics
    path('analytics/', hr_views.hr_analytics_list, name='analytics_list'),
    path('analytics/<int:analytics_id>/', hr_views.hr_analytics_detail, name='analytics_detail'),
    
    # API Endpoints
    path('api/employee-analytics/', hr_views.employee_analytics_api, name='employee_analytics_api'),
    path('api/leave-analytics/', hr_views.leave_analytics_api, name='leave_analytics_api'),
    path('api/performance-analytics/', hr_views.performance_analytics_api, name='performance_analytics_api'),
] 