from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Main Analytics Dashboard
    path('', views.analytics_dashboard, name='dashboard'),
    
    # Specialized Analytics Views
    path('students/', views.student_analytics, name='student-analytics'),
    path('financial/', views.financial_analytics, name='financial-analytics'),
    path('attendance/', views.attendance_analytics, name='attendance-analytics'),
    path('performance/', views.performance_analytics, name='performance-analytics'),
    path('predictive/', views.predictive_analytics, name='predictive-analytics'),
    
    # Export Functions
    path('export/', views.export_analytics_data, name='export-data'),
    
    # API Endpoints for Charts and Real-time Data
    path('api/chart-data/', views.chart_data_api, name='chart-data-api'),
    
    # Advanced Analytics (Future Implementation)
    path('ml-insights/', views.analytics_dashboard, name='ml-insights'),  # Placeholder for ML insights
    path('trends/', views.analytics_dashboard, name='trends'),  # Placeholder for trend analysis
    path('reports/', views.analytics_dashboard, name='reports'),  # Placeholder for custom reports
] 