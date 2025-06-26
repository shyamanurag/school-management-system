from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.utils import timezone
from datetime import timedelta, datetime
from .models import (
    Subject, ExamType, ExamSchedule, Exam, QuestionBank, OnlineExam,
    StudentExamAttempt, ExamResult, GradingScheme, HallTicket, ExamReport
)
from .serializers import (
    SubjectSerializer, ExamTypeSerializer, ExamScheduleSerializer, ExamSerializer,
    QuestionBankSerializer, OnlineExamSerializer, StudentExamAttemptSerializer,
    ExamResultSerializer, GradingSchemeSerializer, HallTicketSerializer,
    ExamReportSerializer
)

class SubjectViewSet(viewsets.ModelViewSet):
    """API endpoints for Subject management"""
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Subject.objects.filter(school=self.request.user.profile.school)
    
    @action(detail=True, methods=['get'])
    def performance_analytics(self, request, pk=None):
        """Get subject performance analytics"""
        subject = self.get_object()
        
        # Get recent exam results for this subject
        recent_results = ExamResult.objects.filter(
            exam__subject=subject,
            exam__schedule__academic_year=self.request.user.profile.school.current_academic_year
        )
        
        analytics = {
            'total_exams': subject.exams.count(),
            'total_students_appeared': recent_results.count(),
            'average_marks': recent_results.aggregate(avg=Avg('total_marks_obtained'))['avg'] or 0,
            'pass_percentage': (recent_results.filter(is_passed=True).count() / recent_results.count() * 100) if recent_results.count() > 0 else 0,
            'grade_distribution': recent_results.values('grade').annotate(count=Count('id')),
            'class_wise_performance': recent_results.values('exam__school_class__name').annotate(
                avg_marks=Avg('total_marks_obtained'),
                count=Count('id')
            )
        }
        return Response(analytics)
    
    @action(detail=True, methods=['get'])
    def question_bank_stats(self, request, pk=None):
        """Get question bank statistics for subject"""
        subject = self.get_object()
        questions = subject.questions.filter(is_active=True)
        
        stats = {
            'total_questions': questions.count(),
            'difficulty_distribution': questions.values('difficulty_level').annotate(count=Count('id')),
            'question_type_distribution': questions.values('question_type').annotate(count=Count('id')),
            'chapter_wise_distribution': questions.values('chapter').annotate(count=Count('id')),
            'approved_questions': questions.filter(is_approved=True).count(),
            'pending_approval': questions.filter(is_approved=False).count()
        }
        return Response(stats)

class ExamTypeViewSet(viewsets.ModelViewSet):
    """API endpoints for Exam Type management"""
    serializer_class = ExamTypeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ExamType.objects.filter(school=self.request.user.profile.school)

class ExamScheduleViewSet(viewsets.ModelViewSet):
    """API endpoints for Exam Schedule management"""
    serializer_class = ExamScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ExamSchedule.objects.filter(school=self.request.user.profile.school)
    
    @action(detail=True, methods=['post'])
    def publish_schedule(self, request, pk=None):
        """Publish exam schedule"""
        schedule = self.get_object()
        schedule.is_published = True
        schedule.save()
        
        # Generate hall tickets for students
        self._generate_hall_tickets(schedule)
        
        return Response({'status': 'Schedule published successfully'})
    
    @action(detail=True, methods=['get'])
    def schedule_overview(self, request, pk=None):
        """Get comprehensive schedule overview"""
        schedule = self.get_object()
        
        overview = {
            'schedule_details': self.get_serializer(schedule).data,
            'total_exams': schedule.exams.count(),
            'total_students': self._get_total_students(schedule),
            'hall_tickets_generated': schedule.hall_tickets.count(),
            'results_status': {
                'exams_completed': schedule.exams.filter(is_completed=True).count(),
                'results_entered': schedule.exams.filter(results_entered=True).count(),
                'results_verified': schedule.exams.filter(results_verified=True).count()
            },
            'upcoming_exams': schedule.exams.filter(
                exam_date__gte=timezone.now().date(),
                is_completed=False
            ).count()
        }
        return Response(overview)
    
    def _get_total_students(self, schedule):
        """Get total students for all exams in schedule"""
        from students.models import Student
        class_ids = schedule.applicable_classes.values_list('id', flat=True)
        return Student.objects.filter(current_class_id__in=class_ids, is_active=True).count()
    
    def _generate_hall_tickets(self, schedule):
        """Generate hall tickets for all students in schedule"""
        from students.models import Student
        
        for class_obj in schedule.applicable_classes.all():
            students = Student.objects.filter(current_class=class_obj, is_active=True)
            for student in students:
                HallTicket.objects.get_or_create(
                    student=student,
                    exam_schedule=schedule,
                    defaults={
                        'exam_center': 'Main Campus',
                        'general_instructions': 'Please follow all examination rules and regulations.',
                        'is_issued': True,
                        'issued_date': timezone.now().date()
                    }
                )

class ExamViewSet(viewsets.ModelViewSet):
    """API endpoints for Exam management"""
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Exam.objects.filter(schedule__school=self.request.user.profile.school)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark exam as completed"""
        exam = self.get_object()
        exam.is_completed = True
        exam.save()
        
        return Response({'status': 'Exam marked as completed'})
    
    @action(detail=True, methods=['get'])
    def exam_analytics(self, request, pk=None):
        """Get comprehensive exam analytics"""
        exam = self.get_object()
        results = exam.results.all()
        
        if not results.exists():
            return Response({'message': 'No results available yet'})
        
        analytics = {
            'basic_stats': {
                'total_students': results.count(),
                'appeared_students': results.filter(is_absent=False).count(),
                'absent_students': results.filter(is_absent=True).count(),
                'passed_students': results.filter(is_passed=True).count(),
                'failed_students': results.filter(is_passed=False).count()
            },
            'performance_metrics': {
                'highest_marks': results.aggregate(max=Max('total_marks_obtained'))['max'] or 0,
                'lowest_marks': results.aggregate(min=Min('total_marks_obtained'))['min'] or 0,
                'average_marks': results.aggregate(avg=Avg('total_marks_obtained'))['avg'] or 0,
                'average_percentage': results.aggregate(avg=Avg('percentage'))['avg'] or 0,
                'pass_percentage': (results.filter(is_passed=True).count() / results.filter(is_absent=False).count() * 100) if results.filter(is_absent=False).count() > 0 else 0
            },
            'grade_distribution': results.values('grade').annotate(count=Count('id')),
            'section_wise_performance': results.values('student__section__name').annotate(
                avg_marks=Avg('total_marks_obtained'),
                count=Count('id'),
                pass_count=Count('id', filter=Q(is_passed=True))
            ),
            'mark_ranges': {
                '90-100': results.filter(percentage__gte=90).count(),
                '80-89': results.filter(percentage__gte=80, percentage__lt=90).count(),
                '70-79': results.filter(percentage__gte=70, percentage__lt=80).count(),
                '60-69': results.filter(percentage__gte=60, percentage__lt=70).count(),
                '50-59': results.filter(percentage__gte=50, percentage__lt=60).count(),
                'Below 50': results.filter(percentage__lt=50).count()
            }
        }
        return Response(analytics)
    
    @action(detail=True, methods=['get'])
    def toppers_list(self, request, pk=None):
        """Get toppers list for exam"""
        exam = self.get_object()
        limit = int(request.query_params.get('limit', 10))
        
        toppers = exam.results.filter(is_absent=False).order_by('-total_marks_obtained')[:limit]
        
        toppers_data = []
        for i, result in enumerate(toppers, 1):
            toppers_data.append({
                'rank': i,
                'student_name': result.student.full_name,
                'class_section': f"{result.student.current_class.name} - {result.student.section.name}",
                'marks_obtained': result.total_marks_obtained,
                'total_marks': exam.total_marks,
                'percentage': result.percentage,
                'grade': result.grade
            })
        
        return Response(toppers_data)

class QuestionBankViewSet(viewsets.ModelViewSet):
    """API endpoints for Question Bank management"""
    serializer_class = QuestionBankSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return QuestionBank.objects.filter(school=self.request.user.profile.school)
    
    @action(detail=True, methods=['post'])
    def approve_question(self, request, pk=None):
        """Approve a question in question bank"""
        question = self.get_object()
        question.is_approved = True
        question.reviewed_by = request.user
        question.save()
        
        return Response({'status': 'Question approved successfully'})
    
    @action(detail=False, methods=['get'])
    def question_analytics(self, request):
        """Get question bank analytics"""
        questions = self.get_queryset()
        
        analytics = {
            'total_questions': questions.count(),
            'approved_questions': questions.filter(is_approved=True).count(),
            'pending_approval': questions.filter(is_approved=False).count(),
            'subject_wise_distribution': questions.values('subject__name').annotate(count=Count('id')),
            'difficulty_distribution': questions.values('difficulty_level').annotate(count=Count('id')),
            'question_type_distribution': questions.values('question_type').annotate(count=Count('id')),
            'usage_statistics': {
                'most_used_questions': questions.order_by('-times_used')[:5].values('question_text', 'times_used'),
                'average_score': questions.aggregate(avg=Avg('average_score'))['avg'] or 0
            }
        }
        return Response(analytics)
    
    @action(detail=False, methods=['post'])
    def generate_question_paper(self, request):
        """Generate question paper from question bank"""
        subject_id = request.data.get('subject_id')
        class_id = request.data.get('class_id')
        total_marks = request.data.get('total_marks', 100)
        difficulty_distribution = request.data.get('difficulty_distribution', {
            'EASY': 40, 'MEDIUM': 40, 'HARD': 20
        })
        
        questions = self.get_queryset().filter(
            subject_id=subject_id,
            school_class_id=class_id,
            is_approved=True,
            is_active=True
        )
        
        # Generate question paper logic
        selected_questions = self._select_questions_by_difficulty(
            questions, total_marks, difficulty_distribution
        )
        
        return Response({
            'total_questions': len(selected_questions),
            'total_marks': sum(q['marks'] for q in selected_questions),
            'questions': selected_questions
        })
    
    def _select_questions_by_difficulty(self, questions, total_marks, difficulty_distribution):
        """Select questions based on difficulty distribution"""
        selected = []
        
        for difficulty, percentage in difficulty_distribution.items():
            marks_needed = (total_marks * percentage) / 100
            difficulty_questions = questions.filter(difficulty_level=difficulty)
            
            current_marks = 0
            for question in difficulty_questions:
                if current_marks + question.marks <= marks_needed:
                    selected.append({
                        'id': question.id,
                        'question_text': question.question_text,
                        'marks': question.marks,
                        'difficulty': question.difficulty_level,
                        'question_type': question.question_type
                    })
                    current_marks += question.marks
                    
                    if current_marks >= marks_needed:
                        break
        
        return selected

class OnlineExamViewSet(viewsets.ModelViewSet):
    """API endpoints for Online Exam management"""
    serializer_class = OnlineExamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return OnlineExam.objects.filter(exam__schedule__school=self.request.user.profile.school)
    
    @action(detail=True, methods=['get'])
    def exam_config(self, request, pk=None):
        """Get online exam configuration for students"""
        online_exam = self.get_object()
        
        config = {
            'exam_details': {
                'name': online_exam.exam.exam_name,
                'duration_minutes': online_exam.exam.duration_minutes,
                'total_marks': online_exam.exam.total_marks,
                'passing_marks': online_exam.exam.passing_marks,
                'start_time': online_exam.exam.start_time,
                'end_time': online_exam.exam.end_time
            },
            'exam_settings': {
                'auto_submit': online_exam.auto_submit,
                'allow_review': online_exam.allow_review,
                'show_result_immediately': online_exam.show_result_immediately,
                'randomize_questions': online_exam.randomize_questions,
                'randomize_options': online_exam.randomize_options,
                'full_screen_required': online_exam.full_screen_required,
                'disable_copy_paste': online_exam.disable_copy_paste,
                'disable_right_click': online_exam.disable_right_click
            },
            'security_settings': {
                'monitor_tab_switching': online_exam.monitor_tab_switching,
                'max_tab_switches': online_exam.max_tab_switches,
                'capture_screenshots': online_exam.capture_screenshots,
                'enable_webcam_monitoring': online_exam.enable_webcam_monitoring
            }
        }
        return Response(config)
    
    @action(detail=True, methods=['get'])
    def live_monitoring(self, request, pk=None):
        """Get live monitoring data for online exam"""
        online_exam = self.get_object()
        attempts = online_exam.attempts.filter(status='IN_PROGRESS')
        
        monitoring_data = []
        for attempt in attempts:
            monitoring_data.append({
                'student_name': attempt.student.full_name,
                'start_time': attempt.start_time,
                'time_elapsed': (timezone.now() - attempt.start_time).total_seconds() / 60 if attempt.start_time else 0,
                'tab_switches': attempt.tab_switches,
                'violations': {
                    'copy_paste_attempts': attempt.copy_paste_attempts,
                    'right_click_attempts': attempt.right_click_attempts,
                    'full_screen_exits': attempt.full_screen_exits
                },
                'browser_info': attempt.browser_info,
                'ip_address': str(attempt.ip_address) if attempt.ip_address else None
            })
        
        return Response({
            'total_active_attempts': attempts.count(),
            'monitoring_data': monitoring_data,
            'exam_duration': online_exam.exam.duration_minutes,
            'time_remaining': self._calculate_time_remaining(online_exam)
        })
    
    def _calculate_time_remaining(self, online_exam):
        """Calculate time remaining for exam"""
        exam_end = datetime.combine(
            online_exam.exam.exam_date, 
            online_exam.exam.end_time
        )
        now = datetime.now()
        
        if now < exam_end:
            return (exam_end - now).total_seconds() / 60
        return 0

class StudentExamAttemptViewSet(viewsets.ModelViewSet):
    """API endpoints for Student Exam Attempt management"""
    serializer_class = StudentExamAttemptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'student_profile'):
            return StudentExamAttempt.objects.filter(student=user.student_profile)
        else:
            return StudentExamAttempt.objects.filter(
                online_exam__exam__schedule__school=user.profile.school
            )
    
    @action(detail=True, methods=['post'])
    def start_exam(self, request, pk=None):
        """Start exam attempt"""
        attempt = self.get_object()
        
        if attempt.status != 'NOT_STARTED':
            return Response({'error': 'Exam already started'}, status=status.HTTP_400_BAD_REQUEST)
        
        attempt.status = 'IN_PROGRESS'
        attempt.start_time = timezone.now()
        attempt.browser_info = request.data.get('browser_info', {})
        attempt.device_info = request.data.get('device_info', {})
        attempt.ip_address = self._get_client_ip(request)
        attempt.save()
        
        return Response({'status': 'Exam started successfully'})
    
    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """Submit answer for a question"""
        attempt = self.get_object()
        
        if attempt.status != 'IN_PROGRESS':
            return Response({'error': 'Exam not in progress'}, status=status.HTTP_400_BAD_REQUEST)
        
        question_id = request.data.get('question_id')
        answer = request.data.get('answer')
        
        if not attempt.responses:
            attempt.responses = {}
        
        attempt.responses[str(question_id)] = answer
        attempt.last_saved_at = timezone.now()
        attempt.save()
        
        return Response({'status': 'Answer saved successfully'})
    
    @action(detail=True, methods=['post'])
    def submit_exam(self, request, pk=None):
        """Submit exam attempt"""
        attempt = self.get_object()
        
        if attempt.status != 'IN_PROGRESS':
            return Response({'error': 'Exam not in progress'}, status=status.HTTP_400_BAD_REQUEST)
        
        attempt.status = 'COMPLETED'
        attempt.end_time = timezone.now()
        attempt.actual_duration_minutes = (
            (attempt.end_time - attempt.start_time).total_seconds() / 60
        )
        
        # Calculate scores
        self._calculate_exam_scores(attempt)
        attempt.save()
        
        return Response({'status': 'Exam submitted successfully'})
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _calculate_exam_scores(self, attempt):
        """Calculate exam scores based on responses"""
        # Simplified scoring logic - in reality this would be more complex
        total_marks = 0
        correct_answers = 0
        
        for question_id, answer in attempt.responses.items():
            try:
                question = QuestionBank.objects.get(id=question_id)
                if question.correct_answer == answer or question.correct_option == answer:
                    total_marks += question.marks
                    correct_answers += 1
            except QuestionBank.DoesNotExist:
                continue
        
        attempt.total_marks_obtained = total_marks
        attempt.percentage = (total_marks / attempt.online_exam.exam.total_marks) * 100 if attempt.online_exam.exam.total_marks > 0 else 0

class ExamResultViewSet(viewsets.ModelViewSet):
    """API endpoints for Exam Result management"""
    serializer_class = ExamResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'student_profile'):
            return ExamResult.objects.filter(student=user.student_profile)
        else:
            return ExamResult.objects.filter(exam__schedule__school=user.profile.school)
    
    @action(detail=True, methods=['post'])
    def verify_result(self, request, pk=None):
        """Verify exam result"""
        result = self.get_object()
        result.verified_by = request.user
        result.verification_date = timezone.now().date()
        result.save()
        
        return Response({'status': 'Result verified successfully'})
    
    @action(detail=False, methods=['get'])
    def result_analytics(self, request):
        """Get result analytics"""
        results = self.get_queryset()
        exam_id = request.query_params.get('exam_id')
        
        if exam_id:
            results = results.filter(exam_id=exam_id)
        
        analytics = {
            'total_results': results.count(),
            'pass_percentage': (results.filter(is_passed=True).count() / results.count() * 100) if results.count() > 0 else 0,
            'average_percentage': results.aggregate(avg=Avg('percentage'))['avg'] or 0,
            'grade_distribution': results.values('grade').annotate(count=Count('id')),
            'subject_wise_performance': results.values('exam__subject__name').annotate(
                avg_percentage=Avg('percentage'),
                count=Count('id')
            )
        }
        return Response(analytics)

class GradingSchemeViewSet(viewsets.ModelViewSet):
    """API endpoints for Grading Scheme management"""
    serializer_class = GradingSchemeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return GradingScheme.objects.filter(school=self.request.user.profile.school)

class HallTicketViewSet(viewsets.ModelViewSet):
    """API endpoints for Hall Ticket management"""
    serializer_class = HallTicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return HallTicket.objects.filter(exam_schedule__school=self.request.user.profile.school)
    
    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """Generate hall ticket PDF"""
        hall_ticket = self.get_object()
        # PDF generation logic would go here
        return Response({'status': 'PDF generated successfully'})

class ExamReportViewSet(viewsets.ModelViewSet):
    """API endpoints for Exam Report management"""
    serializer_class = ExamReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ExamReport.objects.filter(school=self.request.user.profile.school)
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Generate exam report"""
        report_type = request.data.get('report_type')
        exam_schedule_id = request.data.get('exam_schedule_id')
        
        # Report generation logic
        report_data = self._generate_report_data(report_type, exam_schedule_id)
        
        report = ExamReport.objects.create(
            school=request.user.profile.school,
            exam_schedule_id=exam_schedule_id,
            report_type=report_type,
            generated_by=request.user,
            report_data=report_data
        )
        
        return Response({
            'report_id': report.id,
            'status': 'Report generated successfully',
            'report_data': report_data
        })
    
    def _generate_report_data(self, report_type, exam_schedule_id):
        """Generate report data based on type"""
        # Simplified report generation
        if report_type == 'RESULT_ANALYSIS':
            return {'message': 'Result analysis report data'}
        elif report_type == 'CLASS_PERFORMANCE':
            return {'message': 'Class performance report data'}
        else:
            return {'message': f'{report_type} report data'} 