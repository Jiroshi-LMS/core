import django_filters

from apps.dashboard.courses.models import Course, CourseLesson
from .models import Enrollments

class CourseFilters(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = Course
        fields = ['title', 'created_at']


class CourseLessonFilters(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = CourseLesson
        fields = ['title', 'created_at']


class EnrolledCourseFilters(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="course__title", lookup_expr="icontains")
    created_at = django_filters.DateFromToRangeFilter(field_name="course__created_at")
    enrolled_at = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = Enrollments
        fields = ['title', 'created_at', 'enrolled_at']