from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Book, Author, Category, BookIssue, BookReturn, LibraryMember
from core.models import Student, Teacher, SchoolSettings
import csv
import json

# ===== COMPREHENSIVE LIBRARY DASHBOARD =====
@login_required
def library_dashboard(request):
    """Advanced Library Management Dashboard"""
    school_settings = SchoolSettings.objects.first()
    
    # Comprehensive Statistics
    stats = {
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(is_available=True).count(),
        'issued_books': BookIssue.objects.filter(returned_date__isnull=True).count(),
        'overdue_books': BookIssue.objects.filter(
            returned_date__isnull=True,
            due_date__lt=timezone.now().date()
        ).count(),
        'total_members': LibraryMember.objects.filter(is_active=True).count(),
        'total_authors': Author.objects.count(),
        'total_categories': Category.objects.count(),
        'books_returned_today': BookReturn.objects.filter(
            return_date=timezone.now().date()
        ).count(),
    }
    
    # Recent Activities
    recent_issues = BookIssue.objects.select_related('book', 'member').order_by('-issue_date')[:10]
    recent_returns = BookReturn.objects.select_related('book_issue__book', 'book_issue__member').order_by('-return_date')[:10]
    
    # Popular Books & Categories
    popular_books = Book.objects.annotate(
        issue_count=Count('bookissue')
    ).order_by('-issue_count')[:10]
    
    popular_categories = Category.objects.annotate(
        book_count=Count('book'),
        issue_count=Count('book__bookissue')
    ).order_by('-issue_count')[:5]
    
    # Overdue Analysis
    overdue_issues = BookIssue.objects.filter(
        returned_date__isnull=True,
        due_date__lt=timezone.now().date()
    ).select_related('book', 'member').order_by('due_date')[:20]
    
    # Monthly Statistics
    current_month = timezone.now().replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    
    monthly_stats = {
        'current_month_issues': BookIssue.objects.filter(
            issue_date__gte=current_month
        ).count(),
        'last_month_issues': BookIssue.objects.filter(
            issue_date__gte=last_month,
            issue_date__lt=current_month
        ).count(),
        'current_month_returns': BookReturn.objects.filter(
            return_date__gte=current_month
        ).count(),
    }
    
    context = {
        'page_title': 'Library Management Dashboard',
        'school_settings': school_settings,
        'stats': stats,
        'monthly_stats': monthly_stats,
        'recent_issues': recent_issues,
        'recent_returns': recent_returns,
        'popular_books': popular_books,
        'popular_categories': popular_categories,
        'overdue_issues': overdue_issues,
    }
    
    return render(request, 'library/dashboard.html', context)

# ===== BOOK MANAGEMENT =====
class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Book.objects.select_related('author', 'category').annotate(
            issue_count=Count('bookissue')
        )
        
        search_query = self.request.GET.get('search', '')
        category_filter = self.request.GET.get('category', '')
        availability_filter = self.request.GET.get('availability', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__name__icontains=search_query) |
                Q(isbn__icontains=search_query)
            )
        
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        if availability_filter == 'available':
            queryset = queryset.filter(is_available=True)
        elif availability_filter == 'issued':
            queryset = queryset.filter(is_available=False)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Book Management'
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_availability'] = self.request.GET.get('availability', '')
        return context

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        
        # Issue History
        context['issue_history'] = BookIssue.objects.filter(
            book=book
        ).select_related('member').order_by('-issue_date')[:20]
        
        # Current Issue Status
        current_issue = BookIssue.objects.filter(
            book=book,
            returned_date__isnull=True
        ).select_related('member').first()
        
        context['current_issue'] = current_issue
        context['page_title'] = f'Book: {book.title}'
        return context

# ===== BOOK ISSUE MANAGEMENT =====
@login_required
def issue_book(request):
    """Issue a book to a member"""
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        member_id = request.POST.get('member_id')
        due_date = request.POST.get('due_date')
        
        try:
            book = Book.objects.get(id=book_id, is_available=True)
            member = LibraryMember.objects.get(id=member_id, is_active=True)
            
            # Check if member has overdue books
            overdue_count = BookIssue.objects.filter(
                member=member,
                returned_date__isnull=True,
                due_date__lt=timezone.now().date()
            ).count()
            
            if overdue_count > 0:
                messages.error(request, f'{member.name} has {overdue_count} overdue books. Please return them first.')
                return redirect('library:issue_book')
            
            # Check issue limit
            current_issues = BookIssue.objects.filter(
                member=member,
                returned_date__isnull=True
            ).count()
            
            if current_issues >= 5:  # Maximum 5 books per member
                messages.error(request, f'{member.name} has reached the maximum book limit (5 books).')
                return redirect('library:issue_book')
            
            # Create book issue
            book_issue = BookIssue.objects.create(
                book=book,
                member=member,
                issue_date=timezone.now().date(),
                due_date=due_date,
                issued_by=request.user
            )
            
            # Update book availability
            book.is_available = False
            book.save()
            
            messages.success(request, f'Book "{book.title}" issued successfully to {member.name}')
            return redirect('library:book_issue_detail', pk=book_issue.pk)
            
        except Book.DoesNotExist:
            messages.error(request, 'Book not found or not available')
        except LibraryMember.DoesNotExist:
            messages.error(request, 'Library member not found')
        except Exception as e:
            messages.error(request, f'Error issuing book: {str(e)}')
    
    # GET request - show issue form
    available_books = Book.objects.filter(is_available=True).select_related('author', 'category')
    active_members = LibraryMember.objects.filter(is_active=True)
    
    context = {
        'page_title': 'Issue Book',
        'available_books': available_books,
        'active_members': active_members,
        'default_due_date': (timezone.now() + timedelta(days=14)).date()  # 2 weeks default
    }
    
    return render(request, 'library/issue_book.html', context)

@login_required
def return_book(request):
    """Return a book"""
    if request.method == 'POST':
        issue_id = request.POST.get('issue_id')
        fine_amount = request.POST.get('fine_amount', 0)
        remarks = request.POST.get('remarks', '')
        
        try:
            book_issue = BookIssue.objects.get(
                id=issue_id,
                returned_date__isnull=True
            )
            
            # Calculate fine for overdue books
            today = timezone.now().date()
            if today > book_issue.due_date:
                overdue_days = (today - book_issue.due_date).days
                calculated_fine = overdue_days * 5  # Rs. 5 per day
                if not fine_amount:
                    fine_amount = calculated_fine
            
            # Create return record
            book_return = BookReturn.objects.create(
                book_issue=book_issue,
                return_date=today,
                fine_amount=fine_amount or 0,
                remarks=remarks,
                returned_by=request.user
            )
            
            # Update issue record
            book_issue.returned_date = today
            book_issue.save()
            
            # Update book availability
            book_issue.book.is_available = True
            book_issue.book.save()
            
            messages.success(request, f'Book "{book_issue.book.title}" returned successfully')
            if fine_amount and float(fine_amount) > 0:
                messages.info(request, f'Fine collected: Rs. {fine_amount}')
            
            return redirect('library:book_return_detail', pk=book_return.pk)
            
        except BookIssue.DoesNotExist:
            messages.error(request, 'Book issue record not found')
        except Exception as e:
            messages.error(request, f'Error returning book: {str(e)}')
    
    # GET request - show return form
    issued_books = BookIssue.objects.filter(
        returned_date__isnull=True
    ).select_related('book', 'member').order_by('due_date')
    
    context = {
        'page_title': 'Return Book',
        'issued_books': issued_books,
    }
    
    return render(request, 'library/return_book.html', context)

# ===== LIBRARY MEMBER MANAGEMENT =====
class LibraryMemberListView(LoginRequiredMixin, ListView):
    model = LibraryMember
    template_name = 'library/member_list.html'
    context_object_name = 'members'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = LibraryMember.objects.annotate(
            current_issues=Count('bookissue', filter=Q(bookissue__returned_date__isnull=True)),
            total_issues=Count('bookissue'),
            overdue_books=Count('bookissue', filter=Q(
                bookissue__returned_date__isnull=True,
                bookissue__due_date__lt=timezone.now().date()
            ))
        )
        
        search_query = self.request.GET.get('search', '')
        status_filter = self.request.GET.get('status', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(membership_id__icontains=search_query)
            )
        
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status_filter == 'overdue':
            queryset = queryset.filter(overdue_books__gt=0)
        
        return queryset.order_by('-created_at')

# ===== REPORTS AND ANALYTICS =====
@login_required
def library_reports(request):
    """Library Reports and Analytics"""
    # Date range filtering
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Issue/Return Statistics
    issues_in_period = BookIssue.objects.filter(
        issue_date__range=[start_date, end_date]
    )
    
    returns_in_period = BookReturn.objects.filter(
        return_date__range=[start_date, end_date]
    )
    
    # Most Popular Books
    popular_books = Book.objects.annotate(
        issue_count=Count('bookissue', filter=Q(
            bookissue__issue_date__range=[start_date, end_date]
        ))
    ).filter(issue_count__gt=0).order_by('-issue_count')[:20]
    
    # Category-wise Statistics
    category_stats = Category.objects.annotate(
        total_books=Count('book'),
        issued_books=Count('book__bookissue', filter=Q(
            book__bookissue__issue_date__range=[start_date, end_date]
        ))
    ).order_by('-issued_books')
    
    # Member Statistics
    active_members = LibraryMember.objects.annotate(
        books_issued=Count('bookissue', filter=Q(
            bookissue__issue_date__range=[start_date, end_date]
        ))
    ).filter(books_issued__gt=0).order_by('-books_issued')[:20]
    
    # Fine Collection
    total_fine = returns_in_period.aggregate(
        total=Sum('fine_amount')
    )['total'] or 0
    
    context = {
        'page_title': 'Library Reports & Analytics',
        'start_date': start_date,
        'end_date': end_date,
        'issues_count': issues_in_period.count(),
        'returns_count': returns_in_period.count(),
        'total_fine': total_fine,
        'popular_books': popular_books,
        'category_stats': category_stats,
        'active_members': active_members,
    }
    
    return render(request, 'library/reports.html', context)

# ===== API ENDPOINTS =====
@login_required
def library_analytics_api(request):
    """API endpoint for library analytics data"""
    # Monthly issue trends (last 12 months)
    twelve_months_ago = timezone.now() - timedelta(days=365)
    monthly_issues = []
    
    for i in range(12):
        month_start = (timezone.now().replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        issues_count = BookIssue.objects.filter(
            issue_date__range=[month_start, month_end]
        ).count()
        
        monthly_issues.append({
            'month': month_start.strftime('%b %Y'),
            'issues': issues_count
        })
    
    # Category-wise distribution
    category_data = Category.objects.annotate(
        book_count=Count('book'),
        issue_count=Count('book__bookissue')
    ).values('name', 'book_count', 'issue_count')
    
    # Current status overview
    overview = {
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(is_available=True).count(),
        'issued_books': BookIssue.objects.filter(returned_date__isnull=True).count(),
        'overdue_books': BookIssue.objects.filter(
            returned_date__isnull=True,
            due_date__lt=timezone.now().date()
        ).count(),
        'total_members': LibraryMember.objects.filter(is_active=True).count(),
    }
    
    return JsonResponse({
        'monthly_trends': list(reversed(monthly_issues)),
        'category_distribution': list(category_data),
        'overview': overview,
        'status': 'success'
    })

# ===== DATA EXPORT FUNCTIONS =====
@login_required
def export_books_csv(request):
    """Export books data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="library_books.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Title', 'Author', 'Category', 'ISBN', 'Publication Year',
        'Available', 'Total Issues', 'Current Status'
    ])
    
    books = Book.objects.select_related('author', 'category').annotate(
        total_issues=Count('bookissue')
    )
    
    for book in books:
        writer.writerow([
            book.title,
            book.author.name,
            book.category.name,
            book.isbn,
            book.publication_year,
            'Yes' if book.is_available else 'No',
            book.total_issues,
            'Available' if book.is_available else 'Issued'
        ])
    
    return response

@login_required
def export_members_csv(request):
    """Export library members data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="library_members.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Membership ID', 'Name', 'Email', 'Phone', 'Member Type',
        'Join Date', 'Status', 'Current Issues', 'Total Issues'
    ])
    
    members = LibraryMember.objects.annotate(
        current_issues=Count('bookissue', filter=Q(bookissue__returned_date__isnull=True)),
        total_issues=Count('bookissue')
    )
    
    for member in members:
        writer.writerow([
            member.membership_id,
            member.name,
            member.email,
            member.phone,
            member.member_type,
            member.created_at.date(),
            'Active' if member.is_active else 'Inactive',
            member.current_issues,
            member.total_issues
        ])
    
    return response
