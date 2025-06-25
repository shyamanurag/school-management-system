from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
from core.models import Employee, HRAnalytics, Department, LeaveApplication, PerformanceReview, TrainingEnrollment
import json


class Command(BaseCommand):
    help = 'Generate comprehensive HR analytics reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='all',
            help='Type of analytics to generate (employee_turnover, performance_trends, attendance_patterns, all)',
        )
        parser.add_argument(
            '--department',
            type=str,
            help='Department ID to generate analytics for (optional)',
        )
        parser.add_argument(
            '--period',
            type=int,
            default=12,
            help='Analysis period in months (default: 12)',
        )

    def handle(self, *args, **options):
        analytics_type = options['type']
        department_id = options.get('department')
        period_months = options['period']
        
        # Calculate analysis period
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=period_months * 30)
        
        department = None
        if department_id:
            try:
                department = Department.objects.get(id=department_id)
                self.stdout.write(f"Generating analytics for department: {department.name}")
            except Department.DoesNotExist:
                raise CommandError(f'Department with ID "{department_id}" does not exist.')
        
        self.stdout.write(f"Generating HR analytics from {start_date} to {end_date}")
        
        if analytics_type == 'all' or analytics_type == 'employee_turnover':
            self.generate_employee_turnover_analytics(start_date, end_date, department)
        
        if analytics_type == 'all' or analytics_type == 'performance_trends':
            self.generate_performance_trends_analytics(start_date, end_date, department)
        
        if analytics_type == 'all' or analytics_type == 'training_effectiveness':
            self.generate_training_effectiveness_analytics(start_date, end_date, department)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully generated HR analytics reports')
        )

    def generate_employee_turnover_analytics(self, start_date, end_date, department=None):
        """Generate employee turnover analytics"""
        self.stdout.write("Generating Employee Turnover Analytics...")
        
        # Base queryset
        employees_qs = Employee.objects.all()
        if department:
            employees_qs = employees_qs.filter(department=department)
        
        # Calculate metrics
        total_employees = employees_qs.filter(employment_status='ACTIVE').count()
        terminated_employees = employees_qs.filter(
            employment_status__in=['TERMINATED', 'RESIGNED'],
            date_of_leaving__range=[start_date, end_date]
        ).count()
        
        new_hires = employees_qs.filter(
            date_of_joining__range=[start_date, end_date]
        ).count()
        
        # Calculate turnover rate
        turnover_rate = (terminated_employees / total_employees * 100) if total_employees > 0 else 0
        
        # Department-wise breakdown
        dept_breakdown = {}
        if not department:  # Only if not filtering by specific department
            for dept in Department.objects.all():
                dept_total = Employee.objects.filter(department=dept, employment_status='ACTIVE').count()
                dept_terminated = Employee.objects.filter(
                    department=dept,
                    employment_status__in=['TERMINATED', 'RESIGNED'],
                    date_of_leaving__range=[start_date, end_date]
                ).count()
                dept_rate = (dept_terminated / dept_total * 100) if dept_total > 0 else 0
                dept_breakdown[dept.name] = {
                    'total_employees': dept_total,
                    'terminated': dept_terminated,
                    'turnover_rate': round(dept_rate, 2)
                }
        
        # Generate insights
        insights = []
        if turnover_rate > 15:
            insights.append("High turnover rate detected - requires immediate attention")
        elif turnover_rate > 10:
            insights.append("Moderate turnover rate - monitor closely")
        else:
            insights.append("Healthy turnover rate")
        
        if new_hires > terminated_employees:
            insights.append("Positive growth - more hires than departures")
        
        # Recommendations
        recommendations = []
        if turnover_rate > 15:
            recommendations.extend([
                "Conduct exit interviews to identify root causes",
                "Review compensation and benefits packages",
                "Implement employee retention programs",
                "Improve work-life balance initiatives"
            ])
        
        # Store analytics
        analytics_data = {
            'total_employees': total_employees,
            'terminated_employees': terminated_employees,
            'new_hires': new_hires,
            'turnover_rate': round(turnover_rate, 2),
            'department_breakdown': dept_breakdown
        }
        
        HRAnalytics.objects.create(
            analytics_type='EMPLOYEE_TURNOVER',
            department=department,
            analysis_period_start=start_date,
            analysis_period_end=end_date,
            metrics_data=analytics_data,
            key_insights=insights,
            recommendations=recommendations,
            risk_score=min(turnover_rate / 2, 10),  # Scale to 0-10
            is_automated=True
        )
        
        self.stdout.write(f"  - Total Employees: {total_employees}")
        self.stdout.write(f"  - Terminated: {terminated_employees}")
        self.stdout.write(f"  - New Hires: {new_hires}")
        self.stdout.write(f"  - Turnover Rate: {turnover_rate:.2f}%")

    def generate_performance_trends_analytics(self, start_date, end_date, department=None):
        """Generate performance trends analytics"""
        self.stdout.write("Generating Performance Trends Analytics...")
        
        # Base queryset
        reviews_qs = PerformanceReview.objects.filter(
            review_period_start__gte=start_date,
            review_period_end__lte=end_date,
            status='COMPLETED'
        )
        
        if department:
            reviews_qs = reviews_qs.filter(employee__department=department)
        
        # Calculate metrics
        total_reviews = reviews_qs.count()
        if total_reviews == 0:
            self.stdout.write("  - No completed performance reviews found for the period")
            return
        
        avg_overall_rating = reviews_qs.aggregate(avg_rating=Avg('overall_rating'))['avg_rating'] or 0
        avg_manager_rating = reviews_qs.aggregate(avg_rating=Avg('manager_rating'))['avg_rating'] or 0
        avg_self_rating = reviews_qs.aggregate(avg_rating=Avg('self_rating'))['avg_rating'] or 0
        
        # Performance distribution
        rating_distribution = {
            'excellent': reviews_qs.filter(overall_rating__gte=4.5).count(),
            'good': reviews_qs.filter(overall_rating__gte=3.5, overall_rating__lt=4.5).count(),
            'average': reviews_qs.filter(overall_rating__gte=2.5, overall_rating__lt=3.5).count(),
            'below_average': reviews_qs.filter(overall_rating__lt=2.5).count(),
        }
        
        # Department comparison (if not filtering by department)
        dept_comparison = {}
        if not department:
            for dept in Department.objects.all():
                dept_reviews = reviews_qs.filter(employee__department=dept)
                if dept_reviews.exists():
                    dept_avg = dept_reviews.aggregate(avg_rating=Avg('overall_rating'))['avg_rating']
                    dept_comparison[dept.name] = round(dept_avg, 2)
        
        # Generate insights
        insights = []
        if avg_overall_rating >= 4.0:
            insights.append("Excellent overall performance across the organization")
        elif avg_overall_rating >= 3.0:
            insights.append("Good performance levels maintained")
        else:
            insights.append("Performance improvement needed organization-wide")
        
        if avg_self_rating > avg_manager_rating + 0.5:
            insights.append("Employees tend to rate themselves higher than managers - calibration needed")
        
        # Recommendations
        recommendations = []
        if avg_overall_rating < 3.0:
            recommendations.extend([
                "Implement performance improvement programs",
                "Provide additional training and development opportunities",
                "Review goal-setting processes"
            ])
        
        if rating_distribution['below_average'] > total_reviews * 0.2:
            recommendations.append("Focus on underperformers with targeted support")
        
        # Store analytics
        analytics_data = {
            'total_reviews': total_reviews,
            'avg_overall_rating': round(avg_overall_rating, 2),
            'avg_manager_rating': round(avg_manager_rating, 2),
            'avg_self_rating': round(avg_self_rating, 2),
            'rating_distribution': rating_distribution,
            'department_comparison': dept_comparison
        }
        
        HRAnalytics.objects.create(
            analytics_type='PERFORMANCE_TRENDS',
            department=department,
            analysis_period_start=start_date,
            analysis_period_end=end_date,
            metrics_data=analytics_data,
            key_insights=insights,
            recommendations=recommendations,
            risk_score=max(0, (3.0 - avg_overall_rating) * 2),  # Higher risk for lower performance
            is_automated=True
        )
        
        self.stdout.write(f"  - Total Reviews: {total_reviews}")
        self.stdout.write(f"  - Average Overall Rating: {avg_overall_rating:.2f}")
        self.stdout.write(f"  - Performance Distribution: {rating_distribution}")

    def generate_training_effectiveness_analytics(self, start_date, end_date, department=None):
        """Generate training effectiveness analytics"""
        self.stdout.write("Generating Training Effectiveness Analytics...")
        
        # Base queryset
        enrollments_qs = TrainingEnrollment.objects.filter(
            enrollment_date__range=[start_date, end_date]
        )
        
        if department:
            enrollments_qs = enrollments_qs.filter(employee__department=department)
        
        # Calculate metrics
        total_enrollments = enrollments_qs.count()
        if total_enrollments == 0:
            self.stdout.write("  - No training enrollments found for the period")
            return
        
        completed_trainings = enrollments_qs.filter(status='COMPLETED').count()
        completion_rate = (completed_trainings / total_enrollments * 100) if total_enrollments > 0 else 0
        
        # Average scores
        avg_final_score = enrollments_qs.filter(
            final_score__isnull=False
        ).aggregate(avg_score=Avg('final_score'))['avg_score'] or 0
        
        avg_trainer_rating = enrollments_qs.filter(
            trainer_rating__isnull=False
        ).aggregate(avg_rating=Avg('trainer_rating'))['avg_rating'] or 0
        
        # Certification metrics
        certificates_issued = enrollments_qs.filter(certificate_issued=True).count()
        certification_rate = (certificates_issued / completed_trainings * 100) if completed_trainings > 0 else 0
        
        # Training type effectiveness
        type_effectiveness = {}
        for enrollment in enrollments_qs.filter(status='COMPLETED'):
            training_type = enrollment.training_program.training_type
            if training_type not in type_effectiveness:
                type_effectiveness[training_type] = {
                    'count': 0,
                    'avg_score': 0,
                    'avg_rating': 0
                }
            type_effectiveness[training_type]['count'] += 1
            if enrollment.final_score:
                type_effectiveness[training_type]['avg_score'] += enrollment.final_score
            if enrollment.trainer_rating:
                type_effectiveness[training_type]['avg_rating'] += enrollment.trainer_rating
        
        # Calculate averages
        for training_type in type_effectiveness:
            count = type_effectiveness[training_type]['count']
            if count > 0:
                type_effectiveness[training_type]['avg_score'] = round(
                    type_effectiveness[training_type]['avg_score'] / count, 2
                )
                type_effectiveness[training_type]['avg_rating'] = round(
                    type_effectiveness[training_type]['avg_rating'] / count, 2
                )
        
        # Generate insights
        insights = []
        if completion_rate >= 90:
            insights.append("Excellent training completion rate")
        elif completion_rate >= 70:
            insights.append("Good training engagement")
        else:
            insights.append("Low training completion rate - review training programs")
        
        if avg_final_score >= 80:
            insights.append("High learning effectiveness demonstrated")
        elif avg_final_score >= 60:
            insights.append("Moderate learning outcomes")
        else:
            insights.append("Learning effectiveness needs improvement")
        
        # Recommendations
        recommendations = []
        if completion_rate < 70:
            recommendations.extend([
                "Review training scheduling and accessibility",
                "Implement mandatory training policies",
                "Improve training engagement strategies"
            ])
        
        if avg_trainer_rating < 3.5:
            recommendations.append("Evaluate and improve trainer quality")
        
        if certification_rate < 80:
            recommendations.append("Review certification criteria and processes")
        
        # Store analytics
        analytics_data = {
            'total_enrollments': total_enrollments,
            'completed_trainings': completed_trainings,
            'completion_rate': round(completion_rate, 2),
            'avg_final_score': round(avg_final_score, 2),
            'avg_trainer_rating': round(avg_trainer_rating, 2),
            'certificates_issued': certificates_issued,
            'certification_rate': round(certification_rate, 2),
            'type_effectiveness': type_effectiveness
        }
        
        HRAnalytics.objects.create(
            analytics_type='TRAINING_EFFECTIVENESS',
            department=department,
            analysis_period_start=start_date,
            analysis_period_end=end_date,
            metrics_data=analytics_data,
            key_insights=insights,
            recommendations=recommendations,
            risk_score=max(0, (90 - completion_rate) / 10),  # Higher risk for lower completion
            is_automated=True
        )
        
        self.stdout.write(f"  - Total Enrollments: {total_enrollments}")
        self.stdout.write(f"  - Completion Rate: {completion_rate:.2f}%")
        self.stdout.write(f"  - Average Final Score: {avg_final_score:.2f}")
        self.stdout.write(f"  - Certificates Issued: {certificates_issued}") 