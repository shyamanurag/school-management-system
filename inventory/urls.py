from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import (
    InventoryCategoryViewSet,
    SupplierViewSet,
    BrandViewSet,
    InventoryItemViewSet,
    PurchaseOrderViewSet,
    PurchaseOrderItemViewSet,
    GoodsReceiptViewSet,
    StockTransactionViewSet,
    StockIssueViewSet,
    InventoryAuditViewSet,
    InventoryReportViewSet
)

# API Router
router = DefaultRouter()
router.register(r'categories', InventoryCategoryViewSet, basename='inventorycategory')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'items', InventoryItemViewSet, basename='inventoryitem')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchaseorder')
router.register(r'purchase-order-items', PurchaseOrderItemViewSet, basename='purchaseorderitem')
router.register(r'goods-receipts', GoodsReceiptViewSet, basename='goodsreceipt')
router.register(r'stock-transactions', StockTransactionViewSet, basename='stocktransaction')
router.register(r'stock-issues', StockIssueViewSet, basename='stockissue')
router.register(r'audits', InventoryAuditViewSet, basename='inventoryaudit')
router.register(r'reports', InventoryReportViewSet, basename='inventoryreport')

urlpatterns = [
    # === WEB INTERFACE URLS ===
    path('', views.ItemListView.as_view(), name='inventory-dashboard'),
    path('items/', views.ItemListView.as_view(), name='items-list'),
    
    # Class-based views for CRUD operations
    path('items/create/', views.ItemCreateView.as_view(), name='item-create'),
    path('items/<int:pk>/update/', views.ItemUpdateView.as_view(), name='item-update'),
    path('items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item-delete'),
    
    # === API URLS ===
    path('api/', include(router.urls)),
] 