from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Sum, Avg, F, Case, When, Value, BooleanField
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.mail import send_mass_mail
from django.core.paginator import Paginator
from .models import Notice, Notification, Message
from core.models import Student, Teacher, Grade, SchoolSettings, Employee
from django.contrib.auth.models import User
import csv
import json

# ===== COMPREHENSIVE COMMUNICATION DASHBOARD =====
@login_required
def communication_dashboard(request):
    """Advanced Communication Management Dashboard"""
    school_settings = SchoolSettings.objects.first()
    
    # Notice Statistics
    notice_stats = {
        'total_notices': Notice.objects.count(),
        'active_notices': Notice.objects.filter(is_active=True).count(),
        'published_today': Notice.objects.filter(
            publish_date=timezone.now().date()
        ).count(),
        'recent_notices': Notice.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count(),
    }
    
    # Notification Statistics  
    notification_stats = {
        'total_notifications': Notification.objects.count(),
        'unread_notifications': Notification.objects.filter(
            is_read=False
        ).count(),
        'sent_today': Notification.objects.filter(
            created_at__date=timezone.now().date()
        ).count(),
        'user_unread': Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count(),
    }
    
    # Message Statistics
    message_stats = {
        'total_messages': Message.objects.count(),
        'unread_messages': Message.objects.filter(
            is_read=False
        ).count(),
        'sent_today': Message.objects.filter(
            created_at__date=timezone.now().date()
        ).count(),
        'user_unread': Message.objects.filter(
            recipient=request.user, is_read=False
        ).count(),
    }
    
    # Recent Activity
    recent_notices = Notice.objects.filter(
        is_active=True
    ).select_related('created_by').order_by('-created_at')[:10]
    
    recent_notifications = Notification.objects.select_related(
        'recipient', 'sender'
    ).order_by('-created_at')[:15]
    
    recent_messages = Message.objects.select_related(
        'sender', 'recipient'
    ).order_by('-created_at')[:10]
    
    # Communication Trends (Last 7 days)
    communication_trends = []
    for i in range(7):
        date = (timezone.now() - timedelta(days=i)).date()
        daily_stats = {
            'date': date.strftime('%Y-%m-%d'),
            'notices': Notice.objects.filter(publish_date=date).count(),
            'notifications': Notification.objects.filter(
                created_at__date=date
            ).count(),
            'messages': Message.objects.filter(created_at__date=date).count(),
        }
        communication_trends.append(daily_stats)
    
    # Audience Reach Analytics
    audience_reach = {
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_teachers': Teacher.objects.filter(is_active=True).count(),
        'total_staff': Employee.objects.filter(status='active').count(),
        'total_users': User.objects.filter(is_active=True).count(),
    }
    
    # Engagement Analytics
    engagement_stats = {
        'notification_read_rate': (
            notification_stats['total_notifications'] - notification_stats['unread_notifications']
        ) / max(notification_stats['total_notifications'], 1) * 100,
        'message_read_rate': (
            message_stats['total_messages'] - message_stats['unread_messages']
        ) / max(message_stats['total_messages'], 1) * 100,
        'active_communicators': User.objects.filter(
            Q(sent_notifications__created_at__gte=timezone.now() - timedelta(days=30)) |
            Q(sent_messages__created_at__gte=timezone.now() - timedelta(days=30))
        ).distinct().count(),
    }
    
    context = {
        'page_title': 'Communication Management Dashboard',
        'school_settings': school_settings,
        'notice_stats': notice_stats,
        'notification_stats': notification_stats,
        'message_stats': message_stats,
        'recent_notices': recent_notices,
        'recent_notifications': recent_notifications,
        'recent_messages': recent_messages,
        'communication_trends': list(reversed(communication_trends)),
        'audience_reach': audience_reach,
        'engagement_stats': engagement_stats,
    }
    
    return render(request, 'communication/dashboard.html', context)

# ===== NOTICE MANAGEMENT =====
class NoticeListView(LoginRequiredMixin, ListView):
    model = Notice
    template_name = 'communication/notice_list.html'
    context_object_name = 'notices'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Notice.objects.select_related('created_by')
        
        # Filtering
        status_filter = self.request.GET.get('status', '')
        visible_to_filter = self.request.GET.get('visible_to', '')
        search_query = self.request.GET.get('search', '')
        
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        if visible_to_filter:
            queryset = queryset.filter(visible_to=visible_to_filter)
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(created_by__first_name__icontains=search_query) |
                Q(created_by__last_name__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Notice Management'
        context['total_notices'] = Notice.objects.count()
        context['active_notices'] = Notice.objects.filter(is_active=True).count()
        context['visible_to_choices'] = [
            ('students', 'Students'),
            ('teachers', 'Teachers'),
            ('staff', 'Staff'),
            ('all', 'All'),
        ]
        return context

class NoticeDetailView(LoginRequiredMixin, DetailView):
    model = Notice
    template_name = 'communication/notice_detail.html'
    context_object_name = 'notice'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notice = self.get_object()
        
        # Delivery statistics
        context['delivery_stats'] = {
            'total_recipients': self.get_recipient_count(notice),
            'delivery_status': 'published' if notice.is_active else 'draft',
            'published_date': notice.publish_date,
        }
        
        # Related notices
        context['related_notices'] = Notice.objects.filter(
            visible_to=notice.visible_to,
            is_active=True
        ).exclude(id=notice.id)[:5]
        
        context['page_title'] = f'Notice: {notice.title}'
        return context
    
    def get_recipient_count(self, notice):
        """Calculate the number of potential recipients based on visible_to"""
        if notice.visible_to == 'students':
            return Student.objects.filter(is_active=True).count()
        elif notice.visible_to == 'teachers':
            return Teacher.objects.filter(is_active=True).count()
        elif notice.visible_to == 'staff':
            return Employee.objects.filter(status='active').count()
        else:  # all
            return (Student.objects.filter(is_active=True).count() +
                   Teacher.objects.filter(is_active=True).count() +
                   Employee.objects.filter(status='active').count())

class NoticeCreateView(LoginRequiredMixin, CreateView):
    model = Notice
    template_name = 'communication/notice_form.html'
    fields = ['title', 'content', 'visible_to', 'publish_date', 'is_active']
    success_url = reverse_lazy('communication:notice-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Create notifications for relevant users
        self.send_notice_notifications(form.instance)
        
        messages.success(self.request, f'Notice "{form.instance.title}" created successfully!')
        return response
    
    def send_notice_notifications(self, notice):
        """Send notifications to target audience"""
        try:
            # Get recipients based on visible_to field
            recipients = []
            
            if notice.visible_to == 'students':
                recipients = User.objects.filter(
                    student__is_active=True
                ).distinct()
            elif notice.visible_to == 'teachers':
                recipients = User.objects.filter(
                    teacher__is_active=True
                ).distinct()
            elif notice.visible_to == 'staff':
                recipients = User.objects.filter(
                    employee__status='active'
                ).distinct()
            elif notice.visible_to == 'all':
                recipients = User.objects.filter(is_active=True)
            
            # Create notification records for users
            notifications = []
            for user in recipients[:50]:  # Limit to avoid overwhelming
                notifications.append(
                    Notification(
                        title=f"New Notice: {notice.title}",
                        message=notice.content[:200] + "..." if len(notice.content) > 200 else notice.content,
                        recipient=user,
                        sender=self.request.user
                    )
                )
            
            if notifications:
                Notification.objects.bulk_create(notifications)
                
        except Exception as e:
            messages.warning(self.request, f"Notice created but notification sending failed: {str(e)}")

class NoticeUpdateView(LoginRequiredMixin, UpdateView):
    model = Notice
    template_name = 'communication/notice_form.html'
    fields = ['title', 'content', 'visible_to', 'publish_date', 'is_active']
    success_url = reverse_lazy('communication:notice-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Notice "{form.instance.title}" updated successfully!')
        return super().form_valid(form)

class NoticeDeleteView(LoginRequiredMixin, DeleteView):
    model = Notice
    template_name = 'communication/notice_confirm_delete.html'
    success_url = reverse_lazy('communication:notice-list')
    
    def delete(self, request, *args, **kwargs):
        notice = self.get_object()
        messages.success(request, f'Notice "{notice.title}" deleted successfully!')
        return super().delete(request, *args, **kwargs)

# ===== NOTIFICATION MANAGEMENT =====
class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'communication/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Notification.objects.select_related('recipient', 'sender')
        
        # Filter by user's notifications or all if admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(recipient=self.request.user)
        
        read_filter = self.request.GET.get('read_status', '')
        
        if read_filter == 'unread':
            queryset = queryset.filter(is_read=False)
        elif read_filter == 'read':
            queryset = queryset.filter(is_read=True)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Notifications'
        
        # User-specific stats
        user_notifications = Notification.objects.filter(recipient=self.request.user)
        context['unread_count'] = user_notifications.filter(is_read=False).count()
        context['total_count'] = user_notifications.count()
        
        return context

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'})

@login_required
def mark_all_notifications_read(request):
    """Mark all user notifications as read"""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    messages.success(request, f'Marked {count} notifications as read')
    return redirect('communication:notification-list')

# ===== MESSAGE MANAGEMENT =====
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'communication/message_list.html'
    context_object_name = 'messages'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        
        # Show messages where user is sender or recipient
        queryset = Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).select_related('sender', 'recipient')
        
        message_type = self.request.GET.get('type', 'inbox')
        
        if message_type == 'inbox':
            queryset = queryset.filter(recipient=user)
        elif message_type == 'sent':
            queryset = queryset.filter(sender=user)
        elif message_type == 'unread':
            queryset = queryset.filter(recipient=user, is_read=False)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['page_title'] = 'Messages'
        context['inbox_count'] = Message.objects.filter(recipient=user).count()
        context['sent_count'] = Message.objects.filter(sender=user).count()
        context['unread_count'] = Message.objects.filter(
            recipient=user, is_read=False
        ).count()
        context['current_type'] = self.request.GET.get('type', 'inbox')
        
        return context

class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'communication/message_detail.html'
    context_object_name = 'message'
    
    def get_object(self, queryset=None):
        message = super().get_object(queryset)
        
        # Mark as read if user is recipient and message is unread
        if message.recipient == self.request.user and not message.is_read:
            message.is_read = True
            message.save()
        
        return message
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = self.get_object()
        
        context['page_title'] = f'Message: {message.subject}'
        return context

@login_required
def send_message(request):
    """Send a new message"""
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        
        try:
            recipient = get_object_or_404(User, id=recipient_id)
            
            message = Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                content=content,
            )
            
            # Create notification for recipient
            Notification.objects.create(
                recipient=recipient,
                title=f"New Message: {subject}",
                message=f"You have received a new message from {request.user.get_full_name()}",
                sender=request.user
            )
            
            messages.success(request, 'Message sent successfully!')
            return redirect('communication:message-detail', pk=message.pk)
            
        except Exception as e:
            messages.error(request, f'Error sending message: {str(e)}')
    
    # GET request
    users = User.objects.filter(is_active=True).exclude(
        id=request.user.id
    ).order_by('first_name', 'last_name')
    
    context = {
        'page_title': 'Send Message',
        'users': users,
    }
    
    return render(request, 'communication/send_message.html', context)

# ===== BULK COMMUNICATION =====
@login_required
def bulk_notification(request):
    """Send bulk notifications to multiple users"""
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        target_audience = request.POST.get('target_audience')
        
        try:
            # Get recipients based on target audience
            recipients = []
            
            if target_audience == 'students':
                recipients = User.objects.filter(
                    student__is_active=True
                ).distinct()
            elif target_audience == 'teachers':
                recipients = User.objects.filter(
                    teacher__is_active=True
                ).distinct()
            elif target_audience == 'staff':
                recipients = User.objects.filter(
                    employee__status='active'
                ).distinct()
            elif target_audience == 'all':
                recipients = User.objects.filter(is_active=True)
            
            # Create notifications
            notifications = [
                Notification(
                    recipient=user,
                    title=title,
                    message=message,
                    sender=request.user
                ) for user in recipients
            ]
            
            Notification.objects.bulk_create(notifications)
            
            messages.success(
                request, 
                f'Bulk notification sent to {len(recipients)} recipients successfully!'
            )
            return redirect('communication:dashboard')
            
        except Exception as e:
            messages.error(request, f'Error sending bulk notification: {str(e)}')
    
    # GET request
    context = {
        'page_title': 'Send Bulk Notification',
        'audience_choices': [
            ('students', 'Students'),
            ('teachers', 'Teachers'),
            ('staff', 'Staff'),
            ('all', 'All Users'),
        ],
    }
    
    return render(request, 'communication/bulk_notification.html', context)

# ===== COMMUNICATION REPORTS =====
@login_required
def communication_reports(request):
    """Comprehensive Communication Analytics & Reports"""
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
    
    # Notice Analytics
    notice_analytics = {
        'total_published': Notice.objects.filter(
            publish_date__range=[start_date, end_date],
            is_active=True
        ).count(),
        'by_audience': Notice.objects.filter(
            publish_date__range=[start_date, end_date]
        ).values('visible_to').annotate(count=Count('id')),
    }
    
    # Notification Analytics
    notification_analytics = {
        'total_sent': Notification.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).count(),
        'read_rate': 0,
    }
    
    # Calculate read rate
    total_notifications = notification_analytics['total_sent']
    if total_notifications > 0:
        read_notifications = Notification.objects.filter(
            created_at__date__range=[start_date, end_date],
            is_read=True
        ).count()
        notification_analytics['read_rate'] = (read_notifications / total_notifications) * 100
    
    # Message Analytics
    message_analytics = {
        'total_sent': Message.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).count(),
        'read_rate': 0,
    }
    
    # Calculate message read rate
    total_messages = message_analytics['total_sent']
    if total_messages > 0:
        read_messages = Message.objects.filter(
            created_at__date__range=[start_date, end_date],
            is_read=True
        ).count()
        message_analytics['read_rate'] = (read_messages / total_messages) * 100
    
    # Daily Communication Trends
    daily_trends = []
    current_date = start_date
    while current_date <= end_date:
        daily_data = {
            'date': current_date.strftime('%Y-%m-%d'),
            'notices': Notice.objects.filter(publish_date=current_date).count(),
            'notifications': Notification.objects.filter(
                created_at__date=current_date
            ).count(),
            'messages': Message.objects.filter(created_at__date=current_date).count(),
        }
        daily_trends.append(daily_data)
        current_date += timedelta(days=1)
    
    # Top Communicators
    top_notice_creators = Notice.objects.filter(
        publish_date__range=[start_date, end_date]
    ).values(
        'created_by__first_name', 'created_by__last_name'
    ).annotate(count=Count('id')).order_by('-count')[:10]
    
    top_message_senders = Message.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).values(
        'sender__first_name', 'sender__last_name'
    ).annotate(count=Count('id')).order_by('-count')[:10]
    
    context = {
        'page_title': 'Communication Reports & Analytics',
        'start_date': start_date,
        'end_date': end_date,
        'notice_analytics': notice_analytics,
        'notification_analytics': notification_analytics,
        'message_analytics': message_analytics,
        'daily_trends': daily_trends,
        'top_notice_creators': top_notice_creators,
        'top_message_senders': top_message_senders,
    }
    
    return render(request, 'communication/reports.html', context)

# ===== API ENDPOINTS =====
@login_required
def communication_analytics_api(request):
    """API endpoint for communication analytics charts"""
    
    # Last 30 days trend
    trends = []
    for i in range(30):
        date = (timezone.now() - timedelta(days=i)).date()
        daily_stats = {
            'date': date.strftime('%Y-%m-%d'),
            'notices': Notice.objects.filter(publish_date=date).count(),
            'notifications': Notification.objects.filter(
                created_at__date=date
            ).count(),
            'messages': Message.objects.filter(created_at__date=date).count(),
        }
        trends.append(daily_stats)
    
    # Audience reach
    audience_data = Notice.objects.filter(
        is_active=True
    ).values('visible_to').annotate(count=Count('id'))
    
    data = {
        'trends': list(reversed(trends)),
        'audience_reach': list(audience_data),
        'engagement_metrics': {
            'unread_notifications': Notification.objects.filter(
                is_read=False
            ).count(),
            'unread_messages': Message.objects.filter(
                is_read=False
            ).count(),
        }
    }
    
    return JsonResponse(data)

# ===== EXPORT FUNCTIONS =====
@login_required
def export_communication_data(request):
    """Export communication data to CSV"""
    data_type = request.GET.get('type', 'notices')
    
    response = HttpResponse(content_type='text/csv')
    
    if data_type == 'notices':
        response['Content-Disposition'] = 'attachment; filename="notices_export.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Title', 'Visible To', 'Publish Date', 'Status', 'Created By'
        ])
        
        notices = Notice.objects.select_related('created_by').order_by('-created_at')
        for notice in notices:
            writer.writerow([
                notice.title,
                notice.visible_to,
                notice.publish_date,
                'Active' if notice.is_active else 'Inactive',
                notice.created_by.get_full_name() if notice.created_by else 'N/A'
            ])
    
    elif data_type == 'messages':
        response['Content-Disposition'] = 'attachment; filename="messages_export.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Subject', 'Sender', 'Recipient', 'Sent Date', 'Read Status'
        ])
        
        messages = Message.objects.select_related(
            'sender', 'recipient'
        ).order_by('-created_at')
        
        for message in messages:
            writer.writerow([
                message.subject,
                message.sender.get_full_name(),
                message.recipient.get_full_name(),
                message.created_at,
                'Read' if message.is_read else 'Unread'
            ])
    
    return response 