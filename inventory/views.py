from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import InventoryItem, InventoryCategory, Supplier, PurchaseOrder, StockTransaction

def inventory_dashboard(request):
    """Inventory management dashboard"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    
    # Statistics
    total_items = InventoryItem.objects.filter(is_active=True).count()
    total_categories = InventoryCategory.objects.filter(is_active=True).count()
    total_suppliers = Supplier.objects.filter(is_active=True).count()
    total_purchase_orders = PurchaseOrder.objects.count()
    
    # Stock status
    low_stock_items = InventoryItem.objects.filter(
        is_active=True,
        current_stock__lte=models.F('minimum_stock_level')
    ).count()
    
    # Recent transactions
    recent_transactions = StockTransaction.objects.select_related('item').order_by('-created_at')[:10]
    
    # Recent items
    recent_items = InventoryItem.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    context = {
        'school_settings': school_settings,
        'total_items': total_items,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'total_purchase_orders': total_purchase_orders,
        'low_stock_items': low_stock_items,
        'recent_transactions': recent_transactions,
        'recent_items': recent_items,
        'page_title': 'Inventory Management Dashboard'
    }
    return render(request, 'inventory/dashboard.html', context)

def items_list(request):
    """List all inventory items"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    items = InventoryItem.objects.filter(is_active=True).select_related('category', 'supplier').order_by('name')
    
    context = {
        'school_settings': school_settings,
        'items': items,
        'page_title': 'Inventory Items'
    }
    return render(request, 'inventory/items_list.html', context)

def categories_list(request):
    """List all inventory categories"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    categories = InventoryCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'school_settings': school_settings,
        'categories': categories,
        'page_title': 'Inventory Categories'
    }
    return render(request, 'inventory/categories_list.html', context)

def suppliers_list(request):
    """List all suppliers"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    suppliers = Supplier.objects.filter(is_active=True).order_by('name')
    
    context = {
        'school_settings': school_settings,
        'suppliers': suppliers,
        'page_title': 'Supplier Management'
    }
    return render(request, 'inventory/suppliers_list.html', context)

def stock_transactions_list(request):
    """List all stock transactions"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    transactions = StockTransaction.objects.select_related('item').order_by('-created_at')[:100]
    
    context = {
        'school_settings': school_settings,
        'transactions': transactions,
        'page_title': 'Stock Transactions'
    }
    return render(request, 'inventory/transactions_list.html', context)

def inventory_reports(request):
    """Inventory reports and analytics"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    
    # Category-wise item count
    category_stats = InventoryCategory.objects.annotate(
        item_count=Count('items', filter=Q(items__is_active=True))
    ).filter(is_active=True)
    
    # Low stock items
    low_stock_items = InventoryItem.objects.filter(
        is_active=True,
        current_stock__lte=models.F('minimum_stock_level')
    )
    
    context = {
        'school_settings': school_settings,
        'category_stats': category_stats,
        'low_stock_items': low_stock_items,
        'page_title': 'Inventory Reports & Analytics'
    }
    return render(request, 'inventory/reports.html', context)

# Class-based views for CRUD operations
class ItemListView(ListView):
    model = InventoryItem
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'

class ItemCreateView(CreateView):
    model = InventoryItem
    fields = ['category', 'name', 'description', 'current_stock', 'minimum_stock_level']
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('item-list')

class ItemUpdateView(UpdateView):
    model = InventoryItem
    fields = ['category', 'name', 'description', 'current_stock', 'minimum_stock_level']
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('item-list')

class ItemDeleteView(DeleteView):
    model = InventoryItem
    template_name = 'inventory/item_confirm_delete.html'
    success_url = reverse_lazy('item-list')
