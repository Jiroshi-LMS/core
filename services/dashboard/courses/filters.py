import django_filters
from .models import Course


class CourseFilters(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    status = django_filters.CharFilter(field_name="access_status", lookup_expr="iexact")

    class Meta:
        model = Course
        fields = ['title', 'status']