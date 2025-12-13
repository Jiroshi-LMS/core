import django_filters

from apps.dashboard.courses.models import Course

class CourseFilters(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = Course
        fields = ['title', 'created_at']