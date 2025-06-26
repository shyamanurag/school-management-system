from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    DepartmentViewSet, DesignationViewSet, EmployeeViewSet,
    EmployeeDocumentViewSet, SalaryStructureViewSet, PayrollMonthViewSet,
    PayslipViewSet, LeaveTypeViewSet, LeaveApplicationViewSet,
    EmployeeLeaveBalanceViewSet
)

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

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
] 