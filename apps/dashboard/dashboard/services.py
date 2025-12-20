from apps.dashboard.instructors.models import Instructor
from apps.dashboard.courses.selectors import CourseSelector
from apps.headless.students.selectors import StudentSelector
from apps.headless.courses.selectors import EnrollmentSelector
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta



class DashboardKPIService():

    @staticmethod
    def get_kpi_data(instructor: Instructor):
        """
        Fetches Course count (with this month only count),
        student count (with signups this month),
        and enrolled count (with enrollments this month)
        """
        today = timezone.now()
        thiry_days_from_now = today - timedelta(days=30)

        active_course_queryset = CourseSelector.get_all_active(instructor)
        student_queryset = StudentSelector.get_all(instructor)
        enrollments_queryset = EnrollmentSelector.get_all(instructor)

        course_counts = active_course_queryset.aggregate(
            total_count = Count('id'),
            count_this_month=Count(
                'id',
                filter=Q(created_at__gte=thiry_days_from_now)
            )
        )

        student_counts = student_queryset.aggregate(
            total_count = Count('id'),
            count_this_month=Count(
                'id',
                filter=Q(created_at__gte=thiry_days_from_now)
            )
        )

        enrollment_counts = enrollments_queryset.aggregate(
            total_count = Count('id'),
            count_this_month=Count(
                'id',
                filter=Q(created_at__gte=thiry_days_from_now)
            )
        )

        return {
            'courses': {
                'total': course_counts.get('total_count', 0),
                'in_last_thirty_days': course_counts.get('count_this_month', 0)
            },
            'signups': {
                'total': student_counts.get('total_count', 0),
                'in_last_thirty_days': student_counts.get('count_this_month', 0)
            },
            'enrollments': {
                'total': enrollment_counts.get('total_count', 0),
                'in_last_thirty_days': enrollment_counts.get('count_this_month', 0)
            },
        }