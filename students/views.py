from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from .models import Student

class StudentListView(ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 50
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Students'
        context['total_students'] = Student.objects.count()
        return context

class StudentDetailView(DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Student - {self.object.first_name} {self.object.last_name}'
        return context

class StudentCreateView(CreateView):
    model = Student
    template_name = 'students/student_form.html'
    fields = [
        'admission_number', 'roll_number', 'first_name', 'last_name', 
        'date_of_birth', 'gender', 'phone', 'email', 'address',
        'class_enrolled', 'section_enrolled', 'admission_date',
        'parent_name', 'parent_phone', 'parent_email', 'emergency_contact',
        'photo', 'is_active'
    ]
    success_url = reverse_lazy('student-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add New Student'
        context['form_title'] = 'Add New Student'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Student added successfully!')
        return super().form_valid(form)

class StudentUpdateView(UpdateView):
    model = Student
    template_name = 'students/student_form.html'
    fields = [
        'admission_number', 'roll_number', 'first_name', 'last_name', 
        'date_of_birth', 'gender', 'phone', 'email', 'address',
        'class_enrolled', 'section_enrolled', 'admission_date',
        'parent_name', 'parent_phone', 'parent_email', 'emergency_contact',
        'photo', 'is_active'
    ]
    success_url = reverse_lazy('student-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit Student - {self.object.first_name} {self.object.last_name}'
        context['form_title'] = f'Edit Student - {self.object.first_name} {self.object.last_name}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Student updated successfully!')
        return super().form_valid(form)

class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Delete Student - {self.object.first_name} {self.object.last_name}'
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Student deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Create your views here.
