from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import (
    TransportVendorViewSet,
    VehicleViewSet, 
    TransportRouteViewSet,
    StudentTransportViewSet
)

# API Router
router = DefaultRouter()
router.register(r'vendors', TransportVendorViewSet, basename='transportvendor')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'routes', TransportRouteViewSet, basename='transportroute')
router.register(r'assignments', StudentTransportViewSet, basename='studenttransport')

urlpatterns = [
    # === WEB INTERFACE URLS ===
    path('', views.transport_dashboard, name='transport-dashboard'),
    path('vehicles/', views.vehicles_list, name='vehicles-list'),
    path('drivers/', views.drivers_list, name='drivers-list'),
    path('routes/', views.routes_list, name='routes-list'),
    path('vendors/', views.vendors_list, name='vendors-list'),
    path('assignments/', views.student_transport_list, name='student-transport-list'),
    path('reports/', views.transport_reports, name='transport-reports'),
    
    # Class-based views for CRUD operations
    path('routes/list/', views.RouteListView.as_view(), name='route-list'),
    path('routes/create/', views.RouteCreateView.as_view(), name='route-create'),
    path('routes/<int:pk>/update/', views.RouteUpdateView.as_view(), name='route-update'),
    path('routes/<int:pk>/delete/', views.RouteDeleteView.as_view(), name='route-delete'),
    
    # === API URLS ===
    path('api/', include(router.urls)),
] 