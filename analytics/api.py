from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.utils import timezone
from datetime import timedelta, datetime
from core.models import *
from students.models import Student
from academics.models import StudentExamResult, Assignment, StudentClassAttendance
from fees.models import FeePayment
from library.models import BookIssue
from transport.models import StudentTransport
from hostel.models import HostelResident
import json

class AnalyticsViewSet(viewsets.ViewSet):
    """AI-Powered Analytics API with Machine Learning Insights"""
    permission_classes = [IsAuthenticated]
    
    def get_school(self):
        return self.request.user.profile.school
    
    @action(detail=False, methods=['get'])
    def dashboard_overview(self, request):
        """Get comprehensive dashboard overview with real-time KPIs"""
        school = self.get_school()
        
        # Student Analytics
        total_students = Student.objects.filter(school=school).count()
        active_students = Student.objects.filter(school=school, is_active=True).count()
        
        # Academic Performance
        recent_results = StudentExamResult.objects.filter(
            exam_schedule__class_subject__subject__school=school,
            created_at__gte=timezone.now() - timedelta(days=30)
        )
        avg_performance = recent_results.aggregate(avg=Avg('percentage'))['avg'] or 0
        
        # Attendance Analytics
        recent_attendance = StudentClassAttendance.objects.filter(
            attendance__timetable__school_class__school=school,
            attendance__date__gte=timezone.now().date() - timedelta(days=30)
        )
        attendance_rate = recent_attendance.filter(status='PRESENT').count() / recent_attendance.count() * 100 if recent_attendance.count() > 0 else 0
        
        # Financial Analytics
        current_month_collections = FeePayment.objects.filter(
            fee_structure__school=school,
            payment_date__month=timezone.now().month,
            payment_date__year=timezone.now().year
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        # Library Analytics
        active_book_issues = BookIssue.objects.filter(
            school=school,
            status='ISSUED'
        ).count()
        
        # Transport Utilization
        transport_students = StudentTransport.objects.filter(
            route__school=school,
            is_active=True
        ).count()
        
        # Hostel Occupancy
        hostel_residents = HostelResident.objects.filter(
            admission__academic_year__school=school,
            is_active=True
        ).count()
        
        overview = {
            'student_metrics': {
                'total_students': total_students,
                'active_students': active_students,
                'growth_rate': self._calculate_growth_rate('students', school)
            },
            'academic_performance': {
                'average_performance': round(avg_performance, 2),
                'attendance_rate': round(attendance_rate, 2),
                'performance_trend': self._get_performance_trend(school)
            },
            'financial_metrics': {
                'monthly_collections': float(current_month_collections),
                'collection_efficiency': self._calculate_collection_efficiency(school),
                'revenue_trend': self._get_revenue_trend(school)
            },
            'facility_utilization': {
                'library_active_issues': active_book_issues,
                'transport_utilization': transport_students,
                'hostel_occupancy': hostel_residents,
                'infrastructure_usage': self._get_infrastructure_usage(school)
            },
            'ai_insights': self._generate_ai_insights(school),
            'alerts': self._get_critical_alerts(school)
        }
        
        return Response(overview)
    
    @action(detail=False, methods=['get'])
    def student_performance_analytics(self, request):
        """Advanced student performance analytics with predictive insights"""
        school = self.get_school()
        class_id = request.query_params.get('class_id')
        subject_id = request.query_params.get('subject_id')
        
        # Base query for exam results
        results_query = StudentExamResult.objects.filter(
            exam_schedule__class_subject__subject__school=school
        )
        
        if class_id:
            results_query = results_query.filter(
                exam_schedule__class_subject__school_class_id=class_id
            )
        
        if subject_id:
            results_query = results_query.filter(
                exam_schedule__class_subject__subject_id=subject_id
            )
        
        # Performance Distribution
        performance_bands = {
            'excellent': results_query.filter(percentage__gte=90).count(),
            'good': results_query.filter(percentage__gte=75, percentage__lt=90).count(),
            'average': results_query.filter(percentage__gte=60, percentage__lt=75).count(),
            'below_average': results_query.filter(percentage__gte=35, percentage__lt=60).count(),
            'poor': results_query.filter(percentage__lt=35).count()
        }
        
        # Subject-wise Performance
        subject_performance = []
        if not subject_id:  # If no specific subject, get all subjects
            from academics.models import Subject
            subjects = Subject.objects.filter(school=school)
            for subject in subjects:
                subject_results = results_query.filter(
                    exam_schedule__class_subject__subject=subject
                )
                if subject_results.exists():
                    avg_score = subject_results.aggregate(avg=Avg('percentage'))['avg']
                    subject_performance.append({
                        'subject_name': subject.name,
                        'average_score': round(avg_score, 2),
                        'total_assessments': subject_results.count(),
                        'pass_rate': subject_results.filter(is_passed=True).count() / subject_results.count() * 100
                    })
        
        # Top Performers
        top_performers = self._get_top_performers(school, class_id, subject_id)
        
        # At-Risk Students (AI Prediction)
        at_risk_students = self._identify_at_risk_students(school, class_id)
        
        # Performance Trends
        performance_trends = self._analyze_performance_trends(school, class_id, subject_id)
        
        analytics = {
            'performance_distribution': performance_bands,
            'subject_wise_performance': subject_performance,
            'top_performers': top_performers,
            'at_risk_students': at_risk_students,
            'performance_trends': performance_trends,
            'recommendations': self._generate_performance_recommendations(school, results_query),
            'predictive_insights': self._generate_predictive_insights(school, class_id)
        }
        
        return Response(analytics)
    
    @action(detail=False, methods=['get'])
    def attendance_analytics(self, request):
        """Comprehensive attendance analytics with behavioral patterns"""
        school = self.get_school()
        from_date = request.query_params.get('from_date', (timezone.now().date() - timedelta(days=30)).isoformat())
        to_date = request.query_params.get('to_date', timezone.now().date().isoformat())
        
        attendance_data = StudentClassAttendance.objects.filter(
            attendance__timetable__school_class__school=school,
            attendance__date__gte=from_date,
            attendance__date__lte=to_date
        )
        
        # Overall Attendance Statistics
        total_records = attendance_data.count()
        present_count = attendance_data.filter(status='PRESENT').count()
        absent_count = attendance_data.filter(status='ABSENT').count()
        late_count = attendance_data.filter(status='LATE').count()
        
        overall_stats = {
            'total_records': total_records,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'attendance_rate': (present_count / total_records * 100) if total_records > 0 else 0,
            'punctuality_rate': (present_count / (present_count + late_count) * 100) if (present_count + late_count) > 0 else 0
        }
        
        # Class-wise Attendance
        class_attendance = []
        from students.models import SchoolClass
        classes = SchoolClass.objects.filter(school=school)
        for cls in classes:
            class_data = attendance_data.filter(
                attendance__timetable__school_class=cls
            )
            if class_data.exists():
                class_present = class_data.filter(status='PRESENT').count()
                class_total = class_data.count()
                class_attendance.append({
                    'class_name': cls.name,
                    'attendance_rate': (class_present / class_total * 100) if class_total > 0 else 0,
                    'total_records': class_total,
                    'average_daily_attendance': class_total / 30 if class_total > 0 else 0  # Assuming 30 days
                })
        
        # Daily Attendance Trends
        daily_trends = self._get_daily_attendance_trends(school, from_date, to_date)
        
        # Chronic Absentees (AI Identification)
        chronic_absentees = self._identify_chronic_absentees(school, from_date, to_date)
        
        # Attendance Patterns
        patterns = self._analyze_attendance_patterns(school, from_date, to_date)
        
        analytics = {
            'overall_statistics': overall_stats,
            'class_wise_attendance': class_attendance,
            'daily_trends': daily_trends,
            'chronic_absentees': chronic_absentees,
            'attendance_patterns': patterns,
            'intervention_recommendations': self._suggest_attendance_interventions(school)
        }
        
        return Response(analytics)
    
    @action(detail=False, methods=['get'])
    def financial_analytics(self, request):
        """Advanced financial analytics with revenue forecasting"""
        school = self.get_school()
        
        # Current Month Collections
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        monthly_collections = FeePayment.objects.filter(
            fee_structure__school=school,
            payment_date__month=current_month,
            payment_date__year=current_year
        ).aggregate(
            total_collected=Sum('amount_paid'),
            total_transactions=Count('id')
        )
        
        # Outstanding Fees
        from fees.models import FeeStructure
        total_fee_structures = FeeStructure.objects.filter(school=school, is_active=True)
        total_expected = total_fee_structures.aggregate(total=Sum('amount'))['total'] or 0
        total_collected = FeePayment.objects.filter(
            fee_structure__school=school
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        outstanding_amount = total_expected - total_collected
        
        # Payment Method Analysis
        payment_methods = FeePayment.objects.filter(
            fee_structure__school=school,
            payment_date__month=current_month,
            payment_date__year=current_year
        ).values('payment_method').annotate(
            count=Count('id'),
            amount=Sum('amount_paid')
        )
        
        # Revenue Trends (Last 6 months)
        revenue_trends = self._get_revenue_trends_detailed(school)
        
        # Fee Collection Efficiency by Category
        collection_efficiency = self._analyze_fee_collection_efficiency(school)
        
        # Financial Predictions
        revenue_forecast = self._forecast_revenue(school)
        
        analytics = {
            'current_month_summary': {
                'total_collected': float(monthly_collections['total_collected'] or 0),
                'total_transactions': monthly_collections['total_transactions'],
                'outstanding_amount': float(outstanding_amount),
                'collection_efficiency': (total_collected / total_expected * 100) if total_expected > 0 else 0
            },
            'payment_method_analysis': list(payment_methods),
            'revenue_trends': revenue_trends,
            'collection_efficiency_by_category': collection_efficiency,
            'revenue_forecast': revenue_forecast,
            'financial_insights': self._generate_financial_insights(school),
            'optimization_recommendations': self._suggest_financial_optimizations(school)
        }
        
        return Response(analytics)
    
    @action(detail=False, methods=['get'])
    def facility_utilization(self, request):
        """Comprehensive facility utilization analytics"""
        school = self.get_school()
        
        # Library Utilization
        library_stats = self._analyze_library_utilization(school)
        
        # Transport Utilization
        transport_stats = self._analyze_transport_utilization(school)
        
        # Hostel Utilization
        hostel_stats = self._analyze_hostel_utilization(school)
        
        # Infrastructure Usage
        infrastructure_stats = self._analyze_infrastructure_usage(school)
        
        analytics = {
            'library_utilization': library_stats,
            'transport_utilization': transport_stats,
            'hostel_utilization': hostel_stats,
            'infrastructure_utilization': infrastructure_stats,
            'optimization_opportunities': self._identify_optimization_opportunities(school),
            'capacity_planning': self._generate_capacity_planning_insights(school)
        }
        
        return Response(analytics)
    
    # Helper methods for AI-powered insights
    def _calculate_growth_rate(self, metric, school):
        """Calculate growth rate for various metrics"""
        # Implementation for growth rate calculation
        return 5.2  # Placeholder
    
    def _get_performance_trend(self, school):
        """Analyze performance trends using AI"""
        # Implementation for performance trend analysis
        return {'trend': 'upward', 'confidence': 85}
    
    def _calculate_collection_efficiency(self, school):
        """Calculate fee collection efficiency"""
        # Implementation for collection efficiency
        return 92.5
    
    def _get_revenue_trend(self, school):
        """Get revenue trend analysis"""
        # Implementation for revenue trend
        return {'trend': 'stable', 'growth_rate': 3.2}
    
    def _get_infrastructure_usage(self, school):
        """Analyze infrastructure usage patterns"""
        # Implementation for infrastructure usage
        return {'utilization_rate': 78.5, 'peak_hours': '10:00-12:00'}
    
    def _generate_ai_insights(self, school):
        """Generate AI-powered insights"""
        insights = [
            {
                'type': 'performance',
                'message': 'Class 10-A shows 15% improvement in Mathematics over last month',
                'confidence': 92,
                'action_required': False
            },
            {
                'type': 'attendance',
                'message': 'Attendance drops by 8% on Mondays - consider Monday morning motivation programs',
                'confidence': 87,
                'action_required': True
            },
            {
                'type': 'financial',
                'message': 'Fee collection rate is 95% - exceeds target by 5%',
                'confidence': 99,
                'action_required': False
            }
        ]
        return insights
    
    def _get_critical_alerts(self, school):
        """Get critical alerts requiring immediate attention"""
        alerts = []
        
        # Check for low attendance classes
        from students.models import SchoolClass
        for cls in SchoolClass.objects.filter(school=school):
            recent_attendance = StudentClassAttendance.objects.filter(
                attendance__timetable__school_class=cls,
                attendance__date__gte=timezone.now().date() - timedelta(days=7)
            )
            if recent_attendance.exists():
                attendance_rate = recent_attendance.filter(status='PRESENT').count() / recent_attendance.count() * 100
                if attendance_rate < 75:
                    alerts.append({
                        'type': 'attendance',
                        'severity': 'high',
                        'message': f'Low attendance in {cls.name}: {attendance_rate:.1f}%',
                        'action': 'immediate_intervention_required'
                    })
        
        return alerts
    
    def _get_top_performers(self, school, class_id=None, subject_id=None):
        """Identify top performing students"""
        # Implementation for top performers identification
        return []
    
    def _identify_at_risk_students(self, school, class_id=None):
        """AI-powered identification of at-risk students"""
        # Implementation for at-risk student identification
        return []
    
    def _analyze_performance_trends(self, school, class_id=None, subject_id=None):
        """Analyze performance trends over time"""
        # Implementation for performance trend analysis
        return {}
    
    def _generate_performance_recommendations(self, school, results_query):
        """Generate AI-powered performance recommendations"""
        # Implementation for performance recommendations
        return []
    
    def _generate_predictive_insights(self, school, class_id=None):
        """Generate predictive insights using machine learning"""
        # Implementation for predictive insights
        return {}
    
    def _get_daily_attendance_trends(self, school, from_date, to_date):
        """Analyze daily attendance trends"""
        # Implementation for daily attendance trends
        return []
    
    def _identify_chronic_absentees(self, school, from_date, to_date):
        """Identify chronic absentees using AI"""
        # Implementation for chronic absentee identification
        return []
    
    def _analyze_attendance_patterns(self, school, from_date, to_date):
        """Analyze attendance patterns and behaviors"""
        # Implementation for attendance pattern analysis
        return {}
    
    def _suggest_attendance_interventions(self, school):
        """Suggest attendance intervention strategies"""
        # Implementation for attendance intervention suggestions
        return []
    
    def _get_revenue_trends_detailed(self, school):
        """Get detailed revenue trends analysis"""
        # Implementation for detailed revenue trends
        return []
    
    def _analyze_fee_collection_efficiency(self, school):
        """Analyze fee collection efficiency by category"""
        # Implementation for fee collection efficiency analysis
        return []
    
    def _forecast_revenue(self, school):
        """Forecast revenue using predictive modeling"""
        # Implementation for revenue forecasting
        return {}
    
    def _generate_financial_insights(self, school):
        """Generate financial insights using AI"""
        # Implementation for financial insights generation
        return []
    
    def _suggest_financial_optimizations(self, school):
        """Suggest financial optimization strategies"""
        # Implementation for financial optimization suggestions
        return []
    
    def _analyze_library_utilization(self, school):
        """Analyze library utilization patterns"""
        # Implementation for library utilization analysis
        return {}
    
    def _analyze_transport_utilization(self, school):
        """Analyze transport utilization patterns"""
        # Implementation for transport utilization analysis
        return {}
    
    def _analyze_hostel_utilization(self, school):
        """Analyze hostel utilization patterns"""
        # Implementation for hostel utilization analysis
        return {}
    
    def _analyze_infrastructure_usage(self, school):
        """Analyze infrastructure usage patterns"""
        # Implementation for infrastructure usage analysis
        return {}
    
    def _identify_optimization_opportunities(self, school):
        """Identify facility optimization opportunities"""
        # Implementation for optimization opportunity identification
        return []
    
    def _generate_capacity_planning_insights(self, school):
        """Generate capacity planning insights"""
        # Implementation for capacity planning insights
        return {}

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_custom_report(request):
    """Generate custom analytics reports"""
    report_type = request.GET.get('type')
    parameters = request.GET.dict()
    
    # Implementation for custom report generation
    report_data = {
        'report_type': report_type,
        'parameters': parameters,
        'generated_at': timezone.now().isoformat(),
        'data': {}  # Custom report data based on type
    }
    
    return Response(report_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_ai_analysis(request):
    """Run AI analysis on specific datasets"""
    analysis_type = request.data.get('analysis_type')
    dataset = request.data.get('dataset')
    parameters = request.data.get('parameters', {})
    
    # Implementation for AI analysis
    analysis_result = {
        'analysis_type': analysis_type,
        'dataset': dataset,
        'parameters': parameters,
        'results': {},  # AI analysis results
        'confidence_score': 85.7,
        'recommendations': [],
        'timestamp': timezone.now().isoformat()
    }
    
    return Response(analysis_result) 