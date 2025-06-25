from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import FeeCategory

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
