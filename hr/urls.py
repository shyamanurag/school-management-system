from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    DepartmentViewSet, DesignationViewSet, EmployeeViewSet,
    EmployeeDocumentViewSet, SalaryStructureViewSet, PayrollMonthViewSet,
    PayslipViewSet, LeaveTypeViewSet, LeaveApplicationViewSet,
    EmployeeLeaveBalanceViewSet
)
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='hr-department')
router.register(r'designations', DesignationViewSet, basename='hr-designation')
router.register(r'employees', EmployeeViewSet, basename='hr-employee')
router.register(r'employee-documents', EmployeeDocumentViewSet, basename='hr-employee-document')
router.register(r'salary-structures', SalaryStructureViewSet, basename='hr-salary-structure')
router.register(r'payroll-months', PayrollMonthViewSet, basename='hr-payroll-month')
router.register(r'payslips', PayslipViewSet, basename='hr-payslip')
router.register(r'leave-types', LeaveTypeViewSet, basename='hr-leave-type')
router.register(r'leave-applications', LeaveApplicationViewSet, basename='hr-leave-application')
router.register(r'leave-balances', EmployeeLeaveBalanceViewSet, basename='hr-leave-balance')

# Web Interface URLs - NUCLEAR REBUILD OF HR MODULE
urlpatterns = [
    # HR Dashboard
    path('', views.hr_dashboard, name='hr-dashboard'),
    
    # Employee Management
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee-update'),
    path('employees/export/', views.export_employees, name='export-employees'),
    
    # Leave Management
    path('leaves/', views.LeaveListView.as_view(), name='leave-list'),
    path('leaves/<int:pk>/', views.LeaveDetailView.as_view(), name='leave-detail'),
    path('leaves/apply/', views.LeaveCreateView.as_view(), name='leave-apply'),
    path('leaves/<int:pk>/approve/', views.approve_leave, name='leave-approve'),
    path('leaves/<int:pk>/reject/', views.reject_leave, name='leave-reject'),
    
    # Performance Reviews
    path('performance/', views.PerformanceListView.as_view(), name='performance-list'),
    path('performance/<int:pk>/', views.PerformanceDetailView.as_view(), name='performance-detail'),
    path('performance/create/', views.PerformanceCreateView.as_view(), name='performance-create'),
    
    # Training Management
    path('training/', views.TrainingListView.as_view(), name='training-list'),
    path('training/<int:pk>/', views.TrainingDetailView.as_view(), name='training-detail'),
    path('training/create/', views.TrainingCreateView.as_view(), name='training-create'),
    path('training/<int:pk>/enroll/', views.enroll_training, name='training-enroll'),
    
    # Payroll Management
    path('payroll/', views.PayrollListView.as_view(), name='payroll-list'),
    path('payroll/<int:pk>/', views.PayrollDetailView.as_view(), name='payroll-detail'),
    path('payroll/generate/', views.generate_payroll, name='payroll-generate'),
    
    # Reports and Analytics
    path('reports/', views.hr_reports, name='hr-reports'),
    path('analytics/', views.hr_analytics, name='hr-analytics'),
    
    # API URLs
    path('api/', include(router.urls)),
] 