from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_dashboard, name='dashboard'),
    path('items/', views.InventoryItemListView.as_view(), name='item-list'),
    path('items/<int:pk>/', views.InventoryItemDetailView.as_view(), name='item-detail'),
    path('reports/', views.inventory_reports, name='reports'),
    path('export/', views.export_inventory, name='export-inventory'),
]
