from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import RouteViewSet, VehicleViewSet, TransportAssignmentViewSet

router = DefaultRouter()
router.register(r'api/routes', RouteViewSet)
router.register(r'api/vehicles', VehicleViewSet)
router.register(r'api/transportassignments', TransportAssignmentViewSet)

urlpatterns = [
    path('', views.RouteListView.as_view(), name='route-list'),
    path('add/', views.RouteCreateView.as_view(), name='route-add'),
    path('<int:pk>/edit/', views.RouteUpdateView.as_view(), name='route-edit'),
    path('<int:pk>/delete/', views.RouteDeleteView.as_view(), name='route-delete'),
    path('', include(router.urls)),
]
