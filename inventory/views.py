from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
from .models import InventoryItem, InventoryCategory, Supplier, PurchaseOrder
from core.models import SchoolSettings

@login_required
def inventory_dashboard(request):
    return render(request, 'inventory/dashboard.html', {'page_title': 'Inventory Dashboard'})

class InventoryItemListView(LoginRequiredMixin, ListView):
    model = InventoryItem
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 20

class InventoryItemDetailView(LoginRequiredMixin, DetailView):
    model = InventoryItem
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item'

@login_required
def export_inventory(request):
    return HttpResponse("Export functionality coming soon")

@login_required
def inventory_reports(request):
    return render(request, 'inventory/reports.html', {'page_title': 'Inventory Reports'})
