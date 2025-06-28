from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .simple_views import simple_transport_dashboard

# Create router for API (temporarily disabled)
router = DefaultRouter()
# router.register(r'vehicles', VehicleViewSet, basename='transport-vehicle')
# router.register(r'routes', RouteViewSet, basename='transport-route')
# router.register(r'route-stops', RouteStopViewSet, basename='transport-route-stop')

# Web Interface URLs - NUCLEAR REBUILD OF TRANSPORT MODULE
urlpatterns = [
    # Transport Dashboard
    path('', simple_transport_dashboard, name='dashboard'),
    
    # Vehicle Management
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle-list'),
    path('vehicles/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    
    # Route Management
    path('routes/', views.RouteListView.as_view(), name='route-list'),
    path('routes/<int:pk>/', views.RouteDetailView.as_view(), name='route-detail'),
    
    # Student Transport Assignments
    path('assign/', views.assign_transport, name='assign-transport'),
    path('assignments/', views.StudentTransportListView.as_view(), name='student-assignments'),
    path('assignments/<int:assignment_id>/remove/', views.remove_transport_assignment, name='remove-assignment'),
    
    # Reports
    path('reports/', views.transport_reports, name='reports'),
    path('export/', views.export_transport_data, name='export-data'),
    
    # API URLs (temporarily disabled)
    # path('api/', include(router.urls)),
] 