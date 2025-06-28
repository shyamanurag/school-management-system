from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
from .models import Book, Author, Subject, LibraryMember

@login_required
def library_dashboard(request):
    return render(request, 'library/dashboard.html', {'page_title': 'Library Dashboard'})

class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'
    paginate_by = 20

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'

class LibraryMemberListView(LoginRequiredMixin, ListView):
    model = LibraryMember
    template_name = 'library/member_list.html'
    context_object_name = 'members'
    paginate_by = 20

@login_required
def export_books(request):
    return HttpResponse("Export functionality coming soon")

@login_required  
def issue_book(request):
    return render(request, 'library/issue_book.html', {'page_title': 'Issue Book'})

@login_required
def return_book(request, issue_id):
    return render(request, 'library/return_book.html', {'page_title': 'Return Book'})

@login_required
def library_reports(request):
    return render(request, 'library/reports.html', {'page_title': 'Library Reports'})
