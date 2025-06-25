from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Notice

class NoticeListView(ListView):
    model = Notice
    template_name = 'communication/notice_list.html'
    context_object_name = 'notices'

class NoticeCreateView(CreateView):
    model = Notice
    fields = ['title', 'content', 'publish_date', 'visible_to']
    template_name = 'communication/notice_form.html'
    success_url = reverse_lazy('notice-list')

class NoticeUpdateView(UpdateView):
    model = Notice
    fields = ['title', 'content', 'publish_date', 'visible_to']
    template_name = 'communication/notice_form.html'
    success_url = reverse_lazy('notice-list')

class NoticeDeleteView(DeleteView):
    model = Notice
    template_name = 'communication/notice_confirm_delete.html'
    success_url = reverse_lazy('notice-list')
