from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Book, Author, Subject, LibraryMember
from core.models import SchoolSettings
import csv

@login_required
def library_dashboard(request):
    """Professional Library Management Dashboard"""
    school_settings = SchoolSettings.objects.first()
    
    # Core Statistics
    total_books = Book.objects.count()
    available_books = Book.objects.filter(is_active=True, available_copies__gt=0).count()
    total_members = LibraryMember.objects.filter(status='ACTIVE').count()
    total_authors = Author.objects.count()
    total_subjects = Subject.objects.count()
    
    # Popular Books and Subjects
    popular_books = Book.objects.order_by('-total_copies')[:10]
    popular_subjects = Subject.objects.annotate(
        book_count=Count('books')
    ).order_by('-book_count')[:5]
    
    # Recent Books
    recent_books = Book.objects.select_related('section').order_by('-created_at')[:10]
    
    context = {
        'page_title': 'Library Management Dashboard',
        'school_settings': school_settings,
        'stats': {
            'total_books': total_books,
            'available_books': available_books,
            'total_members': total_members,
            'total_authors': total_authors,
            'total_subjects': total_subjects,
        },
        'popular_books': popular_books,
        'popular_subjects': popular_subjects,
        'recent_books': recent_books,
    }
    
    return render(request, 'library/dashboard.html', context)

class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Book.objects.select_related('section').prefetch_related('subjects', 'authors')
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(authors__name__icontains=search_query) |
                Q(isbn__icontains=search_query)
            ).distinct()
        
        return queryset.order_by('title')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Book Management'
        context['search_query'] = self.request.GET.get('search', '')
        context['total_books'] = Book.objects.count()
        return context

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        context['page_title'] = f'Book: {book.title}'
        context['is_available'] = book.available_copies > 0
        return context

class LibraryMemberListView(LoginRequiredMixin, ListView):
    model = LibraryMember
    template_name = 'library/member_list.html'
    context_object_name = 'members'
    paginate_by = 25
    
    def get_queryset(self):
        return LibraryMember.objects.select_related('student', 'employee').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Library Members'
        return context

@login_required
def issue_book(request):
    return render(request, 'library/issue_book.html', {'page_title': 'Issue Book'})

@login_required
def return_book(request, issue_id=None):
    return render(request, 'library/return_book.html', {'page_title': 'Return Book'})

@login_required
def library_reports(request):
    return render(request, 'library/reports.html', {'page_title': 'Library Reports'})

@login_required
def export_books(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=\"library_books_export.csv\"'
    
    writer = csv.writer(response)
    writer.writerow(['Title', 'Authors', 'ISBN', 'Total Copies', 'Available'])
    
    books = Book.objects.prefetch_related('authors')
    for book in books:
        authors = ', '.join([author.name for author in book.authors.all()])
        writer.writerow([book.title, authors, book.isbn or '', book.total_copies, book.available_copies])
    
    return response
