import django_filters

from apps.headless.students.models import Student


class StudentsFilterset(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter(field_name='created_at')

    class Meta:
        model = Student
        fields = ['created_at']