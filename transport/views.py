from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Route

class RouteListView(ListView):
    model = Route
    template_name = 'transport/route_list.html'
    context_object_name = 'routes'

class RouteCreateView(CreateView):
    model = Route
    fields = ['name', 'start_point', 'end_point']
    template_name = 'transport/route_form.html'
    success_url = reverse_lazy('route-list')

class RouteUpdateView(UpdateView):
    model = Route
    fields = ['name', 'start_point', 'end_point']
    template_name = 'transport/route_form.html'
    success_url = reverse_lazy('route-list')

class RouteDeleteView(DeleteView):
    model = Route
    template_name = 'transport/route_confirm_delete.html'
    success_url = reverse_lazy('route-list')
