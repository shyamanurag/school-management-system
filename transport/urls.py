from django.urls import path
from . import views

urlpatterns = [
    path('', views.transport_dashboard, name='dashboard'),
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle-list'),
    path('vehicles/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('routes/', views.RouteListView.as_view(), name='route-list'),
    path('routes/<int:pk>/', views.RouteDetailView.as_view(), name='route-detail'),
    path('students/', views.StudentTransportListView.as_view(), name='student-assignments'),
    path('assign/', views.assign_transport, name='assign-transport'),
    path('reports/', views.transport_reports, name='reports'),
    path('export/', views.export_transport_data, name='export-transport'),
]
