from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Sum, Avg, F, Case, When, Value, CharField, BooleanField
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    Category, Item, StockTransaction, PurchaseOrder, Supplier,
    Asset, AssetMaintenance, Requisition, StockAlert, Vendor,
    InventoryAudit, ItemLocation, StockMovement
)
from core.models import SchoolSettings, User
import csv
import json

# ===== COMPREHENSIVE INVENTORY DASHBOARD =====
@login_required
def inventory_dashboard(request):
    """Advanced Inventory Management Dashboard"""
    school_settings = SchoolSettings.objects.first()
    
    # Inventory Overview Statistics
    inventory_stats = {
        'total_items': Item.objects.count(),
        'low_stock_items': Item.objects.filter(
            current_stock__lte=F('minimum_stock_level')
        ).count(),
        'out_of_stock_items': Item.objects.filter(current_stock=0).count(),
        'total_categories': Category.objects.count(),
        'active_suppliers': Supplier.objects.filter(is_active=True).count(),
        'total_assets': Asset.objects.count(),
        'assets_due_maintenance': Asset.objects.filter(
            next_maintenance_date__lte=timezone.now().date()
        ).count(),
    }
    
    # Current Month Statistics
    current_month = timezone.now().replace(day=1)
    monthly_stats = {
        'purchase_orders': PurchaseOrder.objects.filter(
            order_date__gte=current_month
        ).count(),
        'pending_orders': PurchaseOrder.objects.filter(
            status='pending'
        ).count(),
        'completed_orders': PurchaseOrder.objects.filter(
            status='completed',
            order_date__gte=current_month
        ).count(),
        'total_procurement_value': PurchaseOrder.objects.filter(
            order_date__gte=current_month,
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0,
    }
    
    # Stock Movement Analysis
    stock_movements = StockMovement.objects.filter(
        movement_date__gte=current_month
    ).values('movement_type').annotate(
        count=Count('id'),
        total_quantity=Sum('quantity')
    )
    
    # Low Stock Alerts
    low_stock_items = Item.objects.filter(
        current_stock__lte=F('minimum_stock_level')
    ).select_related('category').order_by('current_stock')[:20]
    
    # Recent Purchase Orders
    recent_orders = PurchaseOrder.objects.select_related(
        'supplier'
    ).order_by('-order_date')[:10]
    
    # Asset Maintenance Due
    maintenance_due = Asset.objects.filter(
        next_maintenance_date__lte=timezone.now().date() + timedelta(days=30)
    ).order_by('next_maintenance_date')[:10]
    
    # Top Categories by Value
    category_value = Category.objects.annotate(
        total_value=Sum(F('item__current_stock') * F('item__unit_price'))
    ).filter(total_value__gt=0).order_by('-total_value')[:10]
    
    # Recent Stock Transactions
    recent_transactions = StockTransaction.objects.select_related(
        'item', 'item__category'
    ).order_by('-transaction_date')[:15]
    
    # Pending Requisitions
    pending_requisitions = Requisition.objects.filter(
        status='pending'
    ).select_related('requested_by').order_by('-request_date')[:10]
    
    # Monthly Inventory Value Trend
    monthly_trends = []
    for i in range(6):
        month_start = (timezone.now().replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        purchase_value = PurchaseOrder.objects.filter(
            order_date__range=[month_start, month_end],
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        monthly_trends.append({
            'month': month_start.strftime('%b %Y'),
            'purchase_value': float(purchase_value)
        })
    
    context = {
        'page_title': 'Inventory Management Dashboard',
        'school_settings': school_settings,
        'inventory_stats': inventory_stats,
        'monthly_stats': monthly_stats,
        'stock_movements': stock_movements,
        'low_stock_items': low_stock_items,
        'recent_orders': recent_orders,
        'maintenance_due': maintenance_due,
        'category_value': category_value,
        'recent_transactions': recent_transactions,
        'pending_requisitions': pending_requisitions,
        'monthly_trends': list(reversed(monthly_trends)),
    }
    
    return render(request, 'inventory/dashboard.html', context)

# ===== ITEM MANAGEMENT =====
class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Item.objects.select_related('category').annotate(
            total_value=F('current_stock') * F('unit_price'),
            stock_status=Case(
                When(current_stock=0, then=Value('out_of_stock')),
                When(current_stock__lte=F('minimum_stock_level'), then=Value('low_stock')),
                default=Value('in_stock'),
                output_field=CharField()
            )
        )
        
        # Filtering
        category_filter = self.request.GET.get('category', '')
        stock_status_filter = self.request.GET.get('stock_status', '')
        search_query = self.request.GET.get('search', '')
        
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        if stock_status_filter == 'low_stock':
            queryset = queryset.filter(current_stock__lte=F('minimum_stock_level'))
        elif stock_status_filter == 'out_of_stock':
            queryset = queryset.filter(current_stock=0)
        elif stock_status_filter == 'in_stock':
            queryset = queryset.filter(current_stock__gt=F('minimum_stock_level'))
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(item_code__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Inventory Items'
        context['categories'] = Category.objects.all()
        context['total_value'] = self.get_queryset().aggregate(
            total=Sum('total_value')
        )['total'] or 0
        return context

class ItemDetailView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.get_object()
        
        # Stock Transaction History
        context['transactions'] = StockTransaction.objects.filter(
            item=item
        ).order_by('-transaction_date')[:20]
        
        # Stock Movement History
        context['movements'] = StockMovement.objects.filter(
            item=item
        ).order_by('-movement_date')[:20]
        
        # Current Stock Value
        context['stock_value'] = item.current_stock * item.unit_price
        
        # Stock Alerts
        context['has_low_stock'] = item.current_stock <= item.minimum_stock_level
        context['is_out_of_stock'] = item.current_stock == 0
        
        # Recent Purchase Orders
        context['recent_purchases'] = PurchaseOrder.objects.filter(
            items__item=item
        ).distinct().order_by('-order_date')[:10]
        
        context['page_title'] = f'Item: {item.name}'
        return context

# ===== STOCK MANAGEMENT =====
@login_required
def stock_management(request):
    """Stock Movement and Transaction Management"""
    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 0))
        unit_price = Decimal(request.POST.get('unit_price', '0'))
        remarks = request.POST.get('remarks', '')
        
        try:
            item = Item.objects.get(id=item_id)
            
            if action == 'stock_in':
                # Add stock
                item.current_stock += quantity
                item.save()
                
                # Create transaction record
                StockTransaction.objects.create(
                    item=item,
                    transaction_type='in',
                    quantity=quantity,
                    unit_price=unit_price,
                    total_value=quantity * unit_price,
                    remarks=remarks,
                    created_by=request.user
                )
                
                # Create movement record
                StockMovement.objects.create(
                    item=item,
                    movement_type='inward',
                    quantity=quantity,
                    reference_number=f"IN-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    remarks=remarks,
                    created_by=request.user
                )
                
                messages.success(request, f'Stock added successfully for {item.name}')
                
            elif action == 'stock_out':
                # Check available stock
                if item.current_stock >= quantity:
                    item.current_stock -= quantity
                    item.save()
                    
                    # Create transaction record
                    StockTransaction.objects.create(
                        item=item,
                        transaction_type='out',
                        quantity=quantity,
                        unit_price=unit_price,
                        total_value=quantity * unit_price,
                        remarks=remarks,
                        created_by=request.user
                    )
                    
                    # Create movement record
                    StockMovement.objects.create(
                        item=item,
                        movement_type='outward',
                        quantity=quantity,
                        reference_number=f"OUT-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                        remarks=remarks,
                        created_by=request.user
                    )
                    
                    messages.success(request, f'Stock issued successfully for {item.name}')
                else:
                    messages.error(request, f'Insufficient stock for {item.name}. Available: {item.current_stock}')
            
            elif action == 'stock_adjust':
                # Stock adjustment
                old_stock = item.current_stock
                item.current_stock = quantity
                item.save()
                
                adjustment_quantity = quantity - old_stock
                
                # Create transaction record
                StockTransaction.objects.create(
                    item=item,
                    transaction_type='adjustment',
                    quantity=abs(adjustment_quantity),
                    unit_price=unit_price,
                    total_value=abs(adjustment_quantity) * unit_price,
                    remarks=f"Adjustment: {old_stock} → {quantity}. {remarks}",
                    created_by=request.user
                )
                
                # Create movement record
                StockMovement.objects.create(
                    item=item,
                    movement_type='adjustment',
                    quantity=adjustment_quantity,
                    reference_number=f"ADJ-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    remarks=f"Stock adjustment from {old_stock} to {quantity}",
                    created_by=request.user
                )
                
                messages.success(request, f'Stock adjusted successfully for {item.name}')
            
            return redirect('inventory:stock_management')
            
        except Item.DoesNotExist:
            messages.error(request, 'Item not found')
        except Exception as e:
            messages.error(request, f'Error processing stock transaction: {str(e)}')
    
    # GET request
    items = Item.objects.select_related('category').order_by('name')
    recent_transactions = StockTransaction.objects.select_related(
        'item', 'item__category'
    ).order_by('-transaction_date')[:20]
    
    context = {
        'page_title': 'Stock Management',
        'items': items,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'inventory/stock_management.html', context)

# ===== PURCHASE ORDER MANAGEMENT =====
class PurchaseOrderListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'inventory/purchase_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = PurchaseOrder.objects.select_related('supplier')
        
        status_filter = self.request.GET.get('status', '')
        supplier_filter = self.request.GET.get('supplier', '')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if supplier_filter:
            queryset = queryset.filter(supplier_id=supplier_filter)
        
        return queryset.order_by('-order_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Purchase Orders'
        context['suppliers'] = Supplier.objects.filter(is_active=True)
        context['status_choices'] = PurchaseOrder.STATUS_CHOICES
        context['total_value'] = self.get_queryset().aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        return context

@login_required
def create_purchase_order(request):
    """Create new purchase order"""
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier_id')
        order_date = request.POST.get('order_date')
        expected_delivery = request.POST.get('expected_delivery')
        remarks = request.POST.get('remarks', '')
        
        # Items data
        item_ids = request.POST.getlist('item_ids[]')
        quantities = request.POST.getlist('quantities[]')
        unit_prices = request.POST.getlist('unit_prices[]')
        
        try:
            supplier = Supplier.objects.get(id=supplier_id)
            
            # Calculate total amount
            total_amount = Decimal('0')
            order_items = []
            
            for i, item_id in enumerate(item_ids):
                if item_id and i < len(quantities) and i < len(unit_prices):
                    item = Item.objects.get(id=item_id)
                    quantity = int(quantities[i])
                    unit_price = Decimal(unit_prices[i])
                    total_price = quantity * unit_price
                    
                    order_items.append({
                        'item': item,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_price': total_price
                    })
                    
                    total_amount += total_price
            
            if order_items:
                # Create purchase order
                order = PurchaseOrder.objects.create(
                    order_number=f"PO-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    supplier=supplier,
                    order_date=order_date,
                    expected_delivery_date=expected_delivery,
                    total_amount=total_amount,
                    remarks=remarks,
                    status='pending',
                    created_by=request.user
                )
                
                # Create order items (assuming you have a PurchaseOrderItem model)
                for item_data in order_items:
                    # You would create PurchaseOrderItem records here
                    pass
                
                messages.success(request, f'Purchase order {order.order_number} created successfully')
                return redirect('inventory:purchase_order_detail', pk=order.pk)
            else:
                messages.error(request, 'Please add at least one item to the order')
                
        except (Supplier.DoesNotExist, Item.DoesNotExist):
            messages.error(request, 'Invalid supplier or item selected')
        except Exception as e:
            messages.error(request, f'Error creating purchase order: {str(e)}')
    
    # GET request
    suppliers = Supplier.objects.filter(is_active=True)
    items = Item.objects.select_related('category').order_by('name')
    
    context = {
        'page_title': 'Create Purchase Order',
        'suppliers': suppliers,
        'items': items,
    }
    
    return render(request, 'inventory/create_purchase_order.html', context)

# ===== ASSET MANAGEMENT =====
class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'inventory/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Asset.objects.select_related('category').annotate(
            maintenance_overdue=Case(
                When(next_maintenance_date__lt=timezone.now().date(), then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
        
        category_filter = self.request.GET.get('category', '')
        status_filter = self.request.GET.get('status', '')
        location_filter = self.request.GET.get('location', '')
        
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if location_filter:
            queryset = queryset.filter(location__icontains=location_filter)
        
        return queryset.order_by('asset_tag')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Asset Management'
        context['categories'] = Category.objects.all()
        context['status_choices'] = Asset.STATUS_CHOICES
        context['total_value'] = self.get_queryset().aggregate(
            total=Sum('purchase_value')
        )['total'] or 0
        return context

# ===== REQUISITION MANAGEMENT =====
@login_required
def requisition_management(request):
    """Material Requisition Management"""
    requisitions = Requisition.objects.select_related(
        'requested_by', 'approved_by'
    ).order_by('-request_date')
    
    status_filter = request.GET.get('status', '')
    department_filter = request.GET.get('department', '')
    
    if status_filter:
        requisitions = requisitions.filter(status=status_filter)
    if department_filter:
        requisitions = requisitions.filter(department__icontains=department_filter)
    
    # Statistics
    requisition_stats = {
        'total_requisitions': requisitions.count(),
        'pending': requisitions.filter(status='pending').count(),
        'approved': requisitions.filter(status='approved').count(),
        'rejected': requisitions.filter(status='rejected').count(),
        'completed': requisitions.filter(status='completed').count(),
    }
    
    context = {
        'page_title': 'Requisition Management',
        'requisitions': requisitions[:50],
        'requisition_stats': requisition_stats,
        'status_choices': Requisition.STATUS_CHOICES,
        'selected_status': status_filter,
    }
    
    return render(request, 'inventory/requisition_management.html', context)

# ===== SUPPLIER MANAGEMENT =====
class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Supplier.objects.annotate(
            total_orders=Count('purchaseorder'),
            total_value=Sum('purchaseorder__total_amount')
        )
        
        status_filter = self.request.GET.get('status', '')
        search_query = self.request.GET.get('search', '')
        
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(contact_person__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Supplier Management'
        return context

# ===== REPORTS AND ANALYTICS =====
@login_required
def inventory_reports(request):
    """Inventory Reports and Analytics"""
    # Date range filtering
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    report_type = request.GET.get('report_type', 'summary')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Stock Movement Analysis
    stock_movements = StockMovement.objects.filter(
        movement_date__range=[start_date, end_date]
    ).values('movement_type').annotate(
        total_quantity=Sum('quantity'),
        count=Count('id')
    )
    
    # Purchase Analysis
    purchase_orders = PurchaseOrder.objects.filter(
        order_date__range=[start_date, end_date]
    )
    
    total_purchase_value = purchase_orders.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Supplier Performance
    supplier_performance = Supplier.objects.annotate(
        orders_count=Count('purchaseorder', filter=Q(
            purchaseorder__order_date__range=[start_date, end_date]
        )),
        total_value=Sum('purchaseorder__total_amount', filter=Q(
            purchaseorder__order_date__range=[start_date, end_date]
        ))
    ).filter(orders_count__gt=0).order_by('-total_value')
    
    # Category-wise Inventory Value
    category_analysis = Category.objects.annotate(
        total_items=Count('item'),
        total_stock_value=Sum(F('item__current_stock') * F('item__unit_price'))
    ).filter(total_stock_value__gt=0).order_by('-total_stock_value')
    
    # Low Stock Items
    low_stock_items = Item.objects.filter(
        current_stock__lte=F('minimum_stock_level')
    ).select_related('category').order_by('current_stock')
    
    context = {
        'page_title': 'Inventory Reports & Analytics',
        'start_date': start_date,
        'end_date': end_date,
        'report_type': report_type,
        'stock_movements': stock_movements,
        'total_purchase_value': total_purchase_value,
        'supplier_performance': supplier_performance,
        'category_analysis': category_analysis,
        'low_stock_items': low_stock_items,
    }
    
    return render(request, 'inventory/inventory_reports.html', context)

# ===== API ENDPOINTS =====
@login_required
def inventory_analytics_api(request):
    """API endpoint for inventory analytics data"""
    # Monthly stock movement trends
    monthly_data = []
    for i in range(12):
        month_start = (timezone.now().replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        inward_qty = StockMovement.objects.filter(
            movement_date__range=[month_start, month_end],
            movement_type='inward'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        outward_qty = StockMovement.objects.filter(
            movement_date__range=[month_start, month_end],
            movement_type='outward'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'inward': inward_qty,
            'outward': outward_qty
        })
    
    # Category distribution
    category_data = Category.objects.annotate(
        item_count=Count('item'),
        stock_value=Sum(F('item__current_stock') * F('item__unit_price'))
    ).values('name', 'item_count', 'stock_value')
    
    # Stock status overview
    stock_overview = {
        'in_stock': Item.objects.filter(current_stock__gt=F('minimum_stock_level')).count(),
        'low_stock': Item.objects.filter(
            current_stock__lte=F('minimum_stock_level'),
            current_stock__gt=0
        ).count(),
        'out_of_stock': Item.objects.filter(current_stock=0).count(),
    }
    
    return JsonResponse({
        'monthly_trends': list(reversed(monthly_data)),
        'category_distribution': list(category_data),
        'stock_overview': stock_overview,
        'status': 'success'
    })

# ===== DATA EXPORT FUNCTIONS =====
@login_required
def export_inventory_csv(request):
    """Export inventory data to CSV"""
    export_type = request.GET.get('type', 'items')
    
    response = HttpResponse(content_type='text/csv')
    
    if export_type == 'items':
        response['Content-Disposition'] = 'attachment; filename="inventory_items.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Item Code', 'Name', 'Category', 'Current Stock', 'Minimum Stock Level',
            'Unit Price', 'Stock Value', 'Location', 'Status'
        ])
        
        items = Item.objects.select_related('category')
        
        for item in items:
            stock_value = item.current_stock * item.unit_price
            writer.writerow([
                item.item_code,
                item.name,
                item.category.name if item.category else '',
                item.current_stock,
                item.minimum_stock_level,
                item.unit_price,
                stock_value,
                item.location,
                'Low Stock' if item.current_stock <= item.minimum_stock_level else 'In Stock'
            ])
    
    elif export_type == 'assets':
        response['Content-Disposition'] = 'attachment; filename="asset_register.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Asset Tag', 'Name', 'Category', 'Purchase Date', 'Purchase Value',
            'Current Value', 'Location', 'Status', 'Next Maintenance'
        ])
        
        assets = Asset.objects.select_related('category')
        
        for asset in assets:
            writer.writerow([
                asset.asset_tag,
                asset.name,
                asset.category.name if asset.category else '',
                asset.purchase_date,
                asset.purchase_value,
                asset.current_value,
                asset.location,
                asset.get_status_display(),
                asset.next_maintenance_date
            ])
    
    return response
