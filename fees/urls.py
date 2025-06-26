from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import (
    FeeCategoryViewSet, 
    FeeStructureViewSet, 
    FeePaymentViewSet
)

# API Router
router = DefaultRouter()
router.register(r'categories', FeeCategoryViewSet, basename='feecategory')
router.register(r'structures', FeeStructureViewSet, basename='feestructure')
router.register(r'payments', FeePaymentViewSet, basename='feepayment')

urlpatterns = [
    # === WEB INTERFACE URLS ===
    path('', views.fee_dashboard, name='fee-dashboard'),
    path('categories/', views.fee_categories_list, name='fee-categories-list'),
    path('structures/', views.fee_structures_list, name='fee-structures-list'),
    path('payments/', views.fee_payments_list, name='fee-payments-list'),
    path('reports/', views.fee_reports, name='fee-reports'),
    
    # Class-based views for CRUD operations
    path('categories/list/', views.FeeCategoryListView.as_view(), name='fee-category-list'),
    path('categories/create/', views.FeeCategoryCreateView.as_view(), name='fee-category-create'),
    path('categories/<int:pk>/update/', views.FeeCategoryUpdateView.as_view(), name='fee-category-update'),
    path('categories/<int:pk>/delete/', views.FeeCategoryDeleteView.as_view(), name='fee-category-delete'),
    
    # === API URLS ===
    path('api/', include(router.urls)),
] 