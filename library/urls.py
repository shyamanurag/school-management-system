from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets (temporarily disabled)
router = DefaultRouter()
# router.register(r'books', BookViewSet, basename='library-book')
# router.register(r'members', LibraryMemberViewSet, basename='library-member')
# router.register(r'issues', BookIssueViewSet, basename='library-issue')

# Web Interface URLs - NUCLEAR REBUILD OF LIBRARY MODULE
urlpatterns = [
    # Library Dashboard
    path('', views.library_dashboard, name='dashboard'),
    
    # Book Management
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('books/export/', views.export_books, name='export-books'),
    
    # Book Circulation
    path('issue/', views.issue_book, name='issue-book'),
    path('return/<int:issue_id>/', views.return_book, name='return-book'),
    
    # Member Management
    path('members/', views.LibraryMemberListView.as_view(), name='member-list'),
    
    # Reports
    path('reports/', views.library_reports, name='reports'),
    
    # API URLs (temporarily disabled)
    # path('api/', include(router.urls)),
]
