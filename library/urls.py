from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import BookViewSet, LibraryMemberViewSet, BookIssueViewSet

router = DefaultRouter()
router.register(r'api/books', BookViewSet)
router.register(r'api/librarymembers', LibraryMemberViewSet)
router.register(r'api/bookissues', BookIssueViewSet)

urlpatterns = [
    path('', views.BookListView.as_view(), name='book-list'),
    path('add/', views.BookCreateView.as_view(), name='book-add'),
    path('<int:pk>/edit/', views.BookUpdateView.as_view(), name='book-edit'),
    path('<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    path('', include(router.urls)),
]
