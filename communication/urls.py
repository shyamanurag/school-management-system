from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    # Dashboard
    path('', views.communication_dashboard, name='dashboard'),
    
    # Notice Management
    path('notices/', views.NoticeListView.as_view(), name='notice-list'),
    path('notices/create/', views.NoticeCreateView.as_view(), name='notice-create'),
    path('notices/<int:pk>/', views.NoticeDetailView.as_view(), name='notice-detail'),
    path('notices/<int:pk>/edit/', views.NoticeUpdateView.as_view(), name='notice-update'),
    path('notices/<int:pk>/delete/', views.NoticeDeleteView.as_view(), name='notice-delete'),
    
    # Notification Management
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark-notification-read'),
    
    # Messaging System
    path('messages/', views.MessageListView.as_view(), name='message-list'),
    path('messages/send/', views.send_message, name='send-message'),
    
    # Bulk Communication
    path('bulk-notification/', views.bulk_notification, name='bulk-notification'),
    
    # Reports
    path('reports/', views.communication_reports, name='reports'),
]