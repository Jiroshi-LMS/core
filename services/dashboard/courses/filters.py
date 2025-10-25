import django_filters
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