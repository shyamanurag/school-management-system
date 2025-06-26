from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .models import (
    Subject, ClassSubject, Exam, ExamSchedule, StudentExamResult,
    Grade, Assignment, StudentAssignment, Timetable, Attendance,
    StudentClassAttendance, Holiday
)
from .serializers import (
    SubjectSerializer, ClassSubjectSerializer, ExamSerializer,
    ExamScheduleSerializer, StudentExamResultSerializer, GradeSerializer,
    AssignmentSerializer, StudentAssignmentSerializer, TimetableSerializer,
    AttendanceSerializer, StudentClassAttendanceSerializer, HolidaySerializer
)

class SubjectViewSet(viewsets.ModelViewSet):
    """API endpoints for Subject management"""
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Subject.objects.filter(school=self.request.user.profile.school)
    
    @action(detail=True, methods=['get'])
    def class_assignments(self, request, pk=None):
        """Get all class assignments for this subject"""
        subject = self.get_object()
        assignments = ClassSubject.objects.filter(subject=subject)
        serializer = ClassSubjectSerializer(assignments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def performance_analytics(self, request, pk=None):
        """Get performance analytics for this subject"""
        subject = self.get_object()
        results = StudentExamResult.objects.filter(
            exam_schedule__class_subject__subject=subject
        )
        
        analytics = {
            'total_students': results.values('student').distinct().count(),
            'average_marks': results.aggregate(avg=Avg('marks_obtained'))['avg'],
            'pass_percentage': results.filter(is_passed=True).count() / results.count() * 100 if results.count() > 0 else 0,
            'grade_distribution': results.values('grade').annotate(count=Count('grade'))
        }
        return Response(analytics)

class ExamViewSet(viewsets.ModelViewSet):
    """API endpoints for Exam management"""
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Exam.objects.filter(school=self.request.user.profile.school)
    
    @action(detail=True, methods=['post'])
    def publish_results(self, request, pk=None):
        """Publish exam results"""
        exam = self.get_object()
        exam.is_published = True
        exam.published_at = timezone.now()
        exam.save()
        return Response({'status': 'Results published successfully'})
    
    @action(detail=True, methods=['get'])
    def result_analytics(self, request, pk=None):
        """Get comprehensive result analytics"""
        exam = self.get_object()
        schedules = exam.schedules.all()
        all_results = StudentExamResult.objects.filter(exam_schedule__in=schedules)
        
        analytics = {
            'total_students': all_results.values('student').distinct().count(),
            'subjects_conducted': schedules.count(),
            'overall_pass_percentage': all_results.filter(is_passed=True).count() / all_results.count() * 100 if all_results.count() > 0 else 0,
            'subject_wise_performance': [],
            'grade_distribution': all_results.values('grade').annotate(count=Count('grade'))
        }
        
        for schedule in schedules:
            results = all_results.filter(exam_schedule=schedule)
            subject_analytics = {
                'subject_name': schedule.class_subject.subject.name,
                'class_name': schedule.class_subject.school_class.name,
                'total_students': results.count(),
                'average_marks': results.aggregate(avg=Avg('marks_obtained'))['avg'],
                'pass_percentage': results.filter(is_passed=True).count() / results.count() * 100 if results.count() > 0 else 0
            }
            analytics['subject_wise_performance'].append(subject_analytics)
        
        return Response(analytics)

class AssignmentViewSet(viewsets.ModelViewSet):
    """API endpoints for Assignment management"""
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Assignment.objects.filter(
            class_subject__subject__school=self.request.user.profile.school
        )
    
    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """Get all submissions for this assignment"""
        assignment = self.get_object()
        submissions = assignment.submissions.all()
        serializer = StudentAssignmentSerializer(submissions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def submission_analytics(self, request, pk=None):
        """Get submission analytics"""
        assignment = self.get_object()
        submissions = assignment.submissions.all()
        
        analytics = {
            'total_submissions': submissions.filter(is_submitted=True).count(),
            'pending_submissions': submissions.filter(is_submitted=False).count(),
            'graded_submissions': submissions.filter(is_graded=True).count(),
            'average_marks': submissions.filter(is_graded=True).aggregate(avg=Avg('marks_obtained'))['avg'],
            'on_time_submissions': submissions.filter(is_late=False, is_submitted=True).count(),
            'late_submissions': submissions.filter(is_late=True).count()
        }
        return Response(analytics)

class TimetableViewSet(viewsets.ModelViewSet):
    """API endpoints for Timetable management"""
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Timetable.objects.filter(
            school_class__school=self.request.user.profile.school
        )
    
    @action(detail=False, methods=['get'])
    def weekly_schedule(self, request):
        """Get weekly timetable for a class"""
        class_id = request.query_params.get('class_id')
        section_id = request.query_params.get('section_id')
        
        if not class_id or not section_id:
            return Response({'error': 'class_id and section_id are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        timetable = self.get_queryset().filter(
            school_class_id=class_id,
            section_id=section_id,
            is_active=True
        ).order_by('day_of_week', 'period_number')
        
        serializer = self.get_serializer(timetable, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def teacher_schedule(self, request):
        """Get teacher's weekly schedule"""
        teacher_id = request.query_params.get('teacher_id')
        
        if not teacher_id:
            return Response({'error': 'teacher_id is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        schedule = self.get_queryset().filter(
            teacher_id=teacher_id,
            is_active=True
        ).order_by('day_of_week', 'period_number')
        
        serializer = self.get_serializer(schedule, many=True)
        return Response(serializer.data)

class AttendanceViewSet(viewsets.ModelViewSet):
    """API endpoints for Attendance management"""
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Attendance.objects.filter(
            timetable__school_class__school=self.request.user.profile.school
        )
    
    @action(detail=True, methods=['post'])
    def mark_attendance(self, request, pk=None):
        """Mark attendance for students"""
        attendance = self.get_object()
        student_attendance_data = request.data.get('student_attendance', [])
        
        for data in student_attendance_data:
            student_attendance, created = StudentClassAttendance.objects.get_or_create(
                attendance=attendance,
                student_id=data['student_id'],
                defaults={
                    'status': data['status'],
                    'arrival_time': data.get('arrival_time'),
                    'remarks': data.get('remarks', '')
                }
            )
            if not created:
                student_attendance.status = data['status']
                student_attendance.arrival_time = data.get('arrival_time')
                student_attendance.remarks = data.get('remarks', '')
                student_attendance.save()
        
        attendance.is_completed = True
        attendance.save()
        
        return Response({'status': 'Attendance marked successfully'})
    
    @action(detail=False, methods=['get'])
    def attendance_report(self, request):
        """Get attendance report for class/student"""
        class_id = request.query_params.get('class_id')
        student_id = request.query_params.get('student_id')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        queryset = StudentClassAttendance.objects.filter(
            attendance__timetable__school_class__school=self.request.user.profile.school
        )
        
        if class_id:
            queryset = queryset.filter(attendance__timetable__school_class_id=class_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if from_date:
            queryset = queryset.filter(attendance__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(attendance__date__lte=to_date)
        
        # Calculate attendance statistics
        total_classes = queryset.count()
        present_count = queryset.filter(status='PRESENT').count()
        absent_count = queryset.filter(status='ABSENT').count()
        late_count = queryset.filter(status='LATE').count()
        
        report = {
            'total_classes': total_classes,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'attendance_percentage': (present_count / total_classes * 100) if total_classes > 0 else 0,
            'attendance_records': StudentClassAttendanceSerializer(queryset, many=True).data
        }
        
        return Response(report)

class HolidayViewSet(viewsets.ModelViewSet):
    """API endpoints for Holiday management"""
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Holiday.objects.filter(school=self.request.user.profile.school)
    
    @action(detail=False, methods=['get'])
    def upcoming_holidays(self, request):
        """Get upcoming holidays"""
        upcoming = self.get_queryset().filter(
            date__gte=timezone.now().date(),
            is_active=True
        ).order_by('date')[:10]
        
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def academic_calendar(self, request):
        """Get academic calendar for the year"""
        year = request.query_params.get('year', timezone.now().year)
        
        holidays = self.get_queryset().filter(
            date__year=year,
            is_active=True
        ).order_by('date')
        
        calendar_data = {}
        for holiday in holidays:
            month_key = holiday.date.strftime('%Y-%m')
            if month_key not in calendar_data:
                calendar_data[month_key] = []
            calendar_data[month_key].append(HolidaySerializer(holiday).data)
        
        return Response(calendar_data) 