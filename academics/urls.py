from django.urls import path
from . import views

urlpatterns = [
    path('', views.SubjectListView.as_view(), name='subject-list'),
    path('add/', views.SubjectCreateView.as_view(), name='subject-add'),
    path('<int:pk>/edit/', views.SubjectUpdateView.as_view(), name='subject-edit'),
    path('<int:pk>/delete/', views.SubjectDeleteView.as_view(), name='subject-delete'),
]
