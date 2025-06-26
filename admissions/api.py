from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.utils import timezone
from datetime import timedelta, datetime
from .models import (
    AcademicSession, AdmissionCriteria, ApplicationForm, DocumentSubmission,
    EntranceTest, EntranceTestResult, Interview, InterviewSchedule,
    InterviewEvaluation, AdmissionResult, AdmissionReport
)
from .serializers import (
    AcademicSessionSerializer, AdmissionCriteriaSerializer, ApplicationFormSerializer,
    DocumentSubmissionSerializer, EntranceTestSerializer, EntranceTestResultSerializer,
    InterviewSerializer, InterviewScheduleSerializer, InterviewEvaluationSerializer,
    AdmissionResultSerializer, AdmissionReportSerializer
)

class AcademicSessionViewSet(viewsets.ModelViewSet):
    """API endpoints for Academic Session management"""
    serializer_class = AcademicSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AcademicSession.objects.filter(school=self.request.user.profile.school)
    
    @action(detail=True, methods=['post'])
    def publish_session(self, request, pk=None):
        """Publish academic session for applications"""
        session = self.get_object()
        session.is_published = True
        session.save()
        
        return Response({'status': 'Session published successfully'})
    
    @action(detail=True, methods=['get'])
    def session_analytics(self, request, pk=None):
        """Get comprehensive session analytics"""
        session = self.get_object()
        
        analytics = {
            'session_details': self.get_serializer(session).data,
            'application_stats': {
                'total_applications': session.applications.count(),
                'submitted_applications': session.applications.filter(status='SUBMITTED').count(),
                'draft_applications': session.applications.filter(status='DRAFT').count(),
                'selected_applications': session.applications.filter(status='SELECTED').count(),
                'rejected_applications': session.applications.filter(status='REJECTED').count()
            },
            'class_wise_applications': session.applications.values(
                'criteria__school_class__name'
            ).annotate(count=Count('id')),
            'category_wise_applications': session.applications.values('category').annotate(count=Count('id')),
            'payment_stats': {
                'fee_paid': session.applications.filter(application_fee_paid=True).count(),
                'fee_pending': session.applications.filter(application_fee_paid=False).count()
            },
            'document_verification_stats': self._get_document_stats(session),
            'entrance_test_stats': self._get_entrance_test_stats(session),
            'interview_stats': self._get_interview_stats(session)
        }
        return Response(analytics)
    
    def _get_document_stats(self, session):
        """Get document verification statistics"""
        total_docs = DocumentSubmission.objects.filter(application__session=session)
        return {
            'total_documents': total_docs.count(),
            'verified_documents': total_docs.filter(verification_status='VERIFIED').count(),
            'pending_documents': total_docs.filter(verification_status='PENDING').count(),
            'rejected_documents': total_docs.filter(verification_status='REJECTED').count()
        }
    
    def _get_entrance_test_stats(self, session):
        """Get entrance test statistics"""
        test_results = EntranceTestResult.objects.filter(application__session=session)
        return {
            'total_candidates': test_results.count(),
            'appeared_candidates': test_results.filter(is_present=True).count(),
            'qualified_candidates': test_results.filter(is_qualified=True).count(),
            'average_marks': test_results.aggregate(avg=Avg('marks_obtained'))['avg'] or 0
        }
    
    def _get_interview_stats(self, session):
        """Get interview statistics"""
        interviews = InterviewSchedule.objects.filter(application__session=session)
        return {
            'total_scheduled': interviews.count(),
            'completed_interviews': interviews.filter(is_completed=True).count(),
            'pending_interviews': interviews.filter(is_completed=False, is_cancelled=False).count(),
            'cancelled_interviews': interviews.filter(is_cancelled=True).count()
        }

class AdmissionCriteriaViewSet(viewsets.ModelViewSet):
    """API endpoints for Admission Criteria management"""
    serializer_class = AdmissionCriteriaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AdmissionCriteria.objects.filter(session__school=self.request.user.profile.school)
    
    @action(detail=True, methods=['get'])
    def seat_allocation_status(self, request, pk=None):
        """Get current seat allocation status"""
        criteria = self.get_object()
        applications = criteria.applications.filter(status__in=['SELECTED', 'ADMISSION_CONFIRMED'])
        
        status_data = {
            'total_seats': criteria.total_seats,
            'filled_seats': applications.count(),
            'available_seats': criteria.total_seats - applications.count(),
            'category_wise_allocation': {
                'general': applications.filter(category='GENERAL').count(),
                'sc': applications.filter(category='SC').count(),
                'st': applications.filter(category='ST').count(),
                'obc': applications.filter(category='OBC').count(),
                'ews': applications.filter(category='EWS').count(),
                'pwd': applications.filter(category='PWD').count()
            },
            'revenue_generated': applications.aggregate(
                total=Sum('criteria__admission_fee')
            )['total'] or 0
        }
        return Response(status_data)

class ApplicationFormViewSet(viewsets.ModelViewSet):
    """API endpoints for Application Form management"""
    serializer_class = ApplicationFormSerializer
    
    def get_permissions(self):
        """Allow unauthenticated access for creating applications"""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ApplicationForm.objects.filter(session__school=self.request.user.profile.school)
        return ApplicationForm.objects.none()
    
    @action(detail=True, methods=['post'])
    def submit_application(self, request, pk=None):
        """Submit application for review"""
        application = self.get_object()
        
        if application.status != 'DRAFT':
            return Response({'error': 'Only draft applications can be submitted'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Validate required documents
        required_docs = application.criteria.required_documents
        submitted_docs = application.documents.values_list('document_type', flat=True)
        
        missing_docs = set(required_docs) - set(submitted_docs)
        if missing_docs:
            return Response({
                'error': 'Missing required documents',
                'missing_documents': list(missing_docs)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'SUBMITTED'
        application.submitted_at = timezone.now()
        application.save()
        
        return Response({'status': 'Application submitted successfully'})
    
    @action(detail=True, methods=['post'])
    def approve_application(self, request, pk=None):
        """Approve application for next stage"""
        application = self.get_object()
        
        if application.status != 'UNDER_REVIEW':
            return Response({'error': 'Application not under review'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        next_status = self._determine_next_status(application)
        application.status = next_status
        application.reviewed_by = request.user
        application.review_notes = request.data.get('notes', '')
        application.save()
        
        # Schedule entrance test or interview if required
        if next_status == 'ENTRANCE_TEST_SCHEDULED':
            self._schedule_entrance_test(application)
        elif next_status == 'INTERVIEW_SCHEDULED':
            self._schedule_interview(application)
        
        return Response({'status': f'Application moved to {next_status}'})
    
    @action(detail=True, methods=['post'])
    def reject_application(self, request, pk=None):
        """Reject application"""
        application = self.get_object()
        application.status = 'REJECTED'
        application.reviewed_by = request.user
        application.review_notes = request.data.get('reason', '')
        application.save()
        
        return Response({'status': 'Application rejected'})
    
    @action(detail=True, methods=['get'])
    def application_timeline(self, request, pk=None):
        """Get application processing timeline"""
        application = self.get_object()
        
        timeline = [
            {
                'stage': 'Application Created',
                'date': application.created_at,
                'status': 'completed'
            }
        ]
        
        if application.submitted_at:
            timeline.append({
                'stage': 'Application Submitted',
                'date': application.submitted_at,
                'status': 'completed'
            })
        
        # Add other timeline events based on status
        self._add_timeline_events(timeline, application)
        
        return Response(timeline)
    
    def _determine_next_status(self, application):
        """Determine next status based on session configuration"""
        if application.session.is_entrance_test_required:
            return 'ENTRANCE_TEST_SCHEDULED'
        elif application.session.is_interview_required:
            return 'INTERVIEW_SCHEDULED'
        else:
            return 'SELECTED'
    
    def _schedule_entrance_test(self, application):
        """Schedule entrance test for application"""
        # Implementation for scheduling entrance test
        pass
    
    def _schedule_interview(self, application):
        """Schedule interview for application"""
        # Implementation for scheduling interview
        pass
    
    def _add_timeline_events(self, timeline, application):
        """Add timeline events based on application status"""
        status_map = {
            'ENTRANCE_TEST_SCHEDULED': 'Entrance Test Scheduled',
            'ENTRANCE_TEST_COMPLETED': 'Entrance Test Completed',
            'INTERVIEW_SCHEDULED': 'Interview Scheduled',
            'INTERVIEW_COMPLETED': 'Interview Completed',
            'SELECTED': 'Selected for Admission',
            'REJECTED': 'Application Rejected'
        }
        
        if application.status in status_map:
            timeline.append({
                'stage': status_map[application.status],
                'date': application.updated_at,
                'status': 'completed' if application.status in ['SELECTED', 'REJECTED'] else 'current'
            })

class DocumentSubmissionViewSet(viewsets.ModelViewSet):
    """API endpoints for Document Submission management"""
    serializer_class = DocumentSubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DocumentSubmission.objects.filter(
            application__session__school=self.request.user.profile.school
        )
    
    @action(detail=True, methods=['post'])
    def verify_document(self, request, pk=None):
        """Verify submitted document"""
        document = self.get_object()
        document.verification_status = 'VERIFIED'
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.verification_notes = request.data.get('notes', '')
        document.save()
        
        # Check if all required documents are verified
        self._check_application_document_status(document.application)
        
        return Response({'status': 'Document verified successfully'})
    
    @action(detail=True, methods=['post'])
    def reject_document(self, request, pk=None):
        """Reject submitted document"""
        document = self.get_object()
        document.verification_status = 'REJECTED'
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.verification_notes = request.data.get('reason', '')
        document.save()
        
        return Response({'status': 'Document rejected'})
    
    def _check_application_document_status(self, application):
        """Check if all documents are verified and update application status"""
        required_docs = set(application.criteria.required_documents)
        verified_docs = set(
            application.documents.filter(verification_status='VERIFIED').values_list(
                'document_type', flat=True
            )
        )
        
        if required_docs.issubset(verified_docs):
            if application.status == 'DOCUMENT_VERIFICATION':
                # Move to next stage
                if application.session.is_entrance_test_required:
                    application.status = 'ENTRANCE_TEST_SCHEDULED'
                elif application.session.is_interview_required:
                    application.status = 'INTERVIEW_SCHEDULED'
                else:
                    application.status = 'SELECTED'
                application.save()

class EntranceTestViewSet(viewsets.ModelViewSet):
    """API endpoints for Entrance Test management"""
    serializer_class = EntranceTestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EntranceTest.objects.filter(session__school=self.request.user.profile.school)
    
    @action(detail=True, methods=['post'])
    def declare_results(self, request, pk=None):
        """Declare entrance test results"""
        test = self.get_object()
        test.results_declared = True
        test.result_declaration_date = timezone.now().date()
        test.save()
        
        # Update application statuses based on results
        self._update_application_statuses_from_test(test)
        
        return Response({'status': 'Results declared successfully'})
    
    @action(detail=True, methods=['get'])
    def test_analytics(self, request, pk=None):
        """Get entrance test analytics"""
        test = self.get_object()
        results = test.results.all()
        
        analytics = {
            'total_candidates': results.count(),
            'appeared_candidates': results.filter(is_present=True).count(),
            'qualified_candidates': results.filter(is_qualified=True).count(),
            'qualification_rate': (results.filter(is_qualified=True).count() / results.filter(is_present=True).count() * 100) if results.filter(is_present=True).count() > 0 else 0,
            'performance_metrics': {
                'highest_marks': results.aggregate(max=Max('marks_obtained'))['max'] or 0,
                'lowest_marks': results.aggregate(min=Min('marks_obtained'))['min'] or 0,
                'average_marks': results.aggregate(avg=Avg('marks_obtained'))['avg'] or 0,
                'average_percentage': results.aggregate(avg=Avg('percentage'))['avg'] or 0
            },
            'mark_distribution': {
                '90-100%': results.filter(percentage__gte=90).count(),
                '80-89%': results.filter(percentage__gte=80, percentage__lt=90).count(),
                '70-79%': results.filter(percentage__gte=70, percentage__lt=80).count(),
                '60-69%': results.filter(percentage__gte=60, percentage__lt=70).count(),
                'Below 60%': results.filter(percentage__lt=60).count()
            }
        }
        return Response(analytics)
    
    def _update_application_statuses_from_test(self, test):
        """Update application statuses based on test results"""
        qualified_results = test.results.filter(is_qualified=True)
        
        for result in qualified_results:
            application = result.application
            if application.session.is_interview_required:
                application.status = 'INTERVIEW_SCHEDULED'
            else:
                application.status = 'SELECTED'
            application.save()
        
        # Update failed candidates
        failed_results = test.results.filter(is_qualified=False)
        for result in failed_results:
            result.application.status = 'REJECTED'
            result.application.save()

class InterviewViewSet(viewsets.ModelViewSet):
    """API endpoints for Interview management"""
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Interview.objects.filter(session__school=self.request.user.profile.school)
    
    @action(detail=True, methods=['get'])
    def interview_schedule(self, request, pk=None):
        """Get interview schedule for the day"""
        interview = self.get_object()
        schedules = interview.schedules.filter(is_cancelled=False).order_by('interview_time')
        
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'application_number': schedule.application.application_number,
                'student_name': schedule.application.full_name,
                'interview_time': schedule.interview_time,
                'room_number': schedule.room_number,
                'is_completed': schedule.is_completed,
                'evaluation_status': hasattr(schedule, 'evaluation')
            })
        
        return Response({
            'interview_date': interview.interview_date,
            'total_candidates': schedules.count(),
            'completed_interviews': schedules.filter(is_completed=True).count(),
            'pending_interviews': schedules.filter(is_completed=False).count(),
            'schedule': schedule_data
        })

class AdmissionResultViewSet(viewsets.ModelViewSet):
    """API endpoints for Admission Result management"""
    serializer_class = AdmissionResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AdmissionResult.objects.filter(
            application__session__school=self.request.user.profile.school
        )
    
    @action(detail=False, methods=['post'])
    def declare_final_results(self, request):
        """Declare final admission results"""
        session_id = request.data.get('session_id')
        
        # Process applications and generate results
        applications = ApplicationForm.objects.filter(
            session_id=session_id,
            status__in=['INTERVIEW_COMPLETED', 'ENTRANCE_TEST_COMPLETED']
        )
        
        results_created = 0
        for application in applications:
            result_status = self._calculate_final_result(application)
            
            result, created = AdmissionResult.objects.get_or_create(
                application=application,
                defaults={
                    'result_status': result_status,
                    'declared_date': timezone.now().date(),
                    'declared_by': request.user,
                    'confirmation_deadline': timezone.now().date() + timedelta(days=7),
                    'fee_payment_deadline': timezone.now().date() + timedelta(days=10)
                }
            )
            
            if created:
                results_created += 1
                # Update application status
                application.status = result_status
                application.save()
        
        return Response({
            'status': 'Results declared successfully',
            'results_created': results_created
        })
    
    def _calculate_final_result(self, application):
        """Calculate final admission result based on scores"""
        # Simplified logic - in reality this would be more complex
        total_score = 0
        
        # Add entrance test score if available
        if hasattr(application, 'entrance_test_result'):
            total_score += application.entrance_test_result.percentage * 0.6
        
        # Add interview score if available
        if hasattr(application, 'interview_schedule') and hasattr(application.interview_schedule, 'evaluation'):
            total_score += application.interview_schedule.evaluation.percentage * 0.4
        
        # Determine result based on score and seat availability
        if total_score >= 70:  # Simplified threshold
            return 'SELECTED'
        elif total_score >= 60:
            return 'WAITLISTED'
        else:
            return 'REJECTED'

class AdmissionReportViewSet(viewsets.ModelViewSet):
    """API endpoints for Admission Report management"""
    serializer_class = AdmissionReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AdmissionReport.objects.filter(session__school=self.request.user.profile.school)
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Generate admission report"""
        report_type = request.data.get('report_type')
        session_id = request.data.get('session_id')
        
        # Generate report data based on type
        report_data = self._generate_report_data(report_type, session_id)
        
        report = AdmissionReport.objects.create(
            session_id=session_id,
            report_type=report_type,
            generated_by=request.user,
            report_data=report_data
        )
        
        return Response({
            'report_id': report.id,
            'status': 'Report generated successfully',
            'report_data': report_data
        })
    
    def _generate_report_data(self, report_type, session_id):
        """Generate report data based on type"""
        session = AcademicSession.objects.get(id=session_id)
        
        if report_type == 'APPLICATION_SUMMARY':
            return self._generate_application_summary(session)
        elif report_type == 'CATEGORY_WISE_ANALYSIS':
            return self._generate_category_analysis(session)
        elif report_type == 'REVENUE_ANALYSIS':
            return self._generate_revenue_analysis(session)
        else:
            return {'message': f'{report_type} report data'}
    
    def _generate_application_summary(self, session):
        """Generate application summary report"""
        applications = session.applications.all()
        
        return {
            'total_applications': applications.count(),
            'status_breakdown': applications.values('status').annotate(count=Count('id')),
            'class_wise_breakdown': applications.values('criteria__school_class__name').annotate(count=Count('id')),
            'gender_breakdown': applications.values('gender').annotate(count=Count('id')),
            'payment_status': {
                'paid': applications.filter(application_fee_paid=True).count(),
                'pending': applications.filter(application_fee_paid=False).count()
            }
        }
    
    def _generate_category_analysis(self, session):
        """Generate category-wise analysis"""
        applications = session.applications.all()
        
        return {
            'category_distribution': applications.values('category').annotate(count=Count('id')),
            'category_wise_selection': applications.filter(status='SELECTED').values('category').annotate(count=Count('id')),
            'category_wise_performance': applications.values('category').annotate(
                total=Count('id'),
                selected=Count('id', filter=Q(status='SELECTED'))
            )
        }
    
    def _generate_revenue_analysis(self, session):
        """Generate revenue analysis"""
        applications = session.applications.filter(application_fee_paid=True)
        
        return {
            'total_application_fee_collected': applications.count() * applications.first().criteria.application_fee if applications.exists() else 0,
            'class_wise_revenue': applications.values('criteria__school_class__name').annotate(
                count=Count('id'),
                revenue=Count('id') * applications.first().criteria.application_fee if applications.exists() else 0
            ),
            'projected_admission_fee': AdmissionResult.objects.filter(
                application__session=session,
                result_status='SELECTED'
            ).count() * (applications.first().criteria.admission_fee if applications.exists() else 0)
        } 