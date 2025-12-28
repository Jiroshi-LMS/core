from apps.core.decorators import handle_exceptions
from apps.core.throttles.dashboard_throttle import InstructorRateThrottle
from apps.dashboard.common.utilities.Response import Res
from apps.dashboard.common.utilities.Paginator import DashboardPageNumberPaginator
from apps.headless.students.models import Student
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter


from .filters import StudentsFilterset
from .serializers import StudentListSerializer


class StudentListView(ListAPIView):
    """
    View for listing instructor students
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [InstructorRateThrottle]
    pagination_class = DashboardPageNumberPaginator
    serializer_class = StudentListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentsFilterset
    search_fields = ['identifier']
    ordering_fields = ['created_at', 'enrollments_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Student.objects.filter(
            instructor=self.request.user
        ).annotate(
            enrollments_count=Count("enrollments")
        )

    @handle_exceptions
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.paginator.get_paginated_response(data=serializer.data, msg="Students Fetched !")
