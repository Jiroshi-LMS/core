import django_filters

from apps.headless.courses.models import Enrollments
from .models import Course, CourseLesson


class CourseFilters(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    status = django_filters.CharFilter(field_name="access_status", lookup_expr="iexact")
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = Course
        fields = ['title', 'status', 'created_at']


class LessonFilters(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    status = django_filters.CharFilter(field_name="access_status", lookup_expr="iexact")
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = CourseLesson
        fields = ['title', 'status', 'created_at']


class EnrollmentFilters(django_filters.FilterSet):
    course_uuid = django_filters.UUIDFilter(field_name="course__uuid")
    student_uuid = django_filters.UUIDFilter(field_name="student__uuid")
    course_title = django_filters.CharFilter(field_name="course__title", lookup_expr='icontains')
    student_identifier = django_filters.CharFilter(field_name="student__identifier", lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter(field_name='created_at')

    class Meta:
        model = Enrollments
        fields = ['course_uuid', 'student_uuid', 'course_title',
                  'student_identifier', 'created_at']