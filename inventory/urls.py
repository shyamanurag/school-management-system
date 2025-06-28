from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for API (temporarily disabled)
router = DefaultRouter()
# router.register(r'items', InventoryItemViewSet, basename='inventory-item')
# router.register(r'transactions', InventoryTransactionViewSet, basename='inventory-transaction')
# router.register(r'suppliers', SupplierViewSet, basename='inventory-supplier')

# Web Interface URLs - NUCLEAR REBUILD OF INVENTORY MODULE
urlpatterns = [
    # Inventory Dashboard
    path('', views.inventory_dashboard, name='dashboard'),
    
    # Item Management
    path('items/', views.InventoryItemListView.as_view(), name='item-list'),
    path('items/<int:pk>/', views.InventoryItemDetailView.as_view(), name='item-detail'),
    
    # Stock Management
    path('stock/add/', views.add_stock, name='add-stock'),
    path('stock/remove/', views.remove_stock, name='remove-stock'),
    
    # Transaction Management
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    
    # Supplier Management
    path('suppliers/', views.SupplierListView.as_view(), name='supplier-list'),
    
    # Stock Alerts
    # path('alerts/', views.StockAlertListView.as_view(), name='stock-alerts'),
    path('alerts/<int:alert_id>/resolve/', views.resolve_alert, name='resolve-alert'),
    
    # Reports
    path('reports/', views.inventory_reports, name='reports'),
    path('export/', views.export_inventory, name='export-inventory'),
    
    # API URLs (temporarily disabled)
    # path('api/', include(router.urls)),
] 
