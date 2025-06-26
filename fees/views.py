from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import FeeCategory, FeeStructure, FeePayment, FeeItem, StudentFeeAssignment

class FeeCategoryListView(ListView):
    model = FeeCategory
    template_name = 'fees/fee_category_list.html'
    context_object_name = 'fee_categories'

class FeeCategoryCreateView(CreateView):
    model = FeeCategory
    fields = ['name', 'description']
    template_name = 'fees/fee_category_form.html'
    success_url = reverse_lazy('fee-category-list')

class FeeCategoryUpdateView(UpdateView):
    model = FeeCategory
    fields = ['name', 'description']
    template_name = 'fees/fee_category_form.html'
    success_url = reverse_lazy('fee-category-list')

class FeeCategoryDeleteView(DeleteView):
    model = FeeCategory
    template_name = 'fees/fee_category_confirm_delete.html'
    success_url = reverse_lazy('fee-category-list')

def fee_dashboard(request):
    """Fee management dashboard"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    
    # Statistics
    total_categories = FeeCategory.objects.filter(is_active=True).count()
    total_structures = FeeStructure.objects.filter(is_active=True).count()
    total_payments = FeePayment.objects.count()
    total_amount_collected = FeePayment.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Recent payments
    recent_payments = FeePayment.objects.select_related('student', 'fee_category').order_by('-payment_date')[:10]
    
    context = {
        'school_settings': school_settings,
        'total_categories': total_categories,
        'total_structures': total_structures,
        'total_payments': total_payments,
        'total_amount_collected': total_amount_collected,
        'recent_payments': recent_payments,
        'page_title': 'Fee Management Dashboard'
    }
    return render(request, 'fees/dashboard.html', context)

def fee_categories_list(request):
    """List all fee categories"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    categories = FeeCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'school_settings': school_settings,
        'categories': categories,
        'page_title': 'Fee Categories'
    }
    return render(request, 'fees/categories_list.html', context)

def fee_structures_list(request):
    """List all fee structures"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    structures = FeeStructure.objects.filter(is_active=True).select_related('academic_year', 'school_class').order_by('-created_at')
    
    context = {
        'school_settings': school_settings,
        'structures': structures,
        'page_title': 'Fee Structures'
    }
    return render(request, 'fees/structures_list.html', context)

def fee_payments_list(request):
    """List all fee payments"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    payments = FeePayment.objects.select_related('student', 'fee_category').order_by('-payment_date')[:100]
    
    context = {
        'school_settings': school_settings,
        'payments': payments,
        'page_title': 'Fee Payments'
    }
    return render(request, 'fees/payments_list.html', context)

def fee_reports(request):
    """Fee reports and analytics"""
    from core.models import SchoolSettings
    
    school_settings = SchoolSettings.objects.first()
    
    # Monthly collection data
    monthly_collections = FeePayment.objects.extra(
        select={'month': "EXTRACT(month FROM payment_date)"}
    ).values('month').annotate(total=Sum('amount_paid')).order_by('month')
    
    # Category-wise collection
    category_collections = FeePayment.objects.values('fee_category__name').annotate(
        total=Sum('amount_paid')
    ).order_by('-total')
    
    context = {
        'school_settings': school_settings,
        'monthly_collections': monthly_collections,
        'category_collections': category_collections,
        'page_title': 'Fee Reports & Analytics'
    }
    return render(request, 'fees/reports.html', context)
