from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Sum, Avg, F, Case, When, Value
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    Hostel, Room, RoomAllocation, HostelStudent, MessMenu, MessAttendance,
    HostelFee, Warden, HostelExpense, RoomMaintenance, HostelVisitor,
    HostelInventory, OutpassRequest, HostelComplaint
)
from core.models import SchoolSettings, Student, Grade
import csv
import json

# ===== COMPREHENSIVE HOSTEL DASHBOARD =====
@login_required
def hostel_dashboard(request):
    """Advanced Hostel Management Dashboard"""
    school_settings = SchoolSettings.objects.first()
    
    # Hostel Overview Statistics
    hostel_stats = {
        'total_hostels': Hostel.objects.count(),
        'total_rooms': Room.objects.count(),
        'occupied_rooms': Room.objects.filter(is_occupied=True).count(),
        'available_rooms': Room.objects.filter(is_occupied=False).count(),
        'total_students': HostelStudent.objects.filter(is_active=True).count(),
        'total_capacity': Room.objects.aggregate(
            total=Sum('capacity')
        )['total'] or 0,
    }
    
    # Calculate occupancy rate
    if hostel_stats['total_capacity'] > 0:
        hostel_stats['occupancy_rate'] = (
            hostel_stats['total_students'] / hostel_stats['total_capacity'] * 100
        )
    else:
        hostel_stats['occupancy_rate'] = 0
    
    # Current Month Statistics
    current_month = timezone.now().replace(day=1)
    monthly_stats = {
        'new_admissions': HostelStudent.objects.filter(
            admission_date__gte=current_month
        ).count(),
        'checkout_requests': HostelStudent.objects.filter(
            checkout_date__gte=current_month
        ).count(),
        'maintenance_requests': RoomMaintenance.objects.filter(
            request_date__gte=current_month,
            status='pending'
        ).count(),
        'total_expenses': HostelExpense.objects.filter(
            expense_date__gte=current_month
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Hostel-wise Occupancy
    hostel_occupancy = Hostel.objects.annotate(
        total_rooms=Count('room'),
        occupied_rooms=Count('room', filter=Q(room__is_occupied=True)),
        total_capacity=Sum('room__capacity'),
        current_students=Count('room__roomallocation__student',
                             filter=Q(room__roomallocation__is_active=True)),
        occupancy_rate=Case(
            When(total_capacity=0, then=Value(0)),
            default=F('current_students') * 100.0 / F('total_capacity')
        )
    )
    
    # Recent Room Allocations
    recent_allocations = RoomAllocation.objects.select_related(
        'student', 'room', 'room__hostel'
    ).order_by('-allocation_date')[:15]
    
    # Pending Outpass Requests
    pending_outpass = OutpassRequest.objects.filter(
        status='pending'
    ).select_related('student').order_by('-request_date')[:10]
    
    # Mess Attendance Today
    today = timezone.now().date()
    mess_attendance_today = {
        'breakfast': MessAttendance.objects.filter(
            date=today,
            meal_type='breakfast',
            is_present=True
        ).count(),
        'lunch': MessAttendance.objects.filter(
            date=today,
            meal_type='lunch',
            is_present=True
        ).count(),
        'dinner': MessAttendance.objects.filter(
            date=today,
            meal_type='dinner',
            is_present=True
        ).count(),
    }
    
    # Fee Collection Statistics
    fee_stats = {
        'total_fees_collected': HostelFee.objects.filter(
            payment_status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'pending_fees': HostelFee.objects.filter(
            payment_status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'overdue_fees': HostelFee.objects.filter(
            payment_status='overdue'
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Recent Complaints
    recent_complaints = HostelComplaint.objects.select_related(
        'student', 'hostel'
    ).order_by('-complaint_date')[:10]
    
    # Maintenance Alerts
    maintenance_alerts = RoomMaintenance.objects.filter(
        status='pending'
    ).select_related('room', 'room__hostel').order_by('-request_date')[:10]
    
    # Monthly Trends
    monthly_trends = []
    for i in range(6):
        month_start = (timezone.now().replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        admissions = HostelStudent.objects.filter(
            admission_date__range=[month_start, month_end]
        ).count()
        
        expenses = HostelExpense.objects.filter(
            expense_date__range=[month_start, month_end]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        revenue = HostelFee.objects.filter(
            payment_date__range=[month_start, month_end],
            payment_status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_trends.append({
            'month': month_start.strftime('%b %Y'),
            'admissions': admissions,
            'expenses': float(expenses),
            'revenue': float(revenue)
        })
    
    context = {
        'page_title': 'Hostel Management Dashboard',
        'school_settings': school_settings,
        'hostel_stats': hostel_stats,
        'monthly_stats': monthly_stats,
        'hostel_occupancy': hostel_occupancy,
        'recent_allocations': recent_allocations,
        'pending_outpass': pending_outpass,
        'mess_attendance_today': mess_attendance_today,
        'fee_stats': fee_stats,
        'recent_complaints': recent_complaints,
        'maintenance_alerts': maintenance_alerts,
        'monthly_trends': list(reversed(monthly_trends)),
    }
    
    return render(request, 'hostel/dashboard.html', context)

# ===== HOSTEL MANAGEMENT =====
class HostelListView(LoginRequiredMixin, ListView):
    model = Hostel
    template_name = 'hostel/hostel_list.html'
    context_object_name = 'hostels'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Hostel.objects.annotate(
            total_rooms=Count('room'),
            occupied_rooms=Count('room', filter=Q(room__is_occupied=True)),
            total_capacity=Sum('room__capacity'),
            current_students=Count('room__roomallocation__student',
                                 filter=Q(room__roomallocation__is_active=True)),
            occupancy_rate=Case(
                When(total_capacity=0, then=Value(0)),
                default=F('current_students') * 100.0 / F('total_capacity')
            )
        )
        
        # Filtering
        gender_filter = self.request.GET.get('gender', '')
        status_filter = self.request.GET.get('status', '')
        
        if gender_filter:
            queryset = queryset.filter(gender=gender_filter)
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Hostel Management'
        context['gender_choices'] = Hostel.GENDER_CHOICES
        return context

class HostelDetailView(LoginRequiredMixin, DetailView):
    model = Hostel
    template_name = 'hostel/hostel_detail.html'
    context_object_name = 'hostel'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hostel = self.get_object()
        
        # Room information
        context['rooms'] = Room.objects.filter(hostel=hostel).annotate(
            current_occupants=Count('roomallocation',
                                  filter=Q(roomallocation__is_active=True))
        )
        
        # Current students
        context['current_students'] = HostelStudent.objects.filter(
            current_room__hostel=hostel,
            is_active=True
        ).select_related('student', 'current_room')
        
        # Warden information
        context['wardens'] = Warden.objects.filter(hostel=hostel, is_active=True)
        
        # Recent maintenance requests
        context['maintenance_requests'] = RoomMaintenance.objects.filter(
            room__hostel=hostel
        ).select_related('room').order_by('-request_date')[:10]
        
        # Occupancy statistics
        total_capacity = context['rooms'].aggregate(
            total=Sum('capacity')
        )['total'] or 0
        
        current_occupants = context['rooms'].aggregate(
            total=Sum('current_occupants')
        )['total'] or 0
        
        context['occupancy_stats'] = {
            'total_capacity': total_capacity,
            'current_occupants': current_occupants,
            'occupancy_rate': (current_occupants / total_capacity * 100) if total_capacity > 0 else 0,
            'available_beds': total_capacity - current_occupants
        }
        
        context['page_title'] = f'Hostel: {hostel.name}'
        return context

# ===== ROOM MANAGEMENT =====
class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'hostel/room_list.html'
    context_object_name = 'rooms'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Room.objects.select_related('hostel').annotate(
            current_occupants=Count('roomallocation',
                                  filter=Q(roomallocation__is_active=True)),
            available_beds=F('capacity') - F('current_occupants')
        )
        
        # Filtering
        hostel_filter = self.request.GET.get('hostel', '')
        status_filter = self.request.GET.get('status', '')
        room_type_filter = self.request.GET.get('room_type', '')
        
        if hostel_filter:
            queryset = queryset.filter(hostel_id=hostel_filter)
        if status_filter == 'available':
            queryset = queryset.filter(is_occupied=False)
        elif status_filter == 'occupied':
            queryset = queryset.filter(is_occupied=True)
        elif status_filter == 'maintenance':
            queryset = queryset.filter(status='maintenance')
        if room_type_filter:
            queryset = queryset.filter(room_type=room_type_filter)
        
        return queryset.order_by('hostel__name', 'room_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Room Management'
        context['hostels'] = Hostel.objects.filter(is_active=True)
        context['room_types'] = Room.ROOM_TYPE_CHOICES
        context['status_choices'] = Room.STATUS_CHOICES
        return context

# ===== ROOM ALLOCATION =====
@login_required
def room_allocation(request):
    """Allocate rooms to students"""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        room_id = request.POST.get('room_id')
        allocation_date = request.POST.get('allocation_date')
        remarks = request.POST.get('remarks', '')
        
        try:
            student = Student.objects.get(id=student_id)
            room = Room.objects.get(id=room_id)
            
            # Check if room has available capacity
            current_occupants = RoomAllocation.objects.filter(
                room=room,
                is_active=True
            ).count()
            
            if current_occupants >= room.capacity:
                messages.error(request, f'Room {room.room_number} is already at full capacity')
                return redirect('hostel:room_allocation')
            
            # Check if student already has active allocation
            existing_allocation = RoomAllocation.objects.filter(
                student=student,
                is_active=True
            ).first()
            
            if existing_allocation:
                messages.warning(request, f'{student.first_name} {student.last_name} already has an active room allocation')
                return redirect('hostel:room_allocation')
            
            # Create room allocation
            allocation = RoomAllocation.objects.create(
                student=student,
                room=room,
                allocation_date=allocation_date,
                remarks=remarks,
                allocated_by=request.user,
                is_active=True
            )
            
            # Create or update hostel student record
            hostel_student, created = HostelStudent.objects.get_or_create(
                student=student,
                defaults={
                    'admission_date': allocation_date,
                    'current_room': room,
                    'is_active': True
                }
            )
            
            if not created:
                hostel_student.current_room = room
                hostel_student.is_active = True
                hostel_student.save()
            
            # Update room occupancy status
            room.is_occupied = True
            room.save()
            
            messages.success(request, f'Room {room.room_number} allocated to {student.first_name} {student.last_name}')
            return redirect('hostel:room_allocation')
            
        except (Student.DoesNotExist, Room.DoesNotExist):
            messages.error(request, 'Invalid student or room selected')
        except Exception as e:
            messages.error(request, f'Error allocating room: {str(e)}')
    
    # GET request
    # Available rooms
    available_rooms = Room.objects.filter(
        status='active'
    ).annotate(
        current_occupants=Count('roomallocation',
                              filter=Q(roomallocation__is_active=True)),
        available_beds=F('capacity') - F('current_occupants')
    ).filter(available_beds__gt=0).select_related('hostel')
    
    # Students without room allocation
    allocated_student_ids = RoomAllocation.objects.filter(
        is_active=True
    ).values_list('student_id', flat=True)
    
    unallocated_students = Student.objects.filter(
        is_active=True
    ).exclude(id__in=allocated_student_ids).select_related('grade')
    
    # Recent allocations
    recent_allocations = RoomAllocation.objects.select_related(
        'student', 'room', 'room__hostel'
    ).order_by('-allocation_date')[:20]
    
    context = {
        'page_title': 'Room Allocation',
        'available_rooms': available_rooms,
        'unallocated_students': unallocated_students,
        'recent_allocations': recent_allocations,
    }
    
    return render(request, 'hostel/room_allocation.html', context)

# ===== STUDENT MANAGEMENT =====
class HostelStudentListView(LoginRequiredMixin, ListView):
    model = HostelStudent
    template_name = 'hostel/student_list.html'
    context_object_name = 'hostel_students'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = HostelStudent.objects.select_related(
            'student', 'student__grade', 'current_room', 'current_room__hostel'
        ).filter(is_active=True)
        
        # Filtering
        hostel_filter = self.request.GET.get('hostel', '')
        grade_filter = self.request.GET.get('grade', '')
        search_query = self.request.GET.get('search', '')
        
        if hostel_filter:
            queryset = queryset.filter(current_room__hostel_id=hostel_filter)
        if grade_filter:
            queryset = queryset.filter(student__grade_id=grade_filter)
        if search_query:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search_query) |
                Q(student__last_name__icontains=search_query) |
                Q(student__student_id__icontains=search_query)
            )
        
        return queryset.order_by('student__first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Hostel Students'
        context['hostels'] = Hostel.objects.filter(is_active=True)
        context['grades'] = Grade.objects.all()
        return context

# ===== MESS MANAGEMENT =====
@login_required
def mess_management(request):
    """Mess Management and Menu Planning"""
    # Current week's menu
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    current_menu = MessMenu.objects.filter(
        date__range=[start_of_week, end_of_week]
    ).order_by('date', 'meal_type')
    
    # Today's attendance
    todays_attendance = {
        'breakfast': MessAttendance.objects.filter(
            date=today,
            meal_type='breakfast'
        ).aggregate(
            present=Count('id', filter=Q(is_present=True)),
            total=Count('id')
        ),
        'lunch': MessAttendance.objects.filter(
            date=today,
            meal_type='lunch'
        ).aggregate(
            present=Count('id', filter=Q(is_present=True)),
            total=Count('id')
        ),
        'dinner': MessAttendance.objects.filter(
            date=today,
            meal_type='dinner'
        ).aggregate(
            present=Count('id', filter=Q(is_present=True)),
            total=Count('id')
        ),
    }
    
    # Weekly attendance trends
    weekly_attendance = []
    for i in range(7):
        date = start_of_week + timedelta(days=i)
        day_attendance = MessAttendance.objects.filter(
            date=date
        ).values('meal_type').annotate(
            present=Count('id', filter=Q(is_present=True)),
            total=Count('id')
        )
        
        weekly_attendance.append({
            'date': date,
            'day_name': date.strftime('%A'),
            'attendance': {item['meal_type']: item for item in day_attendance}
        })
    
    context = {
        'page_title': 'Mess Management',
        'current_menu': current_menu,
        'todays_attendance': todays_attendance,
        'weekly_attendance': weekly_attendance,
        'total_students': HostelStudent.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'hostel/mess_management.html', context)

# ===== OUTPASS MANAGEMENT =====
@login_required
def outpass_management(request):
    """Outpass Request Management"""
    outpass_requests = OutpassRequest.objects.select_related(
        'student', 'approved_by'
    ).order_by('-request_date')
    
    # Filtering
    status_filter = request.GET.get('status', '')
    hostel_filter = request.GET.get('hostel', '')
    
    if status_filter:
        outpass_requests = outpass_requests.filter(status=status_filter)
    if hostel_filter:
        outpass_requests = outpass_requests.filter(
            student__hostelstudent__current_room__hostel_id=hostel_filter
        )
    
    # Statistics
    outpass_stats = {
        'total_requests': outpass_requests.count(),
        'pending': outpass_requests.filter(status='pending').count(),
        'approved': outpass_requests.filter(status='approved').count(),
        'rejected': outpass_requests.filter(status='rejected').count(),
        'returned': outpass_requests.filter(status='returned').count(),
    }
    
    context = {
        'page_title': 'Outpass Management',
        'outpass_requests': outpass_requests[:50],
        'outpass_stats': outpass_stats,
        'hostels': Hostel.objects.filter(is_active=True),
        'status_choices': OutpassRequest.STATUS_CHOICES,
        'selected_status': status_filter,
        'selected_hostel': hostel_filter,
    }
    
    return render(request, 'hostel/outpass_management.html', context)

@login_required
def approve_outpass(request, pk):
    """Approve or reject outpass request"""
    outpass = get_object_or_404(OutpassRequest, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        
        if action == 'approve':
            outpass.status = 'approved'
            outpass.approved_by = request.user
            outpass.approval_date = timezone.now()
            outpass.approval_remarks = remarks
            
            messages.success(request, f'Outpass approved for {outpass.student.first_name} {outpass.student.last_name}')
            
        elif action == 'reject':
            outpass.status = 'rejected'
            outpass.approved_by = request.user
            outpass.approval_date = timezone.now()
            outpass.approval_remarks = remarks
            
            messages.warning(request, f'Outpass rejected for {outpass.student.first_name} {outpass.student.last_name}')
        
        outpass.save()
        return redirect('hostel:outpass_management')
    
    context = {
        'outpass': outpass,
        'page_title': f'Outpass Approval - {outpass.student.first_name} {outpass.student.last_name}'
    }
    
    return render(request, 'hostel/outpass_approval.html', context)

# ===== MAINTENANCE MANAGEMENT =====
@login_required
def maintenance_management(request):
    """Room Maintenance Management"""
    maintenance_requests = RoomMaintenance.objects.select_related(
        'room', 'room__hostel', 'reported_by', 'assigned_to'
    ).order_by('-request_date')
    
    # Filtering
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    hostel_filter = request.GET.get('hostel', '')
    
    if status_filter:
        maintenance_requests = maintenance_requests.filter(status=status_filter)
    if priority_filter:
        maintenance_requests = maintenance_requests.filter(priority=priority_filter)
    if hostel_filter:
        maintenance_requests = maintenance_requests.filter(room__hostel_id=hostel_filter)
    
    # Statistics
    maintenance_stats = {
        'total_requests': maintenance_requests.count(),
        'pending': maintenance_requests.filter(status='pending').count(),
        'in_progress': maintenance_requests.filter(status='in_progress').count(),
        'completed': maintenance_requests.filter(status='completed').count(),
        'high_priority': maintenance_requests.filter(priority='high').count(),
    }
    
    context = {
        'page_title': 'Maintenance Management',
        'maintenance_requests': maintenance_requests[:50],
        'maintenance_stats': maintenance_stats,
        'hostels': Hostel.objects.filter(is_active=True),
        'status_choices': RoomMaintenance.STATUS_CHOICES,
        'priority_choices': RoomMaintenance.PRIORITY_CHOICES,
        'selected_status': status_filter,
        'selected_priority': priority_filter,
        'selected_hostel': hostel_filter,
    }
    
    return render(request, 'hostel/maintenance_management.html', context)

# ===== FEE MANAGEMENT =====
@login_required
def hostel_fee_management(request):
    """Hostel Fee Management"""
    fees = HostelFee.objects.select_related(
        'student', 'student__hostelstudent__current_room__hostel'
    ).order_by('-due_date')
    
    # Filtering
    status_filter = request.GET.get('status', '')
    hostel_filter = request.GET.get('hostel', '')
    
    if status_filter:
        fees = fees.filter(payment_status=status_filter)
    if hostel_filter:
        fees = fees.filter(
            student__hostelstudent__current_room__hostel_id=hostel_filter
        )
    
    # Fee statistics
    fee_stats = {
        'total_collected': fees.filter(payment_status='paid').aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'pending_amount': fees.filter(payment_status='pending').aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'overdue_amount': fees.filter(payment_status='overdue').aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'collection_rate': 0,
    }
    
    # Calculate collection rate
    total_fees = fee_stats['total_collected'] + fee_stats['pending_amount'] + fee_stats['overdue_amount']
    if total_fees > 0:
        fee_stats['collection_rate'] = (fee_stats['total_collected'] / total_fees * 100)
    
    context = {
        'page_title': 'Hostel Fee Management',
        'fees': fees[:50],
        'fee_stats': fee_stats,
        'hostels': Hostel.objects.filter(is_active=True),
        'status_choices': HostelFee.STATUS_CHOICES,
        'selected_status': status_filter,
        'selected_hostel': hostel_filter,
    }
    
    return render(request, 'hostel/fee_management.html', context)

# ===== REPORTS AND ANALYTICS =====
@login_required
def hostel_reports(request):
    """Hostel Reports and Analytics"""
    # Date range filtering
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    report_type = request.GET.get('report_type', 'summary')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Occupancy analysis
    occupancy_stats = Hostel.objects.annotate(
        total_capacity=Sum('room__capacity'),
        current_occupants=Count('room__roomallocation__student',
                              filter=Q(room__roomallocation__is_active=True)),
        occupancy_rate=Case(
            When(total_capacity=0, then=Value(0)),
            default=F('current_occupants') * 100.0 / F('total_capacity')
        )
    )
    
    # Financial analysis
    financial_stats = {
        'total_revenue': HostelFee.objects.filter(
            payment_date__range=[start_date, end_date],
            payment_status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'total_expenses': HostelExpense.objects.filter(
            expense_date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'pending_fees': HostelFee.objects.filter(
            payment_status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Maintenance analysis
    maintenance_stats = RoomMaintenance.objects.filter(
        request_date__range=[start_date, end_date]
    ).values('status').annotate(count=Count('id'))
    
    # Student analysis
    student_stats = {
        'new_admissions': HostelStudent.objects.filter(
            admission_date__range=[start_date, end_date]
        ).count(),
        'checkouts': HostelStudent.objects.filter(
            checkout_date__range=[start_date, end_date]
        ).count(),
        'current_residents': HostelStudent.objects.filter(is_active=True).count(),
    }
    
    context = {
        'page_title': 'Hostel Reports & Analytics',
        'start_date': start_date,
        'end_date': end_date,
        'report_type': report_type,
        'occupancy_stats': occupancy_stats,
        'financial_stats': financial_stats,
        'maintenance_stats': maintenance_stats,
        'student_stats': student_stats,
    }
    
    return render(request, 'hostel/hostel_reports.html', context)

# ===== API ENDPOINTS =====
@login_required
def hostel_analytics_api(request):
    """API endpoint for hostel analytics data"""
    # Monthly occupancy trends
    monthly_data = []
    for i in range(12):
        month_start = (timezone.now().replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        occupants = HostelStudent.objects.filter(
            admission_date__lte=month_end,
            Q(checkout_date__gte=month_start) | Q(checkout_date__isnull=True)
        ).count()
        
        capacity = Room.objects.aggregate(total=Sum('capacity'))['total'] or 0
        occupancy_rate = (occupants / capacity * 100) if capacity > 0 else 0
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'occupancy_rate': round(occupancy_rate, 2),
            'occupants': occupants
        })
    
    # Hostel-wise occupancy
    hostel_occupancy = Hostel.objects.annotate(
        total_capacity=Sum('room__capacity'),
        current_occupants=Count('room__roomallocation__student',
                              filter=Q(room__roomallocation__is_active=True))
    ).values('name', 'total_capacity', 'current_occupants')
    
    # Mess attendance trends
    mess_trends = []
    for i in range(7):
        date = (timezone.now() - timedelta(days=i)).date()
        attendance = MessAttendance.objects.filter(date=date).aggregate(
            breakfast=Count('id', filter=Q(meal_type='breakfast', is_present=True)),
            lunch=Count('id', filter=Q(meal_type='lunch', is_present=True)),
            dinner=Count('id', filter=Q(meal_type='dinner', is_present=True))
        )
        
        mess_trends.append({
            'date': date.strftime('%Y-%m-%d'),
            'breakfast': attendance['breakfast'],
            'lunch': attendance['lunch'],
            'dinner': attendance['dinner']
        })
    
    return JsonResponse({
        'monthly_occupancy': list(reversed(monthly_data)),
        'hostel_occupancy': list(hostel_occupancy),
        'mess_trends': list(reversed(mess_trends)),
        'status': 'success'
    })

# ===== DATA EXPORT FUNCTIONS =====
@login_required
def export_hostel_data_csv(request):
    """Export hostel data to CSV"""
    export_type = request.GET.get('type', 'students')
    
    response = HttpResponse(content_type='text/csv')
    
    if export_type == 'students':
        response['Content-Disposition'] = 'attachment; filename="hostel_students.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Student Name', 'Student ID', 'Grade', 'Hostel', 'Room Number',
            'Admission Date', 'Contact Phone', 'Guardian Name', 'Status'
        ])
        
        students = HostelStudent.objects.select_related(
            'student', 'student__grade', 'current_room', 'current_room__hostel'
        ).filter(is_active=True)
        
        for hs in students:
            writer.writerow([
                f"{hs.student.first_name} {hs.student.last_name}",
                hs.student.student_id,
                hs.student.grade.name if hs.student.grade else '',
                hs.current_room.hostel.name if hs.current_room else '',
                hs.current_room.room_number if hs.current_room else '',
                hs.admission_date,
                hs.student.contact_phone,
                hs.student.father_name,
                'Active' if hs.is_active else 'Inactive'
            ])
    
    elif export_type == 'occupancy':
        response['Content-Disposition'] = 'attachment; filename="hostel_occupancy.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Hostel Name', 'Total Rooms', 'Total Capacity', 'Current Occupants',
            'Occupancy Rate', 'Available Beds'
        ])
        
        hostels = Hostel.objects.annotate(
            total_rooms=Count('room'),
            total_capacity=Sum('room__capacity'),
            current_occupants=Count('room__roomallocation__student',
                                  filter=Q(room__roomallocation__is_active=True))
        )
        
        for hostel in hostels:
            occupancy_rate = 0
            if hostel.total_capacity and hostel.total_capacity > 0:
                occupancy_rate = (hostel.current_occupants / hostel.total_capacity * 100)
            
            available_beds = (hostel.total_capacity or 0) - (hostel.current_occupants or 0)
            
            writer.writerow([
                hostel.name,
                hostel.total_rooms,
                hostel.total_capacity,
                hostel.current_occupants,
                f"{occupancy_rate:.2f}%",
                available_beds
            ])
    
    return response
