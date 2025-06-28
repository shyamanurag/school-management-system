from django.urls import path
from . import views

urlpatterns = [
    # Basic working URLs
    path('', views.fee_dashboard, name='fee-dashboard'),
    path('dashboard/', views.fee_dashboard, name='fee-dashboard-alt'),
    path('categories/', views.fee_categories_list, name='fee-categories-list'),  
    path('structures/', views.fee_structures_list, name='fee-structures-list'),
    path('payments/', views.fee_payments_list, name='fee-payments-list'),
    path('payments/receipt/<int:payment_id>/', views.payment_receipt, name='payment-receipt'),
    path('reports/', views.fee_reports, name='fee-reports'),
    path('collection-report/', views.fee_collection_report, name='fee-collection-report'),
    path('export/', views.export_fee_data, name='export-fee-data'),
]
