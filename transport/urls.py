from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    TransportVendorViewSet,
    VehicleViewSet, 
    TransportRouteViewSet,
    StudentTransportViewSet
)

router = DefaultRouter()
router.register(r'vendors', TransportVendorViewSet, basename='transportvendor')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'routes', TransportRouteViewSet, basename='transportroute')
router.register(r'assignments', StudentTransportViewSet, basename='studenttransport')

urlpatterns = [
    path('', include(router.urls)),
] 