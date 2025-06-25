from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Hostel

class HostelListView(ListView):
    model = Hostel
    template_name = 'hostel/hostel_list.html'
    context_object_name = 'hostels'

class HostelCreateView(CreateView):
    model = Hostel
    fields = ['name', 'address']
    template_name = 'hostel/hostel_form.html'
    success_url = reverse_lazy('hostel-list')

class HostelUpdateView(UpdateView):
    model = Hostel
    fields = ['name', 'address']
    template_name = 'hostel/hostel_form.html'
    success_url = reverse_lazy('hostel-list')

class HostelDeleteView(DeleteView):
    model = Hostel
    template_name = 'hostel/hostel_confirm_delete.html'
    success_url = reverse_lazy('hostel-list')
