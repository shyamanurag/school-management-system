from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Subject

class SubjectListView(ListView):
    model = Subject
    template_name = 'academics/subject_list.html'
    context_object_name = 'subjects'

class SubjectCreateView(CreateView):
    model = Subject
    fields = ['name', 'code', 'type']
    template_name = 'academics/subject_form.html'
    success_url = reverse_lazy('subject-list')

class SubjectUpdateView(UpdateView):
    model = Subject
    fields = ['name', 'code', 'type']
    template_name = 'academics/subject_form.html'
    success_url = reverse_lazy('subject-list')

class SubjectDeleteView(DeleteView):
    model = Subject
    template_name = 'academics/subject_confirm_delete.html'
    success_url = reverse_lazy('subject-list')
